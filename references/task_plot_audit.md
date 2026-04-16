# Task Plot Audit

- generated_at: 2026-04-16T00:46:16
- mode: existing
- task_path: E:\Taskbeacon\T000045-hand-laterality-judgment

## 1. Inputs and provenance

- E:\Taskbeacon\T000045-hand-laterality-judgment\README.md
- E:\Taskbeacon\T000045-hand-laterality-judgment\config\config.yaml
- E:\Taskbeacon\T000045-hand-laterality-judgment\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | Fixation | A centered fixation cross appears before each judgment trial. |
- | Hand Stimulus | A generated hand image is shown in the center of the screen. |
- | Response Window | Participants choose left (`f`) or right (`j`) within the response deadline. |
- | Practice Feedback | Practice trials show correctness feedback or timeout feedback. |
- | ITI | A brief fixation-only inter-trial interval separates trials. |

## 3. Evidence extracted from config/source

- practice: phase=fixation, deadline_expr=resolve_deadline(fixation_duration), response_expr=n/a, stim_expr='fixation'
- practice: phase=response window, deadline_expr=resolve_deadline(response_deadline), response_expr=response_deadline, stim_expr=preview_stimulus_name
- practice: phase=feedback, deadline_expr=resolve_deadline(practice_feedback_duration), response_expr=n/a, stim_expr=feedback_stim
- practice: phase=iti, deadline_expr=resolve_deadline(iti_duration), response_expr=n/a, stim_expr='fixation'
- test: phase=fixation, deadline_expr=resolve_deadline(fixation_duration), response_expr=n/a, stim_expr='fixation'
- test: phase=response window, deadline_expr=resolve_deadline(response_deadline), response_expr=response_deadline, stim_expr=preview_stimulus_name
- test: phase=iti, deadline_expr=resolve_deadline(iti_duration), response_expr=n/a, stim_expr='fixation'

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 2
- screens_per_timeline: 7
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.057, right=0.057, blank=0.170
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0573, 'right_ratio': 0.0573, 'blank_ratio': 0.1702}
- validator_warnings:
  - timelines[0].phases[0] missing duration_ms; renderer will annotate as n/a.
  - timelines[0].phases[1] missing duration_ms; renderer will annotate as n/a.
  - timelines[0].phases[2] missing duration_ms; renderer will annotate as n/a.
  - timelines[0].phases[3] missing duration_ms; renderer will annotate as n/a.
  - timelines[1].phases[0] missing duration_ms; renderer will annotate as n/a.
  - timelines[1].phases[1] missing duration_ms; renderer will annotate as n/a.
  - timelines[1].phases[2] missing duration_ms; renderer will annotate as n/a.

## 7. Output files and checksums

- E:\Taskbeacon\T000045-hand-laterality-judgment\references\task_plot_spec.yaml: sha256=c2a4be64608a162fdd0f4b41bae9d3278c390515186ade838870bfa9fcc02d2b
- E:\Taskbeacon\T000045-hand-laterality-judgment\references\task_plot_spec.json: sha256=29ba8fc1a64c2490bf75ec01df2c5276475693a92000853ee4225bd0f4344737
- E:\Taskbeacon\T000045-hand-laterality-judgment\references\task_plot_source_excerpt.md: sha256=f83146cf577a2086ce41988b63b40b3a0d076858fd76dc2b37815135e33b3b0b
- E:\Taskbeacon\T000045-hand-laterality-judgment\task_flow.png: sha256=f430bef46b7f0c7989c9e97cfdbf61eb9814a1afc4c3c078c4e61193708943bb

## 8. Inferred/uncertain items

- practice:fixation:unable to resolve duration from 'resolve_deadline(fixation_duration)'
- practice:response window:unable to resolve duration from 'resolve_deadline(response_deadline)'
- practice:response window:heuristic numeric parse from 'float(getattr(settings, 'response_deadline', 8.0))'
- practice:feedback:unable to resolve duration from 'resolve_deadline(practice_feedback_duration)'
- practice:iti:unable to resolve duration from 'resolve_deadline(iti_duration)'
- test:fixation:unable to resolve duration from 'resolve_deadline(fixation_duration)'
- test:response window:unable to resolve duration from 'resolve_deadline(response_deadline)'
- test:response window:heuristic numeric parse from 'float(getattr(settings, 'response_deadline', 8.0))'
- test:iti:unable to resolve duration from 'resolve_deadline(iti_duration)'
- unparsed if-tests defaulted to condition-agnostic applicability: correct_key not in valid_response_keys; response_correct; timed_out; trial_condition.startswith('practice_left_palm'); trial_condition.startswith('test_left_palm'); trial_condition.startswith('practice_right_back'); trial_condition.startswith('test_right_back'); trial_condition.startswith('practice_right_palm'); trial_condition.startswith('test_right_palm')
