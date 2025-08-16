import os, re, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras

APP_ENV = os.getenv("ENV", "production")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def ensure_table():
    ddl = '''
    CREATE TABLE IF NOT EXISTS waitlist (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        source TEXT
    );
    '''
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
            conn.commit()

@app.get("/healthz")
def healthz():
    return {"ok": True, "env": APP_ENV}, 200

@app.post("/api/waitlist")
def waitlist():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    source = (data.get("source") or "coming-soon").strip()

    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email"}), 400

    try:
        ensure_table()
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "INSERT INTO waitlist (email, source) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING",
                    (email, source),
                )
                conn.commit()
        return jsonify({"ok": True}), 200
    except Exception as e:
        # Log error to stdout for Render logs
        print(f"[waitlist] error: {e}")
        return jsonify({"ok": False, "error": "server_error"}), 500

if __name__ == "__main__":
    ensure_table()
    app.run(host="0.0.0.0", port=10000)