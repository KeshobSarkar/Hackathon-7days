import json
import os
from datetime import datetime, timedelta
import uuid

class RewardDB:
    def __init__(self):
        # Use JSON files instead of PostgreSQL
        self.users_file = "database/users.json"
        self.rewards_file = "database/rewards.json"
        self.transactions_file = "database/transactions.json"
        
        # Create database directory if it doesn't exist
        os.makedirs("database", exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with default data"""
        # Users file
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        # Rewards file
        if not os.path.exists(self.rewards_file):
            with open(self.rewards_file, 'w') as f:
                json.dump({}, f)
        
        # Transactions file
        if not os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'w') as f:
                json.dump({}, f)
    
    def _read_json(self, filename):
        """Read JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_json(self, filename, data):
        """Write JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_wallet(self, user_id):
        """Get user wallet data"""
        users = self._read_json(self.users_file)
        
        if str(user_id) not in users:
            # Create new user
            users[str(user_id)] = {
                "points": 0,
                "streak": {
                    "current": 0,
                    "last_quiz": None,
                    "warnings": 0
                },
                "coupons": [],
                "quiz_history": []  # Added for leaderboard
            }
            self._write_json(self.users_file, users)
        
        return users[str(user_id)]
    
    def add_points(self, user_id, points, reason):
        """Add points to user"""
        users = self._read_json(self.users_file)
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            self.get_user_wallet(user_id)  # Initialize user
        
        users[user_id_str]["points"] += points
        
        # Log transaction
        transactions = self._read_json(self.transactions_file)
        transaction_id = str(uuid.uuid4())
        transactions[transaction_id] = {
            "user_id": user_id_str,  # Store as string
            "points": points,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self._write_json(self.users_file, users)
        self._write_json(self.transactions_file, transactions)
        
        print(f"✅ Added {points} points to user {user_id} for: {reason}")
    
    def update_streak(self, user_id, quiz_passed):
        """Update user streak"""
        users = self._read_json(self.users_file)
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            self.get_user_wallet(user_id)  # Initialize user
        
        current_time = datetime.now().isoformat()
        
        if quiz_passed:
            users[user_id_str]["streak"]["current"] += 1
            users[user_id_str]["streak"]["last_quiz"] = current_time
            users[user_id_str]["streak"]["warnings"] = 0
            print(f"🔥 Streak updated: {users[user_id_str]['streak']['current']} weeks")
        else:
            # Failed quiz - reset streak
            users[user_id_str]["streak"]["current"] = 0
            users[user_id_str]["streak"]["warnings"] += 1
            print(f"❌ Streak reset for user {user_id}")
        
        self._write_json(self.users_file, users)
    
    def issue_coupon(self, user_id, discount, valid_days):
        """Issue a coupon to user"""
        users = self._read_json(self.users_file)
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            self.get_user_wallet(user_id)  # Initialize user
        
        coupon_code = f"QIC{str(uuid.uuid4())[:8].upper()}"
        expires_at = (datetime.now() + timedelta(days=valid_days)).isoformat()
        
        coupon = {
            "code": coupon_code,
            "discount": discount,
            "issued_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "used": False
        }
        
        users[user_id_str]["coupons"].append(coupon)
        
        # Store in rewards file too
        rewards = self._read_json(self.rewards_file)
        rewards[coupon_code] = coupon
        rewards[coupon_code]["user_id"] = user_id_str  # Store as string
        
        self._write_json(self.users_file, users)
        self._write_json(self.rewards_file, rewards)
        
        print(f"🎫 Issued coupon {coupon_code} to user {user_id}")
        return coupon_code

    def add_quiz_attempt(self, user_id, theme, score, total_questions, points_earned):
        """Record a quiz attempt for leaderboard"""
        users = self._read_json(self.users_file)
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            self.get_user_wallet(user_id)  # Initialize user
        
        # Add quiz history
        if "quiz_history" not in users[user_id_str]:
            users[user_id_str]["quiz_history"] = []
        
        quiz_attempt = {
            "theme": theme,
            "score": score,
            "total_questions": total_questions,
            "points_earned": points_earned,
            "timestamp": datetime.now().isoformat()
        }
        
        users[user_id_str]["quiz_history"].append(quiz_attempt)
        
        # Keep only last 20 attempts to prevent file from growing too large
        users[user_id_str]["quiz_history"] = users[user_id_str]["quiz_history"][-20:]
        
        self._write_json(self.users_file, users)
        print(f"📊 Recorded quiz attempt for user {user_id}: {score}/{total_questions} correct")

    def get_leaderboard(self, limit=10):
        """Get top users for leaderboard based on points"""
        users = self._read_json(self.users_file)
        
        leaderboard = []
        for user_id, user_data in users.items():
            total_points = user_data.get("points", 0)
            streak = user_data.get("streak", {}).get("current", 0)
            quiz_count = len(user_data.get("quiz_history", []))
            
            # Calculate average score
            quiz_history = user_data.get("quiz_history", [])
            avg_score = 0
            if quiz_history:
                total_correct = sum(quiz.get("score", 0) for quiz in quiz_history)
                total_questions = sum(quiz.get("total_questions", 0) for quiz in quiz_history)
                if total_questions > 0:
                    avg_score = (total_correct / total_questions) * 100
            
            leaderboard.append({
                "user_id": user_id,  # Keep as string to support usernames
                "points": total_points,
                "streak": streak,
                "quiz_count": quiz_count,
                "avg_score": round(avg_score, 1)
            })
        
        # Sort by points (descending), then by streak, then by average score
        leaderboard.sort(key=lambda x: (-x["points"], -x["streak"], -x["avg_score"]))
        
        return leaderboard[:limit]

    def get_user_rank(self, user_id):
        """Get user's current rank in leaderboard"""
        leaderboard = self.get_leaderboard(limit=100)  # Get larger list to find rank
        user_id_str = str(user_id)  # Convert to string for comparison
        
        for rank, user in enumerate(leaderboard, 1):
            if user["user_id"] == user_id_str:
                return rank
        return None

    def get_all_users(self):
        """Get all users for admin purposes"""
        return self._read_json(self.users_file)

    def reset_user_data(self, user_id):
        """Reset user data (for testing)"""
        users = self._read_json(self.users_file)
        user_id_str = str(user_id)
        
        if user_id_str in users:
            users[user_id_str] = {
                "points": 0,
                "streak": {
                    "current": 0,
                    "last_quiz": None,
                    "warnings": 0
                },
                "coupons": [],
                "quiz_history": []
            }
            self._write_json(self.users_file, users)
            print(f"🔄 Reset data for user {user_id}")
        return True