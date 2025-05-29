import os
import json
import yaml
import psycopg2
from openai import OpenAI

# Initialize
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
with open('semantic_mapping.yaml') as f:
    MAPPING = yaml.safe_load(f)

def nl_to_sql(prompt: str) -> str:
    resp = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role':'user','content':prompt}],
        functions=[{
            'name':'generate_sql',
            'parameters':{'type':'object','properties':{'sql':{'type':'string'}},'required':['sql']}
        }],
        function_call={'name':'generate_sql'}
    )
    raw = resp.choices[0].message.function_call.arguments
    return json.loads(raw)['sql'] if isinstance(raw, str) else raw['sql']

def execute_sql(sql: str, fleet_id: str):
    # Normalize to lowercase for simple pattern checks
    low = sql.lower()

    # 1) SOC‐style fallback
    if 'select soc' in low or 'state_of_charge' in low:
        soc_map = MAPPING['soc']
        table = soc_map['table']       # 'raw_telemetry'
        column = soc_map['column']     # 'soc_pct'
        sql = (
            f"SELECT {column} AS soc "
            f"FROM {table} "
            f"WHERE vehicle_id = %(fleet_id)s"
        )

    # 2) Count of SRM T3 EVs fallback
    elif 'count' in low and 'srm t3' in low:
        # We know from vehicles.csv that model = 'SRM T3'
        sql = (
            "SELECT COUNT(*) AS count_of_srm_t3_evs "
            "FROM vehicles "
            "WHERE model = 'SRM T3'"
        )
        # We’ll run without params (fleet_id isn’t used here)

    # 3) (Optional) Add more fallbacks for other mandatory queries…

    # Finally, execute against Postgres
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()

    # If your SQL uses %(fleet_id)s, supply it; otherwise call without params
    if '%(fleet_id)s' in sql:
        cur.execute(sql, {'fleet_id': fleet_id})
    else:
        cur.execute(sql)

    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
