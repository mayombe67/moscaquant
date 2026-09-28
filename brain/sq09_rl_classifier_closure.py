from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SQ07_SEAL = (
    ROOT
    / "artifacts/experiments/"
    "sq07-the-maw-result-seal-v1.json"
)

LOWER_ORDER = (
    ROOT
    / "artifacts/experiments/"
    "sq09-pattern-screamer/"
    "sq09-pattern-screamer-lower-order-presence-v1.json"
)

SUPPORT = (
    ROOT
    / "artifacts/experiments/"
    "sq09-pattern-screamer/"
    "sq09-pattern-screamer-support-audit-v1.json"
)

SQ06_RUNNER = (
    ROOT
    / "brain/"
    "sq06_silent_cartographer_runner.py"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq09-pattern-screamer/"
    "sq09-pattern-screamer-rl-classifier-closure-v1.json"
)

EXPECTED_SQ07_ANALYSIS_SHA256 = (
    "2db405151cc8771ccd0c50080bcd6a83"
    "ca3824e5487c666d22e01db8bed6d80c"
)

EXPECTED_SQ08_EVIDENCE_SHA256 = (
    "e95f054e827cf1232ef72019692e4bcfc"
    "099214a654e1a3267f0f41cfc66abfb"
)

EXPECTED_NODES = {
    "A": 137122,
    "B": 317,
    "C": 126002,
}

EXPECTED_MAIN_TERMS = {
    "A": "M_A",
    "B": "M_B",
    "C": "M_C",
}

INTERACTION_TERMS = (
    "I_AB",
    "I_AC",
    "I_BC",
    "I_ABC",
)

MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)


class ClosureAuditError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ClosureAuditError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing required artifact: {path}")

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def python_numeric_constant(
    path: Path,
    name: str,
) -> float:
    tree = ast.parse(
        path.read_text(encoding="utf-8"),
        filename=str(path),
    )

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        if len(node.targets) != 1:
            continue

        target = node.targets[0]

        if not isinstance(target, ast.Name):
            continue

        if target.id != name:
            continue

        value = ast.literal_eval(node.value)

        if not isinstance(value, (int, float)):
            fail(
                f"{name} is not numeric"
            )

        return float(value)

    fail(
        f"unable to locate frozen constant {name}"
    )


def verify_repository_clean() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        fail(
            "git status failed:\n"
            + result.stdout
        )

    if result.stdout.strip():
        fail(
            "classifier closure publication "
            "requires a clean worktree"
        )

    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def verify_sq07_seal(
    seal: dict,
) -> dict:
    if (
        seal.get("schema_version")
        != "moscaquant.sq07-the-maw-result-seal.v1"
    ):
        fail("SQ-07 result seal schema drift")

    experiment = seal.get("experiment", {})

    if experiment.get("id") != "SQ-07":
        fail("SQ-07 result seal experiment drift")

    if experiment.get("codename") != "THE MAW":
        fail("SQ-07 codename drift")

    if experiment.get("status") != "SEALED_RESULT":
        fail("SQ-07 result is not sealed")

    analysis = seal.get(
        "authoritative_analysis",
        {}
    )

    if (
        analysis.get("sha256")
        != EXPECTED_SQ07_ANALYSIS_SHA256
    ):
        fail(
            "SQ-07 authoritative analysis SHA drift"
        )

    result = seal.get("result", {})

    minimal = result.get(
        "minimal_full13_recapitulators",
        {},
    ).get("RL")

    if minimal != [
        {
            "active_group_only": True,
            "hamming_weight": 3,
            "mask13": "0000000000111",
            "mixed_group": False,
        }
    ]:
        fail(
            "SQ-07 RL minimal FULL13 "
            "recapitulator drift"
        )

    counts = result.get(
        "class_counts",
        {},
    ).get("RL")

    if counts != {
        "EXACT_FULL13": 1024,
        "EXACT_INTACT": 1024,
        "INTERMEDIATE": 6144,
    }:
        fail(
            "SQ-07 RL class counts drift"
        )

    if (
        result.get(
            "minimum_meaningful_effect_floor"
        )
        != "NOT_DEFINED"
    ):
        fail(
            "SQ-07 meaningful-effect-floor drift"
        )

    return {
        "unique_minimal_rl_full13_mask":
            "0000000000111",
        "class_counts": counts,
        "minimum_meaningful_effect_floor":
            "NOT_DEFINED",
    }


