import streamlit as st
from datetime import datetime, timedelta
from quiz_generator import QuizGenerator
from reward_db import RewardDB

# Initialize components
quiz_gen = QuizGenerator()
reward = RewardDB()

TESTING_MODE = True  # short cooldown

# ---------------------------
# Helper Functions
# ---------------------------

def is_same_week(date_string):
    """Check if last quiz was within 1 min (test) or same week (real)"""
    try:
        date_obj = datetime.fromisoformat(date_string)
        now = datetime.now()
        if TESTING_MODE:
            return (now - date_obj).total_seconds() < 60
        else:
            return date_obj.isocalendar()[1] == now.isocalendar()[1]
    except:
        return False

def main():
    st.set_page_config(page_title="🎯 QIC Quiz Challenge", page_icon="🎯", layout="wide")
    st.title("🎯 QIC Weekly Quiz")

    if TESTING_MODE:
        st.info("🧪 Testing Mode: 1-minute cooldown between quizzes")

    # User input
    user_id = st.text_input("👤 Enter your User ID:", placeholder="e.g., 1")
    if not user_id:
        st.warning("Enter a user ID to begin.")
        return

    user_id = int(user_id)

    # Get current user wallet
    user_wallet = reward.get_user_wallet(user_id)
    st.write(f"💎 **Points:** {user_wallet['points']} | 🔥 **Streak:** {user_wallet['streak']['current']} week(s)")

    # Select theme
    theme = st.selectbox("Choose a quiz theme:", [
        "Car Insurance",
        "Visitors Insurance",
        "Travel Insurance",
        "QIC Company",
        "Claims Process",
        "Insurance Products",
        "Qatar Living"
    ])

    # Generate Quiz
    if st.button("🎲 Generate Quiz"):
        st.session_state.quiz = quiz_gen.generate_quiz(theme=theme, difficulty="easy", num_questions=3)

    # Display Quiz
    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        st.subheader(f"🧩 {quiz['theme']} Quiz ({quiz['difficulty']})")

        answers = []
        for i, q in enumerate(quiz["questions"]):
            st.write(f"**Q{i+1}. {q['question']}**")
            answer = st.radio("Choose one:", q["options"], key=f"q_{i}", label_visibility="collapsed")
            answers.append(answer)

        if st.button("📤 Submit Answers"):
            if None in answers or "" in answers:
                st.warning("Please answer all questions.")
                return

            # Evaluate
            results = quiz_gen.evaluate_answers(quiz, answers)
            correct = sum(r["is_correct"] for r in results)
            total = len(results)
            passed = correct / total >= 0.6

            # Results display
            st.subheader("📊 Results")
            st.write(f"✅ Correct: {correct}/{total} ({(correct/total)*100:.1f}%)")
            for r in results:
                st.write(f"**{r['question']}** — {'✅' if r['is_correct'] else '❌'}")
                st.caption(f"Answer: {r['correct_answer']} | {r['explanation']}")

            # Database updates
            points = correct * 50
            reward.add_points(user_id, points, "weekly_quiz")
            reward.update_streak(user_id, passed)

            if passed:
                reward.issue_coupon(user_id, "20% off", 7)
                st.success(f"🎉 You earned {points} points and a new coupon!")
            else:
                st.warning(f"💡 You earned {points} points, but need 60%+ to get a coupon.")

            # Show updated wallet
            wallet = reward.get_user_wallet(user_id)
            st.write("💎 **Updated Wallet:**")
            st.json(wallet)

            # Reset quiz
            st.session_state.pop("quiz", None)

    # Show coupons
    st.write("---")
    st.subheader("🎫 Your Coupons")
    coupons = user_wallet["coupons"]
    if coupons:
        for c in coupons:
            st.write(f"• {c['code']} — {c['discount']} (expires {c['expires_at']})")
    else:
        st.info("No active coupons yet. Score 60%+ to earn one!")

if __name__ == "__main__":
    main()
