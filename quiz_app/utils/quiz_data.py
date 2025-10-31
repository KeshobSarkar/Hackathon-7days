import requests
import json

prompt = "Generate 5 multiple-choice questions about Artificial Intelligence. Format each question as JSON with 'question', 'options', and 'answer'."

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt}
)

data = response.json()
print(data['response'])

# Optionally, save to file
with open("quiz_data.json", "w") as f:
    f.write(data['response'])
