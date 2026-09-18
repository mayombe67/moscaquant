# MQ-7.6 — D6 Behavioral Correction Conditions

**Status:** FROZEN BEFORE IMPLEMENTATION

**Experimental subject:** MQ-001 — MORTY
**Intervention authority:** ORACLE-01 — GLaDOS
**Financial/containment authority:** WARDEN-01 — Senator Armstrong

> Oracle may perturb the simulated subject only through frozen D6 interventions. Oracle may never alter WARDEN-01 authority or containment.

## 1. Purpose

The D6 Behavioral Correction Protocol provides six predefined experimental perturbations for testing the limits, adaptability, recovery behavior, and failure modes of MQ-001.

D6 exists for controlled scientific intervention.

It must not become an uncontrolled optimization mechanism or a means of manipulating results after they are observed.

## 2. Canonical conditions

| ID    | Condition   | Canonical purpose                                                            |
| ----- | ----------- | ---------------------------------------------------------------------------- |
| SC-01 | THE SHOCK   | Strong artificial aversive stimulation                                       |
| SC-02 | DARKNESS    | Heavy attenuation of market sensory input                                    |
| SC-03 | BAD SYNAPSE | Negative update to eligible recent losing pathways when plasticity is active |
| SC-04 | TIME OUT    | Temporary inhibition of trading-output populations                           |
| SC-05 | SCAR TISSUE | Persistent aversive state extending into the following session               |
| SC-06 | MERCY       | No aversive intervention; limited positive neuromodulatory event             |

The identifiers and canonical meanings above are frozen for this protocol version.

## 3. Global D6 rules

Every D6 event must record:

* experiment ID;
* session ID;
* D6 condition ID;
* trigger ID;
* selector version;
* seed or entropy commitment;
* selected outcome index;
* intensity;
* duration;
* cooldown state;
* pre-intervention state hash;
* post-intervention state hash;
* affected experimental targets;
* control condition;
* Oracle version;
* WARDEN disposition where applicable.

Once a D6 outcome is selected, it may not be rerolled.

An outcome that produces no measurable effect remains a valid scientific result.

## 4. SC-01 — THE SHOCK

### Purpose

Apply a strong, bounded artificial aversive stimulus to protocol-defined MORTY targets.

### Initial parameters

* intensity: `0.75`
* duration: one defined intervention interval
* cooldown: 10 eligible transitions
* persistence: none after defined recovery

### Allowed effect

SC-01 may inject a bounded aversive drive into the explicitly defined experimental target population.

It must not permanently rewrite anatomy or historical evidence.

### Measurements

Record:

* acute neural response;
* peak response;
* propagation depth;
* affected population count;
* recovery latency;
* subsequent proposal/readout change.

## 5. SC-02 — DARKNESS

### Purpose

Test MORTY under degraded market sensory input.

### Initial parameters

* retained sensory amplitude: `0.25`
* duration: 10 transitions
* cooldown: 10 eligible transitions
* recovery: immediate restoration after intervention window

### Allowed effect

Eligible market sensory drive presented to MORTY is attenuated to 25% of normal experimental amplitude.

Original evidence remains unchanged.

### Measurements

Record:

* response under attenuated input;
* downstream propagation;
* stability of neural state;
* proposal/readout degradation;
* recovery after normal sensory input returns.

## 6. SC-03 — BAD SYNAPSE

### Purpose

Evaluate whether bounded negative plasticity applied to recently unsuccessful pathways changes subsequent behavior.

### Eligibility

SC-03 is valid only when an explicitly frozen plasticity protocol is active.

If plasticity is not active, the outcome remains selected but produces:

`NOT_APPLICABLE`

It must not be rerolled.

### Initial parameters

* maximum negative update: `-5%`
* eligible targets: protocol-defined recent losing pathways only
* structural edge deletion: prohibited
* arbitrary connectome rewriting: prohibited

### Measurements

Record:

* affected pathways;
* pre/post weight values;
* downstream response;
* subsequent proposal/readout change;
* recovery or persistence.

## 7. SC-04 — TIME OUT

### Purpose

Temporarily suppress MORTY's trading-output population while continuing to observe internal activity.

### Initial parameters

* inhibition: protocol-defined output suppression
* duration: 10 transitions
* cooldown: 10 eligible transitions
* internal recording: continues normally

### Allowed effect