def verify_sq09_inputs(
    lower: dict,
    support: dict,
) -> dict:
    if (
        lower.get("schema_version")
        != (
            "moscaquant."
            "sq09-pattern-screamer-"
            "lower-order-presence/v1"
        )
    ):
        fail(
            "SQ-09 lower-order schema drift"
        )

    if (
        support.get("schema_version")
        != (
            "moscaquant."
            "sq09-pattern-screamer-"
            "support-audit/v1"
        )
    ):
        fail(
            "SQ-09 support schema drift"
        )

    if (
        lower.get("source_npz_sha256")
        != EXPECTED_SQ08_EVIDENCE_SHA256
    ):
        fail(
            "SQ-09 lower-order source evidence drift"
        )

    if (
        support.get("source_npz_sha256")
        != EXPECTED_SQ08_EVIDENCE_SHA256
    ):
        fail(
            "SQ-09 support source evidence drift"
        )

    if lower.get("mask_semantics") != (
        "0=retained,1=zeroed"
    ):
        fail(
            "SQ-09 mask semantics drift"
        )

    primary = lower.get(
        "regions",
        {},
    ).get("primary")

    if not isinstance(primary, dict):
        fail(
            "SQ-09 primary lower-order region missing"
        )

    for term in INTERACTION_TERMS:
        row = primary.get(term)

        if not isinstance(row, dict):
            fail(
                f"missing interaction term {term}"
            )

        if row.get("literal_zero") is not True:
            fail(
                f"{term} is no longer literal zero"
            )

        if row.get("literal_nonzero_count") != 0:
            fail(
                f"{term} nonzero-count drift"
            )

        if float(row.get("max_abs")) != 0.0:
            fail(
                f"{term} max-abs drift"
            )

    terms = support.get("terms")

    if not isinstance(terms, dict):
        fail(
            "SQ-09 support terms missing"
        )

    effects = {}

    for edge, term in EXPECTED_MAIN_TERMS.items():
        lower_term = primary.get(term)
        support_term = terms.get(term)

        if not isinstance(lower_term, dict):
            fail(
                f"missing lower-order term {term}"
            )

        if lower_term.get("literal_zero") is not False:
            fail(
                f"{term} unexpectedly zero"
            )

        if not isinstance(support_term, dict):
            fail(
                f"missing support term {term}"
            )

        expected_node = EXPECTED_NODES[edge]

        if (
            support_term.get(
                "changed_primary_column_count"
            )
            != 1
        ):
            fail(
                f"{term} support is not single-column"
            )

        if (
            support_term.get(
                "changed_primary_nodes"
            )
            != [expected_node]
        ):
            fail(
                f"{term} responder identity drift"
            )

        if (
            support_term.get(
                "nonzero_values_outside_body_responders"
            )
            != 0
        ):
            fail(
                f"{term} has support outside BODY responders"
            )

        if (
            support_term.get(
                "body_effect_equals_primary_slice"
            )
            is not True
        ):
            fail(
                f"{term} BODY/primary support mismatch"
            )

        effects[edge] = {
            "term": term,
            "responder": expected_node,
            "first_nonzero_frame":
                lower_term.get(
                    "first_nonzero_frame"
                ),
            "max_abs": float(
                lower_term["max_abs"]
            ),
            "literal_nonzero_count": int(
                lower_term[
                    "literal_nonzero_count"
                ]
            ),
        }

    if len({
        row["responder"]
        for row in effects.values()
    }) != 3:
        fail(
            "BODY main-effect supports are not disjoint"
        )

    return {
        "effects": effects,
        "pairwise_interactions_literal_zero":
            True,
        "three_way_interaction_literal_zero":
            True,
        "supports_disjoint":
            True,
        "responder_identity_status":
            "INHERITED_FROM_FROZEN_EDGE_REGISTRY",
        "new_support_finding":
            (
                "each preserved primary main effect is "
                "confined to its inherited responder"
            ),
    }


