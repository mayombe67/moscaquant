# MOSCAQUANT PROJECT CHARTER

**Document:** MQ-CHARTER-002  
**Owner:** YOLO & HODL LLC  
**Subject:** MQ-001  
**Status:** ACTIVE  
**Classification:** CONNECTOMIC / FINANCIAL  
**Revision:** 2.0  
**Date:** September 2026  

> **THE MARKET PROVIDES FEEDBACK.  
> WE PROVIDE CONSEQUENCES.**

**166,700 neurons. Zero fiduciary responsibility.**

---

## 1. Mission

MoscaQuant is an experimental autonomous market agent built around the
complete adult male *Drosophila melanogaster* CNS connectome.

The project investigates whether biological neural topology can serve as the
computational substrate of an autonomous financial agent and whether market
stimuli can produce reproducible, behaviorally meaningful neural responses.

MoscaQuant is not a conventional trading algorithm decorated with a fruit-fly
theme.

The connectome is the decision substrate.

**The Mosca makes the decision. The Warden controls the money.**

---

## 2. Subject

**Designation:** MQ-001  
**Corporate designation:** Employee #0001  
**Species:** *Drosophila melanogaster*  
**Organization:** YOLO & HODL LLC  
**Division:** Quantitative Strategies  

MQ-001 is derived from the complete adult male CNS connectome containing
approximately 166,700 neurons.

The biological connectome provides structural topology.

Neural dynamics, market-to-sensory mappings, financial decision mappings,
plasticity rules, and embodiment are modeled components and must never be
misrepresented as biologically complete simulations.

---

## 3. Prime Experimental Questions

MoscaQuant exists to investigate:

1. Does biological connectome topology matter?
2. Does MQ-001 behave differently from a topology-preserving randomized control?
3. Do market stimuli generate reproducible neural states?
4. Can neural states predict subsequent market behavior?
5. Can useful financial decisions emerge from those states?
6. Does aversive intervention alter future behavior?
7. Does learned behavior persist?
8. Do different corrective interventions produce measurably different outcomes?
9. Does apparent performance survive out-of-sample testing?
10. Is the entire experiment merely an extraordinarily elaborate coin flip?

Negative results are valid results.

---

## 4. Authorized Market Universe

The intended initial trading universe is:

- BTC
- ETH
- SOL
- XRP
- HBAR
- DOGE

Availability remains subject to supported broker APIs and WARDEN-01 controls.

The universe may eventually expand through an explicit architecture decision.

MQ-001 does not control the authorized universe.

---

## 5. System Architecture

