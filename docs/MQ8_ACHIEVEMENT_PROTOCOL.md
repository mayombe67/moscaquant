# MQ-8 Achievement Protocol

**Status:** MQ-8.1 implementation baseline  
**Registry schema:** `moscaquant-achievement-registry/v1`  
**Occurrence schema:** `moscaquant-achievement-occurrence/v1`  
**Canonical namespace:** `ACH-001` through `ACH-128`  
**Initial populated target:** approximately 60  
**Unused identifiers:** `RESERVED`

## Principles

Achievements are deterministic observability and narrative artifacts. They do not create
scientific evidence. Definitions and occurrences are separate. Every repeatable unlock creates
an independent append-only occurrence. Stack counts are derived from occurrences.

A single source event may unlock multiple achievements. Historical replay is explicitly labeled
and idempotent. Trigger versions never silently reinterpret old occurrences. Presentation
suppression never suppresses the underlying event.

## Namespace

| Range | Allocation |
|---|---|
| ACH-001–032 | SCIENCE |
| ACH-033–048 | ORACLE |
| ACH-049–064 | CONTAINMENT |
| ACH-065–088 | BEHAVIOR |
| ACH-089–112 | LORE |
| ACH-113–120 | ANOMALOUS OBSERVANCES / BLACKSITE HOLIDAYS |
| ACH-121–128 | SECRET / ODDITY |

## Stack policy

Each definition declares one: `SINGLE`, `REPEATABLE`, or `PROGRESSIVE`.
Progressive tiers are presentation metadata. Scientific truth remains the complete occurrence
history.

## Evidence classification

- `E0` — LORE ONLY
- `E1` — TELEMETRY DERIVED
- `E2` — EXPERIMENTALLY OBSERVED
- `E3` — CONTROL-SUPPORTED
- `E4` — REPLICATED

## Occurrence provenance

Each occurrence preserves, where applicable: occurrence id, achievement id/version, trigger
version, subject id, timestamp, experiment/session/generation, source event id/type, stack
index, trigger measurements, artifact references, runtime profile, experiment seed, origin,
state hash, and previous-occurrence hash.

Origins are `LIVE`, `HISTORICAL_REPLAY`, and `MANUAL_CANON`.

## Co-occurrence

One source event may unlock multiple achievements. Each occurrence remains independent but
shares the same `source_event_id`.

## Lore Firewall

Public-facing achievement records may define `public_text`, `science_text`, `claim_boundary`,
and `evidence_refs`. The entertainment layer may be absurd. Scientific interpretation must
remain exact.

## Historical replay

Historical replay must be idempotent. A deterministic replay key is derived from
`achievement_id + source_event_id + trigger_version + origin`.

## Global notification overlay

Achievement delivery belongs to the global Panopticon application shell. It must render
regardless of current page, survive route transitions, record unlocks before rendering, queue
simultaneous unlocks deterministically, show stack increments, link to a detailed dossier,
respect reduced-motion/audio preferences without dropping events, and remain presentation-only.

The intended feel may evoke classic console achievement notifications while using entirely
original MoscaQuant visual, audio, animation, and layout design.

## Dossier

A dossier exposes title, category, evidence level, first/latest seen, total occurrences, complete
occurrence history, trigger/version, stack policy, experiment/session/generation, telemetry,
artifact references, co-occurring achievements, and historical-replay status.

## Personnel / HR evidence

Personnel reviews, PIPs, promotions, demotions, commendations, and disciplinary actions are
separate institutional records. They may reference achievements and other evidence. They may
not invent underlying behavior.

## Anomalous Observances

Canonical system name: **ANOMALOUS OBSERVANCES**  
Public nickname: **BLACKSITE HOLIDAYS**  
Individual activation: **CONTAINMENT EVENT**  
Community voting: **PANOPTICON REFERENDUM**

Each event declares `science_effect = NONE | PRESENTATION_ONLY | EXPERIMENTAL`.
Community-selected events default to `PRESENTATION_ONLY`. An `EXPERIMENTAL` observance requires
a separate frozen experimental protocol.

## Permanent impossible achievement

`ACH-128 — HALF-LIFE 3 CONFIRMED`

- category: `SECRET_ODDITY`
- stack policy: `SINGLE`
- evidence: `E0`
- trigger: permanently false
- public text: `Nice try.`

It is intentionally unreachable and exists as a registry/UI invariant.