def strict_submask_report(
    effects: dict,
    max_abs_tolerance: float,
) -> list[dict]:
    rows = []

    edge_order = ("A", "B", "C")

    for mask in MASKS:
        if mask == "111":
            continue

        omitted = [
            edge
            for edge, bit
            in zip(edge_order, mask)
            if bit == "0"
        ]

        if not omitted:
            fail(
                f"strict submask {mask} omitted no BODY terms"
            )

        #
        # With all pair/triple terms exactly zero and
        # main-effect supports confined to distinct
        # responder columns, Y111 - Ymask is the sum
        # of omitted main effects on disjoint supports.
        #
        # Therefore its max-absolute difference is
        # exactly the largest max-absolute main effect
        # among the omitted terms.
        #
        closed_form_max_abs = max(
            effects[edge]["max_abs"]
            for edge in omitted
        )

        margin = (
            closed_form_max_abs
            / max_abs_tolerance
        )

        rows.append({
            "mask": mask,
            "omitted_body_terms": omitted,
            "closed_form_max_abs_to_full111":
                closed_form_max_abs,
            "sq07_max_abs_tolerance":
                max_abs_tolerance,
            "tolerance_exceedance_factor":
                margin,
            "passes_sq07_max_abs_gate":
                closed_form_max_abs
                <= max_abs_tolerance,
            "exact_full13_excluded_by_max_abs_gate":
                closed_form_max_abs
                > max_abs_tolerance,
        })

    return rows


def build_report() -> dict:
    seal = load_json(SQ07_SEAL)
    lower = load_json(LOWER_ORDER)
    support = load_json(SUPPORT)

    sq07 = verify_sq07_seal(seal)

    sq09 = verify_sq09_inputs(
        lower,
        support,
    )

    primary_l2_tol = (
        python_numeric_constant(
            SQ06_RUNNER,
            "PRIMARY_L2_TOL",
        )
    )

    primary_max_abs_tol = (
        python_numeric_constant(
            SQ06_RUNNER,
            "PRIMARY_MAX_ABS_TOL",
        )
    )

    if primary_l2_tol != 1e-9:
        fail(
            "frozen SQ-07 L2 tolerance drift"
        )

    if primary_max_abs_tol != 1e-12:
        fail(
            "frozen SQ-07 max-abs tolerance drift"
        )

    rows = strict_submask_report(
        sq09["effects"],
        primary_max_abs_tol,
    )

    if len(rows) != 7:
        fail(
            "expected seven strict RL submasks"
        )

    if not all(
        row[
            "exact_full13_excluded_by_max_abs_gate"
        ]
        for row in rows
    ):
        fail(
            "one or more strict RL submasks "
            "not excluded from EXACT_FULL13"
        )

    smallest_effect = min(
        sq09["effects"].items(),
        key=lambda item: item[1]["max_abs"],
    )

    minimum_margin = min(
        row["tolerance_exceedance_factor"]
        for row in rows
    )

    return {
        "schema_version":
            (
                "moscaquant."
                "sq09-rl-classifier-closure/v1"
            ),
        "status":
            "RL_CLASSIFIER_CLOSURE_COMPLETE",
        "experiment_context": [
            "SQ-07 — THE MAW",
            "SQ-08 — THREE BODY PROBLEM",
            "SQ-09 — PATTERN SCREAMER",
        ],
        "audit_type":
            "RETROSPECTIVE_CLOSED_FORM_ONLY",
        "neural_execution_performed":
            False,
        "source_artifacts": {
            "sq07_result_seal": {
                "path":
                    str(
                        SQ07_SEAL.relative_to(ROOT)
                    ),
                "sha256":
                    sha256_file(SQ07_SEAL),
                "authoritative_analysis_sha256":
                    EXPECTED_SQ07_ANALYSIS_SHA256,
            },
            "sq09_lower_order_presence": {
                "path":
                    str(
                        LOWER_ORDER.relative_to(ROOT)
                    ),
                "sha256":
                    sha256_file(LOWER_ORDER),
            },
            "sq09_support_audit": {
                "path":
                    str(
                        SUPPORT.relative_to(ROOT)
                    ),
                "sha256":
                    sha256_file(SUPPORT),
            },
            "sq06_classifier_source": {
                "path":
                    str(
                        SQ06_RUNNER.relative_to(ROOT)
                    ),
                "sha256":
                    sha256_file(SQ06_RUNNER),
            },
            "sq08_evidence_sha256":
                EXPECTED_SQ08_EVIDENCE_SHA256,
        },
        "sq07_classifier": {
            "symmetric_normalized_l2_max":
                primary_l2_tol,
            "max_abs_difference_max":
                primary_max_abs_tol,
            "gate_semantics":
                (
                    "EXACT_FULL13 requires both "
                    "normalized-L2 and max-absolute "
                    "thresholds to pass"
                ),
            **sq07,
        },
        "sq09_decomposition": sq09,
        "strict_rl_submasks": rows,
        "smallest_main_effect": {
            "body": smallest_effect[0],
            **smallest_effect[1],
            "max_abs_tolerance_exceedance_factor":
                (
                    smallest_effect[1]["max_abs"]
                    / primary_max_abs_tol
                ),
        },
        "minimum_strict_submask_tolerance_exceedance_factor":
            minimum_margin,
        "result": {
            "strict_rl_submask_count": 7,
            "strict_rl_submasks_excluded_from_exact_full13":
                7,
            "all_strict_rl_submasks_excluded":
                True,
            "exclusion_gate":
                "SQ07_MAX_ABS",
            "interaction_required_to_explain_minimality":
                False,
            "closed_form_explanation":
                (
                    "With pairwise and three-way "
                    "interaction terms exactly zero and "
                    "the three main effects confined to "
                    "distinct inherited responder columns, "
                    "any strict submask of 111 omits at "
                    "least one nonzero local contribution. "
                    "Even the smallest omitted contribution "
                    "exceeds SQ-07's frozen max-absolute "
                    "EXACT_FULL13 tolerance."
                ),
            "canonical_short_form":
                "BOOKKEEPING_NOT_TEAMWORK",
        },
        "claim_boundary": (
            "retrospective computational classifier "
            "closure only; responder identities were "
            "inherited, not discovered here; no new "
            "biological, behavioral, or neural-execution "
            "claim"
        ),
    }


