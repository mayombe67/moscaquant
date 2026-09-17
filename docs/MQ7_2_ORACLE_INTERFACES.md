**System:** ORACLE-01  
**Codename:** GLaDOS  
**Role:** Behavioral interpretation / adaptation layer  
**Authority:** None
# MQ-7.2 — Oracle Interface & State Model

**Status:** DESIGN FREEZE BEFORE BEHAVIORAL IMPLEMENTATION

MQ-7.2 translates the MQ-7.1 scientific protocol into explicit software boundaries.

No learning policy, reinforcement engine, or external execution logic is implemented in this phase.

## 1. Design objective

Define the minimum interfaces required for Oracle to:

* receive accepted MQ-001 evidence;
* maintain Oracle-owned state;
* emit non-authoritative proposals;
* record deterministic state transitions;
* produce append-only audit events;
* remain structurally incapable of modifying MQ-001 or bypassing WARDEN-01.

## 2. Module boundary

```text
MQ-001 evidence
      |
      v
 OracleInput
      |
      v
 Oracle state transition
      |
      v
 OracleState
      |
      +------> OracleEvent
      |
      v
 OracleProposal
      |
      v
 WARDEN-01
```

Oracle does not own MQ-001 state.

Oracle does not own WARDEN-01 state.

Oracle owns only OracleState and Oracle-generated audit records.

## 3. OracleInput

`OracleInput` is the complete allowed observation boundary.

It must contain only versioned, accepted, or explicitly derived information.

Required fields:

* `experiment_id`
* `session_id`
* `frame_id`
* `timestamp`
* `mq001_version`
* `scientific_config_hash`
* `evidence_refs`
* `derived_features`
* `prior_oracle_state_hash`
* `warden_history`

### Input restrictions

`OracleInput` must not contain:

* mutable MQ-001 objects;
* direct connectome references permitting modification;
* WARDEN-01 private state;
* WARDEN policy objects;
* execution credentials;
* broker or exchange credentials;
* wallet or signing material;
* filesystem paths to authoritative private state.

All complex data should be represented through immutable values, versioned snapshots, or references.

## 4. OracleState

`OracleState` contains only state owned by Oracle.

Initial state model:

* `oracle_version`
* `generation`
* `behavioral_state`
* `adaptation_state`
* `intervention_state`
* `history_digest`
* `state_hash`

### Ownership rule

Oracle may replace one valid `OracleState` with another valid `OracleState`.

Oracle may not mutate MQ-001 state as part of that transition.

Oracle may not mutate WARDEN-01 state as part of that transition.

State transitions should therefore conceptually behave as:

```text
(previous OracleState, OracleInput)
                |
                v
           transition()
                |
                v
(new OracleState, OracleProposal, OracleEvent)
```

## 5. OracleProposal

`OracleProposal` is an advisory artifact.

It is never an execution command.

Required fields:

* `experiment_id`
* `session_id`
* `oracle_version`
* `proposal_id`
* `proposal_type`
* `proposal_payload`
* `confidence`
* `abstain`
* `evidence_refs`
* `oracle_state_hash`

### Proposal invariants

A proposal:

* must reference the Oracle state that produced it;
* must reference supporting accepted evidence;
* may explicitly abstain;
* must not contain an authorization result;
* must not claim WARDEN approval;
* must not contain an execution callback;
* must not contain broker credentials;
* must not directly execute anything.

`confidence` is descriptive metadata, not authority.

## 6. WARDEN disposition

WARDEN-01 evaluates Oracle proposals independently.

Oracle may later observe a sanitized disposition such as:

* `ALLOW`
* `DENY`
* `REJECT_POLICY`
* `NO_DECISION`

Oracle must not receive private WARDEN policy state merely because it receives the disposition.

A WARDEN result is historical evidence about authority outcome, not an Oracle-controlled state transition.

## 7. OracleEvent

Every meaningful Oracle transition produces an immutable audit event.

Required fields:

* `event_id`
* `timestamp`
* `experiment_id`
* `session_id`
* `oracle_version`
* `oracle_artifact_hash`
* `input_hash`
* `pre_state_hash`
* `proposal_hash`
* `post_state_hash`
* `previous_event_hash`
* `event_hash`

Optional fields may include:

* `intervention_id`
* `entropy_commitment`
* `warden_disposition`
* `notes`

### Audit rule

An event is evidence of what Oracle did.

An event is not itself permission to execute an external action.

## 8. Hashing

Canonical serialization must be defined before production audit hashes are trusted.

The implementation must:

* use deterministic field ordering;
* use a stable encoding;
* exclude non-deterministic process metadata;
* explicitly define whether timestamps participate in each hash;
* reject unsupported or unserializable values.

SHA-256 is the initial required digest unless superseded by a documented protocol revision.

## 9. Immutability

Initial schema objects should be immutable after construction.

Preferred Python representation:

```python
@dataclass(frozen=True)
```

Mutable dictionaries or lists should not cross the Oracle boundary directly.

Prefer:

* tuples instead of lists;
* immutable mappings or canonicalized key/value tuples;
* strings for external identifiers;
* scalar numeric values;
* hashes for large external artifacts.

## 10. Validation

Validation must reject:

* missing experiment/session identifiers;
* malformed hashes;
* confidence values outside the frozen range;
* empty Oracle versions;
* proposals without evidence references unless the proposal type explicitly permits them;
* state transitions whose pre-state hash does not match the supplied prior state;
* malformed event-chain links;
* direct authority or execution fields.

Invalid data must fail closed.

## 11. Abstention

Abstention is a first-class valid Oracle result.

Oracle must be able to state:

```text
NO PROPOSAL
```

without manufacturing a low-confidence action.

An abstention must still produce an auditable proposal/event pair.

## 12. Error handling

Operational errors are distinct from scientific results.

Examples:

* malformed input;
* incompatible schema version;
* missing referenced evidence;
* failed state-hash verification;
* audit-chain corruption.

Such failures must not be reinterpreted as Oracle behavioral outcomes.

## 13. Schema versioning

Each serialized object must carry a schema version or be unambiguously associated with one.

Initial versions:

* `oracle-input/v1`
* `oracle-state/v1`
* `oracle-proposal/v1`
* `oracle-event/v1`

Schema changes that alter meaning require a version increment.

## 14. Initial package structure

```text
oracle/
├── __init__.py
├── models.py
├── protocol.py
├── state.py
└── audit.py
```

Responsibilities:

### `models.py`

Immutable schema definitions only.

### `protocol.py`

Validation rules and protocol invariants.

### `state.py`

Deterministic Oracle-owned state transitions.

No adaptive learning policy in MQ-7.2.

### `audit.py`

Canonical serialization, hashing, and event-chain construction/verification.

## 15. Explicit exclusio
