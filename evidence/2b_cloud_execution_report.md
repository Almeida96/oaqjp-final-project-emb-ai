# Task 2, Activity 2 — Cloud execution evidence

Repository: https://github.com/Almeida96/oaqjp-final-project-emb-ai

GitHub Actions run: https://github.com/Almeida96/oaqjp-final-project-emb-ai/actions/runs/40709281407

Test run date: 2026-10-28 UTC. The logs below summarize a real GitHub Actions
execution on ubuntu-latest with Python 3.12.15. They are not generated or
substituted results from the Watson service.

## Job A — Offline import and mocked Watson verification: PASSED

Steps completed successfully:
- Install requests
- Verify Python syntax
- Run python verify_import.py

Selected actual log output:

```text
PASS: Module imported; emotion_detector is callable
PASS: Empty text handled without external request
PASS: Watson request payload and model header verified (mock)
PASS: Mocked Watson response parsed; dominant_emotion=joy; joy=0.90
RESULT: ALL LOCAL CHECKS PASSED
IMPORTANT: The Watson service was MOCKED; live HTTP not verified
```

## Job B — Real Watson NLP endpoint: FAILED

Actual final log line:

```text
LIVE SERVICE UNAVAILABLE: ConnectTimeout: HTTPSConnectionPool(host='sn-watson-emotion.labs.skills.network', port=443): Max retries exceeded with url: /v1/watson.runtime.nlp.v1/NlpService/EmotionPredict (Caused by ConnectTimeoutError(... 'Connection to sn-watson-emotion.labs.skills.network timed out. (connect timeout=15)'))
```

## Assessment note

This report verifies importability and local logic on a GitHub-hosted runner,
without using the user's computer. It does NOT constitute successful live
integration with IBM Watson NLP. The course may require a successful call from
the Skills Network lab or restoration of the remote endpoint.
