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
    # Pre‐emptively catch any SOC query and reroute it
    low = sql.lower()
    if 'select soc' in low or 'state_of_charge' in low:
        soc_map = MAPPING['soc']
        table = soc_map['table']       # raw_telemetry
        column = soc_map['column']     # soc_pct
        sql = f"SELECT {column} AS soc FROM {table} WHERE vehicle_id = %(fleet_id)s"

    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()
    cur.execute(sql, {'fleet_id': fleet_id})
    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
