from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PACKET = (
    ROOT
    / "artifacts"
    / "external-review"
    / "sq08-three-body"
)

REQUIRED = {
    "README.md",
    "SHA256SUMS",
    "sq08-three-body-evidence-v1.json",
    "sq08-three-body-evidence-v1.npz",
    "sq08-three-body-analysis-v1.json",
    "sq08-three-body-analysis-contract-v1.json",
    "sq08-three-body-evidence-schema-v1.json",
}

AUTHORITATIVE_NPZ_SHA256 = (
    "e95f054e827cf1232ef72019692e4bcf"
    "c099214a654e1a3267f0f41cfc66abfb"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def tracked_packet_names() -> set[str]:
    relative = PACKET.relative_to(ROOT)

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            str(relative),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return {
        Path(line).name
        for line in result.stdout.splitlines()
        if line.strip()
    }


def checksum_entries() -> dict[str, str]:
    entries = {}

    for line in (
        PACKET / "SHA256SUMS"
    ).read_text().splitlines():
        if not line.strip():
            continue

        digest, filename = line.split(maxsplit=1)

        filename = filename.lstrip("* ")

        entries[filename] = digest

    return entries


def test_required_packet_files_exist():
    observed = {
        path.name
        for path in PACKET.iterdir()
        if path.is_file()
    }

    assert REQUIRED <= observed


def test_required_packet_files_are_git_tracked():
    assert REQUIRED <= tracked_packet_names()


def test_every_checksum_target_exists():
    for filename in checksum_entries():
        assert (PACKET / filename).is_file()


def test_every_checksum_matches_packet_bytes():
    for filename, expected in checksum_entries().items():
        assert sha256_file(
            PACKET / filename
        ) == expected


def test_authoritative_npz_is_present_and_bound():
    npz = PACKET / "sq08-three-body-evidence-v1.npz"

    assert npz.is_file()
    assert (
        sha256_file(npz)
        == AUTHORITATIVE_NPZ_SHA256
    )

    assert (
        checksum_entries()[
            "sq08-three-body-evidence-v1.npz"
        ]
        == AUTHORITATIVE_NPZ_SHA256
    )


def test_readme_names_authoritative_npz():
    readme = (PACKET / "README.md").read_text()

    assert (
        "sq08-three-body-evidence-v1.npz"
        in readme
    )
