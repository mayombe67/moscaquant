# MQ-3.2 — Causal Path Decomposition and Intervention

## Status

**COMPLETE**

## Purpose

Determine whether the sparse Condition-A descending response identified under
MQ-3.2 can be traced through activity-supported modeled synaptic routes and
tested by direct in-model intervention.

This experiment is downstream of the MQ-3.2 physiology-constrained propagation
result.

No financial semantics are used.

---

## Starting observation

Under the frozen MQ-3.2 runtime:

- neutral remained exactly silent;
- Condition B remained exactly silent;
- Condition A produced a sparse DN-C1 response;
- 9 of 646 DN-C1 neurons became positive;
- no descending neuron spiked.

The nine responders were:

- DNp11_R
- DNc02(SIFa)_L
- DNc02(SIFa)_R
- DNp27_L
- DNp27_R
- DNc01_L
- DNc01_R
- DNp30_L
- DNp30_R

---

## Causal-path precommit

Source types:

- Tm2
- Tm4

Targets:

the nine frozen Condition-A DN-C1 responders.

Path-search constraints:

- time-unrolled replay
- maximum 4 hops
- positive synaptic edges only
- positive presynaptic modeled activity required
- first-positive frame inspected
- peak frame inspected
- maximum 50 reported paths per target/frame

Ranking:

`bottleneck_instantaneous_contribution`

Recorded values included:

- synaptic edge weight
- presynaptic activity
- instantaneous contribution
- path-weight product
- bottleneck contribution

Structural connectivity alone was explicitly insufficient.

---

## Activity-supported path decomposition

Condition A was replayed using the frozen MQ-3.2 runtime.

For every modeled step, the effective presynaptic activity driving that step was
recorded.

Reported paths therefore required:

1. structural connectivity;
2. positive synaptic weight;
3. positive modeled presynaptic activity;
4. temporal consistency with the replay.

### First-positive-frame results

| Target | First frame | Source | Minimum route |
|---|---:|---|---:|
| DNp11_R | 145 | Tm4 | 1 hop |
| DNc02_L | 145 | Tm2 | 1 hop |
| DNc02_R | 147 | Tm4 | 1 hop |
| DNp27_L | 146 | Tm4 | 1 hop |
| DNc01_R | 147 | Tm4 | 1 hop |
| DNp30_R | 146 | Tm2 | 1 hop |
| DNp30_L | 148 | Tm4 | 1 hop |
| DNp27_R | 149 | Tm4 | 1 hop |
| DNc01_L | 147 | Tm4 | 2 hops |

Eight of nine responders therefore had direct activity-supported Tm2/Tm4 input
at their original onset.

DNc01_L required a two-edge route.

At peak frames, all targets reached the reporting ceiling of 50 paths except
where the available path set was slightly narrower.

Therefore, peak-frame path counts are not interpreted as exhaustive counts.

Artifact:

`/home/wil/moscaquant-data/experiments/mq3-2-causal-path-decomposition-v1.json`

SHA-256:

`ed52950dc8799159ef8d138da8717564aefcc13f10b558c394ca5646e32dd9f1`

Claim level at this stage:

**ACTIVITY-SUPPORTED CAUSAL CANDIDATE PATHS**

This is not yet interventional evidence.

---

## Frozen first-onset edge artifact

Before intervention, the union of all edges contained in reported
first-positive paths was frozen.

Targets:

`9`

Unique frozen edges:

`13`

Artifact:

`/home/wil/moscaquant-data/processed/mq3-2-first-onset-causal-edges-v1.json`

SHA-256:

`23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b`

### Frozen edge set

| Presynaptic | Postsynaptic | Weight |
|---:|---:|---:|
| 43417 | 656 | 0.0006644517998211086 |
| 44274 | 55 | 0.00015401201380882412 |
| 55548 | 51 | 0.00012879958376288414 |
| 55925 | 55 | 0.00015401201380882412 |
| 56393 | 68045 | 0.004975124262273312 |
| 64717 | 92 | 0.00010267994366586208 |
| 65084 | 137122 | 0.0002288853283971548 |
| 68045 | 1273 | 0.0005341880605556071 |
| 87441 | 51 | 0.00012879958376288414 |
| 92657 | 129 | 0.00031298905378207564 |
| 93484 | 129 | 0.00015649452689103782 |
| 128590 | 317 | 0.0005941770505160093 |
| 135589 | 126002 | 0.0006234414177015424 |

---

## Intervention precommit

Five runs were precommitted:

1. baseline Condition A
2. targeted Condition A
3. sham Condition A
4. targeted neutral
5. targeted Condition B

### Targeted intervention

Only the 13 frozen first-onset edges were set to zero.

All other modeled parameters and structural connections remained unchanged.

### Sham intervention

Thirteen control edges were selected deterministically.

For each targeted edge:

- the same presynaptic neuron was retained;
- the nearest available positive synaptic weight was chosen;
- frozen intervention edges were excluded;
- the nine responder targets were excluded;
- control edges were unique;
- ties used lowest postsynaptic model index.

### Primary endpoint

For each responder:

