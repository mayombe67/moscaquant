# MQ-8.7 — Achievement Dossiers and Longitudinal Metrics

## Purpose

MQ-8.7 derives dossier and longitudinal views from immutable
`AchievementOccurrence` history.

Derived presentation state never replaces the occurrence record.

## Derived views

For each achievement with one or more occurrences, the v1 projection exposes:

- total occurrence count / stack count;
- first occurrence timestamp and date;
- latest occurrence timestamp and date;
- complete occurrence history;
- definition trigger version;
- observed trigger versions;
- evidence level;
- source-event linkage;
- experiment / session / generation metadata;
- supporting artifact references;
- deterministic longest UTC-calendar-day streak;
- co-occurring achievements reconstructed from shared `source_event_id`;
- achievement family and tags;
- public-safe provenance summaries.

Family summaries expose:

- member achievement IDs;
- achievement count;
- total occurrence count;
- evidence-level distribution.

## Authority boundary

The authoritative state remains the append-only `AchievementOccurrence` history.

The longitudinal projection is disposable and reproducible.

It must never:

- create an achievement occurrence;
- rewrite a trigger version;
- change scientific evidence;
- reinterpret historical occurrences;
- become a substitute for the underlying occurrence ledger.

## Determinism

Daily streaks use UTC calendar dates.

Co-occurrence is defined only by exact shared `source_event_id`.

All IDs and summary lists are sorted before projection where ordering would
otherwise depend on container traversal.

## Acceptance

Run:

```bash
PYTHONPATH=. python3 -m pytest -q tests/test_achievement_longitudinal_v1.py tests/test_achievements.py
```

Expected: all tests pass.
