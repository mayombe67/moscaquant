# MQ-8.7 — Canonical Achievement Occurrence Ledger

## Historical replay bootstrap

The original MQ-8 historical achievement projection contained eleven
`HISTORICAL_REPLAY` achievements but did not persist the corresponding
`AchievementOccurrence` records.

MQ-8.7 corrects that architecture by materializing explicit replay
occurrences for the eleven frozen `HISTORICAL_REPLAY_ELIGIBLE` definitions.

The ledger is:

`achievements/occurrences_v1.jsonl`

Each replay occurrence has:

- a deterministic occurrence ID;
- a deterministic replay source-event ID;
- origin `HISTORICAL_REPLAY`;
- source-event type `HISTORICAL_EVIDENCE_REPLAY`;
- stack index `1`;
- the definition's frozen evidence references;
- an explicit replay marker;
- a deterministic SHA-256 state hash;
- a previous-occurrence hash forming a deterministic chain.

## Timestamp semantics

Historical replay occurrences use:

`2026-09-18T00:00:00Z`

This preserves the date already exposed by the accepted MQ-8 historical
projection.

It is the canonical replay materialization timestamp.

It must **not** be interpreted as the original wall-clock time of the
underlying scientific experiment.

## Authority

After materialization, the occurrence JSONL is the authoritative occurrence
history for these replay records.

`public_data/achievement_longitudinal_v1.json` is derived from that ledger and
is disposable/reproducible presentation data.

## Export

Run:

```bash
PYTHONPATH=. python3 scripts/export_achievement_longitudinal_v1.py
```

The exporter writes identical projections to:

- `public_data/achievement_longitudinal_v1.json`
- `neuroscope/web/public_data/achievement_longitudinal_v1.json`

## Acceptance

Run:

```bash
PYTHONPATH=. python3 -m pytest -q \
  tests/test_achievement_historical_replay_v1.py \
  tests/test_achievement_longitudinal_v1.py \
  tests/test_achievements.py

PYTHONPATH=. python3 scripts/export_achievement_longitudinal_v1.py

cmp \
  public_data/achievement_longitudinal_v1.json \
  neuroscope/web/public_data/achievement_longitudinal_v1.json

git diff --check
```
