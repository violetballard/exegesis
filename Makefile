SHELL := /usr/bin/env bash

.DEFAULT_GOAL := help

.PHONY: help setup scope-check format format-check lint build typecheck test run ci

help:
	@echo "Developer workflow targets:"
	@echo "  make setup        - verify required local toolchain"
	@echo "  make scope-check  - enforce branch file ownership policy"
	@echo "  make format       - apply formatting"
	@echo "  make format-check - verify formatting without writing"
	@echo "  make lint         - run lint checks"
	@echo "  make build        - fast build/compile verification"
	@echo "  make typecheck    - run typecheck/compile checks"
	@echo "  make test         - run test suite"
	@echo "  make run          - run app entrypoint"
	@echo "  make ci           - CI entrypoint (setup + format-check + lint + build + typecheck + test)"

setup:
	@./scripts/setup.sh

scope-check:
	@./scripts/scope-check.sh

format:
	@./quality-format.sh

format-check:
	@./scripts/format-check.sh

lint:
	@./scripts/lint.sh

build:
	@./scripts/build.sh

typecheck:
	@./typecheck-test.sh

test:
	@./scripts/test.sh

run:
	@./scripts/run.sh

ci:
	@./scripts/ci.sh