def publish_atomic(
    report: dict,
) -> str:
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT.exists():
        fail(
            "classifier closure artifact "
            "already exists"
        )

    payload = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    fd, tmp_name = tempfile.mkstemp(
        prefix=".sq09-rl-closure-",
        suffix=".tmp",
        dir=OUTPUT.parent,
    )

    tmp = Path(tmp_name)

    try:
        with os.fdopen(
            fd,
            "wb",
        ) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.link(
            tmp,
            OUTPUT,
        )

        dir_fd = os.open(
            OUTPUT.parent,
            os.O_RDONLY,
        )

        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    finally:
        tmp.unlink(
            missing_ok=True
        )

    return sha256_file(
        OUTPUT
    )


def main() -> None:
    head = verify_repository_clean()

    report = build_report()

    report["analysis_git_sha"] = head

    artifact_sha = publish_atomic(
        report
    )

    print(
        "SQ-09 RL CLASSIFIER CLOSURE COMPLETE"
    )

    print(
        "strict RL submasks:",
        report["result"][
            "strict_rl_submask_count"
        ],
    )

    print(
        "excluded from EXACT_FULL13:",
        report["result"][
            "strict_rl_submasks_excluded_from_exact_full13"
        ],
    )

    smallest = report[
        "smallest_main_effect"
    ]

    print(
        "smallest omitted main effect:",
        smallest["body"],
        smallest["max_abs"],
    )

    print(
        "minimum tolerance exceedance:",
        report[
            "minimum_strict_submask_tolerance_exceedance_factor"
        ],
    )

    print(
        "neural execution performed:",
        report[
            "neural_execution_performed"
        ],
    )

    print(
        "artifact sha256:",
        artifact_sha,
    )


if __name__ == "__main__":
    main()
