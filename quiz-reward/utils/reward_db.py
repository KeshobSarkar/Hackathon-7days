import os
import psycopg2
from datetime import datetime, timedelta

class RewardDB:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found. Please set it with setx or .env")
        self.conn = psycopg2.connect(self.db_url)
        self.conn.autocommit = True

    def add_points(self, user_id, points, reason):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO points (user_id, points, reason) VALUES (%s, %s, %s)",
                (user_id, points, reason)
            )
        print(f"✅ Added {points} points for user {user_id} ({reason})")

    def issue_coupon(self, user_id, discount="20% off", validity_days=7):
        code = f"QIC-{int(datetime.now().timestamp())}"
        expires_at = datetime.now() + timedelta(days=validity_days)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO coupons (user_id, code, discount, expires_at)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, code, discount, expires_at)
            )
        print(f"🎟️ Coupon issued for user {user_id}: {code} (valid {validity_days} days)")

    def update_streak(self, user_id, passed_quiz=True):
        with self.conn.cursor() as cur:
            # check if streak record exists
            cur.execute("SELECT current_streak, warnings FROM streaks WHERE user_id=%s", (user_id,))
            record = cur.fetchone()
            
            if record:
                current_streak, warnings = record
                if passed_quiz:
                    current_streak += 1
                    warnings = 0
                else:
                    warnings += 1
                    if warnings >= 2:
                        current_streak = 0
                        warnings = 0
                cur.execute(
                    """
                    UPDATE streaks 
                    SET current_streak=%s, warnings=%s, last_completed=%s, updated_at=NOW() 
                    WHERE user_id=%s
                    """,
                    (current_streak, warnings, datetime.now().date(), user_id)
                )
            else:
                cur.execute(
                    "INSERT INTO streaks (user_id, current_streak, warnings, last_completed) VALUES (%s, %s, %s, %s)",
                    (user_id, 1 if passed_quiz else 0, 0 if passed_quiz else 1, datetime.now().date())
                )

        print(f"🔥 Updated streak for user {user_id}")

    def get_user_wallet(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(points),0) FROM points WHERE user_id=%s", (user_id,))
            points = cur.fetchone()[0]

            cur.execute("SELECT code, discount, status, expires_at FROM coupons WHERE user_id=%s", (user_id,))
            coupons = cur.fetchall()

            cur.execute("SELECT current_streak, warnings FROM streaks WHERE user_id=%s", (user_id,))
            streak = cur.fetchone()

        return {
            "points": points,
            "coupons": [{"code": c[0], "discount": c[1], "status": c[2], "expires_at": str(c[3])} for c in coupons],
            "streak": {"current": streak[0] if streak else 0, "warnings": streak[1] if streak else 0}
        }
