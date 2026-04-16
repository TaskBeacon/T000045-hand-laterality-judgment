from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random as _py_random

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


_CONTINUE_PHASES = {
    "instruction",
    "practice_break",
    "block_break",
    "good_bye",
    "goodbye",
}


@dataclass
class TaskSamplerResponder:
    """Phase-aware responder for hand laterality QA and simulation.

    The responder advances non-response screens with the configured continue
    key and answers the laterality judgment window using the target hand side
    when that information is available in ``task_factors``.
    """

    left_key: str = "f"
    right_key: str = "j"
    continue_key: str = "space"
    hit_rate: float = 1.0
    error_rate: float = 0.0
    rt_mean_s: float = 0.28
    rt_sd_s: float = 0.05
    rt_min_s: float = 0.12

    def __post_init__(self) -> None:
        self._rng: Any = None
        self.left_key = str(self.left_key or "f").strip().lower()
        self.right_key = str(self.right_key or "j").strip().lower()
        self.continue_key = str(self.continue_key or "space").strip().lower()
        self.hit_rate = max(0.0, min(1.0, float(self.hit_rate)))
        self.error_rate = max(0.0, min(1.0, float(self.error_rate)))
        self.rt_mean_s = float(self.rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _sample_normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        return float(rng.gauss(mean, sd))

    def _sample_random(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return float(_py_random.random())

    @staticmethod
    def _phase_name(obs: Observation) -> str:
        return str(obs.phase or "").strip().lower()

    @staticmethod
    def _valid_keys(obs: Observation) -> list[str]:
        return [str(key).strip().lower() for key in list(obs.valid_keys or []) if str(key).strip()]

    @staticmethod
    def _task_factors(obs: Observation) -> dict[str, Any]:
        factors = obs.task_factors or {}
        return dict(factors) if isinstance(factors, dict) else {}

    def _sample_rt(self) -> float:
        return max(self.rt_min_s, self._sample_normal(self.rt_mean_s, self.rt_sd_s))

    def _continue_action(self, valid_keys: list[str], phase: str) -> Action:
        key = self.continue_key if self.continue_key in valid_keys else (valid_keys[0] if valid_keys else None)
        return Action(
            key=key,
            rt_s=self._sample_rt(),
            meta={"source": "task_sampler", "phase": phase, "kind": "continue"},
        )

    def _resolve_correct_key(self, valid_keys: list[str], factors: dict[str, Any]) -> str | None:
        candidates = [
            factors.get("correct_key"),
            self.left_key if str(factors.get("hand_side", "")).strip().lower() == "left" else None,
            self.right_key if str(factors.get("hand_side", "")).strip().lower() == "right" else None,
        ]
        for candidate in candidates:
            key = str(candidate or "").strip().lower()
            if key and key in valid_keys:
                return key
        return valid_keys[0] if valid_keys else None

    def _response_action(self, valid_keys: list[str], phase: str, factors: dict[str, Any]) -> Action:
        if self._sample_random() > self.hit_rate:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "phase": phase, "kind": "miss"})

        correct_key = self._resolve_correct_key(valid_keys, factors)
        if correct_key is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "phase": phase, "kind": "no_valid_response"})

        choose_error = self._sample_random() < self.error_rate
        if choose_error:
            wrong_keys = [key for key in valid_keys if key != correct_key]
            chosen_key = wrong_keys[0] if wrong_keys else correct_key
            outcome = "error"
        else:
            chosen_key = correct_key
            outcome = "hit"

        return Action(
            key=chosen_key,
            rt_s=self._sample_rt(),
            meta={
                "source": "task_sampler",
                "phase": phase,
                "kind": outcome,
                "correct_key": correct_key,
                "hand_side": str(factors.get("hand_side", "")).strip().lower(),
                "view": str(factors.get("view", "")).strip().lower(),
                "orientation_label": str(factors.get("orientation_label", "")).strip().lower(),
            },
        )

    def act(self, obs: Observation) -> Action:
        valid_keys = self._valid_keys(obs)
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        if self._rng is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "rng_missing"})

        phase = self._phase_name(obs)
        factors = self._task_factors(obs)

        if phase in _CONTINUE_PHASES or phase.endswith("fixation") or phase.endswith("iti") or phase.endswith("ready"):
            return self._continue_action(valid_keys, phase)

        if phase == "response_window" or phase.endswith("response_window") or phase.endswith("response"):
            return self._response_action(valid_keys, phase, factors)

        return self._continue_action(valid_keys, phase)


__all__ = ["TaskSamplerResponder"]
