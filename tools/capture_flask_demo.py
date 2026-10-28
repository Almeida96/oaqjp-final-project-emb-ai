"""Capture a real Flask browser screenshot with an explicitly mocked Watson reply.

The generated image is evidence of a working Flask UI, not proof that the IBM
Watson NLP service is available. The browser prominently labels TEST MODE.
"""

from pathlib import Path
from threading import Thread
from unittest.mock import patch
import shutil

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from server import app


def main():
    """Start the Flask app, submit text in Chromium, and save the screenshot."""
    app.config.update(DEMO_MODE=True, TESTING=True)
    fake_result = {
        "anger": 0.01,
        "disgust": 0.02,
        "fear": 0.03,
        "joy": 0.9,
        "sadness": 0.04,
        "dominant_emotion": "joy",
    }
    server = make_server("127.0.0.1", 0, app)
    flask_thread = Thread(target=server.serve_forever, daemon=True)
    output_file = Path("evidence/6b_deployment_test.png")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with patch("server.emotion_detector", return_value=fake_result):
            flask_thread.start()
            with sync_playwright() as playwright:
                chrome_available = (
                    shutil.which("google-chrome")
                    or shutil.which("google-chrome-stable")
                )
                if chrome_available:
                    browser = playwright.chromium.launch(
                        channel="chrome", headless=True, args=["--no-sandbox"]
                    )
                else:
                    browser = playwright.chromium.launch(
                        headless=True, args=["--no-sandbox"]
                    )

                try:
                    page = browser.new_page(
                        viewport={"width": 1320, "height": 940},
                        device_scale_factor=1,
                    )
                    page.goto(
                        "http://127.0.0.1:" + str(server.server_port),
                        wait_until="networkidle",
                    )
                    page.locator("#textToAnalyze").fill(
                        "I am very happy to learn Python!"
                    )
                    page.get_by_role("button", name="Analyze emotion").click()
                    page.locator("#system_response").get_by_text(
                        "The dominant emotion is joy", exact=False
                    ).wait_for(timeout=10000)
                    page.get_by_text(
                        "TEST MODE", exact=False
                    ).wait_for(timeout=10000)
                    result = page.locator("#system_response").inner_text()
                    assert "The dominant emotion is joy" in result
                    page.screenshot(path=str(output_file), full_page=True)
                    print("PASS: Flask served HTML, CSS, and browser JavaScript")
                    print("PASS: Form submitted text to /emotionDetector")
                    print("PASS: Emotion result rendered in real Chromium browser")
                    print("MODE: Watson HTTP response MOCKED; not a live call")
                    print("SCREENSHOT: " + str(output_file))
                finally:
                    browser.close()
    finally:
        server.shutdown()
        flask_thread.join(timeout=5)


if __name__ == "__main__":
    main()
