# Security

## Supported versions

Security-sensitive fixes are expected to land on the **current default branch** unless a release process explicitly publishes versioned artifacts (see project record in [`docs/aurora.md`](docs/aurora.md)).

## Reporting a vulnerability

Please report security issues through **[GitHub Security Advisories](https://github.com/m-cahill/aurora/security/advisories)** for this repository when that mechanism is available, so the report can remain private until resolved.

If advisories are not available, contact the maintainers through a **private** channel suitable for security disclosure.

**Do not** open a public issue for an undisclosed vulnerability.

Runtime code in this repository is **stdlib-only**; development dependencies are pinned in [`requirements-dev.txt`](requirements-dev.txt). Supply-chain posture for those tools is a separate maintenance concern.

## Code of conduct

For harassment or other community conduct concerns, see [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
