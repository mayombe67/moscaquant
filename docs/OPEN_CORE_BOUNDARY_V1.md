# MoscaQuant Open-Core Boundary v1

## Principle

> **Open the evidence. Protect the experience.**

MoscaQuant should expose enough of the scientific system to let independent researchers:

- inspect what was claimed;
- reproduce published experiments where inputs/data rights allow;
- verify protocol and provenance;
- validate telemetry and RECEIPTS;
- build alternative tooling against stable public interfaces;
- criticize or extend the work without depending on the private product stack.

The public repository is not required to contain the complete Panopticon product,
production operations, commercial systems or proprietary presentation implementation.

## Public repository: `moscaquant`

The public repository should contain the scientific core and verification surface.

### Public by default

- scientific model interfaces;
- experiment protocols;
- frozen configs appropriate for publication;
- authoritative scientific execution contracts and runtime-parity criteria;
- content-addressed execution provenance required to substantiate published results;
- result summaries and provenance;
- tests required to validate public claims;
- OVERWATCH event schemas/contracts;
- public projection rules;
- RECEIPTS and integrity verification;
- motor telemetry contracts;
- constraint/contact/physics telemetry contracts;
- environment/interface schemas needed to interpret published results;
- public-safe replay formats;
- public API/interface contracts;
- minimal/reference visualization examples where useful for reproducibility;
- methodology documentation;
- published sidequest/experiment retrospectives;
- stable lore identifiers where they are part of public interfaces.

### Public visualization reference implementation

The public repository may include a deliberately simple renderer or inspector that proves the
contracts work.

Examples:

- debug skeleton;
- simple pose viewer;
- telemetry timeline;
- minimal HUD;
- replay inspector.

It does not need to reproduce the production Panopticon experience.

## Private repositories / systems

Private systems may include:

- production Panopticon frontend/backend;
- high-fidelity CELL-67 implementation;
- proprietary 3D MORTY rig and art assets;
- production neural-to-rig mapping implementation where not required for a published claim;
- polished real-time rendering pipeline;
- classified modifier catalog;
- sponsorship backend;
- referendum anti-abuse / identity systems;
- achievement content library;
- meme-selection and second-monitor systems;
- Broadcast/social automation;
- production live-stream transport;
- commercial analytics;
- provider-specific cloud/deployment overlays, IaC state and operator tooling;
- production monitoring endpoints;
- broker/execution adapters;
- private Warden enforcement wiring;
- credentials, account mappings and secrets;
- private host inventories and endpoints;
- restricted/licensed/unpublished datasets;
- commercial product experiments not yet published.

## Scientific reproducibility boundary

A component must be public, described sufficiently, or replaced by an auditable equivalent
when it is necessary to substantiate a public scientific claim.

Private implementation is acceptable when the published claim depends only on a stable public
contract and the private layer does not alter the scientific result.

Example:

```text
PUBLIC
motor.state
constraint.state
physics.pose
        |
        v
stable renderer contract

PRIVATE
high-fidelity CELL-67 renderer
MORTY production rig
camera / lighting / art direction
commercial UX
```

If a future claim depends specifically on the proprietary neural-to-rig mapping, the relevant
mapping methodology must be published sufficiently for that claim to be evaluated.

## RASPUTIN public/private boundary

PROJECT RASPUTIN follows the same open-core rule as the rest of MoscaQuant.

Public science includes enough execution information to evaluate an
authoritative result:

- frozen scientific Git revision;
- scientific configuration and input identities;
- runtime-parity / acceptance contract;
- immutable execution-image digest where it substantiates the run;
- authoritative execution/result identifiers appropriate for publication;
- result and seal hashes;
- failure semantics relevant to scientific validity.

Private operations may retain:

- Terraform state and provider-specific deployment composition;
- credentials, account mappings and secret material;
- private host inventories;
- operator convenience tooling;
- internal monitoring details not needed to evaluate a public claim.

The private implementation may change **how much compute** is available. It may
not silently change the scientific question, inputs, stopping rule,
classification rule, or accepted result.

## Product boundary

The following are product features, not scientific requirements:

- polished CELL-67 scene;
- low-poly MORTY art direction;
- full modifier visual treatments;
- corporate-dystopian birthday presentation;
- sponsor presentation;
- hidden unlockable catalog;
- meme deck;
- achievement presentation;
- live audience UX;
- commercial engagement systems.

They may consume scientific telemetry.

They must not silently modify it.

## Lore boundary

Public lore names may remain in the scientific repository when they provide stable identifiers
or make the project understandable.

Examples:

- MORTY / MQ-001;
- LILITH / MQ-002;
- OVERWATCH;
- WARDEN;
- ORACLE;
- RECEIPTS;
- CELL-67;
- PANOPTICON.

The public repository does not need to expose every unreleased modifier, joke, art asset,
scripted presentation concept or future commercial event.

## Contribution routing

Before adding a new component, ask:

1. Is this required to reproduce or audit a scientific claim?
   - Yes -> public or sufficiently documented publicly.

2. Is this a stable interface needed by external researchers?
   - Yes -> public.

3. Is this operationally sensitive?
   - Yes -> private.

4. Is this primarily product experience, art, monetization or audience engagement?
   - Yes -> private unless a thin public contract is useful.

5. Would hiding this component make a published scientific result impossible to evaluate?
   - Yes -> the relevant methodology must not remain opaque.

## No secret science

The open-core boundary must never become an excuse for unverifiable claims.

MoscaQuant may protect product IP.

It must not protect the evidence needed to substantiate its published science.
