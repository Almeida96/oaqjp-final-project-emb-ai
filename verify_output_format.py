"""Demonstrate the required output format using a clearly mocked Watson reply.

This verifies formatting only, not connectivity to the IBM Watson service.
"""

from unittest.mock import Mock, patch

from EmotionDetection.emotion_detection import emotion_detector


def main():
    """Print and assert the response format expected by the course."""
    simulated_watson_response = {
        "emotionPredictions": [
            {
                "emotion": {
                    "anger": 0.01,
                    "disgust": 0.02,
                    "fear": 0.03,
                    "joy": 0.90,
                    "sadness": 0.04,
                }
            }
        ]
    }
    with patch("EmotionDetection.emotion_detection.requests.post") as request:
        request.return_value = Mock(status_code=200)
        request.return_value.json.return_value = simulated_watson_response
        result = emotion_detector("I am glad this happened")
        assert request.call_count == 1

    expected_keys = {
        "anger", "disgust", "fear", "joy", "sadness", "dominant_emotion"
    }
    assert set(result) == expected_keys
    assert result["dominant_emotion"] == "joy"
    assert result["joy"] == 0.9
    print("MODE: MOCKED WATSON RESPONSE (not a live API call)")
    print("emotion_detector('I am glad this happened'):")
    print(result)
    print("PASS: Output contains five emotion scores plus dominant_emotion")


if __name__ == "__main__":
    main()
