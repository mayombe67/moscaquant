"""MQ-8.5B evidence-linked HR record model.

HR records are narrative / organizational artifacts.
They may cite scientific evidence but never create scientific evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


HRAction = Literal[
    "COMMENDATION",
    "PROMOTION",
    "DEMOTION",
    "PIP",
    "DISCIPLINE",
    "REVIEW",
]

HRIssuer = Literal[
    "HR",
    "HAHN",
    "Placeholder McDoctorate",
    "GLaDOS",
    "WARDEN",
    "PANOPTICON",
]

EvidenceKind = Literal[
    "ACHIEVEMENT",
    "EXPERIMENT",
    "CONTAINMENT_EVENT",
    "CANON_MILESTONE",
]


@dataclass(frozen=True)
class HREvidenceRef:
    kind: EvidenceKind
    ref: str
    note: str = ""


@dataclass(frozen=True)
class HRRecord:
    record_id: str
    subject: str
    action: HRAction
    issuer: HRIssuer
    title: str
    public_text: str
    rationale: str
    evidence_refs: tuple[HREvidenceRef, ...] = field(default_factory=tuple)
    provenance_class: str = "MANUAL_CANON"
    public: bool = True

    def validate(self) -> None:
        if not self.record_id.startswith("HR-"):
            raise ValueError("HR record_id must start with HR-")

        if not self.subject.strip():
            raise ValueError("HR subject is required")

        if not self.title.strip():
            raise ValueError("HR title is required")

        if not self.rationale.strip():
            raise ValueError("HR rationale is required")

        if self.action in {
            "COMMENDATION",
            "PROMOTION",
            "DEMOTION",
            "PIP",
            "DISCIPLINE",
        } and not self.evidence_refs:
            raise ValueError(
                f"{self.action} requires at least one evidence reference"
            )
