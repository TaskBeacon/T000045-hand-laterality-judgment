# Task Logic Audit

## 1. Paradigm Intent

- This task measures hand laterality judgment: participants identify whether a rotated hand image depicts a left or right hand.
- The core cognitive target is implicit visuomotor transformation, with biomechanical constraints influencing reaction time and accuracy.
- The build uses the open-access hand-laterality literature as the primary source, especially the 2009 PLoS ONE protocol that defines the exact stimulus set.
- The main dependent variables are response accuracy, correct-trial RT, timeout rate, and block-level learning effects across repeated series.

## 2. Block/Trial Workflow

- The task begins with Chinese instructions, followed by a practice block and then the scored experimental series.
- Practice block: 18 stimulus trials with correctness feedback after each response.
- Test phase: 6 scored series, each series containing 32 trials built from the same 16 unique stimuli repeated twice in randomized order.
- Within each series, the schedule keeps the same hand from appearing more than 4 times consecutively and keeps the same exact stimulus from repeating more than twice consecutively.
- Each trial follows the same state machine: fixation cross -> hand image -> response window -> inter-trial interval.
- Fixation is 2000 ms, the hand stimulus remains until response or timeout, and the blank ITI is jittered between 500 ms and 1000 ms.
- The response window uses an 8000 ms ceiling, matching the paper's RT trimming threshold and keeping the task finite in keyboard mode.
- Practice is the only phase with correctness feedback; the scored series are response-only and end with block summaries.

## 3. Condition Semantics

- The experimental factors are trial-level, not block-level: hand laterality, view, and in-plane orientation.
- Hand laterality has two levels: left hand and right hand.
- View has two levels: palm view and back view.
- Orientation has four levels: 0 degrees upright, 90 degrees medial, 90 degrees lateral, and 180 degrees inverted.
- The task therefore uses a 2 x 2 x 4 stimulus space with 16 unique images, all of which are mirrored pairs rendered from the same base geometry.
- The block labels used in code are `practice` and `test`, because those are the only participant-facing scheduling modes that change feedback and trial count.
- All hand/view/orientation combinations are balanced within the test series, and the practice block exposes the full factorial set plus two additional warm-up trials before scoring begins.

## 4. Response and Scoring Rules

- Response mapping is fixed: `f` means left hand and `j` means right hand.
- Correctness is determined solely by whether the pressed key matches the stimulus laterality.
- RT is measured from stimulus onset to the first valid keypress.
- Responses after the deadline are scored as timeouts and treated as incorrect for block summaries.
- Practice feedback is binary and brief: correct, incorrect, or timeout.
- The scored series report accuracy, mean correct RT, and timeout counts at the block break and at the end of the task.
- There is no point system, adaptive staircasing, or reward schedule.

## 5. Stimulus Layout Plan

- The screen background is black, matching the source protocol's high-contrast presentation style.
- Each hand image is drawn as a black outline on a white card centered on the screen.
- The display size targets the paper's approximate 15 cm by 10 cm aspect at the task viewing distance, mapped to a centered image region that stays inside the 16:9 window.
- The visual hierarchy is simple: one fixation cross, one central hand image, and no competing text during the response window.
- The instruction, feedback, block break, and goodbye screens use centered white Chinese text with `SimHei` as the participant-facing font.
- The trial screen never repeats the left/right mapping text, because the mapping is taught in the instruction phase and should not clutter the response display.
- The 16 stimulus identities are generated from four base images: left-palm, right-palm, left-back, and right-back.
- Orientation is applied at runtime through the trial `ori` value rather than by storing 16 rotated assets.

## 6. Trigger Plan

- Use onset and offset triggers for experiment start/end and for block boundaries.
- Use separate triggers for instruction onset, practice break onset, block break onset, fixation onset, stimulus onset, response-left, response-right, timeout, feedback onset, and ITI onset.
- A simple loopback or serial trigger driver is sufficient for behavior acquisition; no hardware-specific neuroscience trigger protocol is required for this build.
- Every participant-visible phase emits a trigger before the screen update so QA and simulation traces remain aligned with the rendered flow.

## 7. Architecture Decisions (Auditability)

- A custom trial-spec generator is required because each trial combines hand laterality, view, orientation, and block kind; these semantics are richer than a single label-based condition generator.
- `src/utils.py` should build deterministic schedules from the block seed so practice and test orders can be replayed exactly in QA and sim.
- `src/run_trial.py` should instantiate the correct base hand image and rotate it per trial, rather than hardcoding the stimulus logic into multiple ad hoc branches.
- Every participant-visible phase must call `set_trial_context(...)` before `show(...)` or `capture_response(...)` so the plotter and QA trace can reconstruct the full state machine.
- The practice and test flows share the same trial state machine; only feedback, trial count, and block summary behavior differ.
- The simulation responder can remain simple because the response mapping is fixed and the schedule is deterministic.

## 8. Inference Log

- The 2009 paper used touchpad buttons and a separate familiarization phase in which participants physically matched the displayed hand posture; this build maps the response buttons to `f` and `j` and replaces the physical matching step with an on-screen practice block.
- The source protocol trimmed RTs above 8000 ms; this build uses the same cutoff as a hard deadline so response windows are bounded in human, QA, and simulation modes.
- The paper used realistic hand renders created in Poser; this build uses generated silhouette-style hand assets that preserve the same laterality, view, and orientation factors without reusing copyrighted source images.
- The 2 x 2 x 4 stimulus factorization is taken from the open-access 2009 protocol, while the later 2004, 2006, 1998, and 2010 papers support the interpretation of posture, imagery, and rotation effects.
- The exact order of the 6 scored series is randomized from a fixed seed, but the internal balance constraints are deterministic so the same session can be replayed.
