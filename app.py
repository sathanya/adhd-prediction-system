from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys

# ----------------------------
# FLASK APP
# ----------------------------
app = Flask(__name__)
CORS(app)

# ----------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# ----------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scoring.inattention import calculate_inattention
from scoring.impulsivity import calculate_impulsivity
from scoring.hyperactivity import calculate_hyperactivity
from prediction.predict import predict_adhd

# ----------------------------
# FRONTEND ROUTES
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/result")
def result():
    return render_template("result.html")

# ----------------------------
# API ROUTE
# ----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)

    user = data.get("user", {})
    pilot = data.get("adaptive_pilot", {})
    reaction = data.get("flash_reaction", {})
    shield = data.get("steady_shield", {})

    inattention = calculate_inattention(pilot)
    impulsivity = calculate_impulsivity(reaction)
    hyperactivity = calculate_hyperactivity(shield)
    symptom_sum = inattention + impulsivity + hyperactivity

    features = {
        "Age": user.get("Age", 0),
        "Gender": user.get("Gender", "Male"),
        "EducationStage": user.get("EducationStage", "Teen"),
        "InattentionScore": inattention,
        "HyperactivityScore": hyperactivity,
        "ImpulsivityScore": impulsivity,
        "SymptomSum": symptom_sum,
        "Daydream": user.get("Daydream", 0),
        "SleepHours": user.get("SleepHours", 0),
        "ScreenTime": user.get("ScreenTime", 0),
        "FamilyHistory": user.get("FamilyHistory", 0)
    }

    prob, label = predict_adhd(features)

    return jsonify({
        "probability": round(prob * 100, 1),
        "label": int(label),
        "scores": {
            "inattention": inattention,
            "hyperactivity": hyperactivity,
            "impulsivity": impulsivity
        },
        "symptom_sum": symptom_sum,
        "result_text": (
            "ADHD Likely (High correlation with behavioral patterns)"
            if label == 1 else "No ADHD Likely"
        ),
        "disclaimer": "⚠️ This is an AI-based screening tool and NOT a clinical diagnosis."
    })

# ----------------------------
# RUN (LOCAL ONLY)
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
