
import os
import re

import fitz
from flask import Flask, request, jsonify, session
from flask_cors import CORS

from database import create_table, register_user, verify_user


# ==========================================
# FLASK APP CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-secret-key"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="None"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

FRONTEND_URL = "https://ai-resume-analyser-1-nmjl.onrender.com"

CORS(
    app,
    resources={
        r"/*": {
            "origins": [FRONTEND_URL],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    },
    supports_credentials=True
)


# ==========================================
# DATABASE
# ==========================================

create_table()


# ==========================================
# RESUME ANALYSIS
# ==========================================

SKILLS = [
    "python", "java", "c", "c++", "javascript",
    "html", "css", "sql", "mysql", "mongodb",
    "machine learning", "deep learning",
    "artificial intelligence", "data science",
    "flask", "django", "react", "node.js",
    "git", "github", "communication",
    "problem solving", "data structures",
    "algorithms", "excel", "power bi",
    "tableau", "aws", "cloud computing"
]


def analyze_resume(resume_text):

    text = resume_text.lower()

    found_skills = []
    missing_skills = []

    for skill in SKILLS:
        if skill.lower() in text:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    total_skills = len(SKILLS)

    score = round(
        (len(found_skills) / total_skills) * 100
    )

    return {
        "skills": found_skills,
        "missing_skills": missing_skills,
        "score": score
    }


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI Resume Analyser Backend is running"
    }), 200


# ==========================================
# REGISTER ROUTE
# ==========================================

@app.route("/register", methods=["POST"])
def register():

    try:
        data = request.get_json(silent=True) or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "message": "Username and password are required"
            }), 400

        result = register_user(username, password)

        if result is False:
            return jsonify({
                "message": "Username already exists"
            }), 409

        return jsonify({
            "message": "Registration successful"
        }), 201

    except Exception as e:
        print("Registration error:", str(e))

        return jsonify({
            "message": "Registration failed"
        }), 500


# ==========================================
# LOGIN ROUTE
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json(silent=True) or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "message": "Username and password are required"
            }), 400

        if verify_user(username, password):

            session["username"] = username

            return jsonify({
                "message": "Login successful",
                "username": username,
                "token": "login-success"
            }), 200

        return jsonify({
            "message": "Invalid username or password"
        }), 401

    except Exception as e:
        print("Login error:", str(e))

        return jsonify({
            "message": "Login failed"
        }), 500


# ==========================================
# CHECK SESSION ROUTE
# ==========================================

@app.route("/check-session", methods=["GET"])
def check_session():

    username = session.get("username")

    if username:
        return jsonify({
            "logged_in": True,
            "username": username
        }), 200

    return jsonify({
        "logged_in": False
    }), 200


# ==========================================
# UPLOAD RESUME ROUTE
# ==========================================

@app.route("/upload", methods=["POST"])
def upload():

    try:
        if "resume" in request.files:
            file = request.files["resume"]
        elif "file" in request.files:
            file = request.files["file"]
        else:
            return jsonify({
                "message": "No resume file uploaded"
            }), 400

        if file.filename == "":
            return jsonify({
                "message": "Please select a PDF file"
            }), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({
                "message": "Only PDF files are supported"
            }), 400

        pdf_data = file.read()

        document = fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )

        resume_text = ""

        for page in document:
            resume_text += page.get_text()

        document.close()

        if not resume_text.strip():
            return jsonify({
                "message": "Could not extract text from this PDF"
            }), 400

        analysis = analyze_resume(resume_text)

        return jsonify({
            "message": "Resume analysed successfully",
            "resume_text": resume_text,
            "skills": analysis["skills"],
            "missing_skills": analysis["missing_skills"],
            "score": analysis["score"]
        }), 200

    except Exception as e:
        print("Resume upload error:", str(e))

        return jsonify({
            "message": "Resume analysis failed"
        }), 500


# ==========================================
# LOGOUT ROUTE
# ==========================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
