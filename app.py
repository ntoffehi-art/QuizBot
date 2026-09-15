import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import random

load_dotenv()

basedir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
CORS(app)

def get_active_groq_model(api_key):
    """اختيار الموديلات النصية الرسمية الشغالة فقط واستبعاد الموديلات الخارجية"""
    try:
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            models = res.json().get("data", [])
            # استبعاد الموديلات الصوتية أو الخارجية التي تحتوي على '/' أو كلمات حظر
            valid_models = [
                m["id"] for m in models 
                if "/" not in m["id"] 
                and not any(x in m["id"].lower() for x in ["whisper", "embed", "guard", "safeguard", "vision"])
            ]
            
            # ترتيب الموديلات الرسمية حسب الأولوية والاستقرار
            priority_list = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768"
            ]
            for p in priority_list:
                if p in valid_models:
                    return p
            if valid_models:
                return valid_models[0]
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-question', methods=['POST', 'OPTIONS'])
def generate_question():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    raw_key = os.environ.get("GROQ_API_KEY", "")
    api_key = raw_key.strip().strip('"').strip("'")

    if not api_key:
        return jsonify({"error": "GROQ_API_KEY non trouvé dans l'environnement."}), 400

    selected_model = get_active_groq_model(api_key)
    print(f"--- DEBUG: Selected Official Model = {selected_model} ---")

    try:
        data = request.get_json(force=True) or {}
    except Exception:
        data = {}

    category = data.get('category', 'IT')
    language = data.get('language', 'fr')

    random_seed = random.randint(1000, 99999)

    prompt = f"""
    You are a professional trivia quiz generator.
    
    CRITICAL REQUIREMENTS:
    1. LANGUAGE: The question, options, and explanation MUST BE ENTIRELY IN "{language}".
    2. FACTUAL ONLY: Questions MUST be objective facts or trivia. Strictly FORBID subjective, personal opinion, or preference questions (e.g., "What is your favorite...").
    3. QUESTION: Direct and clear (15 words MAXIMUM).
    4. OPTIONS: Exactly 3 VERY SHORT options (1 to 6 words MAX each). Only ONE is objectively correct.
    5. ANSWER: Exact text of the correct option.
    6. EXPLANATION: Short justification of the fact (8 words MAXIMUM).

    Topic: "{category}"
    Uniqueness seed: {random_seed}

    Return ONLY a valid JSON object matching this structure:
    {{
        "question": "Question text in {language}",
        "options": ["Option 1", "Option 2", "Option 3"],
        "answer": "Option 1",
        "explanation": "Short justification in {language}"
    }}
    """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": selected_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,  # رفع درجة العشوائية للتنوع المنوع
        "response_format": {"type": "json_object"}
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res_data = res.json()

        if "error" in res_data:
            return jsonify({"error": res_data["error"].get("message", "Groq API Error")}), 400

        text_response = res_data['choices'][0]['message']['content']
        parsed_data = json.loads(text_response)
        return jsonify(parsed_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)