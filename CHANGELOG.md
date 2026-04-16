# CHANGELOG

All notable development changes for `T000045-hand-laterality-judgment` are documented here.

## [Unreleased] - 2026-04-16

### Added
- Added a Chinese hand laterality judgment task with practice and formal test blocks.
- Added four generated hand-image assets covering back/palm views for left and right hands.
- Added a phase-aware QA/simulation responder that advances instruction screens and answers left/right judgments.

### Changed
- Replaced the scaffold trial logic with a hand-side judgment state machine built around fixation, response, practice feedback, ITI, and break screens.
- Reworked the configs to use `f` and `j` for left/right responses and `space` for continuation screens.
- Updated the README, task metadata, and reference bundle inputs to reflect the new paradigm.

### Fixed
- Removed the placeholder controller import from `src/__init__.py`.
- Aligned the visible screens in `main.py` with `set_trial_context(...)` so QA and plot auditing can trace the full participant flow.
