# Contributing to PrintPrep

Thanks for considering a contribution! PrintPrep is a small, hobby-scale
open-source project. The bar is "is this useful and does it not break the
existing tests?" — that's it.

## Quick start

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep

python -m venv venv
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate      # Windows

pip install -e ".[dev,web,desktop]"
```

Optional extras you may also want when working on related code:

- `pip install -e ".[merge]"` — boolean union (manifold3d)
- `pip install -e ".[repair]"` — pymeshfix escalation in the `fix` command
- `pip install -e ".[analyze]"` — pymeshlab (Python 3.10+) for self-intersection

## Running tests

```bash
# Python
pytest

# JS viewer geometry helpers (Node 18+)
node --test tests/js/geometry-utils.test.mjs
```

The Python suite has ~57 tests across `tests/test_*.py`. JS has a small
unit-test set for the in-browser geometry utilities. PRs are expected to
keep both green.

## Code style

- **Python:** [`ruff`](https://github.com/astral-sh/ruff) +
  [`black`](https://github.com/psf/black). Line length 100.
  ```bash
  ruff check printprep tests
  black --check printprep tests
  ```
- **JavaScript:** the in-browser code (`printprep/web/static/*.js`) is
  intentionally dependency-free and uses standard ES modules + native
  `node --test`. Keep it that way — no bundler, no transpiler.

## Commit messages

- Imperative, present tense. ("Add foo", not "Added foo" or "Adds foo".)
- First line ≤ 72 chars. Body wrapped at 72.
- Reference issues with `Fixes #123` / `Closes #123` when relevant.

## Pull requests

1. Open against `main`.
2. Describe what changed and why. Screenshots/GIFs for UI changes are very
   welcome.
3. Add tests when you fix a bug or add a feature. "It works on my STL" is
   not enough — turn that STL (or a reduced version) into a fixture.
4. Don't bundle unrelated changes. One PR, one topic.
5. Be patient. This is a side project, not a day job.

## What's in scope

- Better mesh analysis (new failure modes, smarter heuristics).
- Better slicer profile mapping (more slicers, more materials).
- 3D viewer improvements (visualizations, performance).
- Bug fixes, doc fixes, test coverage.

## What's out of scope (for now)

- Cloud features, online services, accounts. PrintPrep stays 100% local.
- A full slicing engine — we *recommend* settings, we don't slice.
- Heavy GUI rewrites (Electron, Qt, etc.). The web UI is the GUI.

## Reporting bugs

Open an issue at https://github.com/omerozgen/printprep/issues with:

- PrintPrep version (`printprep --version`)
- Python version + OS
- A minimal reproduction (an STL or a code snippet)
- What you expected vs. what happened

If you can't share the STL publicly, a screenshot of the analysis output
and the file's `is_watertight` / `body_count` / dimensions is usually
enough to start.

## Security issues

See [SECURITY.md](SECURITY.md). Do **not** open a public issue for a
security-sensitive bug — email the maintainer first.

## License

By contributing, you agree your contribution is licensed under the
[MIT License](LICENSE) of the project.
