# Panopticon Beta and Launch Countdown v1

## Canonical date

Prospective public launch / MQ-001 birthday:

**October 30, 2026**

The public Panopticon site may enter beta before launch.

## Pre-launch behavior

During beta:

- the site is explicitly labeled beta;
- `CELL-67.v1` remains the active environment;
- a public countdown is visible;
- birthday privileges remain inactive;
- the countdown is presentation state only and must not alter scientific behavior.

Suggested in-world label:

`EMPLOYEE ACTIVATION WINDOW`

## Launch transition

At the canonical launch timestamp, Panopticon transitions from countdown mode to the launch
state and may activate `CELL-67.BIRTHDAY.v1`.

This transition should be explicit in OVERWATCH telemetry rather than inferred from frontend
time alone.

Relevant events:

- `launch.state`
- `launch.transition`
- `environment.activated`

## Birthday privilege window

During the birthday session:

- the beta label disappears;
- the countdown disappears;
- `CELL-67.BIRTHDAY.v1` becomes active;
- the normal tether is disabled;
- room roaming is enabled;
- temporary birthday props and wearables become available;
- exploratory-condition labeling remains intact.

Suggested in-world label:

`BIRTHDAY PRIVILEGE WINDOW ACTIVE`

## End of birthday session

When the birthday window closes:

- emit `launch.birthday_window_closed`;
- restore `CELL-67.v1`;
- re-enable standard containment constraints;
- clear temporary wearables such as the party hat;
- preserve the full birthday session in telemetry/replay.

## Replay

Historical replay should reconstruct the exact public state:

```text
beta countdown
    |
    v
launch transition
    |
    v
CELL-67.BIRTHDAY.v1
    |
    v
birthday interactions / wearables / roaming
    |
    v
birthday window closes
    |
    v
CELL-67.v1 restored
```

## Scientific boundary

Launch-day presentation and birthday privileges do not upgrade exploratory observations into
baseline scientific evidence.

Any future scientific use of birthday-condition behavior requires an explicit frozen protocol.
