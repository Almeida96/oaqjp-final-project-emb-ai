"""Flask web application for the IBM Watson NLP emotion detector."""

import os

import requests
from flask import Flask, render_template, request

from EmotionDetection import emotion_detector
from EmotionDetection.emotion_detection import MAX_TEXT_LENGTH

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


@app.get("/")
def home_page():
    """Render the application's text analysis form."""
    return render_template(
        "index.html",
        demo_mode=app.config.get("DEMO_MODE", False),
    )


@app.route("/emotionDetector", methods=["GET", "POST"])
def detect_emotions():
    """Process user text and return formatted emotion analysis."""
    payload = request.get_json(silent=True) if request.method == "POST" else request.args
    text_to_analyze = payload.get("textToAnalyze", "") if hasattr(payload, "get") else ""
    if not isinstance(text_to_analyze, str) or len(text_to_analyze) > MAX_TEXT_LENGTH:
        return "Text must contain at most 10,000 characters.", 400
    text_to_analyze = text_to_analyze.strip()
    if not text_to_analyze:
        return "Invalid text! Please try again!", 400

    try:
        result = emotion_detector(text_to_analyze)
    except (requests.RequestException, ValueError) as error:
        app.logger.warning("Watson NLP could not analyze the text: %s", error)
        return "Emotion service unavailable. Please try again later.", 503

    if result["dominant_emotion"] is None:
        return "Invalid text! Please try again!", 400

    message = (
        "For the given statement, the system response is "
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']} and "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )
    return message, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=port)
