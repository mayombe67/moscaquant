#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "config" / "runtime_parity_acceptance_v1.json"
SCHEMA_VERSION = "moscaquant.runtime_parity/v1"

class AcceptanceError(RuntimeError):
    pass

def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise AcceptanceError(f"{path}: top-level JSON value must be an object")
    return value

def load_profile() -> dict[str, Any]:
    return load_json(PROFILE_PATH)

def normalize_artifact_spec(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise AcceptanceError(f"artifact must be LABEL=PATH, got {spec!r}")
    label, raw_path = spec.split("=", 1)
    label = label.strip()
    if not label:
        raise AcceptanceError("artifact label must not be empty")
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise AcceptanceError(f"artifact does not exist: {path}")
    return label, path

def validate_metrics(metrics: dict[str, Any], profile: dict[str, Any]) -> None:
    dataset_class = metrics.get("dataset_class")
    expected_class = profile["authoritative_dataset_class"]
    if dataset_class != expected_class:
        raise AcceptanceError(f"dataset_class={dataset_class!r}; authoritative fixture requires {expected_class!r}")
    for key, expected in profile["required_invariants"].items():
        observed = metrics.get(key)
        if observed != expected:
            raise AcceptanceError(f"invariant {key}: expected {expected!r}, observed {observed!r}")
    outputs = metrics.get("scientific_outputs")
    if not isinstance(outputs, dict) or not outputs:
        raise AcceptanceError("metrics.scientific_outputs must be a non-empty JSON object")

def digest_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest["schema_version"],
        "acceptance_profile": manifest["acceptance_profile"],
        "source_commit": manifest["source_commit"],
        "dataset_class": manifest["dataset_class"],
        "metrics": manifest["metrics"],
        "artifacts": [
            {"label": a["label"], "sha256": a["sha256"], "size_bytes": a["size_bytes"]}
            for a in sorted(manifest["artifacts"], key=lambda x: x["label"])
        ],
        "scientific_outputs": manifest["scientific_outputs"],
    }

def compute_scientific_digest(manifest: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(digest_payload(manifest)))

def create_manifest(args: argparse.Namespace) -> int:
    profile = load_profile()
    metrics = load_json(Path(args.metrics_json))
    validate_metrics(metrics, profile)
    artifacts, seen = [], set()
    for spec in args.artifact:
        label, path = normalize_artifact_spec(spec)
        if label in seen:
            raise AcceptanceError(f"duplicate artifact label: {label}")
        seen.add(label)
        artifacts.append({"label": label, "path": str(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    if not artifacts:
        raise AcceptanceError("at least one --artifact LABEL=PATH is required")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "acceptance_profile": profile["acceptance_profile"],
        "runtime_profile_id": args.runtime_profile,
        "source_commit": args.source_commit,
        "dataset_class": metrics["dataset_class"],
        "metrics": {key: metrics[key] for key in profile["required_invariants"]},
        "scientific_outputs": metrics["scientific_outputs"],
        "artifacts": sorted(artifacts, key=lambda x: x["label"]),
        "generated_by": "scripts/runtime_parity_v1.py",
    }
    manifest["scientific_digest"] = compute_scientific_digest(manifest)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"WROTE {out}")
    print(f"scientific_digest={manifest['scientific_digest']}")
    return 0

def validate_manifest_obj(manifest: dict[str, Any]) -> None:
    profile = load_profile()
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise AcceptanceError(f"schema_version must be {SCHEMA_VERSION!r}")
    if manifest.get("acceptance_profile") != profile["acceptance_profile"]:
        raise AcceptanceError("acceptance_profile mismatch")
    metrics = dict(manifest.get("metrics") or {})
    metrics["dataset_class"] = manifest.get("dataset_class")
    metrics["scientific_outputs"] = manifest.get("scientific_outputs")
    validate_metrics(metrics, profile)
    if not manifest.get("runtime_profile_id"):
        raise AcceptanceError("runtime_profile_id is required")
    if not manifest.get("source_commit"):
        raise AcceptanceError("source_commit is required")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise AcceptanceError("artifacts must be a non-empty list")
    labels = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise AcceptanceError("artifact records must be objects")
        label = artifact.get("label")
        if not label or label in labels:
            raise AcceptanceError("artifact labels must be unique and non-empty")
        labels.add(label)
        if not isinstance(artifact.get("sha256"), str) or len(artifact["sha256"]) != 64:
            raise AcceptanceError(f"{label}: invalid sha256")
        if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] < 0:
            raise AcceptanceError(f"{label}: invalid size_bytes")
    observed = manifest.get("scientific_digest")
    expected = compute_scientific_digest(manifest)
    if observed != expected:
        raise AcceptanceError(f"scientific_digest mismatch: expected {expected}, observed {observed}")

def validate_command(args: argparse.Namespace) -> int:
    manifest = load_json(Path(args.manifest))
    validate_manifest_obj(manifest)
    print("PASS runtime-parity manifest validation")
    print(f"runtime_profile_id={manifest['runtime_profile_id']}")
    print(f"scientific_digest={manifest['scientific_digest']}")
    return 0

def compare_command(args: argparse.Namespace) -> int:
    baseline = load_json(Path(args.baseline))
    candidate = load_json(Path(args.candidate))
    validate_manifest_obj(baseline)
    validate_manifest_obj(candidate)
    failures = []
    if baseline["source_commit"] != candidate["source_commit"]:
        failures.append(f"source_commit differs: {baseline['source_commit']} != {candidate['source_commit']}")
    if baseline["dataset_class"] != candidate["dataset_class"]:
        failures.append(f"dataset_class differs: {baseline['dataset_class']} != {candidate['dataset_class']}")
    if baseline["scientific_digest"] != candidate["scientific_digest"]:
        failures.append(f"scientific_digest differs: {baseline['scientific_digest']} != {candidate['scientific_digest']}")
    if failures:
        print("FAIL runtime parity")
        print(f"baseline_runtime={baseline['runtime_profile_id']}")
        print(f"candidate_runtime={candidate['runtime_profile_id']}")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS runtime parity")
    print(f"baseline_runtime={baseline['runtime_profile_id']}")
    print(f"candidate_runtime={candidate['runtime_profile_id']}")
    print(f"scientific_digest={baseline['scientific_digest']}")
    return 0

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MoscaQuant Runtime Parity Acceptance v1")
    sub = p.add_subparsers(dest="command", required=True)
    make = sub.add_parser("make")
    make.add_argument("--runtime-profile", required=True)
    make.add_argument("--source-commit", required=True)
    make.add_argument("--metrics-json", required=True)
    make.add_argument("--artifact", action="append", default=[])
    make.add_argument("--output", required=True)
    make.set_defaults(func=create_manifest)
    validate = sub.add_parser("validate")
    validate.add_argument("manifest")
    validate.set_defaults(func=validate_command)
    compare = sub.add_parser("compare")
    compare.add_argument("baseline")
    compare.add_argument("candidate")
    compare.set_defaults(func=compare_command)
    return p

def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except AcceptanceError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
