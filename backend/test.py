from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "AI Resume Analyser Backend is Running!"

@app.route("/test")
def test():
    return jsonify({
        "message": "Flask backend is working successfully!"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)