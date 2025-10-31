import json
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname=os.getenv("PGDATABASE")
)
cur = conn.cursor()

# Load questions
with open("./quiz_data.json", "r") as f:
    data = json.load(f)

# Ensure it’s a list of question dicts
if isinstance(data, str):
    data = json.loads(data)

for item in data:
    cur.execute(
        """
        INSERT INTO quiz_sessions (user_id, theme, score, created_at)
        VALUES (%s, %s, %s, NOW())
        """,
        (1, item["question"], 0)
    )

conn.commit()
cur.close()
conn.close()

print("✅ Quiz questions added to PostgreSQL!")