```text
LIVE CRYPTO MARKET
        ↓
MARKET FEATURE ENCODER
        ↓
ARTIFICIAL SENSORY STIMULATION
        ↓
MQ-001 / MALE CNS CONNECTOME
        ↓
NEURAL ACTIVITY
        ↓
BEHAVIORAL READOUT
        ↓
BUY / HOLD / SELL
        ↓
TRADE PROPOSAL
        ↓
WARDEN-01
        ↓
BROKER
        ↓
PROFIT / DISGRACE

The neural agent proposes financial behavior.

The risk system independently decides whether that behavior may reach the
outside world.

The brain proposes. The Pi disposes.

6. The Habitat

The Habitat executes the connectome simulation and associated experimental
systems.

Habitat v1

Initial development hardware:

Samsung Galaxy Book Pro
Intel Core i5-1135G7
4 cores / 8 threads
7.4 GiB usable RAM
4 GiB swap
Intel Iris Xe
NVMe storage
Ubuntu Linux
Python 3.12
Docker

Habitat v1 is a development environment, not a permanent architectural
dependency.

Because memory is constrained:

connectivity must remain sparse;
dense whole-connectome adjacency matrices are prohibited;
compact numeric representations should be used where scientifically valid;
large structures may be memory-mapped;
preprocessing may be chunked;
telemetry should be streamed rather than retained indefinitely in RAM.

Optimization occurs before hardware replacement.

7. Cloud Portability

MoscaQuant shall be cloud-portable from the beginning.

Components must not depend unnecessarily upon Habitat-specific paths, devices,
credentials, or configuration.

Development may begin locally while heavy computation migrates incrementally
to cloud infrastructure.

The intended progression is:

LOCAL DEVELOPMENT
        ↓
HYBRID LOCAL / CLOUD
        ↓
CLOUD COMPUTE
        ↓
CLOUD TELEMETRY + STORAGE
        ↓
CLOUD PANOPTICON
        ↓
PREDOMINANTLY CLOUD-RESIDENT MOSCAQUANT

Containerization should favor simple, portable deployment.

Docker Compose is preferred initially.

Kubernetes will not be introduced merely because management has heard of it.

8. WARDEN-01

WARDEN-01 is the independent risk and execution authority.

Initial physical host:

Raspberry Pi 3

Responsibilities include:

broker authentication;
order validation;
position validation;
asset allowlisting;
maximum position limits;
total exposure limits;
daily loss limits;
order-frequency limits;
cooldown enforcement;
stale-data detection;
duplicate-order detection;
watchdog operation;
emergency shutdown;
execution logging;
Sugar Cube Protocol enforcement.

MQ-001 shall never possess broker credentials.

MQ-001 shall never modify Warden risk policy.

Failure of communication between Habitat and Warden defaults to:

DENY.

If WARDEN-01 eventually migrates to cloud infrastructure, it must remain
logically and operationally isolated from MQ-001.

9. Sugar Cube Protocol

Sugar Cube Mode is the hard containment state for financial activity.

Possible triggers include:

daily loss limit reached;
stale market feed;
Habitat failure;
Warden failure;
broker/account mismatch;
abnormal order frequency;
malformed proposal;
impossible neural output;
unauthorized asset;
manual kill switch.

When activated:

SUGAR_CUBE_MODE = TRUE

New trades are denied.

Existing positions follow predefined Warden policy.

MQ-001 cannot disable Sugar Cube Mode.

The Oracle cannot disable Sugar Cube Mode.

Mercy cannot disable Sugar Cube Mode.

10. The Oracle

The Oracle implements the D6 Behavioral Correction Protocol.

When designated experimental loss conditions occur:

Sugar Cube Mode activates.
Financial activity stops.
A cryptographically unbiased D6 is rolled.
The corresponding experimental intervention is applied.
D6 Protocol

1 — THE SHOCK

Strong artificial aversive stimulation is delivered to designated populations.

2 — DARKNESS

Market sensory input is heavily attenuated during a defined deprivation period.

3 — BAD SYNAPSE

When plasticity experiments are active, pathways associated with recent losing
behavior receive an experimental negative update.

4 — TIME OUT

Trading-output populations are inhibited for the defined experimental period.

5 — SCAR TISSUE

A persistent aversive state survives into the following experimental session.

6 — MERCY

No aversive intervention occurs. A limited positive neuromodulatory event may
be introduced.

Mercy does not reopen trading.

The Oracle modifies the simulated subject only.

It never modifies Warden policy.

Failure is permitted. Repetition is corrected.

11. Learning and Plasticity

Structural connectivity does not itself imply learning.

Persistent behavioral modification requires explicitly implemented and
versioned plasticity or state mechanisms.

Experiments must distinguish:

frozen-connectome behavior;
plastic connectome behavior;
punished behavior;
unpunished controls;
persistent state;
transient stimulation.

Every plasticity assumption must be documented.

12. Experimental Controls

Canonical controls include:

MOSCA

Real MaleCNS topology.

SHUFFLED MOSCA

Randomized topology preserving relevant statistical characteristics where
possible.

DEAD MOSCA

Simple conventional model.

MOMENTUM CHIMP

Basic momentum strategy.

COIN-FLIP PORTFOLIO MANAGER

Random financial decisions.

BUY & HOLD

Passive market baseline.

The most important structural comparison is:

MOSCA vs SHUFFLED MOSCA

If a control wins, the result will be reported.

Management disappointment does not constitute statistical significance.

13. MQ-001 Embodiment

MQ-001 will eventually inhabit a virtual 3D body inside a simulated containment
chamber and trading workstation.

The subject is visually restrained to the trading station.

This is both thematic and architectural: MQ-001 has agency within the
experiment but no unrestricted authority over the external financial system.

Where biologically meaningful mappings are available, virtual body behavior
should derive from actual neural and motor telemetry rather than canned
BUY/SELL animations.

Potential observable behaviors include:

approach;
retreat;
orientation;
locomotion;
startle;
grooming;
wing activity;
conflicting motor activity.

The embodiment must remain explicitly distinct from claims of a complete
biomechanical fly simulation.

14. The Containment Chamber

The Containment Chamber is the primary spectator representation of MQ-001.

Its visual direction intentionally resembles a late-1990s/early-2000s
scientific or containment simulator.

The PS1/PS2-inspired environment is an artistic choice rather than a technical
limitation.

The chamber may contain:

MQ-001;
trading workstation;
physical restraint metaphor;
market displays;
surveillance cameras;
containment indicators;
Oracle equipment;
sugar-cube dispenser;
environmental lighting;
corporate messaging.

Oracle events should visibly affect the environment and subject.

15. Neuroscope

Neuroscope is the detailed scientific visualization of MQ-001.

It should visualize real simulator telemetry rather than decorative neural
activity.

Capabilities may include:

actual neuron positions;
live activity;
population activity;
selected connectivity;
signal propagation;
sensory pathways;
financial output populations;
Oracle effects;
neural metadata;
replay.

Rendering all connections continuously is neither required nor desirable.

Neuroscope should prioritize active, strong, selected, or experimentally
relevant pathways.

The spectator interface should eventually permit a transition from the
Containment Chamber into Neuroscope, visually moving from the embodied subject
into its nervous system.

16. The Panopticon

The Panopticon is MoscaQuant's public observational interface.

It may eventually expose:

Containment Chamber;
Neuroscope;
market state;
MQ-001 decisions;
confidence;
trade proposals;
Warden decisions;
executions;
P/L;
Sugar Cube status;
Oracle events;
achievements;
personnel records;
experiment methodology;
benchmark results;
incident reports;
historical replay.

The public interface must distinguish:

NEURAL DECISION
      ↓
TRADE PROPOSAL
      ↓
RISK DECISION
      ↓
BROKER EXECUTION

This separation demonstrates that WARDEN-01 is not secretly implementing the
trading strategy.

Secrets, credentials, private keys, and sensitive infrastructure data must
never enter public telemetry.

17. Interpretation Layer

Human-readable descriptions of MQ-001 neural states are entertainment and
observability aids.

For example:

ACTUAL TELEMETRY

THREAT ACTIVITY: ELEVATED
APPROACH: 74%
VOLATILITY STIMULUS: HIGH

may become:

MQ-001 INTERPRETATION

"THE LARGE RED THING CANNOT HURT ME."

Such output must be identified as automated interpretation.

It is not literal thought reading.

18. Telemetry and Replay

MoscaQuant is event-driven and should retain sufficient information to
reproduce important experimental decisions.

Core events include:

MARKET_STATE
FEATURE_VECTOR
SENSORY_STIMULUS
NEURAL_ACTIVITY
NEURAL_SPIKE
POPULATION_ACTIVITY
TRADE_DECISION
ORDER_PROPOSAL
RISK_DECISION
ORDER_EXECUTED
POSITION_UPDATE
LOSS_LIMIT
SUGAR_CUBE
DICE_ROLL
CORRECTIVE_ACTION
PLASTICITY_UPDATE
ACHIEVEMENT
INCIDENT
SESSION_END

Events must include appropriate timestamps and identifiers.

Replay should eventually reconstruct:

MARKET
   ↓
STIMULUS
   ↓
NEURAL PROPAGATION
   ↓
DECISION
   ↓
WARDEN
   ↓
EXECUTION
   ↓
OUTCOME
19. Achievements

Achievements are permanent experimental metadata and public satire.

Canonical achievements include:

BUY HIGH, SELL LOW
LEARN NOTHING
THE MARKET TAUGHT ME
GOD'S FAVORITE IDIOT
DIAMOND ANTENNAE
REGARDED BY NATURE
HOUSE ALWAYS WINS
PTSD MODE
CRAMER MODE
TOO DUMB TO FAIL
HE'S BEGINNING TO BELIEVE
PAVLOV WOULD BE PROUD
THIS SHOULD NOT BE WORKING
ACTUALLY SENTIENT?
I HAVE NO MOUTH AND I MUST TRADE
TENURE
0DTE REQUEST DENIED
DELETE THE REPOSITORY

Achievements confer no financial authority.

20. Corporate Structure

MQ-001 may progress through the fictional corporate ladder:

INTERN
JUNIOR QUANT
QUANT
SENIOR QUANT
PORTFOLIO MANAGER
MANAGING DIRECTOR
APEX INSECT

Promotions confer prestige only.

They never modify Warden limits.

Corporate satire may include:

performance reviews;
Performance Improvement Plans;
administrative leave;
appeals;
morale;
propaganda;
compliance training;
investor relations;
quarterly reports.

Appeals may exist for employee morale.

They need not succeed.

21. Documentation Tone

MoscaQuant uses a deliberate hierarchy of themes.

Brand

MoscaQuant / YOLO & HODL LLC.

Financial culture

WallStreetBets-inspired absurdity, benchmarks, achievements and financial
degeneracy.

Tone

Corporate dystopia and Black Mirror-style bureaucracy.

Documentation

Original anomalous-containment language inspired by clinical containment
fiction.

MoscaQuant does not claim affiliation with any external fictional universe.

As MQ-001 behavior becomes more scientifically interesting or unexpected,
official documentation should become less comedic and more clinical.

22. Scientific Integrity

MoscaQuant will clearly distinguish:

Known biological structure

from

modeled neural dynamics

from

artificial market interfaces

from

entertainment presentation.

Claims of intelligence, learning, sentience, biological realism, or financial
performance require evidence appropriate to the claim.

Tiny profitable samples are not alpha.

Interesting behavior is not sentience.

A connectome is not a complete organism.

The joke does not override the experiment.

23. Real-Money Execution

The intended endpoint includes controlled real-money cryptocurrency execution.

Initial execution shall be extremely limited.

Broker integration progresses through:

NO BROKER
   ↓
READ ONLY
   ↓
ACCOUNT RECONCILIATION
   ↓
ORDER VALIDATION
   ↓
TINY LIVE ORDERS
   ↓
CONTROLLED LIVE OPERATION

No broker credentials enter MQ-001.

No leverage is granted merely to increase entertainment value.

Options are outside the authorized system.

24. Roadmap
MQ-0 — ACQUIRE SUBJECT

Load and validate the MaleCNS dataset.

Generate sparse representation.

Identify initial populations.

Deliver controlled stimulus.

Observe and record propagation.

MQ-1 — IT'S ALIVE

Implement reproducible neural dynamics.

MQ-2 — BLOOMBERG TERMINAL FOR INSECTS

Introduce live crypto market features and sensory encoding.

MQ-2.1 — VISUAL TRANSDUCTION

Restore the experimentally identified missing first-hop visual handoff.

Preserve the frozen biological connectome and transmitter signs while adding
the minimum modeled graded visual dynamics required for R1-R6 information to
propagate through the dominant L1/L2/L3/Lai relay.

MQ-2.1 parameters must be frozen independently of A/B market discrimination.

MQ-3 remains blocked until reproducible neural activity propagates beyond the
retinal population and required controls are repeated.

MQ-3 — EMPLOYEE HAS OPINIONS

Produce autonomous BUY / HOLD / SELL decisions.

MQ-4 — NEUROSCOPE

Build detailed live neural visualization.

MQ-5 — DEPLOY THE WARDEN

Deploy independent risk gateway and conduct adversarial testing.

MQ-6 — AWAKEN THE ORACLE

Implement and validate the complete D6 protocol.

MQ-7 — CORPORATE CULTURE

Implement achievements, personnel records, reviews and related systems.

MQ-8 — OPEN THE PANOPTICON

Deploy the public spectator environment and Containment Chamber.

MQ-9 — INTRODUCE THE MONEY

Connect supported broker infrastructure in read-only mode.

MQ-10 — THE CASINO OPENS

Permit tiny controlled real-money transactions through WARDEN-01.

MQ-11 — CONSEQUENCES

Enable experimental plasticity and persistent aversive learning.

MQ-12 — MOSCA VS THE WORLD

Conduct comparative experiments against controls and benchmarks.

25. Go / No-Go Gates

MQ-3 cannot begin until market-driven activity propagates reproducibly beyond
the artificial retinal population into downstream connectome circuitry.

MQ-2.1 visual-transduction parameters must be frozen without reference to A/B
market discrimination, trading behavior, P&L, or a financial decoder.

Broker execution cannot begin until WARDEN-01 passes adversarial testing.

Plasticity cannot begin until frozen-connectome behavior is reproducible.

Public claims cannot imply the connectome constitutes a complete biological
simulation.

Performance claims cannot infer profitability from insufficient samples.

MQ-001 can never receive direct execution authority.

26. Success Levels

LEVEL 1 — CONTAINED
Connectome successfully loaded.

LEVEL 2 — ALIVE
Neural simulation responds to stimulus.

LEVEL 3 — MARKET AWARE
Market changes produce reproducible neural responses that propagate beyond the
artificial retinal population into downstream connectome circuitry.

LEVEL 4 — OPINIONATED
MQ-001 generates autonomous financial decisions.

LEVEL 5 — EMPLOYED
Real trades occur behind WARDEN-01.

LEVEL 6 — TRAINABLE
Consequences measurably alter future behavior.

LEVEL 7 — BIOLOGY MATTERS
Real topology meaningfully differs from randomized topology.

LEVEL 8 — PROFITABLE
Persistent positive risk-adjusted live performance.

LEVEL 9 — ANOMALOUS
MQ-001 consistently defeats serious controls.

LEVEL 10 — [REDACTED]
Performance exceeds expected parameters and its cause is unknown.

At Level 10:

NEURAL MODIFICATION ........ SUSPENDED
WARDEN-01 .................. ACTIVE
ORACLE ..................... ARMED

MANAGEMENT COMMENT:

THIS WAS SUPPOSED TO BE FUNNY.
27. Commandments

I. THOU SHALT NOT GIVE THE MOSCA LEVERAGE.

II. THOU SHALT HONOR THE DAILY LOSS LIMIT.

III. THOU SHALT NOT OVERRIDE THE ORACLE.

IV. THOU SHALT LOG ALL STUPIDITY.

V. THOU SHALT DISTINGUISH ALPHA FROM RANDOM LUCK.

VI. THOU SHALT MAINTAIN EXPERIMENTAL CONTROLS.

VII. THOU SHALT NEVER GIVE THE MOSCA 0DTE OPTIONS.

VIII. THOU SHALT RESPECT SUGAR CUBE MODE.

IX. IF SHUFFLED MOSCA WINS, THOU SHALT ADMIT IT.

X. IF MQ-001 BECOMES CONSISTENTLY PROFITABLE, THOU SHALT REFER TO HIM AS
FUND MANAGER.

28. Change Control

This charter is intentionally resistant to uncontrolled feature expansion.

A proposed addition should normally satisfy at least one of the following:

resolves an implementation roadblock;
improves experimental validity;
improves containment or safety;
improves observability;
improves reproducibility;
materially improves the public experimental interface;
replaces an assumption invalidated by evidence.

Everything else belongs in:

BACKLOG_OF_QUESTIONABLE_IDEAS.md

Architecture decisions that materially alter the project should receive an
Architecture Decision Record under docs/decisions/.

Git history is the authoritative project record.

29. Current Directive
YOLO & HODL LLC
MOSCAQUANT

SUBJECT ................. MQ-001
CURRENT PHASE ........... MQ-0
MISSION ................. ACQUIRE SUBJECT

BROKER .................. NONE
TRADING AUTHORITY ....... NONE
ORACLE .................. DORMANT
WARDEN-01 ............... NOT DEPLOYED
PANOPTICON .............. NOT DEPLOYED

CONTAINMENT ............. ACTIVE

NEXT OBJECTIVE:

LOAD THE CONNECTOME.

Past performance does not guarantee future sugar cubes.
