import streamlit as st
from datetime import datetime, timedelta
import os
import sys
import time

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Initialize components WITH PROPER CACHING - THIS IS THE KEY FIX
@st.cache_resource
def get_quiz_generator():
    from quiz_generator import QuizGenerator
    return QuizGenerator()

@st.cache_resource
def get_reward_db():
    from reward_db import RewardDB
    return RewardDB()

quiz_gen = get_quiz_generator()
reward = get_reward_db()

def main():
    st.set_page_config(
        page_title="🏆 Insurance Quiz Pro",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state to prevent unnecessary re-runs
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.quiz = None
        st.session_state.submitted = False
        st.session_state.results = None
        st.session_state.stats = None
        st.session_state.coupon_earned = None

    # ---------------------------
    # 🎨 Clean modern CSS - FIXED
    # ---------------------------
    st.markdown("""
    <style>
    .stApp > header {
        display: none;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #2e86ab;
        text-align: center;
        margin-bottom: 2rem;
    }
    .quiz-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .coupon-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .coupon-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    .coupon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
    }
    .coupon-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .coupon-details {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.5;
    }
    .leaderboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .rank-1 { background: linear-gradient(135deg, #FFD700, #FFA500) !important; }
    .rank-2 { background: linear-gradient(135deg, #C0C0C0, #A0A0A0) !important; }
    .rank-3 { background: linear-gradient(135deg, #CD7F32, #8B4513) !important; }
    .current-user { border: 3px solid #00FF00 !important; transform: scale(1.02); }
    
    /* HIDE STREAMLIT'S LOADING INDICATOR */
    .stApp > div[data-testid="stToolbar"] {
        display: none;
    }
    .stApp > div[data-testid="stDecoration"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 🎯 Sidebar - Player profile
    # ---------------------------
    with st.sidebar:
        st.header("👤 Player Profile")
        username = st.text_input("Enter your Username:", placeholder="e.g., JohnDoe")

        if not username:
            st.info("🎯 Enter your username to start!")
            st.stop()

        username = username.strip().lower()
        user_wallet = reward.get_user_wallet(username)

        st.subheader("📊 Your Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💎 Points", user_wallet["points"])
        with col2:
            st.metric("🔥 Streak", f"{user_wallet['streak']['current']}w")

        st.metric("⚠️ Strikes", f"{user_wallet['streak']['warnings']}/3")

        if st.button("🔄 Refresh Profile", use_container_width=True):
            st.rerun()

    # ---------------------------
    # 🧩 Main Layout
    # ---------------------------
    col1, col2 = st.columns([2, 1])

    # ---------------------------
    # LEFT: Quiz Section
    # ---------------------------
    with col1:
        st.markdown('<div class="main-header">🏆 Insurance Quiz Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Test Your Insurance Knowledge • Earn Rewards</div>', unsafe_allow_html=True)

        st.markdown('<div class="quiz-section">', unsafe_allow_html=True)
        theme = st.selectbox("Choose Quiz Theme:", [
            "Car Insurance", "Visitors Insurance", "Travel Insurance",
            "QIC Company", "Claims Process", "Insurance Products", "Qatar Living"
        ])
        col_a, col_b = st.columns(2)
        with col_a:
            num_questions = st.slider("Number of Questions:", 3, 10, 5)
        with col_b:
            difficulty = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard"])

        # Generate Quiz - USE FORM TO REDUCE RE-RUNS
        with st.form("quiz_form"):
            generate_clicked = st.form_submit_button("🎲 Generate New Quiz", use_container_width=True)
            
        if generate_clicked:
            with st.spinner("🤖 Generating your quiz..."):
                st.session_state.quiz = quiz_gen.generate_quiz(
                    theme=theme,
                    difficulty=difficulty.lower(),
                    num_questions=num_questions
                )
                st.session_state.submitted = False
                st.session_state.results = None
                st.session_state.stats = None
                st.session_state.coupon_earned = None
            st.success("✅ Quiz generated successfully!")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Display Quiz
        if st.session_state.quiz and not st.session_state.submitted:
            quiz = st.session_state.quiz
            st.subheader(f"🧩 {quiz['theme']} Quiz ({quiz['difficulty'].title()})")

            answers = []
            for i, q in enumerate(quiz["questions"]):
                st.write(f"**Q{i+1}. {q['question']}**")
                answer = st.radio("Select your answer:", q["options"], key=f"q_{i}", label_visibility="collapsed")
                answers.append(answer)

            if st.button("📤 Submit Answers", use_container_width=True):
                if None in answers or "" in answers:
                    st.warning("⚠️ Please answer all questions before submitting.")
                    st.stop()

                results = quiz_gen.evaluate_answers(quiz, answers)
                correct = sum(r["is_correct"] for r in results)
                total = len(results)
                passed = correct / total >= 0.6
                points = correct * 50

                st.session_state.submitted = True
                st.session_state.results = results
                st.session_state.stats = {"correct": correct, "total": total, "passed": passed, "points": points}

                # Update rewards
                reward.add_points(username, points, "weekly_quiz")
                reward.update_streak(username, passed)
                if passed:
                    coupon_code = reward.issue_coupon(username, validity_days=7)
                    st.session_state.coupon_earned = coupon_code
                st.rerun()

        # Show results after submission
        if st.session_state.submitted and st.session_state.results:
            results = st.session_state.results
            stats = st.session_state.stats

            st.header("📊 Quiz Results")
            st.write(f"✅ Correct: {stats['correct']}/{stats['total']} ({(stats['correct']/stats['total'])*100:.1f}%)")

            for r in results:
                if r["is_correct"]:
                    st.success(f"**✅ Q{r['question_number']}: {r['question']}**")
                    st.caption(f"Your Answer: **{r['user_answer']}**")
                else:
                    st.error(f"**❌ Q{r['question_number']}: {r['question']}**")
                    st.caption(f"Your Answer: **{r['user_answer']}**  \n✅ Correct: **{r['correct_answer']}**")
                st.write(f"**Explanation:** {r['explanation']}")
                st.markdown("---")

            if stats["passed"]:
                st.success("🎉 Congratulations! You passed and earned a reward!")
                if st.session_state.coupon_earned:
                    updated_wallet = reward.get_user_wallet(username)
                    if updated_wallet["coupons"]:
                        new_coupon = updated_wallet["coupons"][0]
                        st.markdown(
                            f'<div class="coupon-card">'
                            f'<div class="coupon-header">🎁 {new_coupon["discount"]}</div>'
                            f'<div class="coupon-details">'
                            f'🏷️ {new_coupon["coupon_type"].title()}<br>'
                            f'📅 {new_coupon["received_at"][:19]}<br>'
                            f'⏰ Expires: {new_coupon["expires_at"][:19]}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.warning("💡 Score 60% or higher next time to earn a coupon!")

            if st.button("🔄 Take Another Quiz", use_container_width=True):
                st.session_state.quiz = None
                st.session_state.submitted = False
                st.session_state.results = None
                st.session_state.stats = None
                st.session_state.coupon_earned = None
                st.rerun()

    # ---------------------------
    # RIGHT: Leaderboard + Coupons
    # ---------------------------
    with col2:
        st.header("🏆 Global Leaderboard")
        leaderboard = reward.get_leaderboard(limit=10)
        if leaderboard:
            for i, player in enumerate(leaderboard, 1):
                player_identifier = player.get("username") or player.get("user_id", "Unknown")
                is_current = str(player_identifier).lower() == username.lower()
                
                css_class = f"rank-{i}" if i <= 3 else "leaderboard-card"
                if is_current:
                    css_class += " current-user"

                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                st.write(f"**#{i} {str(player_identifier).title()}** — 💎 {player['points']} pts | 🔥 {player['streak']}w")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No players yet — be the first!")

        st.header("🎫 Your Rewards")
        coupons = user_wallet["coupons"]
        if coupons:
            for c in coupons:
                st.markdown(
                    f'<div class="coupon-card">'
                    f'<div class="coupon-header">🎁 {c["discount"]}</div>'
                    f'<div class="coupon-details">'
                    f'🏷️ {c["coupon_type"].title()}<br>'
                    f'📅 {c["received_at"][:19]}<br>'
                    f'⏰ Expires: {c["expires_at"][:19]}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Complete a quiz (60%+) to earn your first reward!")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🏆 Insurance Quiz Pro • Real-time Rewards & Leaderboard • Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()