from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
token = '<YOUR_JWT_TOKEN>'

# Health check
resp = client.get('/ping')
assert resp.json() == {'status':'ok'}

# Chat endpoint
resp = client.post(
    '/chat',
    json={'user_input':'Count of fleet vehicles'},
    headers={'Authorization': f'Bearer {token}'}
)
print(resp.json())
