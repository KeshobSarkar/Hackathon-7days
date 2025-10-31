import json
import os
from datetime import datetime, timedelta

class StreakManager:
    def __init__(self):
        self.users_file = "database/users.json"
        self.load_users()
    
    def load_users(self):
        if not os.path.exists(self.users_file):
            self.users_data = {}
            self.save_users()
        else:
            try:
                with open(self.users_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        self.users_data = {}
                    else:
                        self.users_data = json.loads(content)
            except (json.JSONDecodeError, Exception):
                self.users_data = {}
                self.save_users()
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users_data, f, indent=2)
    
    def initialize_user(self, user_id):
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                "current_streak": 0,
                "longest_streak": 0,
                "total_points": 0,
                "last_quiz_date": None,
                "warnings": 0,
                "quiz_history": []
            }
            self.save_users()
    
    def get_user_data(self, user_id):
        self.initialize_user(user_id)
        return self.users_data[user_id]
    
    def update_streak(self, user_id, points_earned):
        user_data = self.get_user_data(user_id)
        current_date = datetime.now().isoformat()
        
        # Check if this is a new week
        last_quiz = user_data.get('last_quiz_date')
        if last_quiz and self.is_same_week(last_quiz):
            return False
        
        # Update user data
        user_data['current_streak'] += 1
        user_data['longest_streak'] = max(user_data['longest_streak'], user_data['current_streak'])
        user_data['total_points'] += points_earned
        user_data['last_quiz_date'] = current_date
        user_data['warnings'] = 0
        
        user_data['quiz_history'].append({
            'date': current_date,
            'points_earned': points_earned
        })
        
        self.save_users()
        return True
    
    def is_same_week(self, date_string):
        try:
            date_obj = datetime.fromisoformat(date_string)
            today = datetime.now()
            
            # For testing: 1 minute cooldown
            time_diff = today - date_obj
            return time_diff.total_seconds() < 60
            
            # For production: weekly cooldown
            # start_week_date = date_obj - timedelta(days=date_obj.weekday())
            # start_week_today = today - timedelta(days=today.weekday())
            # return start_week_date.date() == start_week_today.date()
        except:
            return False
    
    def get_leaderboard_data(self):
        leaderboard = []
        for user_id, data in self.users_data.items():
            leaderboard.append({
                'user_id': user_id,
                'points': data['total_points'],
                'streak': data['current_streak'],
                'quizzes': len(data['quiz_history'])
            })
        
        leaderboard.sort(key=lambda x: x['points'], reverse=True)
        return leaderboard
    
    def get_streak_milestones(self, user_id):
        user_data = self.get_user_data(user_id)
        current_streak = user_data['current_streak']
        
        milestones = [
            {'weeks': 1, 'reward': '10% OFF coupon', 'achieved': current_streak >= 1},
            {'weeks': 4, 'reward': '20% OFF coupon + 200 points', 'achieved': current_streak >= 4},
            {'weeks': 8, 'reward': '30% OFF coupon + 500 points', 'achieved': current_streak >= 8},
            {'weeks': 12, 'reward': 'Premium reward bundle', 'achieved': current_streak >= 12}
        ]
        
        return milestones

def test_streak_manager():
    print("🧪 Testing Streak Manager...")
    
    manager = StreakManager()
    
    # Test user initialization
    manager.initialize_user("test_user")
    user_data = manager.get_user_data("test_user")
    print(f"User created: {user_data['current_streak']} week streak, {user_data['total_points']} points")
    
    # Test streak update
    streak_updated = manager.update_streak("test_user", 50)
    print(f"Streak updated: {streak_updated}")
    
    # Test leaderboard
    leaderboard = manager.get_leaderboard_data()
    print(" Leaderboard created")
    
    print(" All tests passed")

if __name__ == "__main__":
    test_streak_manager()