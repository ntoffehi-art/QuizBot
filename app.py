import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-question', methods=['POST', 'OPTIONS'])
def generate_question():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY non trouvé dans l'environnement."}), 500

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
    1. Évite absolument les questions génériques ou répétitives.
    2. La question doit être rédigée clairement sans ambiguïté.
    3. Propose exactement 3 options distinctes et plausibles. Une seule réponse doit être correcte.
    4. L'explication doit être courte et pédagogique.

    Renvoie un objet JSON valide avec cette structure exacte :
    {{
        "question": "Texte de la question",
        "options": ["Option 1", "Option 2", "Option 3"],
        "answer": "Exactement le texte de la bonne option parmi les 3",
        "explanation": "Explication courte"
    }}
    """

    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        res = requests.post(url, json=payload, timeout=60)
        res_data = res.json()

        if "error" in res_data:
            return jsonify({"error": res_data["error"].get("message", "API Error")}), 400

        text_response = res_data['candidates'][0]['content']['parts'][0]['text']
        parsed_data = json.loads(text_response)
        
        return jsonify(parsed_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)