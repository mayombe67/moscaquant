# MoscaQuant Runtime Profiles

MoscaQuant separates scientific configuration from machine/runtime configuration.

Runtime profiles may change computational resources and filesystem paths.

They must not change accepted scientific behavior, experiment semantics, model anatomy, causal evidence, or interpretation rules.

## Available profiles

### habitat

The original constrained development/runtime environment.

Typical characteristics:

- lowest worker count;
- smallest memory ceiling;
- smallest edge-processing batches;
- CPU execution.

### workstation

A larger local development/runtime environment.

Typical characteristics:

- additional workers;
- larger memory ceiling;
- larger edge-processing batches;
- CPU execution.

### cloud

The production cloud runtime.

Current profile:

```toml
[runtime]
name = "cloud"
edge_batch_rows = 8000000
max_memory_gb = 24
workers = 8
device = "cpu"

[paths]
data_dir = "/var/lib/moscaquant"
scratch_dir = "/var/cache/moscaquant"
```

## Allowed runtime differences

Runtime profiles may change:

- worker count;
- batch sizes used for computational efficiency;
- memory ceilings;
- scratch paths;
- data paths;
- compute device selection where scientifically equivalent execution is preserved.

## Prohibited runtime differences

Runtime profiles must not change:

- MQ-001 anatomy;
- frozen connectome structure;
- accepted causal evidence;
- experimental stimuli;
- normalization or transduction semantics;
- intervention definitions;
- control definitions;
- hypothesis definitions;
- pass/fail criteria;
- scientific interpretation rules.

## Selection

The runtime profile is selected using:

```bash
MOSCAQUANT_RUNTIME=cloud
```

If no runtime is explicitly selected, the default runtime is `habitat`.

Runtime selection is infrastructure configuration, not a scientific experiment.
