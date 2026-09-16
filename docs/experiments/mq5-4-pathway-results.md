# MQ-5.4 — Pathway Perturbation Results

Status:

**SUPPORTED PATHWAY INTERVENTION EFFECT**

Scope:

**Frozen MoscaQuant model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Frozen pathway

`56393 → 68045 → 1273`

Frozen causal timing:

- `56393 → 68045` at frame 146
- `68045 → 1273` at frame 147

The pathway and intervention mechanics were pre-registered before outcome
generation.

## Validation

All MQ-5.4 validation gates passed.

- frozen pathway verified
- upstream sham exactly matched baseline
- intermediate sham exactly matched baseline
- upstream dose telemetry verified
- intermediate dose telemetry verified
- upstream 100% intervention reproduced exactly
- intermediate 100% intervention reproduced exactly
- frozen artifacts remained unchanged

## Baseline pathway telemetry

At the frozen pathway frames:

- 56393 effective activity at F146:
  `0.0004448029794730246`

- 68045 voltage after F146:
  `2.2129499939183006e-06`

- 68045 effective activity at F147:
  `2.2129499939183006e-06`

- 1273 voltage after F147:
  `1.1821315037963132e-09`

## Upstream intervention

Neuron 56393 was attenuated at F146.

The resulting intermediate and downstream responses were:

| Attenuation | 68045 V @ F146 | 68045 effective @ F147 | 1273 V @ F147 | Δ integrated 1273 |
| ---: | ---: | ---: | ---: | ---: |
| 25% | 1.659712666e-06 | 1.659712666e-06 | 8.865986834e-10 | -3.983937702e-08 |
| 50% | 1.106474997e-06 | 1.106474997e-06 | 5.910657519e-10 | -7.968252536e-08 |
| 75% | 5.532374985e-07 | 5.532374985e-07 | 2.955328759e-10 | -1.195304307e-07 |
| 100% | 0 | 0 | 0 | -1.593722314e-07 |

Increasing upstream attenuation produced monotonic reduction in:

1. the predefined intermediate response,
2. subsequent intermediate effective activity,
3. the predefined downstream response.

At complete upstream silencing, the measured intermediate contribution at
the frozen pathway frames fell to zero and the downstream F147 response
also fell to zero.

## Intermediate intervention

Neuron 68045 was independently attenuated at F147.

| Attenuation | 68045 effective @ F147 | 1273 V @ F147 | Δ integrated 1273 |
| ---: | ---: | ---: | ---: |
| 25% | 1.659712552e-06 | 8.865986278e-10 | -5.701459693e-09 |
| 50% | 1.106474997e-06 | 5.910657519e-10 | -1.140819428e-08 |
| 75% | 5.532374985e-07 | 2.955328759e-10 | -1.712343140e-08 |
| 100% | 0 | 0 | -2.282565670e-08 |

Increasing intermediate attenuation produced a monotonic reduction in the
predefined downstream response.

## Pathway interpretation

MQ-5.4 supports propagation through the complete predefined pathway:

`56393 → 68045 → 1273`

Upstream perturbation altered the intermediate node in the predicted
direction.

The altered intermediate state subsequently changed its effective
activity at the next frozen pathway frame.

The downstream target changed in the predicted direction as attenuation
increased.

This is stronger than treating the two frozen edges only as unrelated
single-edge interventions because the MQ-5.4 artifact records the
intermediate state linking the upstream intervention to the subsequent
downstream response.

## Upstream versus intermediate intervention magnitude

Complete upstream silencing produced an integrated downstream reduction
of approximately:

`-1.593722314e-07`

Complete one-frame intermediate silencing produced approximately:

`-2.282565670e-08`

The upstream intervention therefore produced a substantially larger
integrated downstream effect in this experiment.

No synergy interpretation is assigned.

The interventions are not equivalent manipulations: upstream perturbation
changes the state entering the intermediate node and therefore its later
trajectory, while the intermediate intervention directly attenuates
effective activity at its designated intervention frame.

MQ-5.2 already demonstrated that causal influence frequently extends
beyond a single frame.

## Result classification

Upstream → intermediate dependence:

**SUPPORTED**

Upstream → downstream pathway propagation:

**SUPPORTED**

Intermediate → downstream dependence:

**SUPPORTED**

Dose-dependent pathway propagation:

**SUPPORTED**

Equal hop strength:

**NOT TESTED / NOT ASSUMED**

Synergy:

**NOT TESTED / NOT ASSUMED**

Single-frame temporal exclusivity:

**NOT CLAIMED**

## Artifacts

Generated immutable experimental artifacts:

- `mq5-4-pathway-56393-68045-1273-v1.json`
- `mq5-4-pathway-56393-68045-1273-v1.npz`

Protocol:

- `docs/experiments/mq5-4-pathway-protocol.md`

Configuration:

- `config/controls/mq5-4-pathway-56393-68045-1273-v1.toml`

## Limitations

The result establishes pathway behavior within the frozen MoscaQuant
simulation.

It does not establish equivalent pathway causality in living Drosophila.

The experiment used the current frozen market-to-sensory encoding. Encoding
robustness remains a separate methodological question and is not inferred
from this experiment.

Financial semantics remain:

**NOT ASSIGNED**