`voltage at original first-positive frame <= 0`

was precommitted as evidence that the original onset had been removed or
delayed.

### Precommitted strong confirmation

Strong confirmation required:

- targeted deletion removes or delays all nine original onsets;
- sham deletion preserves all nine original onsets.

---

## Frozen sham edge set

| Presynaptic | Postsynaptic | Weight |
|---:|---:|---:|
| 43417 | 878 | 0.0006591957644559443 |
| 44274 | 4356 | 0.00013991884770803154 |
| 55548 | 4356 | 0.00013991884770803154 |
| 55925 | 5433 | 0.00016412275726906955 |
| 56393 | 98715 | 0.004950494971126318 |
| 64717 | 4131 | 0.00014202528109308332 |
| 65084 | 369 | 0.00023729295935481787 |
| 68045 | 107 | 0.000545681337825954 |
| 87441 | 137444 | 0.00014233356341719627 |
| 92657 | 6648 | 0.00031565656536258757 |
| 93484 | 6008 | 0.00015220700879581273 |
| 128590 | 5803 | 0.0005770340212620795 |
| 135589 | 3587 | 0.0006313795456662774 |

---

## Baseline reproduction

Baseline Condition A reproduced every original responder onset exactly.

| Target | Original onset |
|---|---:|
| DNp11_R | 145 |
| DNc02_L | 145 |
| DNc02_R | 147 |
| DNp27_L | 146 |
| DNc01_R | 147 |
| DNp30_R | 146 |
| DNp30_L | 148 |
| DNp27_R | 149 |
| DNc01_L | 147 |

Baseline reproduction:

**PASS**

---

## Targeted intervention result

Deleting only the 13 frozen first-onset pathway edges delayed:

**9 / 9 original responder onsets**

| Target | Baseline onset | Targeted onset |
|---|---:|---:|
| DNp11_R | 145 | 146 |
| DNc02_L | 145 | 148 |
| DNc02_R | 147 | 149 |
| DNp27_L | 146 | 150 |
| DNc01_R | 147 | 148 |
| DNp30_R | 146 | 147 |
| DNp30_L | 148 | 149 |
| DNp27_R | 149 | 150 |
| DNc01_L | 147 | 152 |

Targeted onset result:

**9 / 9 REMOVED OR DELAYED**

---

## Sham intervention result

Deleting the deterministic weight-matched sham edges delayed:

**0 / 9 original responder onsets**

Every first-positive frame remained identical to baseline.

Sham onset result:

**0 / 9 CHANGED**

---

## Response magnitude after targeted deletion

The intervention generally delayed rather than completely abolished subsequent
activity.

This indicates redundant or alternative later routes.

However, several responder amplitudes were strongly reduced.

### DNc02_L

Baseline maximum:

`0.0019789475481957197`

Targeted maximum:

`0.00010799081064760685`

### DNp27_L

Baseline maximum:

`0.00020043256517965347`

Targeted maximum:

`8.813651142247636e-09`

### DNc01_L

Baseline maximum:

`3.2192949674936244e-06`

Targeted maximum:

`6.032255858018365e-13`

---

## Responder-ensemble diagnostic

The nine-neuron responder-ensemble diagnostic score was:

Baseline:

`0.00011496507367307156`

Targeted:

`0.00005820236200637074`

This is approximately a 49% reduction.

This value is a subordinate nine-neuron diagnostic.

It is **not** the official frozen 646-neuron DN-C1 episode score.

---

## Neutral and Condition-B controls

Under the targeted 13-edge deletion:

### Neutral

- responder ensemble score: 0
- all nine targets remained exactly silent

### Condition B

- responder ensemble score: 0
- all nine targets remained exactly silent

The intervention therefore did not create activity in either control condition.

---

## Intervention verdict

Precommitted result:

**STRONG_CONFIRMATION**

Summary:

- baseline reproduced: YES
- targeted original onsets removed/delayed: 9 / 9
- sham original onsets removed/delayed: 0 / 9
- targeted neutral clean: YES
- targeted Condition B clean: YES

Artifact:

`/home/wil/moscaquant-data/experiments/mq3-2-causal-intervention-v1.json`

SHA-256:

`0a400d4e9efc415266d51b9ad68eedfaf8318e684a1e504fb005f9609cc5917e`

---

## Interpretation

The first onset of the MQ-3.2 Condition-A descending response depends causally,
within the frozen MoscaQuant computational model, on the preidentified 13-edge
first-onset pathway set.

This conclusion is stronger than structural connectivity or temporal
correlation because direct model intervention altered the predicted response,
while matched sham intervention did not.

The result also demonstrates that later redundant routes exist: targeted
deletion delayed all nine original onsets but did not universally abolish all
subsequent activity.

Supported claim:

**MODEL-LEVEL CAUSAL NECESSITY OF THE IDENTIFIED FIRST-ONSET ROUTES**

Unsupported claims:

- biological causal equivalence
- natural fly behavioral prediction
- financial meaning
- BUY / HOLD / SELL
- profitability
- learning

Financial semantics used:

**NO**

Biological causality claim:

**NO**
