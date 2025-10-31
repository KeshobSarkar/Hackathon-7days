import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="Hackathon_reward",
        user="postgres",
        password="riplife.2",
        host="localhost",
        port="5432"
    )
    return conn

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Connected to PostgreSQL!")
    except Exception as e:
        print("❌ Connection failed:", e)
