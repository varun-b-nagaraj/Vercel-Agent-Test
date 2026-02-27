import json
import os
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3").strip()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()

def handler(request):
    try:
        body = request.get_json() or {}
        prompt = (body.get("prompt") or "Say 'pong'").strip()

        url = f"{OLLAMA_BASE_URL}/api/chat"
        headers = {"Content-Type": "application/json"}
        if OLLAMA_API_KEY:
            headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

        r = requests.post(
            url,
            headers=headers,
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60,
        )

        # Return upstream status + small snippet for debugging
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}

        content = ""
        if isinstance(data, dict):
            msg = data.get("message") or {}
            content = msg.get("content") or data.get("response") or ""

        return {
            "statusCode": r.status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "ok": r.ok,
                "status": r.status_code,
                "model": OLLAMA_MODEL,
                "response": content,
                "debug_keys_present": {
                    "has_api_key": bool(OLLAMA_API_KEY),
                    "base_url": OLLAMA_BASE_URL,
                }
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"ok": False, "error": str(e)}),
        }