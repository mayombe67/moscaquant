# MQ-5.ER Neural Runner Implementation

**Status:** IMPLEMENTED / RESULT EXECUTION DISABLED

## Purpose

Implement the frozen MQ-5.ER neural execution and classification machinery
without authorizing result-bearing execution.

The runner reuses the accepted MQ-5.TS physiology-constrained runtime and
frozen MQ-3.2 responder/causal artifacts.

## Execution gate

Result execution fails closed unless:

- `result_execution_enabled = true`;
- the response classification contract is frozen;
- the real-artifact encoding-verification artifact has its exact frozen SHA;
- the Git working tree is clean;
- every required protocol, implementation, test, and gate file is tracked;
- no result artifact already exists.

At implementation freeze, `result_execution_enabled` remains `false`.

## Frozen Arm A validation

Before any alternative encoding is interpreted, the runner requires:

1. two exact duplicate Arm-A baseline replays;
2. Arm-A baseline canonical payload SHA equal to the accepted MQ-5.TS Arm-A
   payload;
3. Arm-A first-positive onset vector equal to the frozen nine-target contract;
4. Arm-A 13-edge lesion canonical payload SHA equal to the accepted MQ-5.TS
   lesion payload;
5. Arm A to classify as `RESPONSE PATTERN PRESERVED`.

Failure of any item stops the complete experiment.

## Alternative arms

For B, C, E, and every non-identity D remap:

1. regenerate the frozen verified sensory episode;
2. verify its stimulus SHA against the pre-neural encoding artifact/config;
3. run the original connectome;
4. run the same encoding through the frozen 13-edge-lesioned connectome;
5. apply the response-classification contract;
6. preserve every result, including negative outcomes.

No failed alternative is replaced or retuned.

## Causal-expression test

For each of the nine frozen targets, the lesion must produce either:

- a strictly later first-positive onset than that encoding's baseline; or
- no first-positive response within 192 frames.

All nine must satisfy the criterion for the bundle to count as causally
expressed.

This is explicitly a frozen 13-edge bundle intervention, not a claim that every
edge remains individually necessary.

## Arm D

The identity member is excluded from the 11 confirmatory neural remaps because
it is exactly Arm A and was already verified pre-neurally.

All eleven non-identity mappings are executed and classified independently.
The frozen four-way family rule is applied afterward.

## Current authorization

**RESULT EXECUTION DISABLED**

The runner may be installed, reviewed, unit-tested, and committed.

It must not be executed with `--run-frozen-ensemble` until the project
explicitly changes the frozen authorization gate after the pending MQ-5.TS
external audit has been resolved.

Financial semantics remain:

**NOT ASSIGNED**
