
from flask import Flask, request, jsonify
import os

from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import fitz

from database import create_table, register_user, verify_user


# =====================================
# FLASK APPLICATION
# =====================================

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is missing")

app.secret_key = SECRET_KEY

serializer = URLSafeTimedSerializer(SECRET_KEY)


# =====================================
# CORS CONFIGURATION
# =====================================

FRONTEND_URL = "https://ai-resume-analyser-1-nmjl.onrender.com"

CORS(
    app,
    resources={
        r"/*": {
            "origins": [FRONTEND_URL]
        }
    },
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
    methods=[
        "GET",
        "POST",
        "OPTIONS"
    ],
    supports_credentials=False
)


# =====================================
# DATABASE
# =====================================

create_table()


# =====================================
# TOKEN VERIFICATION
# =====================================

def get_logged_in_user():

    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]

    try:

        username = serializer.loads(
            token,
            salt="login-token",
            max_age=86400
        )

        return username

    except (BadSignature, SignatureExpired):
        return None


# =====================================
# RESUME ANALYSIS
# =====================================

def analyze_resume(text):

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Machine Learning",
        "Data Science",
        "Flask"
    ]

    found_skills = []

    for skill in skills:

        if skill.lower() in text.lower():
            found_skills.append(skill)

    missing_skills = [
        skill for skill in skills
        if skill not in found_skills
    ]

    score = int(
        (len(found_skills) / len(skills)) * 100
    )

    return {
        "skills": found_skills,
        "missing_skills": missing_skills,
        "score": score
    }


# =====================================
# HOME ROUTE
# =====================================

@app.route("/", methods=["GET"])
def home():

    return "AI Resume Analyser Backend is Running!"


# =====================================
# USER REGISTRATION
# =====================================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:

        return jsonify({
            "error": "Username and password are required"
        }), 400

    if len(password) < 8:

        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if register_user(username, password):

        return jsonify({
            "message": "Registration successful!"
        }), 200

    return jsonify({
        "error": "Username already exists"
    }), 409


# =====================================
# USER LOGIN
# =====================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:

        return jsonify({
            "error": "Username and password are required"
        }), 400

    if verify_user(username, password):

        token = serializer.dumps(
            username,
            salt="login-token"
        )

        return jsonify({
            "message": "Login successful!",
            "username": username,
            "token": token
        }), 200

    return jsonify({
        "error": "Invalid username or password"
    }), 401


# =====================================
# CHECK LOGIN
# =====================================

@app.route("/check-session", methods=["GET"])
def check_session():

    username = get_logged_in_user()

    if username:

        return jsonify({
            "logged_in": True,
            "username": username
        }), 200

    return jsonify({
        "logged_in": False
    }), 401


# =====================================
# RESUME UPLOAD
# =====================================

@app.route("/upload", methods=["POST"])
def upload_resume():

    username = get_logged_in_user()

    if not username:

        return jsonify({
            "error": "Please log in first!"
        }), 401

    if "resume" not in request.files:

        return jsonify({
            "error": "No resume uploaded"
        }), 400

    file = request.files["resume"]

    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Please upload a PDF file"
        }), 400

    try:

        pdf = fitz.open(
            stream=file.read(),
            filetype="pdf"
        )

        resume_text = ""

        for page in pdf:
            resume_text += page.get_text()

        pdf.close()

        analysis = analyze_resume(resume_text)

        return jsonify({
            "message": "Resume analysed successfully",
            "username": username,
            "resume_text": resume_text,
            "skills": analysis["skills"],
            "missing_skills": analysis["missing_skills"],
            "score": analysis["score"]
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# =====================================
# USER LOGOUT
# =====================================

@app.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "message": "Logged out successfully!"
    }), 200


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
