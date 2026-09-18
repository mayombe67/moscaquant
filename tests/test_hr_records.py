import pytest

from hr.models import HREvidenceRef, HRRecord
from hr.registry import validate_registry


def test_commendation_requires_evidence():
    record = HRRecord(
        record_id="HR-001",
        subject="GLaDOS",
        action="COMMENDATION",
        issuer="HR",
        title="Productive Interference",
        public_text="GLaDOS has been commended.",
        rationale="Intervention produced a documented result.",
        evidence_refs=(),
    )

    with pytest.raises(ValueError):
        record.validate()


def test_review_may_exist_without_evidence():
    record = HRRecord(
        record_id="HR-002",
        subject="MQ-001",
        action="REVIEW",
        issuer="Placeholder McDoctorate",
        title="Replication Requested",
        public_text="Replication requested.",
        rationale="Generalization remains unestablished.",
        evidence_refs=(),
    )

    record.validate()


def test_evidence_linked_record_validates():
    record = HRRecord(
        record_id="HR-003",
        subject="GLaDOS",
        action="COMMENDATION",
        issuer="HR",
        title="Routing Department",
        public_text="Commendation issued.",
        rationale="The intervention program produced a control-supported causal result.",
        evidence_refs=(
            HREvidenceRef(
                kind="ACHIEVEMENT",
                ref="ACH-003",
                note="ROUTING TABLES",
            ),
        ),
    )

    record.validate()


def test_registry_rejects_duplicate_ids():
    evidence = (
        HREvidenceRef(
            kind="ACHIEVEMENT",
            ref="ACH-002",
        ),
    )

    a = HRRecord(
        record_id="HR-004",
        subject="GLaDOS",
        action="COMMENDATION",
        issuer="HR",
        title="One",
        public_text="One",
        rationale="Evidence-linked.",
        evidence_refs=evidence,
    )

    b = HRRecord(
        record_id="HR-004",
        subject="WARDEN",
        action="COMMENDATION",
        issuer="HR",
        title="Two",
        public_text="Two",
        rationale="Evidence-linked.",
        evidence_refs=evidence,
    )

    with pytest.raises(ValueError):
        validate_registry([a, b])


def test_hr_record_does_not_contain_scientific_authority_fields():
    fields = set(HRRecord.__dataclass_fields__)

    forbidden = {
        "evidence_level_override",
        "scientific_truth",
        "warden_override",
        "experiment_mutation",
    }

    assert not (fields & forbidden)
