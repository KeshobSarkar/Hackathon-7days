import requests
import json
import chromadb
import time

class QuizGenerator:
    def __init__(self):
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
            self.questions_collection = self.chroma_client.get_collection("quiz_questions")
            print(" Loaded existing quiz questions collection")
        except:
            self.chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
            self.questions_collection = self.chroma_client.create_collection("quiz_questions")
            print(" Created new quiz questions collection")
    
    def call_ollama(self, prompt, model="llama3:latest"):
        """Call local Ollama API to generate content"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            print(f"🤖 Calling Ollama with model: {model}")
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
            response.raise_for_status()
            result = response.json()
            print("✅ Successfully got response from Ollama")
            return result["response"]
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Make sure 'ollama serve' is running!")
        except Exception as e:
            raise Exception(f"Ollama API error: {e}")
    
    def generate_quiz(self, theme, difficulty="easy", num_questions=3):
        """Generate a quiz using Ollama AI"""
        print(f"🎯 Generating {num_questions} {difficulty} questions about {theme}")
        
        # More specific prompts for each theme
        theme_prompts = {
            "Car Insurance": """
            Focus on QIC car insurance products in Qatar:
            - TPL (Third Party Liability) - mandatory insurance
            - Comprehensive car insurance
            - GCC car insurance for cross-border travel
            - Insurance requirements for car registration
            - Istimara renewal process
            - Premium calculations and coverage options
            """,
            
            "Visitors Insurance": """
            Focus on QIC visitors health insurance in Qatar:
            - Mandatory health insurance for visitors
            - Visa requirements and insurance
            - Coverage details and benefits
            - Application process for visitor insurance
            - Duration and renewal of visitor insurance
            - Emergency medical coverage
            """,
            
            "Travel Insurance": """
            Focus on QIC travel insurance products:
            - Outbound travel insurance from Qatar
            - Schengen area travel insurance requirements
            - International travel coverage
            - Trip cancellation and interruption
            - Medical emergencies abroad
            - Lost baggage and travel delays
            - Adventure sports coverage
            """,
            
            "QIC Company": """
            Focus on QIC Group company information:
            - Founded in 1964, first insurance company in Qatar
            - A- rating from S&P Global
            - 2 million clients across Qatar and GCC
            - Market leader in Qatar insurance
            - Company achievements and awards
            - Subsidiaries and international presence
            """,
            
            "Claims Process": """
            Focus on QIC insurance claims procedures:
            - Motor insurance claims process
            - Travel insurance claims
            - Home insurance claims
            - Required documentation for claims
            - Claim tracking and status updates
            - Claim settlement process
            - Timeframes for claim processing
            """,
            
            "Insurance Products": """
            Focus on QIC's range of insurance products:
            - Home contents insurance
            - Boat and yacht insurance
            - Personal accident insurance
            - Business shield insurance
            - Golf insurance
            - School fees protection
            - Specialized insurance products
            """,
            
            "Qatar Living": """
            Focus on living in Qatar and related insurance:
            - Car ownership transfer process
            - Istimara renewal procedures
            - Visa and residency requirements
            - Road trip preparation in Qatar
            - Local regulations and compliance
            - Seasonal considerations for insurance
            """
        }
        
        theme_description = theme_prompts.get(theme, f"QIC {theme} insurance products and services")
        
        prompt = f"""
        Create exactly {num_questions} multiple choice quiz questions about: {theme}
        
        CONTEXT AND FOCUS:
        {theme_description}
        
        REQUIREMENTS:
        - Questions must be specifically about {theme}
        - Make them educational and practical for insurance customers
        - Options should be clear and distinct
        - Ensure correct answers are factually accurate about QIC
        - Questions should test useful knowledge
        
        RETURN ONLY VALID JSON with this exact structure:
        {{
            "theme": "{theme}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "question": "Specific question about {theme}?",
                    "type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Exact text of the correct option",
                    "explanation": "Brief explanation focusing on QIC services"
                }}
            ]
        }}
        
        Do not include any other text outside the JSON.
        """
        
        try:
            response_text = self.call_ollama(prompt)
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = response_text[json_start:json_end]
            quiz_data = json.loads(json_str)
            
            # Validate we got questions for the right theme
            if quiz_data.get('theme') != theme:
                print(f" AI returned wrong theme: {quiz_data.get('theme')} instead of {theme}")
        
            print(f"Generated {len(quiz_data['questions'])} questions about {theme}")
            
            # Store in database
            self._store_questions(quiz_data, theme, difficulty)
            
            return quiz_data
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            # Return THEME-SPECIFIC demo questions
            return self.get_theme_specific_demo(theme, num_questions)
    
    def get_theme_specific_demo(self, theme, num_questions):
        """Provide theme-specific demo questions when AI fails"""
        theme_demos = {
            "Car Insurance": [
                {
                    "question": "What is the minimum car insurance required by Qatari law?",
                    "type": "multiple_choice",
                    "options": ["Third Party Liability (TPL)", "Comprehensive Insurance", "GCC Insurance", "No insurance required"],
                    "correct_answer": "Third Party Liability (TPL)",
                    "explanation": "TPL is mandatory by Qatari law for all vehicles."
                },
                {
                    "question": "What does comprehensive car insurance from QIC typically cover?",
                    "type": "multiple_choice",
                    "options": ["Only third party damages", "Own vehicle damage and third party", "Only theft coverage", "Only accident coverage"],
                    "correct_answer": "Own vehicle damage and third party",
                    "explanation": "Comprehensive insurance covers both your own vehicle and third party liabilities."
                },
                {
                    "question": "For how long is a typical QIC car insurance policy valid?",
                    "type": "multiple_choice",
                    "options": ["6 months", "1 year", "2 years", "3 years"],
                    "correct_answer": "1 year",
                    "explanation": "QIC car insurance policies are typically valid for one year and renewable."
                }
            ],
            
            "Visitors Insurance": [
                {
                    "question": "Who needs mandatory visitors health insurance in Qatar?",
                    "type": "multiple_choice",
                    "options": ["Only tourists", "All visitors entering Qatar", "Only business visitors", "Only family visitors"],
                    "correct_answer": "All visitors entering Qatar",
                    "explanation": "All visitors to Qatar require mandatory health insurance as per government regulations."
                },
                {
                    "question": "What is typically covered by QIC visitors insurance?",
                    "type": "multiple_choice",
                    "options": ["Emergency medical treatment", "Elective surgeries", "Dental cosmetics", "Vision correction"],
                    "correct_answer": "Emergency medical treatment",
                    "explanation": "Visitors insurance primarily covers emergency medical treatments and hospitalization."
                }
            ],
            
            "Travel Insurance": [
                {
                    "question": "Which destination requires specific Schengen travel insurance from QIC?",
                    "type": "multiple_choice",
                    "options": ["European Schengen countries", "All Asian countries", "African nations", "Middle Eastern countries"],
                    "correct_answer": "European Schengen countries",
                    "explanation": "Schengen area countries require specific travel insurance meeting their requirements."
                },
                {
                    "question": "What common travel incident is covered by QIC travel insurance?",
                    "type": "multiple_choice",
                    "options": ["Lost baggage", "Missed hotel reservations", "Currency exchange losses", "Personal shopping"],
                    "correct_answer": "Lost baggage",
                    "explanation": "QIC travel insurance covers lost or delayed baggage during travel."
                }
            ],
            
            "QIC Company": [
                {
                    "question": "In which year was QIC Group established?",
                    "type": "multiple_choice",
                    "options": ["1964", "1975", "1982", "1990"],
                    "correct_answer": "1964",
                    "explanation": "QIC Group was established in 1964 as Qatar's first national insurance company."
                },
                {
                    "question": "What rating did QIC receive from S&P Global?",
                    "type": "multiple_choice",
                    "options": ["A-", "B+", "AA", "BBB"],
                    "correct_answer": "A-",
                    "explanation": "QIC maintains an A- rating from S&P Global, indicating strong financial stability."
                }
            ],
            
            "Claims Process": [
                {
                    "question": "What is the first step in filing a QIC motor insurance claim?",
                    "type": "multiple_choice",
                    "options": ["Contact police if required", "Repair vehicle immediately", "Wait for insurance call", "Post on social media"],
                    "correct_answer": "Contact police if required",
                    "explanation": "For motor accidents, contact police first if necessary, then inform QIC."
                },
                {
                    "question": "Which document is essential for a QIC travel insurance claim?",
                    "type": "multiple_choice",
                    "options": ["Medical reports and receipts", "Hotel booking confirmations", "Tourist attraction tickets", "Restaurant bills"],
                    "correct_answer": "Medical reports and receipts",
                    "explanation": "Medical documentation is crucial for travel insurance claims involving health issues."
                }
            ],
            
            "Insurance Products": [
                {
                    "question": "Which QIC product protects personal belongings at home?",
                    "type": "multiple_choice",
                    "options": ["Home Contents Insurance", "Car Insurance", "Travel Insurance", "Boat Insurance"],
                    "correct_answer": "Home Contents Insurance",
                    "explanation": "Home Contents Insurance covers personal belongings against theft, fire, and other risks."
                },
                {
                    "question": "What does QIC Personal Accident insurance typically cover?",
                    "type": "multiple_choice",
                    "options": ["Accidental death and disability", "Illness treatments", "Routine health checkups", "Dental care"],
                    "correct_answer": "Accidental death and disability",
                    "explanation": "Personal Accident insurance provides coverage for accidental death and permanent disability."
                }
            ],
            
            "Qatar Living": [
                {
                    "question": "What is 'Istimara' in the context of vehicle ownership in Qatar?",
                    "type": "multiple_choice",
                    "options": ["Vehicle registration card", "Driver's license", "Insurance policy", "Vehicle inspection"],
                    "correct_answer": "Vehicle registration card",
                    "explanation": "Istimara is the vehicle registration card required for all vehicles in Qatar."
                },
                {
                    "question": "How often must vehicle insurance be renewed in Qatar?",
                    "type": "multiple_choice",
                    "options": ["Annually", "Every 6 months", "Every 2 years", "Every 5 years"],
                    "correct_answer": "Annually",
                    "explanation": "Vehicle insurance in Qatar must be renewed annually along with vehicle registration."
                }
            ]
        }
        
        # Get questions for the specific theme, fallback to Car Insurance if theme not found
        questions = theme_demos.get(theme, theme_demos["Car Insurance"])
        return {
            "theme": theme,
            "difficulty": "easy",
            "questions": questions[:num_questions]
        }
    
    def _store_questions(self, quiz_data, theme, difficulty):
        """Store questions in ChromaDB"""
        try:
            for i, question in enumerate(quiz_data['questions']):
                question_id = f"{theme}_{difficulty}_{i}_{hash(question['question']) % 10000}"
                
                metadata = {
                    "theme": theme,
                    "difficulty": difficulty,
                    "type": question.get('type', 'multiple_choice'),
                    "correct_answer": question['correct_answer'],
                    "options": json.dumps(question['options'])
                }
                
                self.questions_collection.add(
                    documents=[question['question']],
                    metadatas=[metadata],
                    ids=[question_id]
                )
            print(f"Stored {len(quiz_data['questions'])} questions for {theme}")
        except Exception as e:
            print(f" Could not store questions: {e}")
    
    def evaluate_answers(self, quiz, user_answers):
        """Evaluate user answers"""
        results = []
        for i, (question, user_answer) in enumerate(zip(quiz['questions'], user_answers)):
            is_correct = user_answer == question['correct_answer']
            results.append({
                'question_number': i + 1,
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'explanation': question.get('explanation', 'No explanation provided.')
            })
        return results

def test_generator():
    print("🧪 Testing Quiz Generator with different themes...")
    generator = QuizGenerator()
    
    themes = ["Car Insurance", "Travel Insurance", "QIC Company", "Insurance Products"]
    
    for theme in themes:
        print(f"\n Testing: {theme}")
        quiz = generator.generate_quiz(theme, "easy", 2)
        print(f"Generated {len(quiz['questions'])} questions about {theme}")
        for i, q in enumerate(quiz['questions']):
            print(f"   Q{i+1}: {q['question'][:50]}...")

        # --- Reward system integration ---
        from reward_db import RewardDB
        reward = RewardDB()

        user_id = 1  # Replace this with real user ID

        # Simulate answers (for now all correct)
        user_answers = [q['correct_answer'] for q in quiz['questions']]

        results = generator.evaluate_answers(quiz, user_answers)
        correct = sum(r['is_correct'] for r in results)
        total = len(quiz['questions'])
        passed = correct / total >= 0.6

        reward.add_points(user_id, correct * 50, 'weekly_quiz_completed')
        reward.update_streak(user_id, passed)

        if passed:
            reward.issue_coupon(user_id, "20% off", 7)

        wallet = reward.get_user_wallet(user_id)
        print("\n💰 User Wallet Summary:", wallet)
        print("-----------------------------------------------------")

if __name__ == "__main__":
    test_generator()