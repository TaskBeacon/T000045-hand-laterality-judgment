from __future__ import annotations

from functools import partial
import random
from typing import Any

from psyflow import StimUnit, next_trial_id, resolve_deadline, set_trial_context


def _build_iti_duration(settings: Any, trial_id: int) -> float:
    iti_min = float(getattr(settings, "iti_min_duration", 0.5))
    iti_max = float(getattr(settings, "iti_max_duration", iti_min))
    if iti_max <= iti_min:
        return max(0.0, iti_min)
    rng = random.Random(int(getattr(settings, "overall_seed", 45045)) + int(trial_id) * 31)
    return float(rng.uniform(iti_min, iti_max))


def run_trial(
    win,
    kb,
    settings,
    trial_spec,
    stim_bank,
    trigger_runtime,
    condition=None,
    block_id=None,
    block_idx=None,
):
    """Run one hand-laterality trial."""
    trial_id = int(next_trial_id())
    condition_label = str(condition or trial_spec.get("condition", trial_spec.get("block_kind", "test"))).strip().lower()
    condition = condition_label
    trial_condition = str(trial_spec.get("condition", condition_label)).strip().lower()
    block_kind = str(trial_spec.get("block_kind", condition_label)).strip().lower()
    block_id_val = str(block_id) if block_id is not None else str(trial_spec.get("block_id", block_kind))
    block_idx_val = int(block_idx) if block_idx is not None else int(trial_spec.get("block_idx", 0))
    trial_in_block = int(trial_spec.get("trial_index_in_block", trial_id))

    left_key = str(getattr(settings, "left_key", "f")).strip().lower()
    right_key = str(getattr(settings, "right_key", "j")).strip().lower()
    continue_key = str(getattr(settings, "continue_key", "space")).strip().lower()
    valid_response_keys = [left_key, right_key]

    hand_side = str(trial_spec.get("hand_side", "left")).strip().lower()
    view = str(trial_spec.get("view", "back")).strip().lower()
    orientation_label = str(trial_spec.get("orientation_label", "upright")).strip().lower()
    orientation_deg = float(trial_spec.get("orientation_deg", 0.0))
    stimulus_name = str(trial_spec.get("stimulus_name", "hand_back_left"))
    preview_stimulus_name = "hand_back_left"
    if trial_condition.startswith("practice_right_back") or trial_condition.startswith("test_right_back"):
        preview_stimulus_name = "hand_back_right"
    elif trial_condition.startswith("practice_right_palm") or trial_condition.startswith("test_right_palm"):
        preview_stimulus_name = "hand_palm_right"
    elif trial_condition.startswith("practice_left_palm") or trial_condition.startswith("test_left_palm"):
        preview_stimulus_name = "hand_palm_left"
    correct_key = str(trial_spec.get("correct_key", left_key if hand_side == "left" else right_key)).strip().lower()
    if correct_key not in valid_response_keys:
        correct_key = left_key if hand_side == "left" else right_key

    fixation_duration = float(getattr(settings, "fixation_duration", 2.0))
    response_deadline = float(getattr(settings, "response_deadline", 8.0))
    practice_feedback_duration = float(getattr(settings, "practice_feedback_duration", 0.8))
    iti_duration = _build_iti_duration(settings, trial_id)

    trial_data = {
        "trial_id": trial_id,
        "block_id": block_id_val,
        "block_idx": block_idx_val,
        "block_kind": block_kind,
        "trial_in_block": trial_in_block,
        "condition": condition_label,
        "condition_label": condition_label,
        "hand_side": hand_side,
        "view": view,
        "orientation_label": orientation_label,
        "orientation_deg": orientation_deg,
        "stimulus_name": stimulus_name,
        "stimulus_preview_name": preview_stimulus_name,
        "trial_tag": str(trial_spec.get("trial_tag", f"{block_kind}_{trial_id}")),
        "correct_key": correct_key,
        "iti_duration": iti_duration,
    }

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    fixation = make_unit(unit_label=f"{block_kind}_fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=resolve_deadline(fixation_duration),
        valid_keys=[],
        block_id=block_id_val,
        condition_id=trial_data["trial_tag"],
        task_factors={
            "stage": "fixation",
            "block_kind": block_kind,
            "hand_side": hand_side,
            "view": view,
            "orientation_label": orientation_label,
            "trial_in_block": trial_in_block,
        },
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    hand_stim = stim_bank.rebuild(stimulus_name, update_cache=False, ori=orientation_deg)
    response_window = make_unit(unit_label="response_window").add_stim(hand_stim)
    set_trial_context(
        response_window,
        trial_id=trial_id,
        phase="response_window",
        deadline_s=resolve_deadline(response_deadline),
        valid_keys=valid_response_keys,
        block_id=block_id_val,
        condition_id=trial_data["trial_tag"],
        task_factors={
            "stage": "response_window",
            "block_kind": block_kind,
            "hand_side": hand_side,
            "view": view,
            "orientation_label": orientation_label,
            "correct_key": correct_key,
            "stimulus_name": stimulus_name,
            "stimulus_preview_name": preview_stimulus_name,
            "trial_in_block": trial_in_block,
        },
        stim_id=preview_stimulus_name,
    )
    response_window.capture_response(
        keys=valid_response_keys,
        correct_keys=[correct_key],
        duration=response_deadline,
        onset_trigger=settings.triggers.get("stimulus_onset"),
        response_trigger={
            left_key: settings.triggers.get("response_left"),
            right_key: settings.triggers.get("response_right"),
        },
        timeout_trigger=settings.triggers.get("response_timeout"),
    )
    response_window.to_dict(trial_data)

    response_key = str(response_window.get_state("response", "")).strip().lower()
    response_rt = response_window.get_state("rt", None)
    responded = response_key in valid_response_keys
    response_correct = bool(responded and response_key == correct_key)
    timed_out = not responded

    trial_data.update(
        {
            "responded": responded,
            "response_key": response_key if responded else "",
            "response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
            "response_correct": response_correct,
            "timed_out": timed_out,
        }
    )

    if condition == "practice":
        if timed_out:
            feedback_stim = "practice_feedback_timeout"
            feedback_trigger = settings.triggers.get("feedback_timeout_onset")
            feedback_kind = "timeout"
        elif response_correct:
            feedback_stim = "practice_feedback_correct"
            feedback_trigger = settings.triggers.get("feedback_correct_onset")
            feedback_kind = "correct"
        else:
            feedback_stim = "practice_feedback_incorrect"
            feedback_trigger = settings.triggers.get("feedback_incorrect_onset")
            feedback_kind = "incorrect"

        feedback = make_unit(unit_label="practice_feedback").add_stim(stim_bank.get(feedback_stim))
        set_trial_context(
            feedback,
            trial_id=trial_id,
            phase="feedback",
            deadline_s=resolve_deadline(practice_feedback_duration),
            valid_keys=[],
            block_id=block_id_val,
            condition_id=trial_data["trial_tag"],
            task_factors={
                "stage": "feedback",
                "block_kind": block_kind,
                "hand_side": hand_side,
                "view": view,
                "orientation_label": orientation_label,
                "feedback_kind": feedback_kind,
                "trial_in_block": trial_in_block,
            },
            stim_id=feedback_stim,
        )
        feedback.show(
            duration=practice_feedback_duration,
            onset_trigger=feedback_trigger,
        ).to_dict(trial_data)
        trial_data["feedback_kind"] = feedback_kind

    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=resolve_deadline(iti_duration),
        valid_keys=[],
        block_id=block_id_val,
        condition_id=trial_data["trial_tag"],
        task_factors={
            "stage": "iti",
            "block_kind": block_kind,
            "hand_side": hand_side,
            "view": view,
            "orientation_label": orientation_label,
            "trial_in_block": trial_in_block,
        },
        stim_id="fixation",
    )
    iti.show(
        duration=iti_duration,
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    trial_data["response_window_response"] = trial_data.get("response_window_response", trial_data["response_key"])
    trial_data["response_window_rt"] = trial_data.get("response_window_rt", trial_data["response_rt"])
    trial_data["response_window_key_press"] = trial_data.get("response_window_key_press", trial_data["response_key"])

    return trial_data
