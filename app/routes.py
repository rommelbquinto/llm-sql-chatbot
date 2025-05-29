import os
from fastapi import APIRouter, Depends
from .auth import get_current_fleet
from .llm_client import nl_to_sql, execute_sql

router = APIRouter()

@router.get("/ping")
async def ping():
    # DEBUG: reveal the secret this process is using
    return {
        "status": "ok",
        "jwt_secret": os.getenv("JWT_SECRET", "<not-set>")
    }

@router.post("/chat")
async def chat(body: dict, fleet=Depends(get_current_fleet)):
    nl = body.get("user_input", "")
    sql = nl_to_sql(nl)
    rows = execute_sql(sql, fleet_id=fleet)
    return {"query": nl, "sql": sql, "results": rows}
