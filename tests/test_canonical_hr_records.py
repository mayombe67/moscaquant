import json
from pathlib import Path

from hr.canonical_records_v1 import CANONICAL_HR_RECORDS
from hr.registry import validate_registry


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "hr" / "canonical_records_v1.json"


def test_first_canonical_hr_registry_validates():
    validate_registry(CANONICAL_HR_RECORDS)
    assert len(CANONICAL_HR_RECORDS) == 4


def test_first_canonical_hr_subjects_are_expected():
    subjects = {record.subject for record in CANONICAL_HR_RECORDS}

    assert subjects == {
        "GLaDOS",
        "Placeholder McDoctorate",
        "WARDEN",
        "MQ-001",
    }


def test_no_unearned_promotion_or_demotion():
    actions = {record.record_id: record.action for record in CANONICAL_HR_RECORDS}

    assert "PROMOTION" not in actions.values()
    assert "DEMOTION" not in actions.values()
    assert "PIP" not in actions.values()
    assert "DISCIPLINE" not in actions.values()


def test_consequential_records_have_evidence():
    for record in CANONICAL_HR_RECORDS:
        if record.action == "COMMENDATION":
            assert record.evidence_refs


def test_export_is_public_safe_shape():
    payload = json.loads(EXPORT.read_text())

    assert payload["schema"] == "moscaquant-hr-records/v1"
    assert payload["count"] == 4

    encoded = json.dumps(payload)

    forbidden = {
        "private_runtime_profile",
        "source_event_id",
        "state_hash",
        "previous_occurrence_hash",
        "warden_override",
    }

    for field in forbidden:
        assert field not in encoded
