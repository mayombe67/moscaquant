# OVERWATCH Behavioral & Experimental Telemetry v1

## Purpose

Runtime telemetry tells us whether the machine survived.

Behavioral telemetry records what MoscaQuant was exposed to, what internal variables changed,
what decision path was taken, what reinforcement occurred, and which checkpoint lineage
followed.

This layer is intended to support longitudinal experiments and Panopticon visualization
without converting presentation metaphors into scientific claims.

## Canonical event families

### `state.mood`

A compact normalized internal-state vector.

Version 1 contains:

- `hunger`
- `arousal`
- `courtship_drive`
- `threat`
- `fatigue`
- `reward`
- `punishment`
- `abnormal_state`
- `sugar_cube_state`

Every indicator uses the closed interval `[0.0, 1.0]`.

These values are operational/model state indicators. They are **not** evidence that MQ-001
experiences subjective human emotions.

Panopticon may map these values to an original expressive fly portrait or other visualization.

### `state.transition`

Records a named state variable before and after a transition, optionally linked to the event
that caused the change.

The causal link is a provenance relationship, not an automatic scientific causal claim.

### `decision.trace`

Records the chain:

```text
input reference
      |
encoded state reference
      |
Oracle proposal
      |
Warden disposition
      |
final output
```

This is the forensic decision record.

Oracle remains proposal/interpretation. Warden remains the authority boundary. OVERWATCH
records both without changing either.

### `reinforcement.applied`

Records:

- reinforcement method;
- normalized intensity;
- duration where applicable;
- trigger reason;
- target reference;
- observed operational outcome.

This event does not itself establish biological efficacy or learning causality. Those remain
experiment-specific claims.

### `lineage.checkpoint`

Records SAVE STATE ancestry:

- checkpoint;
- parent checkpoint;
- generation;
- fork reason;
- canonical codename where applicable;
- lineage status.

Lore concepts such as candidate, promotion, MADE status or other future Panopticon ranks must
remain explicitly downstream of evidence.

## Panopticon mood HUD

The persistent MORTY status portrait should consume `state.mood`.

The frontend may combine indicators into expressions, animation, posture and absurd visual
reactions, but the raw normalized indicators remain separately visible and inspectable.

Example presentation rules may eventually include:

- high threat -> alarmed/agitated portrait;
- high fatigue -> sluggish portrait;
- high reward -> positive/reinforced reaction;
- high punishment -> distressed reaction;
- high courtship drive/arousal -> courtship-mode visual cues;
- Sugar Cube state -> unmistakable abnormal/special-state treatment.

Those mappings belong to Panopticon presentation code, not the scientific telemetry contract.

## Event graph

The long-term evidence graph is:

```text
INPUT / MARKET
      |
      v
 INTERNAL STATE
      |
      v
    ORACLE
      |
      v
    WARDEN
      |
      v
 ACTION / OUTPUT
      |
      v
REINFORCEMENT
      |
      v
 NEXT STATE
```

Every major arrow should eventually emit or reference an OVERWATCH event.

## Longitudinal value

With these event families, future analysis can ask:

- when did a state trajectory change;
- what inputs preceded the change;
- which decisions and Warden dispositions occurred;
- which reinforcement events followed;
- which checkpoint lineage inherited the resulting state;
- whether the same pattern reproduces under a frozen protocol.

This is the foundation for studying how a particular MoscaQuant lineage changes over long
periods without relying on frontend storytelling.

## Public/private boundary

Panopticon receives sanitized projections.

Raw market payloads, licensed data, private infrastructure, brokerage/account identifiers,
credentials, private Warden operations and unpublished sensitive artifacts remain outside the
public projection.

The science repo owns the event contract. Panopticon owns the spectacle. Private ops owns the
secrets.
