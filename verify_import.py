"""Verify the published detector can be imported and tested without network access.

The Watson HTTP response is explicitly MOCKED; this is a unit/smoke test,
not proof that the remote course service is reachable.
"""

import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

from EmotionDetection.emotion_detection import emotion_detector


def main():
    """Check module import, empty input and a deterministic mocked response."""
    file_path = Path(__file__).resolve().parent / "EmotionDetection" / "emotion_detection.py"
    content = file_path.read_bytes()
    git_blob = b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    blob_sha = hashlib.sha1(git_blob).hexdigest()

    print("Module: EmotionDetection.emotion_detection")
    print(f"GitHub-compatible file blob SHA-1: {blob_sha}")
    assert callable(emotion_detector)
    print("PASS: Module imported; emotion_detector is callable")

    result_empty = emotion_detector("  ")
    assert result_empty["dominant_emotion"] is None
    assert all(value is None for value in result_empty.values())
    print("PASS: Empty text handled without external request")

    sample_data = {
        "emotionPredictions": [{"emotion": {
            "anger": 0.01, "disgust": 0.02, "fear": 0.03,
            "joy": 0.90, "sadness": 0.04,
        }}]
    }
    with patch("EmotionDetection.emotion_detection.requests.post") as mocked_post:
        mocked_post.return_value = Mock(status_code=200)
        mocked_post.return_value.json.return_value = sample_data
        result = emotion_detector("I am glad this happened")
        assert result["dominant_emotion"] == "joy"
        assert result["joy"] == 0.90
        assert set(result) == {
            "anger", "disgust", "fear", "joy", "sadness", "dominant_emotion"
        }
        assert mocked_post.call_count == 1
        args, kwargs = mocked_post.call_args
        assert args[0].endswith("/NlpService/EmotionPredict")
        assert kwargs["json"] == {
            "raw_document": {"text": "I am glad this happened"}
        }
        assert kwargs["headers"]["grpc-metadata-mm-model-id"] == (
            "emotion_aggregated-workflow_lang_en_stock"
        )
    print("PASS: Watson request payload and model header verified (mock)")
    print("PASS: Mocked Watson response parsed; dominant_emotion=joy; joy=0.90")
    print("RESULT: ALL LOCAL CHECKS PASSED")
    print("IMPORTANT: The Watson service was MOCKED; live HTTP not verified")


if __name__ == "__main__":
    main()
