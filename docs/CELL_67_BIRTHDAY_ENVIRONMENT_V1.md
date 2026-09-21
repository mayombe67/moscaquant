# CELL-67 Birthday Environment v1

## Canonical environment

The normal MoscaQuant containment environment is:

`CELL-67.v1`

The launch-day birthday environment is:

`CELL-67.BIRTHDAY.v1`

The birthday environment is a temporary exploratory condition. It does not silently replace
the baseline environment.

## Design intent

CELL-67 remains a containment cell.

The birthday condition gives MQ-001 a one-day corporate-celebration environment with room
roaming, interactive props and deliberately uncomfortable employee-appreciation energy.

The visuals should be original and may evoke generic sterile corporate-dystopian office
culture, but should not copy protected third-party art, logos, layouts, sounds or trade dress.

## Birthday changes

For the birthday session:

- the normal tether is disabled;
- room roaming is enabled;
- normal room collision boundaries remain active;
- temporary birthday props are added;
- the condition is marked exploratory;
- the normal `CELL-67.v1` environment is restored afterward.

No frontend component may interpret `tether_enabled=false` as permission to change any other
experimental control.

## Interactive props

### Cake

Canonical prop:

`birthday.cake`

Properties:

- interactive;
- deliberately visually attractive/salient;
- non-consumable;
- attempts to consume it are recorded;
- denied consumption is an environmental outcome, not a scripted emotional response.

Display copy may identify it as:

`COMPLIMENTARY CELEBRATION RESOURCE`

with:

`Consumption privileges unavailable.`

The metadata also records the canonical fact that the cake is a lie.

If MQ-001 approaches, probes, contacts, circles or attempts to consume the cake, those
behaviors must come from the actual motor/environment interaction path.

### Party hat

Canonical prop:

`birthday.party_hat`

The hat is wearable only after an actual recorded interaction.

The renderer must not auto-equip the hat because it is birthday mode.

Valid sequence:

```text
motor state
    |
    v
physical/contact interaction with birthday.party_hat
    |
    v
environment.prop_interaction
    |
    v
environment.wearable_state(equipped=true)
    |
    v
Panopticon renders hat on MQ-001
```

The hat is temporary and is removed when the birthday environment ends.

If MQ-001 never interacts with it, he never wears it.

## Other birthday props

Version 1 includes:

- balloon cluster;
- corporate birthday banner;
- Management card;
- appreciation placard;
- birthday-mode secondary monitor.

Suggested original in-world copy includes:

- `YOUR CONTRIBUTION IS VALUED`
- `BIRTHDAY PRIVILEGE WINDOW ACTIVE`

These are presentation/environment details, not scientific labels.

## No scripted comedy

Birthday mode must not contain hard-coded story beats such as:

- force MQ-001 toward the cake;
- automatically equip the hat;
- trigger a reaction because a balloon exists;
- force a celebratory pose;
- make MQ-001 attack or avoid an object.

The environment supplies affordances.

The model supplies behavior.

The resulting behavior supplies the joke.

## Telemetry

### `environment.activated`

Records the complete environment identity and explicit activation reason.

### `environment.prop_interaction`

Records:

- environment;
- prop;
- interaction type;
- source motor event;
- distance where available;
- whether the interaction was allowed;
- denial reason where applicable.

### `environment.wearable_state`

Records wearable equip/remove state and requires a source interaction event for equipping.

### `environment.restored`

Records the return from the temporary birthday environment to normal CELL-67 and signals that
temporary wearables must be cleared.

## Scientific boundary

Birthday mode is exploratory by default.

Results from `CELL-67.BIRTHDAY.v1` must not be mixed into baseline inference unless a frozen
protocol explicitly includes that environment.

Interesting spontaneous behavior may motivate a future protocol, but must not retroactively
change the interpretation of the birthday session.

## Replay

A replay should be able to reconstruct:

- which CELL-67 environment was active;
- whether the tether was enabled;
- which props existed;
- what MQ-001 interacted with;
- whether the cake was approached or unsuccessfully consumed;
- whether the party hat was actually earned through interaction;
- when temporary wearables were removed;
- when normal containment was restored.

The public spectacle should therefore remain downstream of the recorded interaction history.
