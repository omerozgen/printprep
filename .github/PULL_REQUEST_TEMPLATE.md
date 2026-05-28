### What this changes

<!-- One or two sentences. Why, not just what. -->

### Test plan

<!-- How did you verify this? Pytest output, manual repro steps, screenshots
     of the 3D viewer, etc. -->

- [ ] `pytest` passes locally
- [ ] `node --test tests/js/geometry-utils.test.mjs` passes (if you touched the viewer)
- [ ] I added tests for the new behavior (if it's a user-visible change)

### Related issues

<!-- Closes #123 / Refs #456 -->

### Checklist

- [ ] My change keeps PrintPrep local-first (no cloud calls, no telemetry).
- [ ] I updated CHANGELOG.md under `## [Unreleased]`.
- [ ] I updated the README / docs if user-visible behavior changed.
