# Runtime Parity Acceptance v1

## Purpose

This gate turns MoscaQuant's hardware-independence rule into executable acceptance.

A migration from Habitat to a workstation, cloud worker, GPU host, or other runtime profile is infrastructure work only if the frozen scientific fixture remains scientifically identical.

The runtime may change. The science may not.

## v1 frozen invariants

- dataset class: `EMPIRICAL_MALECNS`
- real spatial provenance: `7,486`
- topology-fallback provenance: `4,989`
- responder spatial provenance: `9 / 9` real
- accepted causal-edge count: `13`

A future legitimate scientific change must create a new versioned acceptance profile rather than silently editing v1 after observing a migration failure.

## Provenance classes

- `EMPIRICAL_MALECNS` — authoritative empirical graph/data fixture
- `SPATIAL_SURROGATE` — declared geometry/topology surrogate
- `SYNTHETIC_TEST` — software/unit-test fixture

Synthetic and surrogate fixtures may prove software behavior. They do not satisfy the authoritative hardware-migration gate.

## Scientific digest

Each runtime manifest records the source commit, runtime profile, frozen invariants, exact scientific outputs, named SHA-256 artifact hashes, and a runtime-independent `scientific_digest`.

Runtime identity and filesystem paths are recorded for provenance but excluded from the scientific digest. Habitat and the workstation should have different runtime identities while producing the same scientific digest.

## Fail-closed comparison

Parity passes only when both manifests satisfy v1 invariants, use the same source commit and empirical dataset class, and have exactly equal scientific digests.

v1 has no post-hoc floating-point tolerance escape hatch. If exact hashable outputs do not reproduce, stop and investigate. Any tolerance policy must be specified in a new acceptance-profile version before inspecting candidate results.

## Adapter boundary

Future sensory and neural-to-world adapters should be hashable as separate artifacts. A market encoder, camera encoder, motor mapping, broker adapter, or public presentation layer must never disappear into the neural-runtime hash.

## Scientific boundary

Runtime parity is reproducibility evidence. It does not establish biological fidelity, biological causality, or financial utility.
