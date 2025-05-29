import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def token():
    # generate valid JWT with fleet_id claim
    import jwt
    return jwt.encode({'fleet_id':'GBM6296G'}, 'your_jwt_secret', algorithm='HS256')

def test_ping():
    r = client.get('/ping')
    assert r.status_code == 200
    assert r.json() == {'status':'ok'}

@pytest.mark.parametrize('nl_query', [
    'What is the SOC of vehicle GBM6296G right now?',
    'Count of SRM T3 EVs',
    'Any SRM T3 battery temp above 33°C in the last 24 hours?'
])
def test_chat(nl_query, token):
    r = client.post('/chat', json={'user_input': nl_query}, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    data = r.json()
    assert 'sql' in data and 'results' in data
