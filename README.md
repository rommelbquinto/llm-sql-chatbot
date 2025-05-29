# LLM-Powered SQL Chatbot

## Configuration
- **OPENAI_API_KEY**: Obtain your API key from the OpenAI Dashboard under API Keys (https://platform.openai.com/account/api-keys). Create a new secret if needed and keep it secure.
  
- **JWT_SECRET**: Generate a strong, random secret for signing JWTs. You can use one of these methods:
  - **OpenSSL** (Linux/Mac): ```bash openssl rand -hex 32```
  - **Python**: ```bash python3 -c "import secrets; print(secrets.token_hex(32))"```
  - Copy the resulting string and set it as `JWT_SECRET` in your `.env` file.

- **DATABASE_URL**: Connection string for your PostgreSQL instance (e.g., from Render, Heroku, or local Postgres).

## Quickstart
1. Copy `.env.example` to `.env` and fill in the variables.
2. Place your CSVs in `data/` and push to GitHub.
3. Start services:
   ```bash
   docker-compose up --build
   python import_data.py
4. Verify: `curl http://localhost:8000/ping`
5. Query the chat endpoint:
   ```bash
   curl -X POST http://localhost:8000/chat \
   -H "Authorization: Bearer <JWT>" \
   -H "Content-Type: application/json" \
   -d '{"user_input":"Count of SRM T3 EVs"}'

## Architecture
- FastAPI backend
- PostgreSQL 15
- JWT auth
- OpenAI function-calling for NL→SQL

## Testing
```bash
pytest --maxfail=1 --disable-warnings -q

### Dockerfile
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
