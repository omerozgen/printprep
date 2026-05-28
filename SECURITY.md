# Security Policy

## Supported versions

PrintPrep is pre-1.0. Only the **latest released version** on `main` gets
security fixes. There is no LTS branch.

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security-sensitive bugs.**

Instead, email the maintainer privately via the address in
[`pyproject.toml`](pyproject.toml) (`authors[0].email`), or use GitHub's
private security advisory feature:

→ https://github.com/omerozgen/printprep/security/advisories/new

When reporting, please include:

- A clear description of the issue
- Steps to reproduce (a minimal repro is ideal)
- The PrintPrep version, Python version, and OS
- Your assessment of the impact (info disclosure, RCE, DoS, etc.)
- Any suggested fix, if you have one

You should get an acknowledgement within **7 days**. After a fix lands,
you'll be credited in the release notes unless you'd rather stay
anonymous.

## Threat model

PrintPrep is designed as a **local-first** tool. It assumes:

- It runs on the user's own machine.
- The web UI binds to `127.0.0.1` by default. The user has to explicitly
  pass `--host 0.0.0.0` to expose it to the LAN, and **doing so is
  expected to be inside a trusted network**. There is no authentication.
- STL files come from the user. We do not sandbox parsing — a malicious
  STL could in principle exploit a bug in `trimesh` or `numpy`. We
  follow upstream security advisories but cannot pre-empt them.

If you deploy PrintPrep on a shared / public-facing host, **that is
unsupported** and you do so at your own risk. Put it behind a reverse
proxy with authentication if you absolutely must.

## What is *not* a vulnerability

- "I uploaded a malformed STL and the analyzer raised an exception." —
  expected; the API returns 400.
- "`--host 0.0.0.0` has no auth." — by design; see threat model above.
- Issues in transitive dependencies — please report those upstream
  first; PrintPrep will pick up the fix on the next release.

## Hardening tips for self-hosters

If you really want to host the web UI for multiple users (against our
advice), at minimum:

- Run behind nginx/Caddy with HTTP basic auth or OIDC.
- Restrict upload size at the reverse-proxy layer (PrintPrep does not
  cap it by default — a future release will).
- Run the process as an unprivileged user, in a container if possible.
- Mount a small writable tmpfs for `/tmp` — uploads are persisted briefly
  to a temp file during analysis.
