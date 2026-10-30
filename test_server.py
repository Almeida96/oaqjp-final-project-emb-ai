"""Test the Flask routes without calling the unavailable Watson service."""

import unittest
from unittest.mock import patch

from requests.exceptions import ConnectTimeout

from server import app


class TestFlaskRoutes(unittest.TestCase):
    """Exercise the real Flask request handlers with mocked NLP results."""

    def setUp(self):
        app.config.update(TESTING=True, DEMO_MODE=False)
        self.client = app.test_client()

    def test_home_renders_input_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Emotion Detector", response.data)
        self.assertIn(b'textToAnalyze', response.data)
        self.assertNotIn(b"TEST MODE", response.data)

    def test_demo_banner_only_when_explicitly_enabled(self):
        with app.test_client() as client:
            app.config["DEMO_MODE"] = True
            response = client.get("/")
            self.assertIn(b"TEST MODE", response.data)
        app.config["DEMO_MODE"] = False

    def test_blank_text_is_rejected(self):
        response = self.client.get("/emotionDetector?textToAnalyze=")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid text!", response.data)

    @patch("server.emotion_detector")
    def test_valid_text_returns_formatted_emotions(self, mocked_detector):
        mocked_detector.return_value = {
            "anger": 0.01,
            "disgust": 0.02,
            "fear": 0.03,
            "joy": 0.9,
            "sadness": 0.04,
            "dominant_emotion": "joy",
        }
        response = self.client.get(
            "/emotionDetector",
            query_string={"textToAnalyze": "I am glad this happened"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The dominant emotion is joy", response.data)
        self.assertIn(b"'anger': 0.01", response.data)
        mocked_detector.assert_called_once_with("I am glad this happened")

    @patch("server.emotion_detector")
    def test_unavailable_watson_returns_http_503(self, mocked_detector):
        mocked_detector.side_effect = ConnectTimeout("IBM service unavailable")
        response = self.client.get(
            "/emotionDetector",
            query_string={"textToAnalyze": "I am glad this happened"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"Emotion service unavailable", response.data)

    @patch("server.emotion_detector")
    def test_invalid_emotion_result_returns_http_400(self, mocked_detector):
        mocked_detector.return_value = {"dominant_emotion": None}
        response = self.client.get(
            "/emotionDetector", query_string={"textToAnalyze": "nonsense"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("server.emotion_detector")
    def test_post_json_and_invalid_input(self, detector):
        detector.return_value = {
            "anger": 0, "disgust": 0, "fear": 0, "joy": 1, "sadness": 0,
            "dominant_emotion": "joy",
        }
        response = self.client.post("/emotionDetector", json={"textToAnalyze": "Example"})
        self.assertEqual(response.status_code, 200)
        detector.reset_mock()
        for payload in ([], {"textToAnalyze": 42}, {"textToAnalyze": "x" * 10001}):
            self.assertEqual(self.client.post("/emotionDetector", json=payload).status_code, 400)
        detector.assert_not_called()

    def test_request_body_limit(self):
        response = self.client.post("/emotionDetector", data="x" * 70000,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
