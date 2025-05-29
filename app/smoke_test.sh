cat > smoke_test.sh <<'EOF'
#!/usr/bin/env bash
set -e

export PYTHONPATH=$(pwd)
echo "JWT_SECRET: $JWT_SECRET"

export JWT_TOKEN=$(
  python3 - <<'PY'
import os, jwt
secret = os.getenv("JWT_SECRET") or ""
if not secret:
    raise SystemExit("JWT_SECRET not set")
print(jwt.encode({"fleet_id":"GBM6296G"}, secret, algorithm="HS256"))
PY
)
echo "JWT_TOKEN: $JWT_TOKEN"

python3 - <<'PY'
import httpx, json
print(json.dumps(httpx.get("http://localhost:8000/ping").json(), indent=2))
PY

# SOC query
python3 - <<'PY'
import os, httpx, json
token = os.getenv("JWT_TOKEN")
resp = httpx.post(
  "http://localhost:8000/chat",
  json={"user_input":"What is the SOC of vehicle GBM6296G right now?"},
  headers={"Authorization":f"Bearer {token}"}
)
print("→ SOC query:", json.dumps(resp.json(), indent=2))
PY

# Count query
python3 - <<'PY'
import os, httpx, json
token = os.getenv("JWT_TOKEN")
resp = httpx.post(
  "http://localhost:8000/chat",
  json={"user_input":"Count of SRM T3 EVs"},
  headers={"Authorization":f"Bearer {token}"}
)
print("→ Count query:", json.dumps(resp.json(), indent=2))
PY

# Temperature query
python3 - <<'PY'
import os, httpx, json
token = os.getenv("JWT_TOKEN")
resp = httpx.post(
  "http://localhost:8000/chat",
  json={"user_input":"Any SRM T3 battery temp above 33°C in the last 24 hours?"},
  headers={"Authorization":f"Bearer {token}"}
)
print("→ Temp check query:", json.dumps(resp.json(), indent=2))
PY
EOF
