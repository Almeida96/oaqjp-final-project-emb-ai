"""Flask web application for the IBM Watson NLP emotion detector."""

import os

import requests
from flask import Flask, render_template, request

from EmotionDetection import emotion_detector

app = Flask(__name__)


@app.get("/")
def home_page():
    """Render the application's text analysis form."""
    return render_template(
        "index.html",
        demo_mode=app.config.get("DEMO_MODE", False),
    )


@app.get("/emotionDetector")
def detect_emotions():
    """Process user text and return formatted emotion analysis."""
    text_to_analyze = request.args.get("textToAnalyze", "").strip()
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
    app.run(host="0.0.0.0", port=port)
