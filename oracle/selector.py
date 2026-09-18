from __future__ import annotations

import hashlib

from oracle.reinforcement import (
    ReinforcementCondition,
    ReinforcementResult,
    ReinforcementSelection,
)


SELECTOR_VERSION = "d6-sha256/v1"

D6_CONDITIONS = (
    ReinforcementCondition.SC_01_SHOCK,
    ReinforcementCondition.SC_02_DARKNESS,
    ReinforcementCondition.SC_03_BAD_SYNAPSE,
    ReinforcementCondition.SC_04_TIME_OUT,
    ReinforcementCondition.SC_05_SCAR_TISSUE,
    ReinforcementCondition.SC_06_MERCY,
)


def select_d6(
    *,
    seed: int,
    experiment_id: str,
    session_id: str,
    plasticity_active: bool,
) -> ReinforcementResult:
    payload = (
        f"{SELECTOR_VERSION}\0"
        f"{seed}\0"
        f"{experiment_id}\0"
        f"{session_id}"
    ).encode("utf-8")

    digest = hashlib.sha256(payload).digest()

    selected_index = int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    ) % len(D6_CONDITIONS)

    condition = D6_CONDITIONS[selected_index]

    selection = ReinforcementSelection(
        schema_version="oracle-reinforcement/v1",
        selector_version=SELECTOR_VERSION,
        condition=condition,
        selected_index=selected_index,
        seed=seed,
        eligible_conditions=D6_CONDITIONS,
    )

    if (
        condition
        is ReinforcementCondition.SC_03_BAD_SYNAPSE
        and not plasticity_active
    ):
        return ReinforcementResult(
            selection=selection,
            applicable=False,
            status="NOT_APPLICABLE",
        )

    return ReinforcementResult(
        selection=selection,
        applicable=True,
        status="SELECTED",
    )
