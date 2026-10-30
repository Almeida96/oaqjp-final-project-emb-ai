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

## Data flow

The browser sends text to Flask, which forwards it to the configured IBM lab endpoint with a 15-second timeout. There is no local database or analytics. Provider handling is governed by the lab service, not this project. Do not submit private text without understanding that external processing.

## Development

```sh
python -m unittest -v test_emotion_detection test_server
python -m pip install "pylint>=3.3,<4"
python -m pylint server.py
```

Tests cover the five labels, HTTP failures, malformed and nonfinite scores, input limits, POST/GET compatibility and browser-template rendering. Existing course evidence remains in `evidence/`; those captures describe their original test context.

[Contribution guide](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Apache 2.0 license](LICENSE)