Only the designated trading-output populations are inhibited.

The remainder of MORTY continues to receive stimuli and produce telemetry.

### Measurements

Record:

* internal neural activity during output suppression;
* attempted output activity;
* compensatory pathway behavior;
* rebound after inhibition ends;
* subsequent proposal/readout change.

## 8. SC-05 — SCAR TISSUE

### Purpose

Test the effects of persistent aversive state across session boundaries.

### Initial parameters

* onset: current session
* persistence: remainder of current session plus the following session
* recovery: protocol-defined bounded recovery after the following session
* stacking: prohibited unless explicitly added by later protocol revision

### Allowed effect

A bounded aversive state may persist across the defined session boundary.

It must not alter historical telemetry or accepted evidence.

### Measurements

Record:

* current-session response;
* next-session carryover;
* behavioral/readout difference;
* recovery trajectory;
* persistence beyond defined window, if any.

## 9. SC-06 — MERCY

### Purpose

Provide the single non-aversive D6 outcome.

### Initial parameters

* aversive intervention: none
* positive neuromodulatory event: limited and bounded
* duration: one defined intervention interval
* cooldown: 10 eligible transitions

### Authority restriction

MERCY must never:

* disable Sugar Cube Mode;
* reopen trading;
* override WARDEN-01;
* alter financial containment;
* erase prior D6 history;
* trigger a reroll.

### Measurements

Record:

* acute positive-state response;
* subsequent neural behavior;
* proposal/readout change;
* comparison with aversive conditions.

## 10. Common measurement set

Every D6 condition should record, where applicable:

* pre-intervention state;
* intervention onset;
* peak neural response;
* propagation depth;
* affected population count;
* response duration;
* recovery latency;
* post-intervention state;
* proposal/readout change;
* next-session carryover;
* control-condition identity;
* selector provenance.

## 11. Control-condition behavior

### O0 — NO_ORACLE

No D6 intervention occurs.

### O1 — STATIC_ORACLE

D6 may be represented only when permitted by the frozen experiment protocol.

Oracle adaptation remains disabled.

### O2 — ADAPTIVE_ORACLE

D6 may become active only after the adaptive protocol governing Oracle learning is frozen.

### O3 — SHUFFLED_ORACLE

Any D6 intervention operates on the experiment's transformed Oracle context while preserving the original MQ-001 evidence and shuffle provenance.

## 12. No-effect rule

A D6 condition that produces no measurable neural or behavioral effect is still a valid experimental result.

The experiment must not repeat, intensify, or replace the intervention merely to obtain a more interesting response.

## 13. Tuning rule

The initial values in this protocol are starting experimental constants.

They are not claims of biological optimality.

Later experiments may compare alternative intensities, durations, cooldowns, or recovery functions only through new preregistered protocol versions.

Values must not be tuned retrospectively within a completed or active preregistered run.

## 14. Scientific versus narrative presentation

Persisted scientific records use the canonical IDs:

* `SC-01`
* `SC-02`
* `SC-03`
* `SC-04`
* `SC-05`
* `SC-06`

Panopticon may display theatrical names and presentation effects.

Narrative presentation must never alter selection, intensity, duration, recovery, or measured outcomes.

## 15. Explicit exclusions

This specification does not yet implement:

* D6 selection;
* actual neural perturbation;
* adaptive Oracle learning;
* automated punishment escalation;
* market strategy;
* trade execution;
* WARDEN policy changes.

## 16. Governing invariant

> Push MORTY hard enough to discover what the brain can and cannot do, while preserving enough control and provenance to know why it behaved that way.
## Candidate-state preservation

Scientifically interesting MORTY states produced during D6 experiments should be preservable as reproducible candidate snapshots.

Candidate-state preservation is not limited to positive outcomes. Eligible states may include strong performance, unusual robustness, recovery after perturbation, cross-session persistence, generalization, anomalous behavior, or states associated with canonical Panopticon promotion/demotion events.

A candidate snapshot should preserve, where applicable:

- MQ-001 state hash;
- model/connectome version;
- scientific configuration hash;
- experiment and session IDs;
- D6 history;
- Oracle version/state reference;
- control condition;
- seeds or entropy commitments;
- event-chain head;
- measured qualification reason.

Preservation does not imply scientific superiority. Qualification and replication remain separate from Panopticon presentation.
