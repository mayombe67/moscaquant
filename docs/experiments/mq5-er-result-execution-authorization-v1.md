# MQ-5.ER Result Execution Authorization v1

**Status:** AUTHORIZED FOR ONE FROZEN ENSEMBLE EXECUTION

This document authorizes execution of the already-frozen MQ-5.ER neural
ensemble after protocol, encoder, real-artifact stimulus verification,
classification contract, causal-expression rule, neural runner, and
pre-audit readiness gate were frozen.

Authorization changes only the execution gate:

`result_execution_enabled = false`

to:

`result_execution_enabled = true`

No scientific threshold, responder definition, stimulus, mapping, lesion,
runtime, topology, or classification rule is changed by this authorization.

## Frozen prerequisites

- readiness lineage includes `d69cc69e7bf266b10c98966516a64d2d16e69e56`
- real-artifact encoding verification SHA-256:
  `15340cae365c291424f88ac3206e7ddc3f16885a52e89aece96d347bba741acb`
- neural runner freeze is already in repository history
- response classification contract is frozen
- result artifact remains non-overwritable
- all B/C/E arms and all eleven non-identity D remaps must be retained
- failed or inconvenient outcomes must not be replaced or retuned

## Execution semantics

The authorized command is the frozen runner's single result-bearing mode:

`python3 -u -m brain.mq5_er_neural_runner --run-frozen-ensemble`

The runner must still pass its own clean-tree, tracked-file, artifact-hash,
Arm-A duplicate, accepted Arm-A payload, accepted 13-edge-lesion payload,
stimulus-hash, and no-existing-result checks before producing an artifact.

## Claim boundary

Authorization to execute is not evidence for any outcome.

Financial semantics remain:

**NOT ASSIGNED**
