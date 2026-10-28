"""Emotion classification via the IBM Skills Network Watson NLP service.

The public course endpoint is intended for the educational lab. If it is no
longer available, the application raises a service error; it does not invent
emotion scores or silently switch to a different model.
"""

import requests

SERVICE_URL = (
    "https://sn-watson-emotion.labs.skills.network/"
    "v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
SERVICE_HEADERS = {
    "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
}
EMOTION_NAMES = ("anger", "disgust", "fear", "joy", "sadness")


def empty_emotion_result():
    """Return the conventional structure for invalid or empty input."""
    result = {emotion: None for emotion in EMOTION_NAMES}
    result["dominant_emotion"] = None
    return result


def emotion_detector(text_to_analyze):
    """Analyze English text and return emotion scores plus dominant emotion.

    Raises:
        requests.RequestException: For service and network failures, except
            the expected HTTP 400 case for invalid input.
        ValueError: If the service responds with an unexpected data shape.
    """
    if not isinstance(text_to_analyze, str) or not text_to_analyze.strip():
        return empty_emotion_result()

    payload = {"raw_document": {"text": text_to_analyze.strip()}}
    response = requests.post(
        SERVICE_URL,
        json=payload,
        headers=SERVICE_HEADERS,
        timeout=15,
    )

    if response.status_code == 400:
        return empty_emotion_result()

    response.raise_for_status()
    try:
        emotions = response.json()["emotionPredictions"][0]["emotion"]
        scores = {name: float(emotions[name]) for name in EMOTION_NAMES}
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ValueError("Unexpected response from the Watson NLP service") from error

    dominant_emotion = max(scores, key=scores.get)
    return {**scores, "dominant_emotion": dominant_emotion}
