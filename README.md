# Emotion detection service

A Flask interface to the IBM Skills Network Watson NLP emotion endpoint. This is a fork of the IBM course project, with additional input validation, HTTP error handling and offline integration tests.

## Run

Requires Python 3.11+.

```sh
python -m venv .venv
# Activate the environment for your shell.
python -m pip install -r requirements.txt
python server.py
```

Open [localhost:5000](http://127.0.0.1:5000). The server binds to loopback; set `HOST` and `PORT` explicitly to change it.

The Watson endpoint belongs to the educational lab. Its availability and access policy are outside this repository's control. Service failures return HTTP 503; the app does not replace missing predictions with invented scores. The checked-in tests use mocked HTTP responses and do not establish that the live service is available.

## API

```sh
curl -X POST http://127.0.0.1:5000/emotionDetector \
  -H "Content-Type: application/json" \
  -d '{"textToAnalyze":"I am glad this happened"}'
```

The response lists anger, disgust, fear, joy and sadness scores and their dominant label. Each accepted score must be finite and between 0 and 1. A label is a model classification of the supplied text, not an assessment of a person's mental state.

| Status | Meaning |
| --- | --- |
| 200 | Valid provider prediction |
| 400 | Empty, invalid or oversized text |
| 413 | Request body exceeds 64 KiB |
| 503 | Provider timeout, HTTP failure or invalid prediction |

Text is limited to 10,000 characters. The browser sends JSON with POST so submitted text is not placed in the URL. The older GET route remains for course compatibility; avoid GET for private text because URLs can appear in logs and browser history.

## JSON integration and provider configuration

`POST /api/emotions` accepts the same JSON input and returns the five scores and `dominant_emotion` as a JSON object. Validation and service errors use an `error` field with HTTP 400 or 503. Input text is not echoed into the response. This route is suitable for scripts and agent tools; it does not require scraping the browser's prose output.

The default remains the IBM course endpoint. To use a Watson-compatible service you operate, set `EMOTION_SERVICE_URL` and, if needed, `EMOTION_MODEL_ID` before starting the process. The endpoint must accept `{"raw_document":{"text":"..."}}` and return `emotionPredictions[0].emotion` with all five score fields. HTTPS is required except for a local loopback service. URLs containing credentials are rejected. This is a protocol adapter, not a bundled local model or a general adapter for unrelated NLP APIs.

## Data flow

The browser sends text to Flask, which forwards it to the configured service with a 15-second timeout. There is no local database or analytics. The default provider is the IBM lab; its data handling is outside this project's control. Review the selected provider's policy before sending private text.

## Development

```sh
python -m unittest -v test_emotion_detection test_server
python -m pip install "pylint>=3.3,<4"
python -m pylint server.py
```

Tests cover the five labels, HTTP failures, malformed and nonfinite scores, input limits, POST/GET compatibility and browser-template rendering. Existing course evidence remains in `evidence/`; those captures describe their original test context.

Push checks run the reproducible offline tests. To check the actual IBM endpoint, manually run **Emotion detector - cloud verification** or **Task 4 - Package import and live Watson check** in GitHub Actions. Their live jobs run only on `workflow_dispatch` and fail if the external endpoint is unavailable or returns invalid predictions. A successful push check therefore does not establish provider availability.

Screenshot workflows upload their captures as run artifacts. They have read-only repository permissions and do not create commits or update checked-in evidence.

[Contribution guide](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Apache 2.0 license](LICENSE)
