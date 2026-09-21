# Containment Modifiers / Panopticon Referendum v1

## Core concept

Containment modifiers behave like unlockable videogame mutators in the Panopticon
presentation layer.

They are not a public settings menu.

The hidden catalog remains classified.

## Public states

Modifiers may conceptually occupy:

- `CLASSIFIED`
- `DISCLOSED`
- `UNLOCKED`
- `ACTIVE`
- `RETIRED`

### CLASSIFIED

Not publicly revealed.

The public API/UI must not expose:

- the complete catalog;
- the number of hidden modifiers;
- hidden names;
- hidden descriptions;
- hidden visual profiles.

### DISCLOSED

Exactly three candidates are revealed for a Panopticon Referendum.

### UNLOCKED

The winning modifier remains permanently visible in the public unlocked collection unless
explicitly retired for a technical, scientific, legal or safety reason.

The two losing candidates return to `CLASSIFIED`.

They may reappear in a future referendum.

### ACTIVE

An unlocked modifier is currently equipped/active.

### RETIRED

No longer eligible for activation.

Retirement should be explicit rather than silently deleting history.

## Referendum rule

Every referendum reveals exactly three candidates.

No more.

No hidden-catalog preview is supplied.

No public catalog count is supplied.

The intended experience is discovery/progression rather than configuration.

## Unlock flow

```text
CLASSIFIED CATALOG
        |
        | Management selects exactly 3
        v
PANOPTICON REFERENDUM
        |
        | community vote
        v
ONE WINNER
        |
        v
UNLOCKED PERMANENTLY

two losing candidates -> CLASSIFIED
```

Future referenda reveal three candidates again while previous winners remain visible in the
unlocked collection.

## Sponsorship

A referendum or activation may be sponsored by an individual or company.

Permitted sponsor influence may include:

- funding an event;
- sponsoring the complete referendum;
- nominating one candidate from the pre-approved catalog;
- at an approved tier, nominating the full three-candidate slate from the pre-approved
  catalog;
- sponsoring reactivation of an already unlocked modifier;
- presentation branding associated with that event;
- an event archive/replay sponsor credit.

Sponsorship must not permit:

- revealing the hidden catalog;
- adding an unreviewed modifier directly to a vote;
- changing experiment results;
- suppressing unfavorable outcomes;
- changing Warden authority;
- changing scientific interpretation;
- bypassing a frozen protocol requirement.

A sponsor may fund science.

A sponsor may not buy the answer.

## 3D visibility

An active modifier must be obvious in Panopticon 3D without requiring a tooltip.

The visual profile may define:

- HUD badge;
- CELL-67 room treatment;
- monitor treatment;
- original signage;
- optional MORTY accessory.

Physical or behavioral consequences still follow the normal evidence boundary.

For example, room signage may appear immediately because it is presentation.

A physical reaction by MORTY must come from model-derived motor/physics telemetry.

## Main page clutter rule

The main Panopticon page shows only a compact active-modifier surface:

- display name;
- science-effect class;
- sponsor, when present.

Detailed lore, unlock history, referendum history, visual profile, activation count and
achievement history belong on the modifier detail/collection surfaces.

The live containment view remains signal-first.

## Public collection

Only unlocked modifiers appear in the collection.

Example:

```text
UNLOCKED CONTAINMENT MODIFIERS

MANAGEMENT CONSULTANT
THE AUDIT
MANDATORY WELLNESS INITIATIVE
```

The UI may use atmospheric `[CLASSIFIED]` elements, but those elements must not correspond to
the actual number of hidden modifiers.

## Replay

Historical replay should preserve:

- referendum identity;
- the three candidates disclosed at that time;
- sponsor, if any;
- winner;
- vote receipt reference where available;
- unlock event;
- activation event;
- visual profile active during the run.

Comedy remains downstream of evidence.
