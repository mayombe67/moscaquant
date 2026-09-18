"""MQ-8.5B.1 first canonical HR records.

These records are organizational/narrative artifacts tied to documented
MoscaQuant evidence. They do not create scientific authority.
"""

from __future__ import annotations

from .models import HREvidenceRef, HRRecord


CANONICAL_HR_RECORDS = [
    HRRecord(
        record_id="HR-001",
        subject="GLaDOS",
        action="COMMENDATION",
        issuer="HR",
        title="Productive Interference",
        public_text=(
            "GLaDOS is formally commended for producing interpretable "
            "intervention outcomes without exceeding assigned authority."
        ),
        rationale=(
            "The MQ-7 intervention series produced control-supported causal "
            "results and bounded perturbation-dependent plasticity findings "
            "while preserving the separation between ORACLE interpretation "
            "and WARDEN financial containment."
        ),
        evidence_refs=(
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-003",
                note="ROUTING TABLES",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-008",
                note="STEALTH BUILD",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-009",
                note="CRITICAL HIT",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-019",
                note="DIMENSIONAL MERGE",
            ),
        ),
        provenance_class="MANUAL_CANON",
    ),
    HRRecord(
        record_id="HR-002",
        subject="Placeholder McDoctorate",
        action="REVIEW",
        issuer="PANOPTICON",
        title="Replication Requested",
        public_text=(
            "Placeholder McDoctorate acknowledges the current findings and "
            "requests replication before broader generalization."
        ),
        rationale=(
            "MQ-7 produced strong frozen-replay results, but current claim "
            "boundaries explicitly limit generalization beyond the tested "
            "conditions. Scientific review therefore remains active."
        ),
        evidence_refs=(
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-003",
                note="ROUTING TABLES claim boundary",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-020",
                note="99.9999% claim boundary",
            ),
        ),
        provenance_class="MANUAL_CANON",
    ),
    HRRecord(
        record_id="HR-003",
        subject="WARDEN",
        action="COMMENDATION",
        issuer="HR",
        title="Containment Without Negotiation",
        public_text=(
            "WARDEN is commended for maintaining independent financial "
            "containment while the rest of the project became increasingly weird."
        ),
        rationale=(
            "WARDEN remained operationally independent from MORTY and GLaDOS, "
            "preserved hard financial containment, and retained sole authority "
            "over financial execution boundaries."
        ),
        evidence_refs=(
            HREvidenceRef(
                kind="CANON_MILESTONE",
                ref="MQ-6",
                note="DEPLOY THE WARDEN complete",
            ),
            HREvidenceRef(
                kind="CANON_MILESTONE",
                ref="CHARTER:WARDEN-INDEPENDENCE",
                note="The Mosca makes the decision. The Warden controls the money.",
            ),
        ),
        provenance_class="MANUAL_CANON",
    ),
    HRRecord(
        record_id="HR-004",
        subject="MQ-001",
        action="REVIEW",
        issuer="Placeholder McDoctorate",
        title="Performance Review: Subject Remains the Subject",
        public_text=(
            "MQ-001 receives a formal performance review. No promotion, "
            "demotion, or additional authority is granted."
        ),
        rationale=(
            "MQ-001 produced measurable modeled responses across the MQ-7 "
            "intervention series, including valid nulls and perturbation-dependent "
            "effects. The organism model remains an experimental subject and "
            "receives no operational authority from those results."
        ),
        evidence_refs=(
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-001",
                note="MISSION FAILED SUCCESSFULLY",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-004",
                note="TEN BUTTONS",
            ),
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-007",
                note="BOOMERANG NEURON",
            ),
        ),
        provenance_class="MANUAL_CANON",
    ),
]
