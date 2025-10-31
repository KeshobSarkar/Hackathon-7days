import random

# Mock question data (we'll replace this later with AI-generated ones)
MOCK_QUESTIONS = {
    "cars": [
        {
            "question": "What does ABS stand for?",
            "options": ["Auto Brake System", "Anti-Lock Braking System", "Air Balance System", "Automatic Braking Sensor"],
            "answer": "Anti-Lock Braking System",
            "explanation": "ABS prevents wheels from locking during hard braking."
        },
        {
            "question": "Which company manufactures the Mustang?",
            "options": ["Chevrolet", "Ford", "Dodge", "Toyota"],
            "answer": "Ford",
            "explanation": "The Ford Mustang is an American muscle car made by Ford."
        }
    ],
    "sports": [
        {
            "question": "How many players are on a football (soccer) team on the field?",
            "options": ["9", "10", "11", "12"],
            "answer": "11",
            "explanation": "Each team fields 11 players in a standard soccer match."
        },
        {
            "question": "In which sport is the term 'love' used?",
            "options": ["Tennis", "Cricket", "Baseball", "Hockey"],
            "answer": "Tennis",
            "explanation": "'Love' in tennis means a score of zero."
        }
    ]
}

def get_quiz_questions(theme="cars", num=2):
    """Get random questions from a given theme."""
    questions = MOCK_QUESTIONS.get(theme, [])
    random.shuffle(questions)
    return questions[:num]

if __name__ == "__main__":
    print("Sample Questions:")
    for q in get_quiz_questions("cars"):
        print(f"Q: {q['question']}")
        for i, opt in enumerate(q["options"], 1):
            print(f"   {i}. {opt}")
        print()

