# SQ-08 — THREE BODY PROBLEM — External Review Packet

## Purpose

This directory contains the authoritative preserved evidence for SQ-08 and is
provided for independent external reanalysis.

Reviewers should not assume that the MoscaQuant interpretation is correct.

The preferred review is to independently reconstruct the factorial analysis
from the NPZ and assess whether the reported classification follows from the
frozen contract.

## Frozen science identity

Science Git SHA:

e4a58df478d7681b612ed9deb85b5ddfe1268acc

Experiment:

SQ-08 — THREE BODY PROBLEM

## Evidence

- `sq08-three-body-evidence-v1.npz`
  - authoritative numerical evidence
- `sq08-three-body-evidence-v1.json`
  - evidence manifest
- `sq08-three-body-analysis-v1.json`
  - output of the preregistered MoscaQuant analyzer
- `sq08-three-body-analysis-contract-v1.json`
  - frozen analysis contract
- `sq08-three-body-evidence-schema-v1.json`
  - frozen evidence schema

## Mask semantics

0 = edge retained

1 = edge zeroed

Bit order:

A, B, C

## Frozen factorial definitions

M_A = Y100 - Y000

M_B = Y010 - Y000

M_C = Y001 - Y000

I_AB = Y110 - Y100 - Y010 + Y000

I_AC = Y101 - Y100 - Y001 + Y000

I_BC = Y011 - Y010 - Y001 + Y000

I_ABC =
Y111 - Y110 - Y101 - Y011 + Y100 + Y010 + Y001 - Y000

Pair-complete reconstruction:

Y111_pairwise =
Y000 + M_A + M_B + M_C + I_AB + I_AC + I_BC

Therefore:

Y111 - Y111_pairwise = I_ABC

## Frozen numerical-zero criteria

THREE_WAY_EXACT_ZERO requires both:

- symmetric normalized L2 <= 1e-9
- max absolute difference <= 1e-12

## Reported MoscaQuant result

The preregistered analyzer reported:

- primary: THREE_WAY_EXACT_ZERO
- BODY responders: THREE_WAY_EXACT_ZERO
- 18-node frontier: THREE_WAY_EXACT_ZERO

The purpose of external review is to verify or challenge that result, not
merely reproduce the wording above.

## Questions for external reviewers

1. Does an independent implementation reproduce the eight-condition cube?
2. Are all eight deterministic replicate pairs exactly identical?
3. Does independent calculation reproduce I_ABC?
4. Does Y111 equal the pair-complete reconstruction within the frozen
   numerical criteria?
5. Are the primary, BODY-responder, and frontier classifications correct?
6. Are there numerical, dtype, indexing, mask-semantic, or factorial-sign
   errors?
7. Does the evidence support any stronger claim than the stated computational
   factorial conclusion?
8. What alternative interpretation, if any, is supported by the same evidence?

## Claim boundary

This packet supports computational analysis of the frozen MoscaQuant model.

It does not establish biological behavior, cognition, consciousness,
organism-level necessity, or financial predictive value.

No SQ-09 exploratory analysis is included in this packet.
