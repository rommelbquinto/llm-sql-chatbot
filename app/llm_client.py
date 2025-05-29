import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

MAPPING = None

def load_mapping():
    global MAPPING
    import yaml
    with open('semantic_mapping.yaml') as f:
        MAPPING = yaml.safe_load(f)

load_mapping()

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
    return response.choices[0].message.function_call.arguments['sql']

def execute_sql(sql: str, fleet_id: str):
    # Connect and run parameterized query with timeout and row limit
    import psycopg2
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=10)
    cur = conn.cursor()
    cur.execute(sql, {'fleet_id': fleet_id})
    rows = cur.fetchmany(5000)
    cur.close()
    conn.close()
    return rows
