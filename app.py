import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

def get_mental_health_response(prompt):
    # Add context to make responses more focused on mental health
    context = """You are a supportive and empathetic mental health chatbot. 
    Provide helpful, non-medical advice and emotional support. 
    If someone appears to be in crisis, always recommend seeking professional help.
    Never provide medical diagnoses or treatment recommendations."""
    
    full_prompt = f"{context}\n\nUser Query: {prompt}"
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            if "rate limit exceeded" in str(e).lower():
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return "I'm currently experiencing high demand. Please try again in a few moments. If you need immediate assistance, please contact a mental health professional or emergency services."
            return "I apologize, but I'm having trouble processing your request. Please try again or seek professional help if you're in crisis."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please enter a message'})
    
    response = get_mental_health_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
