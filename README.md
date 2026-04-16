# Hand Laterality Judgment

| Field | Value |
|---|---|
| Name | Hand Laterality Judgment |
| Version | v0.1.0-dev |
| URL / Repository | E:/Taskbeacon/T000045-hand-laterality-judgment |
| Short Description | Chinese hand laterality judgment task with practice and test blocks, left/right key responses, and four generated hand-image stimuli. |
| Created By | TaskBeacon |
| Date Updated | 2026-04-16 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | Chinese |

## 1. Task Overview

This task measures hand laterality judgment using the classic left-hand/right-hand mental-rotation paradigm. Participants see a hand image and decide whether it is a left hand or a right hand, regardless of whether the image shows the back or palm view and regardless of rotation.

The implementation is built around four generated hand assets, a Chinese instruction screen, one practice block, and six formal test blocks. Responses use `f` for left and `j` for right, while `space` advances instruction and break screens.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| Load Config | `main.py` loads the mode-specific YAML file and initializes task settings. |
| Collect Subject Info | Human mode uses the subject form; QA and sim modes inject deterministic IDs. |
| Initialize Runtime | The PsychoPy window, triggers, and stimulus bank are created. |
| Show Instructions | Participants read the Chinese instructions and press space to begin. |
| Run Practice Block | One practice block presents 18 trials with feedback after each response. |
| Run Test Blocks | Six test blocks present 32 trials each with no feedback. |
| Show Break Screens | Practice and test blocks use separate break screens with summary metrics. |
| Finish | A goodbye screen reports summary metrics, then the data are saved and the task exits. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Fixation | A centered fixation cross appears before each judgment trial. |
| Hand Stimulus | A generated hand image is shown in the center of the screen. |
| Response Window | Participants choose left (`f`) or right (`j`) within the response deadline. |
| Practice Feedback | Practice trials show correctness feedback or timeout feedback. |
| ITI | A brief fixation-only inter-trial interval separates trials. |

### Controller Logic

| Feature | Description |
|---|---|
| Trial generation | `build_session_plan()` creates an 18-trial practice block followed by six 32-trial test blocks. |
| Stimulus selection | `build_trial_sequence()` cycles through left/right hand side, back/palm view, and four orientation labels. |
| Response mapping | `f` means left hand and `j` means right hand; `space` is reserved for continuation screens. |
| Determinism | `overall_seed` and block index drive a repeatable trial sequence for QA and simulation. |
| Summary metrics | The task reports accuracy, mean correct RT in milliseconds, and timeout count. |
| Triggering | Visible screens and trial phases emit dedicated onset triggers for QA, sim, and plot auditing. |

### Other Logic

| Component | Description |
|---|---|
| Generated assets | Four line-art hand images are stored in `assets/` and rotated at runtime. |
| View variants | Back and palm views are represented as separate image assets. |
| QA/sim support | QA and simulation modes use a phase-aware responder that can press continue keys and lateralized response keys. |
| Localization | Participant-facing text remains in YAML and uses `SimHei` for Chinese rendering. |

## 3. Configuration Summary

All human settings are defined in `config/config.yaml`. QA and smoke-test overrides live in `config/config_qa.yaml`, `config/config_scripted_sim.yaml`, and `config/config_sampler_sim.yaml`.

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | 3-digit participant identifier used to seed the run. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | `[1280, 720]` |
| `units` | `pix` |
| `screen` | `0` |
| `bg_color` | `black` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `fixation` | text | Centered fixation cross used before trials and during ITIs. |
| `hand_back_left` | image | Generated left-hand back-view stimulus. |
| `hand_back_right` | image | Generated right-hand back-view stimulus. |
| `hand_palm_left` | image | Generated left-hand palm-view stimulus. |
| `hand_palm_right` | image | Generated right-hand palm-view stimulus. |
| `instruction_text` | text | Chinese instructions for the left/right judgment rule and key mapping. |
| `practice_break_text` | text | Break screen between the practice block and formal blocks. |
| `block_break_text` | text | Summary screen between formal test blocks. |
| `practice_feedback_correct` | text | Correct-response feedback shown during practice. |
| `practice_feedback_incorrect` | text | Incorrect-response feedback shown during practice. |
| `practice_feedback_timeout` | text | Timeout feedback shown during practice. |
| `good_bye_text` | text | Final summary and exit screen. |

### d. Timing

| Parameter | Value |
|---|---|
| `task.practice_trials` | `18` |
| `task.test_series_count` | `6` |
| `task.test_trials_per_series` | `32` |
| `task.fixation_duration` | `2.0 s` |
| `task.response_deadline` | `8.0 s` |
| `task.practice_feedback_duration` | `0.8 s` |
| `task.iti_min_duration` | `0.5 s` |
| `task.iti_max_duration` | `1.0 s` |

### e. Triggers

| Event | Code |
|---|---:|
| Experiment onset | `1` |
| Experiment end | `2` |
| Block onset | `10` |
| Block end | `11` |
| Fixation onset | `20` |
| Stimulus onset | `30` |
| Left response | `31` |
| Right response | `32` |
| Response timeout | `33` |
| Correct feedback onset | `40` |
| Incorrect feedback onset | `41` |
| Timeout feedback onset | `42` |
| Instruction onset | `50` |
| Practice break onset | `51` |
| Block break onset | `52` |
| Goodbye onset | `53` |
| ITI onset | `60` |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| `condition_generation` | Custom practice-first generator in `src/utils.py`. |
| `left_key` | `f` |
| `right_key` | `j` |
| `continue_key` | `space` |
| `overall_seed` | `45045` |
| `qa responder` | `TaskSamplerResponder` with perfect-hit QA defaults. |
| `sampler responder` | `TaskSamplerResponder` with non-zero error and lapse rates. |

## 4. Methods (for academic publication)

Participants completed a computer-based hand laterality judgment task. On each trial, a left or right hand image was shown in either back or palm view and at one of four orientation levels. Participants indicated whether the hand was a left hand or a right hand using dedicated keyboard responses.

The task follows a practice-first structure: an 18-trial practice block with correctness feedback is followed by six formal 32-trial blocks without feedback. Trial order is deterministic given the configured seed and includes all combinations of hand side, view, and orientation. The response deadline, inter-trial interval, and break screens are configuration-driven and documented in the reference bundle.

This implementation uses PsychoPy/PsyFlow with all participant-facing wording stored in YAML for auditability and localization portability. QA and simulation modes reuse the same state machine so the runtime can be checked without manual input before publication or deployment.
