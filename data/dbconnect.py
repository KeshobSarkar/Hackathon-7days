import os
import psycopg2

try:
    db_url = os.getenv("DATABASE_URL")
    print(f"Connecting to: {db_url}")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Simple query
    cur.execute("SELECT datname FROM pg_database;")
    databases = cur.fetchall()
    print("\n✅ Connected successfully!")
    print("Available databases:", [d[0] for d in databases])

    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
