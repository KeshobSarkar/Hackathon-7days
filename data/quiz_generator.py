import openai
import json
import chromadb
import os
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuizGenerator:
    def __init__(self):
        # Initialize OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
        else:
            print("✅ OpenAI API key loaded successfully")
        
        # Cost tracking
        self.total_tokens_used = 0
        self.cost_per_token = 0.0015 / 1000  # GPT-3.5-turbo input cost
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
            self.questions_collection = self.chroma_client.get_collection("quiz_questions")
            print("✅ Loaded existing quiz questions collection")
        except:
            self.chroma_client = chromadb.PersistentClient(path="./database/chroma_db")
            self.questions_collection = self.chroma_client.create_collection("quiz_questions")
            print("✅ Created new quiz questions collection")
    
    def call_openai(self, prompt, model="gpt-3.5-turbo"):
        """Call OpenAI API with error handling"""
        if not self.api_key:
            raise Exception("OpenAI API key not configured")
        
        # Budget check
        current_cost = self.total_tokens_used * self.cost_per_token
        if current_cost > 4.5:  # Stop at $4.5 to be safe
            raise Exception("🚨 Budget limit nearly reached! Switch to demo mode.")
        
        try:
            print(f"🤖 Calling OpenAI with model: {model}")
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a quiz generator specializing in QIC Group insurance products in Qatar. 
                        Always return valid JSON format. Make questions specific to QIC services and accurate."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Track usage
            tokens_used = response.usage.total_tokens
            self.total_tokens_used += tokens_used
            cost_this_call = tokens_used * self.cost_per_token
            total_cost = self.total_tokens_used * self.cost_per_token
            
            print(f"✅ OpenAI response received")
            print(f"💰 Tokens used: {tokens_used} | This call: ${cost_this_call:.4f} | Total: ${total_cost:.4f}")
            
            return response.choices[0].message.content
            
        except openai.AuthenticationError:
            raise Exception("Invalid OpenAI API key. Please check your key.")
        except openai.RateLimitError:
            raise Exception("OpenAI rate limit exceeded. Please wait a moment.")
        except openai.APIConnectionError:
            raise Exception("Network error. Please check your connection.")
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def generate_quiz(self, theme, difficulty="easy", num_questions=5):
        """Generate QIC-themed quiz using OpenAI"""
        
        # Budget check
        remaining_budget = self.get_remaining_budget()
        if remaining_budget < 0.1:
            print("🔄 Low budget - switching to demo mode")
            return self.get_theme_specific_demo(theme, num_questions)
        
        # Check if API key is available
        if not self.api_key:
            print("❌ No OpenAI API key found - using demo questions")
            return self.get_theme_specific_demo(theme, num_questions)
        
        print(f"🎯 Generating {num_questions} {difficulty} questions about {theme}")
        print(f"💰 Remaining budget: ${remaining_budget:.2f}")
        
        # QIC-specific theme details
        theme_contexts = {
            "Car Insurance": """
            QIC Car Insurance in Qatar:
            - TPL (Third Party Liability) - mandatory by Qatari law
            - Comprehensive insurance - covers own damage + third party
            - GCC car insurance for cross-border travel
            - Istimara renewal requirements
            - Premium calculation factors
            - Claims process for motor insurance
            - Online policy purchase through QIC
            - Different coverage options and benefits
            - No-claim discounts and benefits
            """,
            
            "Visitors Insurance": """
            QIC Visitors Health Insurance in Qatar:
            - Mandatory for all visitors entering Qatar
            - Visa requirement linkage
            - Coverage: emergency medical treatment, hospitalization
            - Application process online
            - Duration matching visa validity
            - Family visitor insurance options
            - Benefits and coverage limits
            - Emergency medical evacuation
            - Pre-existing conditions policy
            """,
            
            "Travel Insurance": """
            QIC Travel Insurance from Qatar:
            - Outbound travel insurance
            - Schengen area specific requirements
            - Coverage: trip cancellation, medical emergencies, lost baggage
            - Adventure sports coverage options
            - Online claims submission
            - 24/7 emergency assistance
            - Different travel insurance packages
            - Business travel coverage
            - Family travel insurance
            """,
            
            "QIC Company": """
            QIC Group Company Information:
            - Founded in 1964, first insurance company in Qatar
            - Market leader in Qatar insurance sector
            - A- rating from S&P Global
            - 2 million clients across Qatar and GCC
            - Online insurance pioneer in Qatar
            - Awards and recognitions
            - Subsidiaries and international presence
            - Company achievements and milestones
            - Digital transformation initiatives
            """,
            
            "Claims Process": """
            QIC Claims Handling Process:
            - Motor claims: police report requirements, garage network
            - Travel claims: documentation requirements
            - Home insurance claims process
            - Online claim tracking system
            - Claim settlement timeframes
            - Required documents for different claim types
            - Claim approval process
            - Cashless claim settlements
            - Third-party claim handling
            """,
            
            "Insurance Products": """
            QIC Insurance Product Portfolio:
            - Home Contents Insurance
            - Boat & Yacht Insurance
            - Personal Accident Insurance
            - Business Shield for companies
            - Golf Insurance
            - School Fees Protection
            - Investment-linked products
            - Specialized insurance solutions
            - Cyber insurance options
            - Medical insurance products
            """,
            
            "Qatar Living": """
            Living in Qatar with QIC Services:
            - Istimara (vehicle registration) process
            - Car ownership transfer in Qatar
            - Road trip preparation requirements
            - Family visit visa procedures
            - Mandatory insurance requirements
            - Seasonal considerations for insurance
            - QIC's role in daily life in Qatar
            - Cultural aspects of insurance in Qatar
            - Legal requirements for residents
            """
        }
        
        theme_context = theme_contexts.get(theme, f"QIC {theme} products and services in Qatar")
        
        prompt = f"""
        Create {num_questions} multiple choice questions about {theme} with QIC Group in Qatar.
        
        CONTEXT AND FOCUS:
        {theme_context}
        
        REQUIREMENTS:
        - Questions must be specifically about QIC {theme} products/services in Qatar
        - Make them educational and practical for QIC customers
        - Ensure all facts are accurate about QIC Group
        - Options should be clear, distinct, and plausible
        - Include one correct answer and three incorrect but reasonable alternatives
        - Provide brief explanations focusing on QIC services
        - Make questions diverse and cover different aspects of {theme}
        
        RETURN ONLY VALID JSON with this exact structure:
        {{
            "theme": "{theme}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "question": "Specific question about QIC {theme}?",
                    "type": "multiple_choice",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Exact text of the correct option",
                    "explanation": "Brief explanation about QIC services"
                }}
            ]
        }}
        
        Important: All questions must be factually accurate about QIC Group and relevant to Qatar.
        Make sure the questions are fresh and not repetitive.
        """
        
        try:
            response_text = self.call_openai(prompt)
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = response_text[json_start:json_end]
            quiz_data = json.loads(json_str)
            
            # Validate structure
            if 'questions' not in quiz_data or not isinstance(quiz_data['questions'], list):
                raise ValueError("Invalid quiz structure from AI")
            
            print(f"✅ Generated {len(quiz_data['questions'])} QIC {theme} questions")
            
            # Store in database
            self._store_questions(quiz_data, theme, difficulty)
            
            return quiz_data
            
        except Exception as e:
            print(f"❌ OpenAI generation failed: {e}")
            print("🔄 Falling back to QIC-specific demo questions")
            return self.get_theme_specific_demo(theme, num_questions)
    
    def get_theme_specific_demo(self, theme, num_questions):
        """Provide QIC-specific demo questions when AI fails"""
        qic_demos = {
            "Car Insurance": [
                {
                    "question": "What is the minimum car insurance required by Qatari law that QIC provides?",
                    "type": "multiple_choice",
                    "options": ["Third Party Liability (TPL)", "Comprehensive Insurance", "GCC Cross-border Insurance", "No insurance required"],
                    "correct_answer": "Third Party Liability (TPL)",
                    "explanation": "TPL is mandatory by Qatari law for all vehicles, and QIC is a leading provider."
                },
                {
                    "question": "What does QIC Comprehensive car insurance typically cover?",
                    "type": "multiple_choice", 
                    "options": ["Only third party damages", "Own vehicle damage and third party liabilities", "Only theft coverage", "Only accident coverage for other vehicles"],
                    "correct_answer": "Own vehicle damage and third party liabilities",
                    "explanation": "QIC Comprehensive insurance covers damage to your own vehicle plus third party liabilities."
                },
                {
                    "question": "What is Istimara in the context of QIC car insurance?",
                    "type": "multiple_choice",
                    "options": ["Vehicle registration card", "Insurance policy document", "Driver's license", "Traffic violation ticket"],
                    "correct_answer": "Vehicle registration card", 
                    "explanation": "Istimara is the vehicle registration card required for all vehicles in Qatar, and insurance is needed for its renewal."
                }
            ],
            
            "Visitors Insurance": [
                {
                    "question": "Who needs QIC Visitors Health Insurance in Qatar?",
                    "type": "multiple_choice", 
                    "options": ["Only tourists staying in hotels", "All visitors entering Qatar", "Only business visitors", "Only family visitors on specific visas"],
                    "correct_answer": "All visitors entering Qatar",
                    "explanation": "QIC Visitors Insurance is mandatory for all visitors to Qatar as per government regulations."
                },
                {
                    "question": "What is typically covered by QIC visitors insurance?",
                    "type": "multiple_choice",
                    "options": ["Emergency medical treatment", "Elective surgeries", "Dental cosmetics", "Vision correction"],
                    "correct_answer": "Emergency medical treatment",
                    "explanation": "QIC Visitors insurance primarily covers emergency medical treatments and hospitalization."
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
        questions = qic_demos.get(theme, qic_demos["Car Insurance"])
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
            print(f"💾 Stored {len(quiz_data['questions'])} questions for {theme}")
        except Exception as e:
            print(f"⚠️ Could not store questions: {e}")
    
    def evaluate_answers(self, quiz, user_answers):
        """Evaluate user answers and provide explanations"""
        results = []
        for i, (question, user_answer) in enumerate(zip(quiz['questions'], user_answers)):
            is_correct = user_answer == question['correct_answer']
            results.append({
                'question_number': i + 1,
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'explanation': question.get('explanation', 'QIC provides comprehensive insurance solutions in Qatar.')
            })
        return results
    
    def get_remaining_budget(self):
        """Check remaining API budget"""
        current_cost = self.total_tokens_used * self.cost_per_token
        remaining = 5.0 - current_cost
        return remaining
    
    def get_usage_stats(self):
        """Get API usage statistics"""
        current_cost = self.total_tokens_used * self.cost_per_token
        remaining = 5.0 - current_cost
        
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost": f"${current_cost:.4f}",
            "remaining_budget": f"${remaining:.2f}",
            "estimated_questions_remaining": int(remaining / 0.01)  # rough estimate
        }

def test_qic_quiz():
    """Test the QIC quiz generator with all themes"""
    print("🧪 Testing QIC Quiz Generator with OpenAI...")
    generator = QuizGenerator()
    
    themes = ["Car Insurance", "Visitors Insurance", "Travel Insurance", "QIC Company", "Claims Process", "Insurance Products", "Qatar Living"]
    
    for theme in themes:
        print(f"\n🎯 Testing: {theme}")
        try:
            quiz = generator.generate_quiz(theme, "easy", 3)
            
            print(f"📝 Generated {len(quiz['questions'])} QIC {theme} questions:")
            for i, q in enumerate(quiz['questions']):
                print(f"   Q{i+1}: {q['question']}")
                print(f"   ✅ Correct: {q['correct_answer']}")
            
            # Test evaluation
            user_answers = [q['options'][0] for q in quiz['questions']]  # Pick first option
            results = generator.evaluate_answers(quiz, user_answers)
            
            correct_count = sum(1 for r in results if r['is_correct'])
            print(f"📊 Test Results: {correct_count}/{len(results)} correct")
            
        except Exception as e:
            print(f"❌ Error with {theme}: {e}")
        
        print("─" * 50)
    
    # Show final usage
    if generator.api_key:
        usage = generator.get_usage_stats()
        print(f"\n💰 Final Usage Stats:")
        print(f"   Total Tokens: {usage['total_tokens_used']}")
        print(f"   Total Cost: {usage['total_cost']}")
        print(f"   Remaining Budget: {usage['remaining_budget']}")

if __name__ == "__main__":
    test_qic_quiz()