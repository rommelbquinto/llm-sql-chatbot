import os, yaml
from psycopg2 import errors
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Load NL→column mapping
with open('semantic_mapping.yaml') as f:
    MAPPING = yaml.safe_load(f)

def nl_to_sql(prompt: str) -> str:
    # Call OpenAI with function schema and mapping
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role':'user','content': prompt}],
        functions=[{
            'name':'generate_sql',
            'parameters':{
                'type':'object',
                'properties':{
                    'sql':{'type':'string'}
                },
                'required':['sql']
            }
        }],
        function_call={'name':'generate_sql'}
    )
    # The arguments field may be returned as a JSON string, so parse it
    import json
    raw_args = response.choices[0].message.function_call.arguments
    if isinstance(raw_args, str):
        parsed = json.loads(raw_args)
    else:
        parsed = raw_args
    return parsed['sql']

def execute_sql(sql: str, fleet_id: str):
    import psycopg2
    from psycopg2 import errors
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()
    try:
        cur.execute(sql, {'fleet_id': fleet_id})
    except (errors.UndefinedColumn, errors.UndefinedTable):
        # SOC/state_of_charge fallback
        lowered = sql.lower()
        if ('select soc' in lowered or 'select state_of_charge' in lowered):
            soc_map = MAPPING['soc']
            table = soc_map['table']      # raw_telemetry
            column = soc_map['column']    # soc_pct
            fallback_sql = (
                f"SELECT {column} AS soc "
                f"FROM {table} "
                f"WHERE vehicle_id = %(fleet_id)s"
            )
            cur.execute(fallback_sql, {'fleet_id': fleet_id})
        else:
            raise
    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
