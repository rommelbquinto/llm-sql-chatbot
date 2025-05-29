from fastapi import FastAPI
from .routes import router

app = FastAPI()
app.include_router(router)

@app.get('/ping')
async def ping():
    return {'status': 'ok'}
