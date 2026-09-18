from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from oracle.d6_darkness import (
    DarknessIntervention,
    apply_darkness,
    build_darkness,
)
from oracle.d6_mercy import (
    MercyIntervention,
    apply_mercy_activity,
    build_mercy,
)
from oracle.d6_scar import (
    ScarPhase,
    ScarTissueState,
    advance_scar,
    build_scar,
    scar_can_stack,
)
from oracle.d6_scar_effect import (
    apply_scar_effect,
    select_scar_target,
)
from oracle.d6_shock import (
    ShockIntervention,
    apply_shock_activity,
    build_shock,
)
from oracle.d6_timeout import (
    TimeOutIntervention,
    apply_timeout_readout,
    build_timeout,
)
from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    PlasticityState,
)
from oracle.reinforcement import (
    ReinforcementCondition,
    ReinforcementResult,
)


StimulusModifier = Callable[
    [np.ndarray, int],
    np.ndarray,
]

ActivityModifier = Callable[
    [np.ndarray, int],
    np.ndarray,
]

SynapticModifier = Callable[
    [np.ndarray, np.ndarray],
    np.ndarray,
]

ReadoutModifier = Callable[
    [np.ndarray, np.ndarray, int],
    tuple[np.ndarray, np.ndarray],
]


@dataclass(frozen=True)
class D6ExecutionPlan:
    condition: ReinforcementCondition
    applicable: bool

    stimulus_modifier: StimulusModifier | None
    activity_modifier: ActivityModifier | None
    synaptic_modifier: SynapticModifier | None
    readout_modifier: ReadoutModifier | None

    shock: ShockIntervention | None
    darkness: DarknessIntervention | None
    timeout: TimeOutIntervention | None
    scar_state: ScarTissueState | None
    scar_target_model_index: int | None
    mercy: MercyIntervention | None


def build_d6_execution_plan(
    *,
    d6_result: ReinforcementResult,
    seed: int,
    experiment_id: str,
    session_id: str,
    readout_indices: np.ndarray,
    intervention_generation: int = 0,
    plasticity_state: PlasticityState | None = None,
    prior_scar_state: ScarTissueState | None = None,
    prior_scar_target_model_index: int | None = None,
) -> D6ExecutionPlan:
    condition = d6_result.selection.condition

    #
    # Existing SC-05 state advances at the start
    # of every distinct session, regardless of
    # the newly selected D6 condition.
    #
    scar_state = prior_scar_state
    scar_target = prior_scar_target_model_index

    if scar_state is not None:
        scar_state = advance_scar(
            state=scar_state,
            session_id=session_id,
        )

        if not scar_state.active:
            scar_target = None

    shock = None
    darkness = None
    timeout = None
    mercy = None

    #
    # Current-session intervention.
    #
    if d6_result.applicable:
        if (
            condition
            is ReinforcementCondition.SC_01_SHOCK
        ):
            shock = build_shock(
                seed=seed,
                experiment_id=experiment_id,
                session_id=session_id,
                current_generation=intervention_generation,
            )

        elif (
            condition
            is ReinforcementCondition.SC_02_DARKNESS
        ):
            darkness = build_darkness(
                current_generation=intervention_generation,
            )

        elif (
            condition
            is ReinforcementCondition.SC_04_TIME_OUT
        ):
            timeout = build_timeout(
                current_generation=intervention_generation,
            )

        elif (
            condition
            is ReinforcementCondition.SC_05_SCAR_TISSUE
        ):
            if (
                scar_state is None
                or scar_can_stack(scar_state)
            ):
                scar_state = build_scar(
                    session_id=session_id,
                    current_generation=intervention_generation,
                )

        elif (
            condition
            is ReinforcementCondition.SC_06_MERCY
        ):
            mercy = build_mercy(
                seed=seed,
                experiment_id=experiment_id,
                session_id=session_id,
                current_generation=intervention_generation,
            )

    #
    # Persistent SC-05 target is always derived
    # from its origin session, including the
    # following-session carryover.
    #
    if (
        scar_state is not None
        and scar_state.active
        and scar_target is None
    ):
        _, scar_target = select_scar_target(
            seed=seed,
            experiment_id=experiment_id,
            origin_session_id=(
                scar_state.origin_session_id
            ),
        )

    stimulus_modifier = None

    if darkness is not None:
        def stimulus_modifier(
            stimulus: np.ndarray,
            generation: int,
        ) -> np.ndarray:
            return apply_darkness(
                stimulus=stimulus,
                intervention=darkness,
                generation=generation,
            )

    activity_modifier = None

    if (
        scar_target is not None
        or shock is not None
        or mercy is not None
    ):
        def activity_modifier(
            activity: np.ndarray,
            generation: int,
        ) -> np.ndarray:
            modified = np.asarray(
                activity,
                dtype=np.float32,
            ).copy()

            #
            # Frozen composition order:
            #
            # persistent SC-05 state first,
            # acute current-session activity
            # intervention second.
            #
            scar_active_now = False

            if (
                scar_state is not None
                and scar_target is not None
                and scar_state.active
            ):
                if (
                    scar_state.phase
                    is ScarPhase.CURRENT_SESSION
                ):
                    scar_active_now = (
                        generation
                        >= scar_state.activated_generation
                    )

                elif (
                    scar_state.phase
                    is ScarPhase.FOLLOWING_SESSION
                ):
                    scar_active_now = True

            if scar_active_now:
                modified = apply_scar_effect(
                    effective_activity=modified,
                    scar_state=scar_state,
                    target_model_index=scar_target,
                )

            if shock is not None:
                modified = apply_shock_activity(
                    effective_activity=modified,
                    intervention=shock,
                    generation=generation,
                )

            if mercy is not None:
                modified = apply_mercy_activity(
                    effective_activity=modified,
                    intervention=mercy,
                    generation=generation,
                )

            return modified

    synaptic_modifier = None

    if plasticity_state is not None:
        synaptic_modifier = (
            build_synaptic_modifier(
                plasticity_state
            )
        )

    readout_modifier = None

    if timeout is not None:
        indices = np.asarray(
            readout_indices,
            dtype=np.int64,
        )

        def readout_modifier(
            voltage: np.ndarray,
            spikes: np.ndarray,
            generation: int,
        ) -> tuple[
            np.ndarray,
            np.ndarray,
        ]:
            result = apply_timeout_readout(
                voltage=voltage,
                spikes=spikes,
                readout_indices=indices,
                intervention=timeout,
                generation=generation,
            )

            return (
                result.voltage,
                result.spikes,
            )

    return D6ExecutionPlan(
        condition=condition,
        applicable=d6_result.applicable,
        stimulus_modifier=stimulus_modifier,
        activity_modifier=activity_modifier,
        synaptic_modifier=synaptic_modifier,
        readout_modifier=readout_modifier,
        shock=shock,
        darkness=darkness,
        timeout=timeout,
        scar_state=scar_state,
        scar_target_model_index=scar_target,
        mercy=mercy,
    )
