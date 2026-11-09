
from flask import Flask, request, jsonify, session
import os
from flask_cors import CORS
import fitz
from database import create_table, register_user, verify_user
app = Flask(__name__)
CORS(app)
create_table()
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is missing")

frontend_url = os.environ.get(
    "FRONTEND_URL",
    "http://127.0.0.1:5500"
)

CORS(
    app,
    supports_credentials=True,
    origins=[frontend_url]
)


# def analyze_resume(text):
#     skills = [
#         "Python", "Java", "C", "C++",
#         "SQL", "HTML", "CSS", "JavaScript",
#         "React", "Machine Learning",
#         "Data Science", "Flask"
#     ]
def analyze_resume(text):

    skills = [
        "Python", "Java", "C", "C++", "SQL",
        "HTML", "CSS", "JavaScript", "React",
        "Machine Learning", "Data Science", "Flask"
    ]

    found_skills = []

    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    missing_skills = []

    for skill in skills:
        if skill not in found_skills:
            missing_skills.append(skill)

    score = int((len(found_skills) / len(skills)) * 100)

    return {
        "skills": found_skills,
        "missing_skills": missing_skills,
        "score": score
    }

  

@app.route("/")
def home():
    return "AI Resume Analyser Backend is Running!"

@app.route("/upload", methods=["POST"])
def upload_resume():
  
    if "username" not in session:
        return jsonify({
            "error": "Please log in first!"
        }), 401

    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    file = request.files["resume"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file"}), 400

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
        "resume_text": resume_text,
        "skills": analysis["skills"],
        "missing_skills": analysis["missing_skills"],
        "score": analysis["score"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if register_user(username, password):
        return jsonify({"message": "Registration successful!"})

    return jsonify({"error": "Username already exists"}), 409



@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if verify_user(username, password):
        session["username"] = username

        return jsonify({
            "message": "Login successful!",
            "username": username
        })

    return jsonify({"error": "Invalid username or password"}), 401
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logged out successfully!"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )


