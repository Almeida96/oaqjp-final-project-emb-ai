"""Task 4, Activity 2: verify package import and response format with a mock.

This script simulates the Watson service explicitly. It cannot be used as
evidence that the remote IBM NLP endpoint successfully processed the text.
"""

from unittest.mock import Mock, patch

from EmotionDetection.emotion_detection import emotion_detector


def main():
    """Test anger classification with an explicitly simulated Watson response."""
    simulated_response = {
        "emotionPredictions": [
            {
                "emotion": {
                    "anger": 0.91,
                    "disgust": 0.02,
                    "fear": 0.03,
                    "joy": 0.01,
                    "sadness": 0.03,
                }
            }
        ]
    }
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_response.json.return_value = simulated_response

    print("MODE: MOCKED Watson NLP HTTP response, not live service")
    with patch(
        "EmotionDetection.emotion_detection.requests.post",
        return_value=mocked_response,
    ) as post:
        result = emotion_detector("I am very angry")
    assert post.call_count == 1
    assert post.call_args.kwargs["json"] == {
        "raw_document": {"text": "I am very angry"}
    }
    assert list(result) == [
        "anger", "disgust", "fear", "joy", "sadness", "dominant_emotion"
    ]
    assert result["dominant_emotion"] == "anger"
    print("emotion_detector('I am very angry'):")
    print(result)
    print("PASS: Package import and anger output format")
    print("LIMITATION: Watson response was simulated; live service not verified")


if __name__ == "__main__":
    main()
