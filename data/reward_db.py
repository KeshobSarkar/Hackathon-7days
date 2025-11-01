import os
import psycopg2
from datetime import datetime, timedelta
from uuid import uuid4
from dotenv import dotenv_values

class RewardDB:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        env_vars = dotenv_values(env_path)  # loads only from file, not global
        self.db_url = env_vars.get("DATABASE_URL")

        print(f"📦 Loading from .env file at: {env_path}")
        print("📦 DATABASE_URL loaded:", self.db_url if self.db_url else "❌ Not found")

        if not self.db_url:
            raise ValueError(f"❌ DATABASE_URL missing in .env file: {env_path}")

        # --- Connect to PostgreSQL ---
        try:
            safe_target = self.db_url.split("@")[-1] if "@" in self.db_url else self.db_url
            print(f"🔗 Connecting to: {safe_target}")
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = True
            print("✅ Connection successful!")
            self._create_tables()
        except Exception as e:
            print(f"❌ Connection failed: {e}")

    #-----------------------------
    # DATABASE SETUP
    # -------------------------------
    def _create_tables(self):
        """Ensure tables exist (same as SQL above)."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    points INT DEFAULT 0
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS streaks (
                    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                    current_streak INT DEFAULT 0,
                    longest_streak INT DEFAULT 0,
                    warnings INT DEFAULT 0,
                    last_quiz_date TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS coupons (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                    code VARCHAR(50),
                    discount TEXT,
                    coupon_type TEXT,
                    status TEXT DEFAULT 'active',
                    received_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quiz_history (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                    theme TEXT,
                    score INT,
                    total_questions INT,
                    points_earned INT,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)
        print("✅ Database tables are ready.")

    # -------------------------------
    # USER MANAGEMENT
    # -------------------------------
    def get_or_create_user(self, username):
        """Return user_id; create user if not exists."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE username=%s;", (username,))
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id;", (username,))
            user_id = cur.fetchone()[0]
            print(f"🆕 Created new user: {username} (ID={user_id})")
            return user_id

    def get_user_wallet(self, username):
        """Fetch wallet info by username."""
        user_id = self.get_or_create_user(username)

        with self.conn.cursor() as cur:
            # Points
            cur.execute("SELECT points FROM users WHERE user_id=%s;", (user_id,))
            points = cur.fetchone()[0]

            # Streak
            cur.execute("""
                SELECT current_streak, longest_streak, warnings, last_quiz_date
                FROM streaks WHERE user_id=%s;
            """, (user_id,))
            streak_data = cur.fetchone()
            streak = {
                "current": streak_data[0] if streak_data else 0,
                "longest": streak_data[1] if streak_data else 0,
                "warnings": streak_data[2] if streak_data else 0,
                "last_quiz_date": str(streak_data[3]) if streak_data and streak_data[3] else None
            }

            # Coupons
            cur.execute("""
                SELECT code, discount, coupon_type, received_at, expires_at, status
                FROM coupons WHERE user_id=%s
                ORDER BY received_at DESC;
            """, (user_id,))
            coupons = cur.fetchall()
            coupons_list = [
                {
                    "code": c[0],
                    "discount": c[1],
                    "coupon_type": c[2],
                    "received_at": str(c[3]),
                    "expires_at": str(c[4]),
                    "status": c[5]
                } for c in coupons
            ]

        return {
            "user_id": user_id,
            "username": username,
            "points": points,
            "streak": streak,
            "coupons": coupons_list
        }

    # -------------------------------
    # POINTS
    # -------------------------------
    def add_points(self, username, points, reason="weekly_quiz"):
        """Add points by username."""
        user_id = self.get_or_create_user(username)
        with self.conn.cursor() as cur:
            cur.execute("UPDATE users SET points = points + %s WHERE user_id=%s;", (points, user_id))
        print(f"✅ Added {points} points for {username} ({reason})")

    # -------------------------------
    # Coupon System (Random + Dynamic)
    # -------------------------------

    def issue_coupon(self, username, description=None, validity_days=7, coupon_type=None):
        """Automatically create a coupon with random discount or reward type."""
        import random
        user_id = self.get_or_create_user(username)  # map username → user_id

        received_at = datetime.now()
        expires_at = received_at + timedelta(days=validity_days)

        # Ensure coupon_type is never None
        if not coupon_type:
            coupon_type = random.choice(["discount", "reward", "service", "special"])

        # Randomize description if not provided
        if not description:
            if coupon_type == "discount":
                description = random.choice(["10% off", "15% off", "20% off", "25% off", "30% off"])
            elif coupon_type == "reward":
                description = random.choice(["Bonus 50 Points", "Bonus 100 Points", "Bonus 200 Points"])
            elif coupon_type == "service":
                description = "Free Car Wash"
            elif coupon_type == "special":
                description = "Exclusive Gift Voucher"
            else:
                description = "Special Reward"

        # Insert into DB
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO coupons (user_id, discount, expires_at, status, coupon_type, received_at)
                VALUES (%s, %s, %s, 'active', %s, %s)
            """, (user_id, description, expires_at, coupon_type, received_at))

        print(f"🎟️ {coupon_type.title()} coupon created for user {username}: '{description}' (valid until {expires_at.date()})")
        return description

    # -------------------------------
    # STREAK SYSTEM
    # -------------------------------
    def update_streak(self, username, passed_quiz=True):
        """Handle streak/strikes logic."""
        user_id = self.get_or_create_user(username)
        now = datetime.now()

        with self.conn.cursor() as cur:
            cur.execute("SELECT current_streak, longest_streak, warnings, last_quiz_date FROM streaks WHERE user_id=%s;", (user_id,))
            record = cur.fetchone()

            message = ""
            if record:
                current_streak, longest_streak, warnings, last_date = record
                if last_date and (now - last_date).days > 7:
                    current_streak = 0
                    warnings = 0
                    message = "📅 Missed a week! Streak reset."

                if passed_quiz:
                    current_streak += 1
                    warnings = 0
                    if current_streak > longest_streak:
                        longest_streak = current_streak
                    message = f"✅ Passed quiz! Streak: {current_streak}"
                else:
                    warnings += 1
                    if warnings >= 3:
                        current_streak = 0
                        warnings = 0
                        message = "❌ 3 strikes! Streak reset."
                    else:
                        message = f"⚠️ Strike {warnings}/3."

                cur.execute("""
                    UPDATE streaks
                    SET current_streak=%s, longest_streak=%s, warnings=%s, last_quiz_date=%s, updated_at=NOW()
                    WHERE user_id=%s;
                """, (current_streak, longest_streak, warnings, now, user_id))
            else:
                cur.execute("""
                    INSERT INTO streaks (user_id, current_streak, longest_streak, warnings, last_quiz_date)
                    VALUES (%s, %s, %s, %s, %s);
                """, (user_id, 1 if passed_quiz else 0, 1 if passed_quiz else 0, 0 if passed_quiz else 1, now))
                message = "✅ Streak started!" if passed_quiz else "⚠️ First strike (1/3)."

        print(f"🔥 Updated streak for {username}: {message}")
        return message

    # -------------------------------
    # LEADERBOARD
    # -------------------------------
    def get_leaderboard(self, limit=10):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.points,
                       COALESCE(s.current_streak, 0) AS streak,
                       COALESCE(AVG((q.score * 100.0) / NULLIF(q.total_questions, 0)), 0) AS avg_score
                FROM users u
                LEFT JOIN streaks s ON u.user_id = s.user_id
                LEFT JOIN quiz_history q ON u.user_id = q.user_id
                GROUP BY u.username, u.points, s.current_streak
                ORDER BY u.points DESC, s.current_streak DESC, avg_score DESC
                LIMIT %s;
            """, (limit,))
            rows = cur.fetchall()

        return [
            {"user_id": row[0], "points": row[1], "streak": row[2], "avg_score": round(row[3], 1)}
            for row in rows
        ]
if __name__ == "__main__":
    RewardDB()
