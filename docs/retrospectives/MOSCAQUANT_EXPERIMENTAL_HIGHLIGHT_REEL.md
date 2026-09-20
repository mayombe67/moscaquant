# MoscaQuant Experimental Highlight Reel

**Science, Failure, Causality, and the Increasingly Questionable Treatment of MQ-001**  
Version 0.3 — 2026-09-20
> **Canonical status:** Project retrospective and narrative record.
>
> This document is canonical for MoscaQuant project history, highlight-reel
> framing, and approved science/lore descriptions.
>
> It does not supersede `CHARTER.md`, frozen experiment protocols, experiment
> result records, or Git history. Where a retrospective summary conflicts with
> primary experimental evidence, the primary experimental record controls.
>
> The DOCX companion is a rendered presentation artifact. This Markdown file is
> the canonical editable source.
> Authority order: `CHARTER.md` > `ROADMAP.md` > frozen experiment records > this retrospective.

## Purpose

A formal retrospective of the MoscaQuant experiments that produced the strongest scientific findings, the most useful failures, and the funniest consequences. Every narrative moment is paired with its experimental basis and claim boundary. This document is not a substitute for the Charter, Roadmap, frozen protocols, result artifacts, or git history.

## Executive summary

MoscaQuant began as an intentionally absurd question: can a male Drosophila connectome-derived model be instrumented well enough to receive market-like sensory input, generate bounded output, experience controlled perturbations, and eventually support experimentally testable adaptation without giving the fly financial authority?

The answer became more scientifically interesting than the premise. Across MQ-2.1 through MQ-7, the project moved from restoring a missing visual-transduction handoff, through anonymous descending-neuron readout and causal perturbation, into a deterministic Oracle/D6 framework with persistent state, preregistered controls, reversible plasticity overlays, dynamic trace analysis, and causal mediation experiments.

**Retrospective rule:** The comedy is downstream of the evidence. Null results stay null. Narrative terms never replace the operational scientific description.

## Highlight reel

### 01 — The Neutral Gate That Saved Us From Ourselves
**Reference:** MQ-3.1 global positive-subthreshold propagation test.  
A parameter-free propagation hypothesis pushed activity farther downstream but contaminated the precommitted neutral condition with substantial descending-neuron voltage and spikes. The hypothesis was rejected before A/B replay was inspected.  
**Science:** the neutral gate prevented tuning the model until it merely looked market-aware.  
**Lore:** MORTY developed opinions about a market that was not there. Placeholder McDoctorate pulled the plug.

### 02 — The Bridge Neurons That Refused to Clock In
**Reference:** MQ-3 propagation audit; MQ-3.2 closure.  
Twenty-five first-hop bridge neurons received signed market-conditioned current and projected toward assigned descending populations, but none crossed the baseline LIF threshold.  
**Science:** the failure localized the bottleneck and motivated a physiology-constrained model instead of arbitrary gain inflation.  
**Lore:** Twenty-five employees received the memo. Zero attended the meeting.

### 03 — The Pathway Became Real Enough to Break on Purpose
**Reference:** MQ-5.4 pathway perturbation; validated `56393 -> 68045 -> 1273`.  
Controlled perturbation established upstream-to-intermediate dependence, upstream-to-downstream propagation, intermediate-to-downstream dependence, and dose-dependent propagation.  
**Science:** later SC-03 work had a defensible causal substrate.  
**Lore:** We finally found a wire worth haunting.

### 04 — BAD SYNAPSE Was Allowed to Say “No”
**Reference:** SC-03 credit-assignment protocol; live-plasticity activation.  
Credit assignment could return `ELIGIBLE`, `AMBIGUOUS_CREDIT`, or `NO_ELIGIBLE_PATHWAY`; unsupported cases produced no update.  
**Science:** P&L could trigger review but could not choose a synapse, ranking, or update magnitude.  
**Lore:** Sometimes the correct punishment was paperwork.

