from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
SECRET = 'your_jwt_secret'

security = HTTPBearer()

def get_current_fleet(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=['HS256'])
        return payload['fleet_id']
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
