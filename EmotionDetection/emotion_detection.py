"""Emotion classification via the IBM Skills Network Watson NLP service.

The public course endpoint is intended for the educational lab. If it is no
longer available, the application raises a service error; it does not invent
emotion scores or silently switch to a different model.
"""

import math
import os
from urllib.parse import urlsplit

import requests

SERVICE_URL = (
    "https://sn-watson-emotion.labs.skills.network/"
    "v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
SERVICE_HEADERS = {
    "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
}
MAX_TEXT_LENGTH = 10_000
EMOTION_NAMES = ("anger", "disgust", "fear", "joy", "sadness")


def provider_configuration():
    """Allow an operator-owned Watson-compatible endpoint without changing code."""
    url = os.environ.get("EMOTION_SERVICE_URL", SERVICE_URL).strip()
    parsed = urlsplit(url)
    local_http = parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1", "::1")
    if (not parsed.hostname or parsed.username or parsed.password or parsed.fragment
            or not (parsed.scheme == "https" or local_http)):
        raise ValueError("Emotion service URL must use HTTPS or loopback HTTP without credentials")
    model = os.environ.get("EMOTION_MODEL_ID", SERVICE_HEADERS["grpc-metadata-mm-model-id"])
    if not model or len(model) > 200 or any(ord(char) < 32 for char in model):
        raise ValueError("Invalid emotion model identifier")
    return url, {"grpc-metadata-mm-model-id": model}


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

    if len(text_to_analyze) > MAX_TEXT_LENGTH:
        raise ValueError("Text exceeds 10,000 characters")

    payload = {"raw_document": {"text": text_to_analyze.strip()}}
    service_url, headers = provider_configuration()
    response = requests.post(
        service_url,
        json=payload,
        headers=headers,
        timeout=15,
    )

    if response.status_code == 400:
        return empty_emotion_result()

    response.raise_for_status()
    try:
        emotions = response.json()["emotionPredictions"][0]["emotion"]
        if any(isinstance(emotions[name], bool) for name in EMOTION_NAMES):
            raise ValueError("Boolean scores are invalid")
        scores = {name: float(emotions[name]) for name in EMOTION_NAMES}
        if any(not math.isfinite(score) or not 0 <= score <= 1 for score in scores.values()):
            raise ValueError("Scores must be finite probabilities")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ValueError("Unexpected response from the Watson NLP service") from error

    dominant_emotion = max(scores, key=scores.get)
    return {**scores, "dominant_emotion": dominant_emotion}
