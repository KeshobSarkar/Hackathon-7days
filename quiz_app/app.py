import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Import components
try:
    from utils.quiz_generator import QuizGenerator
    from utils.reward_engine import RewardEngine
    from utils.streak_manager import StreakManager
    
    # Initialize components
    quiz_gen = QuizGenerator()
    reward_engine = RewardEngine()
    streak_manager = StreakManager()
    COMPONENTS_LOADED = True
    
except ImportError as e:
    st.error(f"❌ Component import error: {e}")
    COMPONENTS_LOADED = False

# TESTING MODE - 1 minute cooldown between quizzes
TESTING_MODE = True

def is_same_week(date_string):
    try:
        date_obj = datetime.fromisoformat(date_string)
        today = datetime.now()
        
        if TESTING_MODE:
            # 1 minute cooldown for testing
            return (today - date_obj).total_seconds() < 60
        else:
            # Weekly cooldown for production
            start_week_date = date_obj - timedelta(days=date_obj.weekday())
            start_week_today = today - timedelta(days=today.weekday())
            return start_week_date.date() == start_week_today.date()
    except:
        return False

def calculate_difficulty(user_data):
    streak = user_data.get('current_streak', 0)
    if streak > 4:
        return "hard"
    elif streak > 2:
        return "medium"
    else:
        return "easy"

def main():
    st.set_page_config(page_title="QIC Quiz Challenge", page_icon="🎯", layout="wide")
    
    if not COMPONENTS_LOADED:
        st.error("❌ System components not loaded. Please check the error above.")
        return
    
    if TESTING_MODE:
        st.info("🧪 TESTING MODE: 1-minute cooldown between quizzes")
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 QIC Quiz Master")
        
        user_id = st.text_input("Enter User ID", placeholder="user_123")
        if user_id:
            st.session_state.user_id = user_id
            streak_manager.initialize_user(user_id)
        
        if st.session_state.user_id:
            user_data = streak_manager.get_user_data(st.session_state.user_id)
            st.write(f"👤 User: {st.session_state.user_id}")
            st.write(f"🔥 Streak: {user_data['current_streak']} weeks")
            st.write(f"💎 Points: {user_data['total_points']}")
            
            # Show progress to next reward
            st.write("---")
            st.write("🎯 Next Reward")
            milestones = streak_manager.get_streak_milestones(st.session_state.user_id)
            for milestone in milestones:
                if not milestone['achieved']:
                    weeks_needed = milestone['weeks'] - user_data['current_streak']
                    st.write(f"⏳ {milestone['weeks']} weeks: {milestone['reward']}")
                    st.write(f"   {weeks_needed} week(s) to go!")
                    break
            
            # Show active coupons
            coupons = reward_engine.get_user_coupons(st.session_state.user_id)
            if coupons:
                st.write("---")
                st.write("🎫 Your Coupons:")
                for coupon in coupons:
                    days_left = (datetime.strptime(coupon['expiry_date'], "%Y-%m-%d") - datetime.now()).days
                    st.write(f"• **{coupon['code']}** - {coupon['value']}")
                    st.write(f"  Expires: {days_left} days")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎮 Weekly Quiz", "💰 Rewards", "🏆 Leaderboard"])
    
    with tab1:
        render_weekly_quiz()
    with tab2:
        render_rewards()
    with tab3:
        render_leaderboard()

def render_weekly_quiz():
    st.header("🎯 This Week's QIC Quiz")
    
    if not st.session_state.user_id:
        st.warning("Please enter your User ID in the sidebar to start playing!")
        return
    
    user_data = streak_manager.get_user_data(st.session_state.user_id)
    last_quiz = user_data.get('last_quiz_date')
    
    if last_quiz and is_same_week(last_quiz):
        if TESTING_MODE:
            st.info("⏳ You can take another quiz in 1 minute (Testing Mode)")
        else:
            st.success("🎉 You've already completed this week's quiz! Come back next week.")
        st.write(f"**Last quiz:** {last_quiz[:16]}")
        st.write(f"**Current streak:** {user_data['current_streak']} weeks")
        return
    
    # Generate quiz
    if st.session_state.quiz_data is None:
        st.write("### Create Your QIC Quiz")
        theme = st.selectbox("Choose QIC Theme", [
            "Car Insurance", 
            "Visitors Insurance", 
            "Travel Insurance", 
            "QIC Company", 
            "Claims Process", 
            "Insurance Products", 
            "Qatar Living"
        ])
        
        if st.button("🎲 Generate Quiz", type="primary"):
            with st.spinner("🤖 AI is creating your QIC quiz..."):
                try:
                    st.session_state.quiz_data = quiz_gen.generate_quiz(
                        theme=theme, 
                        difficulty=calculate_difficulty(user_data),
                        num_questions=3
                    )
                except Exception as e:
                    st.error(f"❌ Failed to generate quiz: {e}")
    
    # Display quiz
    if st.session_state.quiz_data:
        display_quiz_questions()

def display_quiz_questions():
    quiz = st.session_state.quiz_data
    user_answers = []
    
    st.subheader(f"📝 {quiz['theme']} Quiz ({quiz['difficulty'].title()})")
    
    # Show scoring rules
    st.info("🎯 **Scoring:** 10 points per correct answer + 25 bonus for perfect score")
    st.info("🎁 **Coupons:** Need 50%+ score or 2+ week streak")
    st.write("---")
    
    for i, question in enumerate(quiz['questions']):
        st.write(f"**Q{i+1}: {question['question']}**")
        
        if question['type'] == 'multiple_choice':
            answer = st.radio(f"Select answer:", 
                            question['options'], 
                            key=f"q_{i}",
                            index=None,
                            label_visibility="collapsed")
            user_answers.append(answer)
    
    if st.button("📤 Submit Quiz", type="primary"):
        if None in user_answers:
            st.error("❌ Please answer all questions before submitting!")
        else:
            results = quiz_gen.evaluate_answers(quiz, user_answers)
            process_quiz_results(results)

