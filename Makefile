# Local workflow helpers (M37). Authoritative merge gate: GitHub Actions ci / repo-safety.
# Requires POSIX-style make (e.g. Git for Windows, WSL). See DEVELOPMENT.md for raw commands.

.PHONY: help install-dev verify compile test coverage mypy ruff audit ci-local clean api-doc-check performance sbom release-evidence

help:
	@echo "Available targets:"
	@echo "  install-dev   Install pinned dev deps and editable package"
	@echo "  verify        Run repository verifier"
	@echo "  compile       Byte-compile scripts, tests, and src"
	@echo "  test          Run unittest suite (no coverage)"
	@echo "  coverage      Run tests under coverage + JSON + threshold gates"
	@echo "  mypy          Run strict mypy on src/aurora"
	@echo "  ruff          Run ruff check (scripts, tests, src)"
	@echo "  audit         Run pip-audit (full environment)"
	@echo "  ci-local      Local sequence: verify, compile, test, coverage, mypy, ruff, audit"
	@echo "  performance   ARB baseline JSON (M38; evidence only — not a gate)"
	@echo "  sbom          CycloneDX JSON via pip-audit (M38; CI is authoritative)"
	@echo "  release-evidence  coverage + performance + sbom (optional aggregate)"
	@echo "  api-doc-check Check API docs vs __all__ (stdlib helper; not in CI)"
	@echo "  clean         Remove __pycache__, .coverage, and local coverage JSON artifacts"

install-dev:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt
	python -m pip install -e .

verify:
	python scripts/verify_repo_state.py

compile:
	python -m compileall -q scripts tests src

test:
	python -m unittest discover -s tests -v

coverage:
	python -c "import pathlib; pathlib.Path('artifacts').mkdir(parents=True, exist_ok=True)"
	PYTHONPATH=src python -m coverage run --branch -m unittest discover -s tests -v
	python -m coverage report
	python -m coverage json -o artifacts/coverage.json
	python scripts/check_coverage_thresholds.py

mypy:
	mypy src/aurora

ruff:
	ruff check scripts tests src

audit:
	pip-audit

ci-local: verify compile test coverage mypy ruff audit

performance:
	python -c "import pathlib; pathlib.Path('artifacts').mkdir(parents=True, exist_ok=True)"
	PYTHONPATH=src python scripts/measure_arb_performance.py --output artifacts/arb_performance_baseline.json

sbom:
	python -c "import pathlib; pathlib.Path('artifacts').mkdir(parents=True, exist_ok=True)"
	pip-audit -f cyclonedx-json -o artifacts/sbom.cdx.json

release-evidence: coverage performance sbom

api-doc-check:
	python scripts/check_api_docs_exports.py

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [p.unlink(missing_ok=True) for p in [pathlib.Path('coverage.json'), pathlib.Path('.coverage'), pathlib.Path('artifacts/coverage.json')]]"
