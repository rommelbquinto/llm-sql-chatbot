import os, yaml
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
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()
    cur.execute(sql, {'fleet_id': fleet_id})
    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