def process_quiz_results(results):
    correct_answers = sum(1 for r in results if r['is_correct'])
    total_questions = len(results)
    score_percentage = (correct_answers / total_questions) * 100
    
    st.subheader("📊 Quiz Results")
    st.write(f"**Score: {correct_answers}/{total_questions} ({score_percentage:.1f}%)**")
    
    # Show detailed results
    for i, result in enumerate(results):
        with st.expander(f"Question {i+1}: {'✅' if result['is_correct'] else '❌'}"):
            st.write(f"**Your answer:** {result['user_answer']}")
            st.write(f"**Correct answer:** {result['correct_answer']}")
            st.write(f"**Explanation:** {result['explanation']}")
    
    # Calculate rewards
    points_earned = reward_engine.calculate_quiz_points(correct_answers, total_questions)
    streak_updated = streak_manager.update_streak(st.session_state.user_id, points_earned)
    reward_engine.record_transaction(st.session_state.user_id, points_earned, "weekly_quiz")
    
    # Show rewards
    if points_earned > 0:
        st.success(f"🎉 You earned **{points_earned} points**!")
    else:
        st.error(f"❌ You earned **0 points**. Try again!")
    
    # Only give coupon for good performance
    user_data = streak_manager.get_user_data(st.session_state.user_id)
    should_give_coupon = reward_engine.should_give_coupon(
        correct_answers, total_questions, user_data['current_streak']
    )
    
    if streak_updated and should_give_coupon:
        coupon = reward_engine.generate_coupon(st.session_state.user_id, user_data['current_streak'])
        if coupon:
            st.balloons()
            st.success(f"🎁 **Coupon Unlocked!**")
            st.info(f"**Code:** {coupon['code']}\n\n**Value:** {coupon['value']}\n\n**Expires:** {coupon['expiry_date']}")
    elif streak_updated and not should_give_coupon:
        st.warning("💡 Score below 50% - no coupon earned. Get 50%+ correct answers to earn coupons!")
    
    # Reset quiz
    if st.button("🔄 Take Another Quiz"):
        st.session_state.quiz_data = None
        st.rerun()

def render_rewards():
    st.header("💰 Your Rewards & Progress")
    
    if not st.session_state.user_id:
        st.warning("Please enter your User ID first!")
        return
    
    user_data = streak_manager.get_user_data(st.session_state.user_id)
    coupons = reward_engine.get_user_coupons(st.session_state.user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Your Stats")
        st.metric("Total Points", user_data['total_points'])
        st.metric("Current Streak", f"{user_data['current_streak']} weeks")
        st.metric("Longest Streak", f"{user_data['longest_streak']} weeks")
        
        # Performance stats
        st.write("---")
        st.subheader("📈 Performance")
        if user_data['quiz_history']:
            total_quizzes = len(user_data['quiz_history'])
            avg_points = sum(quiz['points_earned'] for quiz in user_data['quiz_history']) / total_quizzes
            st.write(f"Quizzes completed: **{total_quizzes}**")
            st.write(f"Average points: **{avg_points:.1f}**")
    
    with col2:
        st.subheader("🏆 Milestone Rewards")
        milestones = streak_manager.get_streak_milestones(st.session_state.user_id)
        
        for milestone in milestones:
            achieved = milestone['achieved']
            icon = "✅" if achieved else "⏳"
            
            if achieved:
                st.write(f"{icon} **{milestone['weeks']} weeks:** {milestone['reward']}")
            else:
                weeks_needed = milestone['weeks'] - user_data['current_streak']
                st.write(f"{icon} **{milestone['weeks']} weeks:** {milestone['reward']}")
                st.write(f"   *{weeks_needed} more week(s) to go!*")
        
        st.write("---")
        st.subheader("🎫 Your Coupons")
        if coupons:
            for coupon in coupons:
                days_left = (datetime.strptime(coupon['expiry_date'], "%Y-%m-%d") - datetime.now()).days
                st.write(f"**{coupon['code']}** - {coupon['value']}")
                st.write(f"Expires in {days_left} days")
                st.write("---")
        else:
            st.info("No active coupons. Get 50%+ score to earn coupons!")

def render_leaderboard():
    st.header("🏆 Leaderboard")
    
    leaderboard = streak_manager.get_leaderboard_data()
    if not leaderboard:
        st.info("No users yet. Be the first to complete a quiz!")
        return
    
    st.subheader("Top Players")
    for i, user in enumerate(leaderboard[:10]):
        if i == 0:
            st.write(f"🥇 **{user['user_id']}** - {user['points']} points (🔥 {user['streak']}w)")
        elif i == 1:
            st.write(f"🥈 **{user['user_id']}** - {user['points']} points (🔥 {user['streak']}w)")
        elif i == 2:
            st.write(f"🥉 **{user['user_id']}** - {user['points']} points (🔥 {user['streak']}w)")
        else:
            st.write(f"{i+1}. **{user['user_id']}** - {user['points']} points (🔥 {user['streak']}w)")

if __name__ == "__main__":
    main()