"""Capture the actual Flask empty-text validation in a Chromium browser.

This test exercises a real HTTP 400 response. There is no mock Watson result:
blank input must be rejected before the service is contacted.
"""

from pathlib import Path
from threading import Thread
from unittest.mock import patch
import shutil

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from server import app


def main():
    """Capture the app after submitting an empty text field."""
    app.config.update(TESTING=True, DEMO_MODE=False)
    web_server = make_server("127.0.0.1", 0, app)
    thread = Thread(target=web_server.serve_forever, daemon=True)
    image_file = Path("evidence/7c_error_handling_interface.png")
    image_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # The detector must never be called on empty input.
        with patch(
            "server.emotion_detector",
            side_effect=AssertionError("Unexpected Watson call on empty input"),
        ) as detector:
            thread.start()
            with sync_playwright() as playwright:
                chrome_executable = (
                    shutil.which("google-chrome")
                    or shutil.which("google-chrome-stable")
                )
                if chrome_executable:
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
                        f"http://127.0.0.1:{web_server.server_port}/",
                        wait_until="networkidle",
                    )
                    assert not page.get_by_text("TEST MODE", exact=False).count()
                    page.locator("#textToAnalyze").fill("")
                    with page.expect_response(
                        lambda response: "/emotionDetector" in response.url
                    ) as response_wait:
                        page.get_by_role(
                            "button", name="Analyze emotion"
                        ).click()

                    response = response_wait.value
                    assert response.status == 400, (
                        f"Expected HTTP 400, received {response.status}"
                    )
                    page.wait_for_function(
                        "document.getElementById('system_response').textContent"
                        ".includes('Invalid text! Please try again!')",
                        timeout=10000,
                    )
                    assert "error" in (
                        page.locator("#responsePanel").get_attribute("class")
                        or ""
                    )
                    detector.assert_not_called()
                    page.screenshot(path=str(image_file), full_page=True)
                    print("PASS: Flask served real browser page")
                    print("PASS: Empty input submitted by Chromium")
                    print("PASS: Flask response HTTP 400")
                    print("PASS: UI displayed 'Invalid text! Please try again!'")
                    print("PASS: No call made to Watson NLP for empty input")
                    print("SCREENSHOT: " + str(image_file))
                finally:
                    browser.close()
    finally:
        web_server.shutdown()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
