from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# ======================================
# GEMINI CONFIG
# ======================================
GEMINI_API_KEY = "AIzaSyAu-dxF8fD_hBsPGuiG0ZwPYO-NqLNwiZM"
GEMINI_MODEL = "gemini-2.5-flash"

# ======================================
# SERVE FRONTEND
# ======================================
@app.route("/")
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ======================================
# CHATBOT ROUTE
# ======================================
@app.route("/api/campus-ai", methods=["POST"])
def campus_ai():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        "You are Campus AI — SmartEra University's official chatbot. "
                        "Provide short, accurate answers about admissions, fees, placements, or programs. "
                        "If unrelated, say 'I only answer SmartEra University related queries.'\n\n"
                        f"User: {user_message}"
                    )
                }]
            }]
        }
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        if response.status_code != 200:
            print("Gemini Error:", response.text)
            return jsonify({"answer": "Gemini API call failed. Check your key or model name."})
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer})
    except Exception as e:
        print("Server Error:", e)
        return jsonify({"answer": f"Internal Error: {str(e)}"})

# ======================================
# CONTACT FORM ROUTE
# ======================================
@app.route("/api/contact", methods=["POST"])
def contact_form():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")
    if not (name and email and message):
        return jsonify({"status": "error", "message": "All fields are required."})
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="smartera_db"
        )
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_form (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO contact_form (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "message": "Message submitted successfully."})
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"status": "error", "message": "Database connection failed."})

# ======================================
# RUN APP
# ======================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Campus AI running at http://127.0.0.1:{port}")
    app.run(debug=True, port=port)
