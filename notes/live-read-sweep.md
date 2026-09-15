# Live read-only endpoint sweep

Date: 2026-09-15
Android app: Clue 269.1
Host: `api.helloclue.com`

No response values were persisted. Only HTTP status, content type, and JSON
field structure were inspected.

## Live HTTP 200

- Account: initialize, authentication methods, current user, consents,
  notifications, tracking preferences, community profile.
- Tracking: measurements, calendar, current cycle, cycle history, cycle
  settings, cycle analysis, feelings analysis, pain analysis.
- Health analysis: BBT, body metrics, resting heart rate, delta temperature,
  heart-rate variability, skin temperature, sleep duration, and weight.
- Features: birth-control settings/spec, wearables and provider details,
  connections, medical-record options, doctor reports and user details,
  enrolled studies, chatbot history, paywall state, and data takeout.

## State-dependent

- Pregnancy, symptom-prediction, and cycle-analysis-diff endpoints require
  account state that is not represented in this public evidence log.

## APK-declared only

Shared-connection calendars, individual studies, and doctor-report downloads
require state-dependent identifiers and were not invoked. They are in the
contract with `x-clue-evidence.level: apk-only`.
