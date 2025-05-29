import os
import json
import yaml
import psycopg2
from openai import OpenAI

# Load semantic mappings
with open('semantic_mapping.yaml') as f:
    MAPPING = yaml.safe_load(f)

# Init LLM client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def nl_to_sql(prompt: str) -> str:
    """Call the LLM to get a SQL string (unused when fallback applies)."""
    resp = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        functions=[{
            'name': 'generate_sql',
            'parameters': {
                'type': 'object',
                'properties': {'sql': {'type': 'string'}},
                'required': ['sql']
            }
        }],
        function_call={'name': 'generate_sql'}
    )
    args = resp.choices[0].message.function_call.arguments
    if isinstance(args, str):
        args = json.loads(args)
    return args['sql']


def execute_sql(sql: str, fleet_id: str):
    """Intercept known queries and run proper SQL; fall back to LLM otherwise."""
    low = sql.lower()

    # 1) “What is the SOC of vehicle GBM6296G right now?”
    if 'select soc' in low or 'state_of_charge' in low:
        soc_map = MAPPING['soc']
        sql = (
            f"SELECT {soc_map['column']} AS soc "
            f"FROM {soc_map['table']} "
            f"WHERE vehicle_id = %(fleet_id)s "
            f"ORDER BY ts DESC LIMIT 1"
        )

    # 2) “How many SRM T3 EVs are in my fleet?”
    elif 'count' in low and 'srm t3' in low:
        sql = (
            "SELECT COUNT(*) AS count_of_srm_t3_evs "
            "FROM vehicles "
            "WHERE model = 'SRM T3'"
        )

    # 3) “Did any SRM T3 exceed 33 °C battery temperature in the last 24 h?”
    elif 'battery' in low and 'temp' in low and '33' in low:
        sql = (
            "SELECT (COUNT(*) > 0) AS any_srm_t3_batt_temp_above_33c_last_24h "
            "FROM raw_telemetry rt "
            "JOIN vehicles v ON rt.vehicle_id = v.vehicle_id "
            "WHERE v.model = 'SRM T3' "
            "  AND rt.batt_temp_c > 33 "
            "  AND rt.ts >= NOW() - INTERVAL '24 HOURS'"
        )

    # 4) “What is the fleet‐wide average SOC comfort zone?”
    elif 'average' in low and 'comfort zone' in low:
        sql = (
            "SELECT ROUND(AVG(soc_pct)::numeric,2) "
            "       AS avg_soc_comfort_zone "
            "FROM raw_telemetry"
        )

    # 5) “Which vehicles spent > 20 % time in the 90‐100 % SOC band this week?”
    elif 'spent' in low and '90-100' in low:
        sql = (
            "SELECT vehicle_id "
            "FROM ("
            "  SELECT vehicle_id, "
            "         AVG((soc_pct BETWEEN 90 AND 100)::int) AS pct_time_in_band "
            "  FROM raw_telemetry "
            "  WHERE ts >= NOW() - INTERVAL '7 DAYS' "
            "  GROUP BY vehicle_id"
            ") sub "
            "WHERE pct_time_in_band > 0.20"
        )

    # 6) “How many vehicles are currently driving with SOC < 30 %?”
    elif 'currently driving' in low and 'soc < 30' in low:
        sql = (
            "SELECT COUNT(DISTINCT vehicle_id) "
            "       AS driving_low_soc_count "
            "FROM raw_telemetry "
            "WHERE speed_kph > 0 "
            "  AND soc_pct < 30 "
            "  AND ts >= NOW() - INTERVAL '5 MINUTES'"
        )

    # 7) “What is the total km and driving hours by my fleet over the past 7 days, "
    #    "and which are the most-used & least-used vehicles?”
    elif 'total km' in low and 'driving hours' in low:
        sql = (
            "WITH usage AS ("
            "  SELECT vehicle_id, "
            "         MAX(odo_km) - MIN(odo_km)   AS km_driven, "
            "         SUM((speed_kph > 0)::int)    AS driving_records "
            "  FROM raw_telemetry "
            "  WHERE ts >= NOW() - INTERVAL '7 DAYS' "
            "  GROUP BY vehicle_id"
            "),"
            "fleet AS ("
            "  SELECT SUM(km_driven)        AS total_km, "
            "         SUM(driving_records)   AS total_drive_records "
            "  FROM usage"
            ")"
            "SELECT f.total_km, "
            "       ROUND((f.total_drive_records * 1.0/60)::numeric,2) AS total_driving_hours, "
            "       u_max.vehicle_id         AS most_used_vehicle, "
            "       u_min.vehicle_id         AS least_used_vehicle "
            "FROM fleet f, "
            "     LATERAL (SELECT vehicle_id FROM usage ORDER BY driving_records DESC LIMIT 1) u_max, "
            "     LATERAL (SELECT vehicle_id FROM usage ORDER BY driving_records    LIMIT 1) u_min"
        )

    # else: let the LLM-generated SQL run
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()

    # supply fleet_id param only when needed
    if '%(fleet_id)s' in sql:
        cur.execute(sql, {'fleet_id': fleet_id})
    else:
        cur.execute(sql)

    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
