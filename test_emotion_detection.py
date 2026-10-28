"""Unit tests for emotion detection using simulated Watson HTTP responses.

These tests verify the application's logic without contacting the IBM service.
They do not establish that the remote Watson endpoint is available.
"""

import unittest
from unittest.mock import Mock, patch

from requests.exceptions import ConnectTimeout, HTTPError

from EmotionDetection.emotion_detection import (
    EMOTION_NAMES,
    SERVICE_HEADERS,
    SERVICE_URL,
    emotion_detector,
)


class TestEmotionDetection(unittest.TestCase):
    """Verify the five emotions, response format, and error handling."""

    def assert_dominant_emotion(self, text, expected_emotion):
        """Supply a fake HTTP response and validate the processed result."""
        scores = {name: 0.01 for name in EMOTION_NAMES}
        scores[expected_emotion] = 0.96
        response = Mock(status_code=200)
        response.json.return_value = {
            "emotionPredictions": [{"emotion": scores}]
        }

        with patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=response,
        ) as post:
            result = emotion_detector(text)

        self.assertEqual(result["dominant_emotion"], expected_emotion)
        self.assertEqual(result[expected_emotion], 0.96)
        self.assertEqual(set(result), set(EMOTION_NAMES) | {"dominant_emotion"})
        post.assert_called_once_with(
            SERVICE_URL,
            json={"raw_document": {"text": text}},
            headers=SERVICE_HEADERS,
            timeout=15,
        )

    def test_joy(self):
        self.assert_dominant_emotion("I am glad this happened", "joy")

    def test_anger(self):
        self.assert_dominant_emotion("I am furious about this", "anger")

    def test_disgust(self):
        self.assert_dominant_emotion("I am disgusted by this", "disgust")

    def test_fear(self):
        self.assert_dominant_emotion("I am terrified of this", "fear")

    def test_sadness(self):
        self.assert_dominant_emotion("I am very sad", "sadness")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_blank_input(self, post):
        result = emotion_detector("  ")
        self.assertTrue(all(value is None for value in result.values()))
        post.assert_not_called()

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_invalid_input_type(self, post):
        result = emotion_detector(None)
        self.assertIsNone(result["dominant_emotion"])
        post.assert_not_called()

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_http_400(self, post):
        post.return_value.status_code = 400
        result = emotion_detector("Invalid text")
        self.assertTrue(all(value is None for value in result.values()))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_http_500_raises(self, post):
        post.return_value.status_code = 500
        post.return_value.raise_for_status.side_effect = HTTPError("500")
        with self.assertRaises(HTTPError):
            emotion_detector("Test request")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_connection_timeout_raises(self, post):
        post.side_effect = ConnectTimeout("Service unavailable")
        with self.assertRaises(ConnectTimeout):
            emotion_detector("Test request")

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_malformed_response_raises(self, post):
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"emotionPredictions": []}
        with self.assertRaises(ValueError):
            emotion_detector("Test request")


if __name__ == "__main__":
    unittest.main()
