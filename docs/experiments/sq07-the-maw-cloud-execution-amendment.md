# SQ-07 THE MAW — AWS Batch Execution-Mode Amendment

## Purpose

This amendment expands the explicit execution-transport vocabulary accepted by
the frozen SQ-07 shard authorization gate.

Before this amendment, the runner accepted only:

- `local`

After this amendment, the runner accepts exactly:

- `local`
- `aws_batch`

No execution mode grants authority by itself. A tracked, explicit,
run-specific human authorization is still required.

## Scientific scope

This amendment does not change:

- the SQ-07 condition plan;
- the 8,192-mask universe;
- the 512-shard partition;
- the 32,768-episode universe;
- the subset operator;
- the episode executor;
- the evidence writer or schema;
- the visual stimulus;
- the inherited physiology/runtime;
- the frozen input data;
- the no-adaptive-selection rule;
- the no-result-driven-pruning rule;
- the no-early-stopping rule;
- the one-canonical-shard-per-invocation rule.

Pre-amendment frozen scientific hashes:

- condition planner: `38b8e628492a475f63c40c332232b36c929512dfae8341f5b64afd1597f5411f`
- shard planner: `7cde07ad921543cdb9dba95f3299ccb4a1cfbb20f32a3a75fc678a2df61ef1af`
- subset operator: `693ae8c2455361351802d0ac0c9cee4ada3bb8a25a60043264de5da14da00a5e`
- episode executor: `a4b85e45779ab98c9a1275a0e97ced9f1abb48bfadd974319bfcecf4305be9d8`
- evidence writer: `255427764b0f0b49273c27c44f000ecb50628fc7d129ec8dc9fcfddeb0af3e11`
- preregistration: `0ff34f0f4c2c1315b766ecc1acf66e2e6c24650aba87ae033e5a71a2b707a84a`
- sharding contract: `ede14b0add5d13e723c443be241504dea36d4bb0424e3f718b199b8c1c665d8a`
- evidence schema: `c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01`

## Authorization boundary

The previously executed shard 000 remains attributable to the original
local-only authorization commit:

`817fa8465ef4049ea6160d9d7ff0b372ddd12ad3`

That authorization is not broadened retroactively.

AWS Batch execution requires a new explicit human authorization created after
this amendment. Automated authorization and AI-generated authorization remain
forbidden.

Changing execution transport does not authorize neural execution by itself.

## Control-plane fingerprint transition

Original local-only execution stack used for shard 000:

- shard runner: `bd736984acad6bbdceb812ca84ee6d413acaaa0f864f4a48899f9fbfacf87312`
- shard runner test: `f4028b709bbdc8679a2ceb70a9c3ec98b52e5ffe0f0826abc4bac6a8ab0c9c2d`
- authorization commit: `817fa8465ef4049ea6160d9d7ff0b372ddd12ad3`

Cloud-aware control-plane amendment:

- shard runner: `45eddddc2edd7c73a9e40f05cc85c0faa3d2d96eb8addfdc1466dad688f2688f`
- shard runner test: `a6f212b0ba008e7f9fb32820bec546ad40aaa439ddf0829160836285f3cf2d0f`

The original authorization file is intentionally not modified. It remains
the provenance record for shard 000 and does not authorize AWS Batch
execution.
