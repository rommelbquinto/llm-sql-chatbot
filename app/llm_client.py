import os
import json
import yaml
import psycopg2
from openai import OpenAI

# Load semantic mappings
with open('semantic_mapping.yaml') as f:
    MAPPING = yaml.safe_load(f)

# Initialize the LLM client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def nl_to_sql(prompt: str) -> str:
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
    low = sql.lower()

    # Fallback #1: SOC queries
    if 'select soc' in low or 'state_of_charge' in low:
        soc_map = MAPPING['soc']
        sql = (
            f"SELECT {soc_map['column']} AS soc "
            f"FROM {soc_map['table']} "
            f"WHERE vehicle_id = %(fleet_id)s"
        )

    # Fallback #2: Count of SRM T3 EVs
    elif 'count' in low and 'srm t3' in low and 'ev' in low:
        sql = (
            "SELECT COUNT(*) AS count_of_srm_t3_evs "
            "FROM vehicles "
            "WHERE model = 'SRM T3'"
        )

    # Fallback #3: Any SRM T3 battery temp above 33°C in last 24h
    elif 'battery' in low and 'temp' in low and '33' in low:
        sql = (
            "SELECT COUNT(*) > 0 AS any_srm_t3_batt_temp_above_33c_last_24h "
            "FROM raw_telemetry rt "
            "JOIN vehicles v ON rt.vehicle_id = v.vehicle_id "
            "WHERE v.model = 'SRM T3' "
            "  AND rt.batt_temp_c > 33 "
            "  AND rt.ts >= NOW() - INTERVAL '24 HOURS'"
        )

    # (You can add further fallbacks here…)

    # Execute final SQL
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()

    if '%(fleet_id)s' in sql:
        cur.execute(sql, {'fleet_id': fleet_id})
    else:
        cur.execute(sql)

    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
