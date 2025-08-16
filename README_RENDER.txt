# HiveReply Coming Soon — Render Deploy

## Structure
- coming-soon/index.html      # Put your Coming Soon page here (the one from canvas)
- render.yaml                 # Render blueprint: static site + Python API
- requirements.txt            # For the Python API service
- api/server.py               # /api/waitlist endpoint (stores emails in Postgres)
- db_init.sql                 # Optional SQL helper

## Steps
1) Create a new GitHub repo and add these files. Place your `index.html` inside a folder named `coming-soon/` at repo root.
2) In Render:
   - Create **Static Site** from this repo → name: hivereply-coming-soon
     • Build Command: (leave blank)
     • Publish Directory: `coming-soon`
   - Create **PostgreSQL** (free) → copy its `DATABASE_URL`.
   - Create **Web Service** (Python) from the same repo:
     • Use the `render.yaml` so it auto-detects.
     • Or manually set: Build `pip install -r requirements.txt`, Start `gunicorn api.server:app -b 0.0.0.0:10000`.
     • Add env var `DATABASE_URL` with the value from Render Postgres.
3) Update DNS (optional): Add your custom domain in the Static Site → follow Render's DNS CNAME instructions.
4) The `index.html` already posts to `/api/waitlist`. If the API isn't live yet, it falls back to `mailto:`.