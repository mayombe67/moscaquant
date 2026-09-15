"""Deterministic spatial mapping for MQ-001 R1-R6 photoreceptors."""

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

import numpy as np


@dataclass(frozen=True)
class RetinalAssignment:
    neuron_index: int
    body_id: int
    partner_body_id: int
    eye: str
    h1: int
    h2: int
    weight: float


def load_optic_columns(
    path: Path,
) -> dict[int, tuple[str, int, int]]:
    """Load official MaleCNS optic-column assignments."""

    ns = {
        "s":
        "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    }

    result: dict[int, tuple[str, int, int]] = {}

    with zipfile.ZipFile(path) as archive:
        strings = [
            "".join(element.itertext())
            for element in ET.fromstring(
                archive.read("xl/sharedStrings.xml")
            )
        ]

        for sheet in (1, 2):
            root = ET.fromstring(
                archive.read(
                    f"xl/worksheets/sheet{sheet}.xml"
                )
            )

            rows = root.findall(
                "s:sheetData/s:row",
                ns,
            )

            for row in rows[1:]:
                cells = {}

                for cell in row:
                    value = cell.find("s:v", ns)

                    if value is None:
                        continue

                    column = re.sub(
                        r"\d",
                        "",
                        cell.attrib["r"],
                    )

                    cells[column] = (
                        strings[int(value.text)]
                        if cell.get("t") == "s"
                        else value.text
                    )

                match = re.fullmatch(
                    r"ME_([LR])_col_(\d+)_(\d+)",
                    cells.get("A", ""),
                )

                if not match:
                    continue

                eye, h1, h2 = match.groups()

                for column in ("B", "C", "E"):
                    try:
                        body = int(
                            cells.get(column, -1)
                        )
                    except ValueError:
                        continue

                    if body > 0:
                        result[body] = (
                            eye,
                            int(h1),
                            int(h2),
                        )

    return result


def infer_r1_r6_retina(
    connectome,
    neuron_ids: np.ndarray,
    r1_r6: np.ndarray,
    columns: dict[int, tuple[str, int, int]],
) -> tuple[list[RetinalAssignment], np.ndarray]:
    """
    Infer R1-R6 retinal positions using the strongest connection
    to an officially column-assigned postsynaptic partner.

    Connectome orientation is post x pre.

    Official coordinates come from the MaleCNS optic-column workbook.
    Photoreceptor-to-column assignment is inferred, not official.
    """

    known = np.array(
        [
            index
            for index, body in enumerate(neuron_ids)
            if int(body) in columns
        ],
        dtype=np.int32,
    )

    links = abs(
        connectome[known][:, r1_r6]
    ).tocsc()

    placed: list[RetinalAssignment] = []
    unplaced: list[int] = []

    for k, neuron in enumerate(r1_r6):
        start = links.indptr[k]
        end = links.indptr[k + 1]

        if end == start:
            unplaced.append(int(neuron))
            continue

        strongest = start + np.argmax(
            links.data[start:end]
        )

        partner_index = known[
            links.indices[strongest]
        ]

        partner_body = int(
            neuron_ids[partner_index]
        )

        eye, h1, h2 = columns[partner_body]

        placed.append(
            RetinalAssignment(
                neuron_index=int(neuron),
                body_id=int(neuron_ids[neuron]),
                partner_body_id=partner_body,
                eye=eye,
                h1=h1,
                h2=h2,
                weight=float(
                    links.data[strongest]
                ),
            )
        )

    return (
        placed,
        np.asarray(
            unplaced,
            dtype=np.int32,
        ),
    )
