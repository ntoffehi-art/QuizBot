import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv  # <--- إضافة هذه المكتبة

load_dotenv()  # <--- تقرأ المفتاح من ملف .env محلياً

basedir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
CORS(app)
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-question', methods=['POST', 'OPTIONS'])
def generate_question():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        data = request.get_json(force=True) or {}
    except Exception:
        data = {}

    category = data.get('category', 'IT')
    language = data.get('language', 'fr')

    prompt = f"""
    Tu es un expert en création de quiz éducatifs et captivants.
    Génère une question de quiz UNIQUE, ORIGINALE et CLAIRE sur le thème "{category}" en langue "{language}".

    Consignes strictes :
    1. Évite absolument les questions génériques, classiques ou répétitives. Choisis un sous-thème précis, un détail intéressant ou un angle original.
    2. La question doit être rédigée clairement, de manière compréhensible et sans ambiguïté.
    3. Propose exactement 3 options distinctes, claires et plausibles. Une seule réponse doit être correcte.
    4. L'explication doit être courte, claire et pédagogique.

    Renvoie UNIQUEMENT un objet JSON valide avec cette structure exacte, sans balises markdown ni texte additionnel :
    {{
        "question": "Texte de la question claire et originale",
        "options": ["Option 1", "Option 2", "Option 3"],
        "answer": "Exactement le texte de la bonne option parmi les 3",
        "explanation": "Explication courte et claire"
    }}
    """

    # الرابط الصحيح الرسمي المعتمد من Google Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
        res_data = res.json()

        if "error" in res_data:
            return jsonify({"error": res_data["error"].get("message", "API Error")}), 400

        text_response = res_data['candidates'][0]['content']['parts'][0]['text']
        clean_json = text_response.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_json)
        
        return jsonify(parsed_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)