# PROJECT RASPUTIN — AWAKEN RASPUTIN

**Program type:** Infrastructure / execution platform

**Canonical authority:** `CHARTER.md`

**Execution plan:** `ROADMAP.md`

**First production scientific workload:** MQ-5.ER.5 — THE GREEK

**Governing invariant:** **RASPUTIN may change horsepower. It may never change
experimental meaning.**

## Platform objective

PROJECT RASPUTIN turns MoscaQuant scientific execution into a reproducible,
provider-neutral workload contract that can run locally or on elastic cloud
capacity without changing the experiment.

The initial cloud implementation targets AWS Spot-backed batch compute, but the
scientific execution contract must not depend on AWS semantics.

## Reference architecture

```text
Developer / CI
      |
      | short-lived identity
      v
RASPUTIN CONTROL PLANE
      |
      +-- Terraform / IaC
      +-- image build + digest
      +-- run manifest
      +-- runtime-parity gate
      +-- job submission
      |
      v
AWS BATCH / SPOT COMPUTE
      |
      +-- cpu profile
      +-- memory profile
      +-- parallel profile
      |
      v
IMMUTABLE SCIENTIFIC RUNNER
      |
      +-- verify git/config/input hashes
      +-- execute frozen command
      +-- collect telemetry
      +-- emit result + manifest
      |
      v
ARTIFACT / PROVENANCE STORE
```

## DevOps standards

### Infrastructure as code

- Terraform only for canonical AWS infrastructure;
- reusable modules with environment composition;
- remote encrypted state with locking;
- no hand-created production resources;
- `plan` review before `apply`;
- destroyability is part of acceptance.

### Identity

- short-lived credentials only;
- CI federation / OIDC where CI is used;
- separate control-plane and worker roles;
- least-privilege S3/ECR/logging permissions;
- no broker, exchange, or wallet credentials in RASPUTIN scientific workers.

### Build and release

- OCI image built from version-controlled sources;
- image referenced by immutable digest for authoritative runs;
- dependency lock / environment identity recorded;
- exact Git SHA recorded in every run manifest;
- scientific config and input hashes verified before process start.

### Scheduling

- AWS Batch is the initial scheduler;
- Spot-backed compute environment;
- diversified compatible instance types;
- runtime profiles describe resources, not science;
- scale-to-zero when idle;
- fan-out supported for independently frozen parallel jobs.

### Artifacts and provenance

Every authoritative run records:

- run ID;
- experiment ID;
- Git SHA;
- image digest;
- scientific config SHA-256;
- input artifact SHA-256 values;
- command;
- runtime profile;
- instance metadata;
- start / finish timestamps;
- wall time;
- peak memory;
- interruption / retry history;
- exit status;
- result artifact SHA-256.

### Failure semantics

Infrastructure failure is not scientific evidence.

- partial runs are non-authoritative by default;
- retries must be idempotent;
- accepted artifacts are immutable;
- interrupted attempts remain visible in provenance;
- resumability must be declared by the frozen experiment;
- budget limits may stop infrastructure but may not rewrite experimental
  stopping rules.

### Observability

Operators must be able to answer without logging into a worker:

- what is running?
- which Git SHA and image digest?
- which experiment/config/input hashes?
- which runtime profile / instance?
- how long has it been running?
- CPU / memory utilization?
- current and estimated cost?
- was it interrupted or retried?
- where are logs and artifacts?
- did teardown complete?

## Campaign map

| Stage | Codename | Technical purpose |
| --- | --- | --- |
| RSP-01 | STRIKE: SERAPH'S SHIELD | IaC, identity, storage, security, cost guardrails |
| RSP-02 | STRIKE: OFF-WORLD RECOVERY | immutable image, exact source/input recovery, manifests |
| RSP-03 | STRIKE: WARMIND NETWORK | AWS Batch + Spot elastic execution |
| RSP-04 | STRIKE: THE TYRANT'S TEST | runtime-parity acceptance |
| RSP-05 | STRIKE: ABHORRENT IMPERATIVE | interruption, idempotence, fail-closed behavior |
| RSP-06 | STRIKE: SERAPH STATION | observability, cost, operator UX |
| RAID | WRATH OF THE MACHINE | authoritative THE GREEK production run |
| BOSS | AKSIS, ARCHON PRIME | complete end-to-end platform integration |

## Completion rule

RASPUTIN is not considered awake because infrastructure exists.

RASPUTIN is awake when a parity-approved runtime completes THE GREEK from its
frozen scientific contract, emits verifiable evidence and provenance, and
tears itself down without hidden manual state.