### 05 — MORTY Earned a Real Persistent State
**Reference:** MQ-7 adaptive activation and 36-session replication.  
O2 earned legitimate 0.95 SC-03 updates on `56393 -> 68045`; repeated updates accumulated and protocol-defined inactivity produced recovery while the structural connectome remained unchanged.  
**Science:** persistent, reversible, replayable model state.  
**Lore:** MORTY acquired character development. It was stored in a hash-verified overlay.

### 06 — DARKNESS Actually Changed Spikes
**Reference:** full D6 integration smoke test.  
SC-02 DARKNESS produced voltage, spike, and readout-score divergence while preserving the structural connectome.  
**Science:** an acute sensory intervention crossed into spike-level divergence under the tested timing.  
**Lore:** GLaDOS turned off the lights and, for once, the fly actually noticed.

### 07 — MERCY Did Absolutely Nothing
**Reference:** SC-06 MERCY smoke result.  
MERCY produced a valid null because its one-transition gain only amplifies existing effective activity.  
**Science:** the project preserved the null instead of rerolling until something happened.  
**Lore:** The cake had zero presynaptic activity.

### 08 — SCAR TISSUE Survived Into Tomorrow
**Reference:** SC-05 integration and target-persistence fix.  
SC-05 persisted into the following session. A smoke test exposed target drift across sessions; the implementation was fixed before the preregistered multi-session experiment.  
**Science:** same-target persistence survived the defined session boundary.  
**Lore:** MORTY’s scar initially teleported to another neuron overnight. We called it a bug.

### 09 — The Full D6 Experiment Refused to Become a Cartoon
**Reference:** MQ-7 full D6 48-session experiment.  
All six D6 outcomes occurred; O2 earned four legitimate SC-03 updates; 10 sessions diverged at voltage/score level; zero diverged at spike or final-decision level; two SC-05 carryovers occurred; structural connectome unchanged.  
**Science:** mixed interventions remained stable while effect levels stayed explicitly separated.  
**Lore:** Forty-eight sessions of behavioral correction and MORTY still refused to become a hedge-fund manager.

### 10 — GLaDOS Found the Bruise — Then Ten More Buttons
**Reference:** MQ-7.8 and MQ-7.9.  
Plasticity was silent under condition B alone. SHOCK exposed it, but 10 of 13 frozen SHOCK targets could do so; `56393` produced the largest effect.  
**Science:** perturbation-dependent expression was supported; unique-node specificity was not.  
**Lore:** GLaDOS found ten buttons that made the bruise complain.

### 11 — The Wiring Diagram Was Helpful — Until It Wasn’t
**Reference:** MQ-7.10, MQ-7.13, MQ-7.14.  
All exposing SHOCK targets were within 0–2 directed hops of `56393`; all three nulls were 3 hops away. Yet the strongest structurally ranked residual branches later produced 0% causal attenuation.  
**Science:** topology characterized exposure, but static path strength failed to identify residual mediation.  
**Lore:** We found 78,471 backup routes, cut the fanciest ones, and MORTY informed us they were decorative.

### 12 — Follow the Electricity, Not the Pretty Graph
**Reference:** MQ-7.15 dynamic differential trace.  
At g32 only `68045` had synaptic divergence. At g33 it became the only activity-divergent neuron while synaptic divergence fanned into 160 neurons. By g44, 374 neurons had activity divergence and 5,898 had synaptic-input divergence.  
**Science:** dynamic propagation became directly observable.  
**Lore:** GLaDOS stopped reading the wiring diagram and started following the electricity.

### 13 — Looking Busy Is Not the Same as Being Important
**Reference:** `68045 -> 82348` control; MQ-7.15.  
`82348` had the second-largest early synaptic divergence yet its lesion produced exactly 0% attenuation of the final DN-C1 effect.  
**Science:** local divergence magnitude is not causal mediation.  
**Lore:** Placeholder McDoctorate discovered that neurons, like coworkers, can look extremely busy while contributing nothing to the deliverable.

