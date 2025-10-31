from flask import Flask, jsonify, request
from dummy_question import get_quiz_questions
from db_connect import get_connection
from datetime import datetime, timedelta
import random, string

app = Flask(__name__)

# Route 1: Get Questions
@app.route("/get_questions", methods=["GET"])
def get_questions():
    theme = request.args.get("theme", "cars")
    questions = get_quiz_questions(theme)
    return jsonify({"theme": theme, "questions": questions})

# Route 2: Submit Quiz
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.json
    user_name = data.get("user_name", "Guest")
    score = data.get("score", 0)
    theme = data.get("theme", "cars")

    conn = get_connection()
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT id, points FROM users WHERE name = %s", (user_name,))
    user = cur.fetchone()

    if user:
        user_id, current_points = user
    else:
        cur.execute("INSERT INTO users (name, points) VALUES (%s, 0) RETURNING id", (user_name,))
        user_id = cur.fetchone()[0]
        current_points = 0

    # Save quiz session
    cur.execute("""
        INSERT INTO quiz_sessions (user_id, theme, score)
        VALUES (%s, %s, %s)
    """, (user_id, theme, score))

    # Reward logic
    points_earned = score * 10
    new_total = current_points + points_earned

    coupon_code = None
    if score >= 2:  # Example: perfect score gets coupon
        coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expires_at = datetime.now() + timedelta(days=7)
        cur.execute("""
            INSERT INTO rewards (user_id, points_awarded, coupon_code, expires_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, points_earned, coupon_code, expires_at))
    else:
        cur.execute("""
            INSERT INTO rewards (user_id, points_awarded)
            VALUES (%s, %s)
        """, (user_id, points_earned))

    # Update total points
    cur.execute("UPDATE users SET points = %s WHERE id = %s", (new_total, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "user": user_name,
        "score": score,
        "points_earned": points_earned,
        "new_total_points": new_total,
        "coupon_code": coupon_code
    })

if __name__ == "__main__":
    app.run(debug=True)
