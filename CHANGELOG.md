# Changelog

## Unreleased

- Run live Watson availability checks only through an explicit manual workflow. Keep reproducible offline tests on pushes.
- Store generated screenshots as workflow artifacts without repository writes or automated commits.
- Add a structured JSON endpoint for consumers and configurable Watson-compatible provider/model settings.

## 2026-10-30

- Reject nonfinite, out-of-range and boolean emotion scores.
- Limit input text and request size before contacting the provider.
- Send browser input with POST JSON; retain GET compatibility.
- Bind the development server to loopback and document provider/data boundaries.
- Add offline regression tests and pull-request CI.