### 14 — Ten First-Wave Neurons, Ten Causal Contributions
**Reference:** MQ-7.16.  
All ten first-wave activity branches produced positive attenuation, ranging from about 3.7% to 33.6%; the `82348` null control remained 0%.  
**Science:** dynamic first-wave activity outperformed static path-strength ranking as a causal candidate selector.  
**Lore:** GLaDOS started interrogating the witnesses who moved first.

### 15 — MORTY’s Ghost Had Routing Tables
**Reference:** MQ-7.17.  
Cumulative removal of the ten first-wave branches attenuated the DN-C1 effect by about 96.5%. Adding `68045 -> 1273` increased attenuation to 99.999972%, leaving a residual fraction of about `2.8e-7`.  
**Science:** distributed but structured mediation was nearly completely reconstructed under the frozen replay.  
**Lore:** We cut one more wire and the haunting became a floating-point rounding error.

### 16 — The Warden Did Not Care
**Reference:** MQ-6 WARDEN containment and all later D6/plasticity experiments.  
WARDEN remained an independent authority boundary. Oracle/D6/plasticity could not grant trading authority, change containment, or rewrite financial policy.  
**Science:** experimental freedom remained separated from financial authority.  
**Lore:** Senator Armstrong kept saying “no” to the budget request.

### 17 — Turning the Knobs Did Not Fix the Ceiling
**Reference:** SQ-04 GLOBAL MODULATION SENSITIVITY.\
Small global changes to spike threshold and membrane time constant produced large, deterministic, directionally ordered changes in retinal and relay activity. Lower threshold or slower membrane decay increased and accelerated relay firing; higher threshold or faster decay suppressed and delayed it. No tested setting produced wider-network spikes.\
**Science:** the frozen runtime is strongly sensitive to global model mechanics, but the wider-network propagation limit was not overcome by the tested excitability and membrane-persistence changes.\
**Lore:** We turned every scientifically permitted knob. MORTY got louder. The rest of the brain still declined the meeting.

### 18 — The Receipts Checked Out
**Reference:** SQ-03B FIND THE DIFFERENCE; SQ-03C CHECK THE RECEIPTS.  
SQ-03B exposed a long-tailed landscape of single-edge counterfactual sensitivities, but its production run used the validated batched execution path. SQ-03C froze 84 upper-tail jobs and 64 low-tail controls, then reran all 148 one at a time through the original scalar `HybridRuntime`. All 148 passed exact A/A replay and all 148 agreed with the SQ-03B metrics under the already-frozen numerical parity contract.  
**Science:** the selected SQ-03B upper-tail localization effects survived independent scalar re-execution; the low-tail controls reproduced as well. This rules out the batched engine as the explanation for the verified upper-tail signal, while remaining a computational replication rather than a biological or population-level statistical result.  
**Lore:** Science accused the batch engine of cooking the books. One hundred forty-eight interrogations later, the machine produced receipts.

## Scientific lessons to keep

- Preregistration beat vibes.
- Nulls are part of the apparatus.
- Voltage, spike, score, and decision effects must remain separate.
- Static anatomy is not dynamic causality.
- Persistent state does not require rewriting the connectome.
- The joke improves when the control is real.

## Achievement seeds emerging from real experiments

These are candidates, not yet the canonical MQ-8 achievement registry: `MISSION FAILED SUCCESSFULLY`, `THE CAKE IS A LIE`, `STATUS EFFECT: SCARRED`, `THE WIRE WAS HAUNTED`, `TEN BUTTONS`, `FOLLOW THE ELECTRICITY`, `LOOKING BUSY`, `ROUTING TABLES`, plus future behavioral achievements such as `PAPER HANDS` and `DIAMOND HANDS`.

## Experiment reference index

