# Anomalous Observances / Blacksite Holidays v1

## Terminology

Formal framework:

**Anomalous Observances**

Public/lore label:

**BLACKSITE HOLIDAYS**

An individual activation may also be described as a:

**CONTAINMENT EVENT**

Future community voting may be presented as a:

**PANOPTICON REFERENDUM**

These names are presentation/lore terminology. They do not alter scientific interpretation.

## Secular-only canon

MoscaQuant observances are secular.

The observance calendar does not encode religious holidays, theology, saints, sacred
festivals or religious doctrine.

Historical dates may still be used when independently relevant to MoscaQuant, science,
project history, operators, or secular cultural presentation.

## Science-effect classes

Every observance declares exactly one science-effect class.

### `PRESENTATION_ONLY`

May change:

- visual presentation;
- original decorations;
- lighting;
- signage;
- meme rotation;
- achievements;
- public overlays.

Must not alter:

- experimental inputs;
- model state;
- thresholds;
- reward/punishment;
- Warden behavior;
- scientific outputs.

### `EXPLORATORY`

May expose MQ-001 to a temporary environment or interactive affordance.

Observations are recorded but are not baseline evidence unless a later frozen protocol
explicitly studies them.

`CELL-67.BIRTHDAY.v1` is the first canonical example.

### `EXPERIMENTAL`

May alter an experimental condition only when backed by a frozen protocol.

Activation requires a protocol reference.

Examples of future candidates include:

- LEFT EYE DAY;
- RIGHT EYE DAY;
- SUPER GENIUS DAY;
- an actual MQ-001 / MQ-002 courtship interaction experiment.

Their names can remain absurd. Their protocol cannot.

## Canonical calendar v1

### BLACKSITE HOLIDAY #001
**MORTY Launch Day / Birthday — October 30**

Class: `EXPLORATORY`

Environment: `CELL-67.BIRTHDAY.v1`

The tether is removed, room roaming is enabled and birthday props become physically
available.

### BLACKSITE HOLIDAY #002
**Elevated Anomaly Readiness — October 31**

Class: `PRESENTATION_ONLY`

Halloween-adjacent secular containment-site presentation.

### BLACKSITE HOLIDAY #003
**Inter-Subject Courtship Observance — February 14**

Class: `PRESENTATION_ONLY`

The observance may use ridiculous romantic presentation.

It does **not** authorize MORTY/LILITH interaction.

An actual MQ-001/MQ-002 social or courtship exposure requires a separate frozen experimental
protocol.

### BLACKSITE HOLIDAY #004
**Founder Day — June 20**

Class: `PRESENTATION_ONLY`

Secular celebration of the project founder/operator.

Permitted lore may include exaggerated Management propaganda.

Suggested status line:

`FOUNDER STATUS: SELF-ASCRIBED OMNIPOTENCE`

Scientific annotation:

`SCIENTIFIC STATUS: UNVERIFIED`

### BLACKSITE HOLIDAY #005
**Resource Extraction Observance**

Class: `PRESENTATION_ONLY`

Corporate procurement/productivity satire associated with Black Friday.

Version 1 contains a placeholder fixed date. A later calendar service may calculate the
actual annual date.

### BLACKSITE HOLIDAY #006
**Annual Containment Recertification — January 1**

Class: `PRESENTATION_ONLY`

Yearly summary of:

- experiments;
- achievements;
- lineage;
- containment status;
- receipts;
- public milestones.

### BLACKSITE HOLIDAY #007
**Information Integrity Incident — April 1**

Class: `PRESENTATION_ONLY`

Panopticon presentation may become intentionally absurd.

Raw telemetry, RECEIPTS and scientific artifacts remain unchanged and accessible.

## Observance manifest

Each observance records:

- stable observance ID;
- display name;
- calendar date;
- science-effect class;
- optional environment variant;
- community-vote eligibility;
- frozen-protocol requirement;
- replay eligibility;
- notes.

## Activation telemetry

### `observance.activated`

Records:

- observance manifest;
- activation date;
- frozen protocol reference when required;
- explicit scientific boundary.

### `observance.closed`

Records the end of the observance and restoration of normal presentation.

## Panopticon Referendum

Future community voting may choose between eligible presentation-only or pre-approved
observance variants.

Voting must never silently authorize a scientific perturbation.

Any option that changes experimental conditions must already point to a frozen protocol and
must remain subject to Warden/experiment-governance rules.

## Replay

Historical Panopticon playback should be capable of reconstructing which Blacksite Holiday was
active without modifying the underlying scientific record.

Comedy remains downstream of evidence.
