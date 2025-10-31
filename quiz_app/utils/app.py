import streamlit as st
from datetime import datetime, timedelta
import os
import sys

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from quiz_generator import QuizGenerator
from reward_db import RewardDB

# Initialize components
quiz_gen = QuizGenerator()
reward = RewardDB()

TESTING_MODE = True

def main():
    st.set_page_config(
        page_title="🏆 Insurance Quiz Pro", 
        page_icon="🎯", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Clean professional CSS
    st.markdown("""
    <style>
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
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .leaderboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .rank-1 { 
        background: linear-gradient(135deg, #FFD700, #FFA500) !important; 
    }
    .rank-2 { 
        background: linear-gradient(135deg, #C0C0C0, #A0A0A0) !important; 
    }
    .rank-3 { 
        background: linear-gradient(135deg, #CD7F32, #8B4513) !important; 
    }
    .current-user {
        border: 3px solid #00FF00 !important;
        transform: scale(1.02);
    }
    .quiz-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .coupon-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Header
    st.markdown('<div class="main-header">🏆 Insurance Quiz Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Test Your Insurance Knowledge • Earn Rewards • Compete Globally</div>', unsafe_allow_html=True)

    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 Player Profile")
        username = st.text_input("Enter Your Username:", placeholder="e.g., john, sarah, alex...", key="username")
        
        # Initialize variables
        user_id = None
        user_wallet = None
        
        if username and username.strip():
            # Use the username as the user_id (convert to lowercase for consistency)
            user_id = username.lower().strip()
            user_wallet = reward.get_user_wallet(user_id)
            
            st.subheader("📊 Your Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💎 Points", user_wallet['points'])
            with col2:
                st.metric("🔥 Streak", f"{user_wallet['streak']['current']}w")
            
            user_rank = reward.get_user_rank(user_id)
            if user_rank:
                st.metric("🏆 Global Rank", f"#{user_rank}")
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        else:
            st.info("🎯 Enter your username to start!")
            user_id = None

    # Main content area - only show if we have a valid username
    if user_id is None:
        st.warning("👆 Please enter your username in the sidebar to begin!")
        return

    # Main layout with columns
    col1, col2 = st.columns([2, 1])

    with col1:
        # Quiz Section
        st.header("📝 Take a Quiz")
        
        with st.container():
            st.markdown('<div class="quiz-section">', unsafe_allow_html=True)
            
            theme = st.selectbox(
                "Choose Quiz Theme:",
                ["Car Insurance", "Visitors Insurance", "Travel Insurance", "QIC Company", 
                 "Claims Process", "Insurance Products", "Qatar Living"]
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                num_questions = st.slider("Number of Questions:", 3, 10, 5)
            with col_b:
                difficulty = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard"])

            # Generate Quiz
            if st.button("🎲 Generate New Quiz", use_container_width=True, type="primary"):
                with st.spinner("🤖 AI is generating your quiz..."):
                    st.session_state.quiz_data = quiz_gen.generate_quiz(
                        theme=theme,
                        difficulty=difficulty.lower(),
                        num_questions=num_questions
                    )
                    st.session_state.user_answers = [None] * num_questions
                    st.session_state.submitted = False
                st.success("✅ Quiz generated successfully!")

            st.markdown('</div>', unsafe_allow_html=True)

        # Display Quiz
        if st.session_state.quiz_data and not st.session_state.submitted:
            quiz = st.session_state.quiz_data
            
            st.subheader(f"🧩 {quiz['theme']} Quiz ({quiz['difficulty'].title()})")
            
            for i, question in enumerate(quiz["questions"]):
                st.write(f"**Q{i+1}. {question['question']}**")
                
                # Display options
                options = question["options"]
                selected_option = st.radio(
                    f"Select your answer for Q{i+1}:",
                    options,
                    key=f"q_{i}",
                    index=None,
                    label_visibility="collapsed"
                )
                
                if selected_option:
                    st.session_state.user_answers[i] = selected_option
                
                if i < len(quiz["questions"]) - 1:
                    st.write("---")

            # Submit Button
            if st.button("📤 Submit Answers", use_container_width=True, type="secondary"):
                if None in st.session_state.user_answers:
                    st.warning("⚠️ Please answer all questions before submitting.")
                else:
                    # Evaluate answers
                    with st.spinner("Evaluating your answers..."):
                        results = quiz_gen.evaluate_answers(quiz, st.session_state.user_answers)
                        correct = sum(r["is_correct"] for r in results)
                        total = len(results)
                        passed = correct / total >= 0.6
                        
                        # Calculate points
                        points = correct * 50
                        bonus = 100 if passed else 0
                        total_points = points + bonus
                        
                        # Update user data
                        reward.add_points(user_id, total_points, "quiz_completion")
                        reward.update_streak(user_id, passed)
                        reward.add_quiz_attempt(user_id, theme, correct, total, total_points)
                        
                        if passed:
                            coupon_code = reward.issue_coupon(user_id, "20% off", 7)
                            st.session_state.coupon_earned = coupon_code
                        else:
                            st.session_state.coupon_earned = None
                        
                        st.session_state.submitted = True
                        st.session_state.results = results
                        st.session_state.quiz_stats = {
                            'correct': correct,
                            'total': total,
                            'points': total_points,
                            'passed': passed
                        }
                    
                    st.rerun()

        # Show Results
        if st.session_state.get('submitted', False):
            stats = st.session_state.quiz_stats
            results = st.session_state.results
            
            st.header("📊 Quiz Results")
            
            # Results summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Correct", f"{stats['correct']}/{stats['total']}")
            with col2:
                st.metric("📈 Score", f"{(stats['correct']/stats['total'])*100:.1f}%")
            with col3:
                st.metric("💎 Points", stats['points'])
            with col4:
                status = "PASSED ✅" if stats['passed'] else "FAILED ❌"
                st.metric("Status", status)
            
            if stats['passed']:
                st.success("🎉 Congratulations! You passed and earned rewards!")
                if st.session_state.get('coupon_earned'):
                    st.info(f"🎫 **Coupon Earned:** `{st.session_state.coupon_earned}`")
            else:
                st.warning("💡 Score 60% or higher next time to earn a coupon!")
            
            # Detailed results
            with st.expander("📝 Review Your Answers", expanded=True):
                for result in results:
                    if result['is_correct']:
                        st.success(f"**Q{result['question_number']}:** {result['user_answer']} ✅")
                    else:
                        st.error(f"**Q{result['question_number']}:** {result['user_answer']} ❌")
                        st.info(f"**Correct Answer:** {result['correct_answer']}")
                    st.write(f"**Explanation:** {result['explanation']}")
                    st.write("---")
            
            # New Quiz Button
            if st.button("🔄 Take Another Quiz", use_container_width=True):
                for key in ['quiz_data', 'user_answers', 'submitted', 'results', 'quiz_stats', 'coupon_earned']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    with col2:
        # Leaderboard Section
        st.header("🏆 Global Leaderboard")
        
        if st.button("🔄 Refresh Leaderboard", use_container_width=True):
            st.rerun()
        
        leaderboard = reward.get_leaderboard(limit=10)
        
        if leaderboard:
            for i, player in enumerate(leaderboard, 1):
                is_current_user = player["user_id"] == user_id
                card_class = f"rank-{i}" if i <= 3 else "leaderboard-card"
                if is_current_user:
                    card_class += " current-user"
                
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                cols = st.columns([1, 3, 2, 2])
                with cols[0]:
                    st.write(f"**#{i}**")
                with cols[1]:
                    if is_current_user:
                        st.write(f"**👤 {player['user_id'].title()} (You)**")
                    else:
                        st.write(f"**{player['user_id'].title()}**")
                with cols[2]:
                    st.write(f"💎 {player['points']}")
                with cols[3]:
                    st.write(f"📊 {player['avg_score']}%")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No players yet. Be the first to take a quiz!")
        
        # Rewards Section
        st.header("🎫 Your Rewards")
        coupons = user_wallet["coupons"]
        
        if coupons:
            for coupon in coupons:
                expires = datetime.fromisoformat(coupon['expires_at'])
                days_left = (expires - datetime.now()).days
                
                st.markdown('<div class="coupon-card">', unsafe_allow_html=True)
                st.write(f"**{coupon['discount']}**")
                st.write(f"**Code:** `{coupon['code']}`")
                
                if days_left > 0:
                    st.write(f"⏰ Expires in {days_left} days")
                else:
                    st.error("⏰ Expired!")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Complete quizzes with 60%+ score to earn coupons! 🎯")
        
        # User Statistics
        with st.expander("📈 Your Statistics"):
            quiz_history = user_wallet.get("quiz_history", [])
            if quiz_history:
                total_quizzes = len(quiz_history)
                total_correct = sum(quiz.get("score", 0) for quiz in quiz_history)
                total_questions = sum(quiz.get("total_questions", 0) for quiz in quiz_history)
                total_points = sum(quiz.get("points_earned", 0) for quiz in quiz_history)
                
                st.write(f"**Total Quizzes Taken:** {total_quizzes}")
                st.write(f"**Total Points Earned:** {total_points}")
                st.write(f"**Overall Accuracy:** {(total_correct/total_questions)*100:.1f}%" if total_questions > 0 else "N/A")
                st.write(f"**Current Streak:** {user_wallet['streak']['current']} weeks")
                
                # Theme breakdown
                if quiz_history:
                    st.write("**Theme Performance:**")
                    themes = {}
                    for quiz in quiz_history:
                        theme = quiz.get('theme', 'Unknown')
                        if theme not in themes:
                            themes[theme] = {'correct': 0, 'total': 0}
                        themes[theme]['correct'] += quiz.get('score', 0)
                        themes[theme]['total'] += quiz.get('total_questions', 0)
                    
                    for theme, data in themes.items():
                        accuracy = (data['correct']/data['total'])*100 if data['total'] > 0 else 0
                        st.write(f"- {theme}: {accuracy:.1f}%")
            else:
                st.write("No quiz history yet. Take your first quiz!")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🏆 Insurance Quiz Pro • Real-time Leaderboard • "
        "Built with Streamlit & OpenAI"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()