import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/api/main")
def health_get():
    return jsonify({"ok": True, "msg": "api is live (GET)"}), 200

@app.post("/api/main")
def health_post():
    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "Say pong").strip()
    return jsonify({"ok": True, "echo": prompt}), 200


# Optional: Ollama test endpoint (uncomment when health works)
@app.post("/api/ollama")
def ollama():
    base = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3")
    key = os.getenv("OLLAMA_API_KEY", "")

    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "Say pong").strip()

    url = f"{base}/api/chat"
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    r = requests.post(
        url,
        headers=headers,
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
        timeout=60,
    )

    # pass-through status + response for debugging
    data = {}
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    content = ""
    if isinstance(data, dict):
        msg = data.get("message") or {}
        content = msg.get("content") or data.get("response") or ""

    return jsonify({
        "ok": r.ok,
        "status": r.status_code,
        "model": model,
        "response": content,
        "raw": data if not r.ok else None
    }), r.status_code