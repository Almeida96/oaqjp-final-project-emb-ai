# Task 4 — Activity 2: Package validation

GitHub Actions run (October 28, 2026):
https://github.com/Almeida96/oaqjp-final-project-emb-ai/actions/runs/40723131503

## Import and mock-format test — PASSED

Actual GitHub Actions console output (timestamps omitted):

```text
$ python3 -c "from EmotionDetection.emotion_detection import emotion_detector; print('PASS: module import')"
PASS: module import
$ python3 -c "from EmotionDetection import emotion_detector; print('PASS: __init__.py export')"
PASS: __init__.py export
$ python3 verify_package.py
MODE: MOCKED Watson NLP HTTP response, not live service
emotion_detector('I am very angry'):
{'anger': 0.91, 'disgust': 0.02, 'fear': 0.03, 'joy': 0.01, 'sadness': 0.03, 'dominant_emotion': 'anger'}
PASS: Package import and anger output format
LIMITATION: Watson response was simulated; live service not verified
```

## Exact course command against Watson NLP — FAILED

GitHub Actions ran this command in a separate job:

```bash
python3 -c "from EmotionDetection.emotion_detection import emotion_detector; print(emotion_detector('I am very angry'))"
```

It returned a connection timeout:

```text
requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='sn-watson-emotion.labs.skills.network', port=443): Max retries exceeded with url: /v1/watson.runtime.nlp.v1/NlpService/EmotionPredict (Caused by ConnectTimeoutError(... 'Connection to sn-watson-emotion.labs.skills.network timed out. (connect timeout=15)'))
```

**Assessment status:** The package and output shape are verified, but this is
not a successful live Watson emotion classification. The grader may require
successful execution from the Skills Network lab after service recovery.
