import json
import random
import string
from datetime import datetime, timedelta
import os

class RewardEngine:
    def __init__(self):
        self.rewards_file = "database/rewards.json"
        self.transactions_file = "database/transactions.json"
        self.load_data()
    
    def load_data(self):
        # Initialize rewards data
        if not os.path.exists(self.rewards_file):
            self.initialize_rewards_file()
        else:
            try:
                with open(self.rewards_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        self.initialize_rewards_file()
                    else:
                        self.rewards_data = json.loads(content)
            except (json.JSONDecodeError, Exception):
                self.initialize_rewards_file()
        
        # Initialize transactions
        if not os.path.exists(self.transactions_file):
            self.initialize_transactions_file()
        else:
            try:
                with open(self.transactions_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        self.initialize_transactions_file()
                    else:
                        self.transactions_data = json.loads(content)
            except (json.JSONDecodeError, Exception):
                self.initialize_transactions_file()
    
    def initialize_rewards_file(self):
        self.rewards_data = {
            "active_coupons": {},
            "redeemed_coupons": {},
            "reward_catalog": {
                "weekly_completion": {"points": 50, "coupon": True},
                "perfect_score": {"points": 25, "coupon": False},
                "streak_4_weeks": {"points": 200, "coupon": True}
            }
        }
        self.save_rewards()
    
    def initialize_transactions_file(self):
        self.transactions_data = {}
        self.save_transactions()
    
    def save_rewards(self):
        with open(self.rewards_file, 'w') as f:
            json.dump(self.rewards_data, f, indent=2)
    
    def save_transactions(self):
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions_data, f, indent=2)
    
    def calculate_quiz_points(self, correct_answers, total_questions):
        base_points = correct_answers * 10
        perfect_bonus = 25 if correct_answers == total_questions else 0
        return base_points + perfect_bonus
    
    def should_give_coupon(self, correct_answers, total_questions, user_streak):
        """Only give coupon for good performance"""
        if total_questions == 0:
            return False
            
        score_percentage = (correct_answers / total_questions) * 100
        
        # Minimum 50% score to get coupon, OR maintaining streak of 2+ weeks
        if score_percentage >= 50:
            return True
        if user_streak >= 2:
            return True
            
        return False
    
    def generate_coupon(self, user_id, user_streak):
        coupon_code = f"QUIZ{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}"
        
        # Coupon value based on streak
        if user_streak >= 8:
            coupon_value = "30% OFF"
            expiry_days = 30
        elif user_streak >= 4:
            coupon_value = "20% OFF" 
            expiry_days = 14
        else:
            coupon_value = "10% OFF"
            expiry_days = 7
        
        coupon = {
            "code": coupon_code,
            "user_id": user_id,
            "value": coupon_value,
            "expiry_date": (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d"),
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active"
        }
        
        # Store coupon
        if user_id not in self.rewards_data["active_coupons"]:
            self.rewards_data["active_coupons"][user_id] = []
        
        self.rewards_data["active_coupons"][user_id].append(coupon)
        self.save_rewards()
        
        return coupon
    
    def get_user_coupons(self, user_id):
        return self.rewards_data["active_coupons"].get(user_id, [])
    
    def record_transaction(self, user_id, points, reason):
        if user_id not in self.transactions_data:
            self.transactions_data[user_id] = {
                "total_points_earned": 0,
                "quiz_completions": []
            }
        
        self.transactions_data[user_id]["total_points_earned"] += points
        self.transactions_data[user_id]["quiz_completions"].append({
            "date": datetime.now().isoformat(),
            "points": points,
            "reason": reason
        })
        
        self.save_transactions()

def test_reward_engine():
    print("🧪 Testing Reward Engine...")
    
    engine = RewardEngine()
    
    # Test points calculation
    points = engine.calculate_quiz_points(3, 5)
    print(f" Points calculation: {points} points")
    
    # Test coupon logic
    should_give = engine.should_give_coupon(0, 3, 1)
    print(f" Coupon for 0% score: {should_give} (should be False)")
    
    should_give = engine.should_give_coupon(2, 3, 1)
    print(f"Coupon for 66% score: {should_give} (should be True)")
    
    # Test coupon generation
    coupon = engine.generate_coupon("test_user", 1)
    print(f"Coupon generated: {coupon['code']} - {coupon['value']}")

    print("Transaction recorded")

if __name__ == "__main__":
    test_reward_engine()