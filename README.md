# LLM-Powered SQL Chatbot

## Quickstart
1. Copy `.env.example` to `.env` and fill in credentials.
2. `docker-compose up --build`
3. Visit `http://localhost:8000/ping` to verify.
4. Use `/chat` endpoint or React widget in `frontend/`.

## Architecture
- FastAPI backend
- PostgreSQL 15
- JWT auth
- OpenAI function-calling for NL→SQL

## Testing
```bash
pytest --maxfail=1 --disable-warnings -q
