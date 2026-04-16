from __future__ import annotations

import random
from typing import Any


HAND_SIDES = ("left", "right")
HAND_VIEWS = ("back", "palm")
ORIENTATION_LABELS = ("upright", "medial", "lateral", "inverted")

BASE_STIMULUS_BY_VIEW_HAND = {
    ("back", "left"): "hand_back_left",
    ("back", "right"): "hand_back_right",
    ("palm", "left"): "hand_palm_left",
    ("palm", "right"): "hand_palm_right",
}

ORIENTATION_ROTATION_DEG = {
    ("left", "upright"): 0.0,
    ("left", "medial"): 90.0,
    ("left", "lateral"): 270.0,
    ("left", "inverted"): 180.0,
    ("right", "upright"): 0.0,
    ("right", "medial"): 270.0,
    ("right", "lateral"): 90.0,
    ("right", "inverted"): 180.0,
}


def _trial_rng(seed: int, block_idx: int, salt: int = 0) -> random.Random:
    return random.Random(int(seed) + int(block_idx) * 1009 + int(salt) * 97)


def _shuffle_with_constraints(items: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    def ok(seq: list[dict[str, Any]]) -> bool:
        hand_run = 1
        stim_run = 1
        for i in range(1, len(seq)):
            prev = seq[i - 1]
            cur = seq[i]
            hand_run = hand_run + 1 if cur["hand_side"] == prev["hand_side"] else 1
            stim_run = stim_run + 1 if cur["stimulus_name"] == prev["stimulus_name"] else 1
            if hand_run > 4 or stim_run > 2:
                return False
        return True

    candidate = list(items)
    for _ in range(256):
        rng.shuffle(candidate)
        if ok(candidate):
            return list(candidate)
    return list(candidate)


def _build_unique_pool() -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for view in HAND_VIEWS:
        for hand_side in HAND_SIDES:
            for orientation_label in ORIENTATION_LABELS:
                pool.append(
                    {
                        "hand_side": hand_side,
                        "view": view,
                        "orientation_label": orientation_label,
                        "orientation_deg": float(ORIENTATION_ROTATION_DEG[(hand_side, orientation_label)]),
                        "stimulus_name": BASE_STIMULUS_BY_VIEW_HAND[(view, hand_side)],
                        "correct_key": "f" if hand_side == "left" else "j",
                    }
                )
    return pool


def build_trial_sequence(*, seed: int, block_idx: int, trial_count: int) -> list[dict[str, Any]]:
    """Create a deterministic trial sequence for one practice/test block."""
    pool = _build_unique_pool()
    rng = _trial_rng(seed, block_idx)
    shuffled_pool = _shuffle_with_constraints(pool, rng)

    if trial_count <= len(shuffled_pool):
        chosen = list(shuffled_pool[: int(trial_count)])
    else:
        repeats = (int(trial_count) + len(shuffled_pool) - 1) // len(shuffled_pool)
        expanded = list(shuffled_pool) * repeats
        rng.shuffle(expanded)
        chosen = _shuffle_with_constraints(expanded[: int(trial_count)], rng)

    trials: list[dict[str, Any]] = []
    for trial_index, trial in enumerate(chosen, start=1):
        payload = dict(trial)
        payload["trial_index_in_block"] = trial_index
        payload["condition"] = "practice" if block_idx == 0 else "test"
        payload["condition_label"] = payload["condition"]
        payload["trial_tag"] = (
            f"{payload['condition']}_{payload['hand_side']}_{payload['view']}"
            f"_{payload['orientation_label']}_{trial_index:03d}"
        )
        trials.append(payload)
    return trials


def build_session_plan(settings: Any) -> list[dict[str, Any]]:
    """Return the ordered block schedule for human/qa/sim modes."""
    seed = int(getattr(settings, "overall_seed", 45045))
    practice_trials = max(1, int(getattr(settings, "practice_trials", 16)))
    test_series_count = max(0, int(getattr(settings, "test_series_count", 6)))
    test_trials_per_series = max(1, int(getattr(settings, "test_trials_per_series", 32)))

    blocks: list[dict[str, Any]] = []
    blocks.append(
        {
            "block_kind": "practice",
            "block_id": "practice",
            "block_idx": 0,
            "trial_count": practice_trials,
            "trials": build_trial_sequence(seed=seed, block_idx=0, trial_count=practice_trials),
            "show_feedback": True,
        }
    )

    for series_idx in range(test_series_count):
        block_idx = series_idx + 1
        trials = build_trial_sequence(
            seed=seed,
            block_idx=block_idx,
            trial_count=test_trials_per_series,
        )
        blocks.append(
            {
                "block_kind": "test",
                "block_id": f"test_{series_idx + 1}",
                "block_idx": block_idx,
                "series_index": series_idx + 1,
                "trial_count": test_trials_per_series,
                "trials": trials,
                "show_feedback": False,
            }
        )

    return blocks


def summarize_trials(trials: list[dict[str, Any]]) -> dict[str, float | int]:
    responded = [t for t in trials if bool(t.get("responded"))]
    correct = [t for t in trials if bool(t.get("response_correct"))]
    rts = [
        float(t["response_rt"])
        for t in trials
        if bool(t.get("response_correct")) and isinstance(t.get("response_rt"), (int, float))
    ]
    return {
        "n_trials": len(trials),
        "n_responded": len(responded),
        "n_correct": len(correct),
        "accuracy": (len(correct) / len(trials)) if trials else 0.0,
        "mean_correct_rt_ms": (sum(rts) / len(rts) * 1000.0) if rts else 0.0,
        "timeout_count": sum(1 for t in trials if bool(t.get("timed_out"))),
    }