- `CHARTER.md`; `ROADMAP.md`
- `docs/experiments/mq4-acceptance.md`; `docs/neuroscope-guide.md`
- MQ-5 intervention records including the validated `56393 -> 68045 -> 1273` path
- `docs/experiments/mq7-bad-synapse-plasticity-protocol.md`
- `docs/experiments/mq7-credit-assignment-protocol.md`
- `docs/experiments/mq7-live-plasticity-activation-protocol.md`
- `docs/experiments/mq7-adaptive-oracle-experiment-protocol.md`
- `docs/experiments/mq7-adaptive-activation-replication-protocol.md`
- `docs/experiments/mq7-adaptive-activation-replication-results.md`
- `docs/experiments/mq7-full-d6-integration-smoke-results.md`
- `docs/experiments/mq7-full-d6-multisession-protocol.md`
- `docs/experiments/mq7-8-shock-plasticity-interaction-protocol.md`
- `docs/experiments/mq7-8-shock-plasticity-interaction-results.md`
- `docs/experiments/mq7-9-shock-target-specificity-protocol.md`
- `docs/experiments/mq7-10-recruitment-topology-protocol.md`
- `docs/experiments/mq7-11-causal-route-ablation-protocol.md`
- `docs/experiments/mq7-12-downstream-mediation-protocol.md`
- `docs/experiments/mq7-13-residual-route-discovery-protocol.md`
- `docs/experiments/mq7-14-residual-branch-mediation-protocol.md`
- `docs/experiments/mq7-15-differential-trace-protocol.md`
- `docs/experiments/mq7-16-first-wave-causal-screen-protocol.md`
- `docs/experiments/mq7-17-cumulative-first-wave-mediation-protocol.md`
- `docs/experiments/mq7-17-cumulative-first-wave-mediation-results.md`
- `docs/experiments/sq04-global-modulation-protocol.md`
- `docs/experiments/sq04-global-modulation-results.md`
- `docs/experiments/sq03b-mechanistic-localization-protocol.md`
- `docs/experiments/sq03b-mechanistic-localization-results.md`
- `docs/experiments/sq03c-scalar-verification-protocol.md`
- `docs/experiments/sq03c-scalar-verification-results.md`

## Closing note

MoscaQuant is still deliberately ridiculous. But the strongest part of the project is no longer the premise. It is the discipline with which the premise has been constrained: frozen baselines, matched controls, replayable state, null-preserving protocols, structural immutability, dynamic tracing, and causal ablation. The humor works because the experiment is allowed to embarrass the story.

> Final management comment: **THIS WAS SUPPOSED TO BE FUNNY.**


## MQ-7.18 / MQ-7.19 — THE ROUTES STARTED COVERING FOR EACH OTHER

A community question about whether downstream routes might partially
compensate for one another reopened the otherwise closed MQ-7 causal-pathway
analysis.

MQ-7.18 tested all 45 unique pairs among the ten frozen first-wave branches
against an independent-residual null rather than assuming that single-branch
effects combine independently.

The strongest pair, `62598 + 77298`, produced approximately **+1.96 percentage
points** of supra-independent interaction excess. Validated null-edge pair
controls produced **0.0** interaction excess.

MQ-7.19 then froze the three strongest MQ-7.18 pairs and asked the stricter
conditional question: does each branch explain more of the residual effect
when its partner is absent?

Across all three pairs, the answer was yes in both directions. Null controls
again produced **0.0** conditional gain.

**Scientific interpretation:** the frozen model supports structured pairwise
interaction and conditional compensation-like dependence.

**Boundary:** this does not establish biological compensation, rewiring,
learning, or living-fly adaptation.

The causal-pathway line was reclosed after MQ-7.19. No blind triple or
higher-order combinatorial fishing expedition is authorized without a new
independent hypothesis.

Approved internal historical footnote: the detour began with a useful Reddit
question shortly before the project's separately nicknamed
**"r/quant neckbeards problem."**

### 19 — Structure Is Not Destiny

**Reference:** SQ-03E — STRUCTURE IS NOT DESTINY

**Science:** Across 114,825 matched candidate edges, structural
male/female weight difference was only weakly associated with modeled dynamic
consequence (`rho≈0.061` for `S`,
`rho≈0.050` for `C`). Frozen top-1%
structural/dynamic overlap was only 188 edges for `S` and
184 for `C`.

**Lore:** The wiring diagram arrived with a résumé. The runtime checked its references.

