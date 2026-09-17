.DEFAULT_GOAL := help
.PHONY: help bootstrap apply check update deps lint test

help:
	@printf '%s\n' 'bootstrap  Prepare prerequisites and apply configuration' 'apply      Install missing packages and apply settings' 'check      Preview configuration (requires bootstrap prerequisites)' 'update     Upgrade declared Homebrew packages only' 'deps       Install pinned tooling, without configuring macOS' 'lint       Run static checks' 'test       Run isolated regression tests'

bootstrap:
	bash scripts/bootstrap.sh $(ARGS)

deps:
	bash scripts/deps.sh

apply:
	bash scripts/run.sh apply $(ARGS)

check:
	bash scripts/run.sh check $(ARGS)

update:
	bash scripts/run.sh update $(ARGS)

lint:
	.venv/bin/yamllint .
	.venv/bin/ansible-lint
	.venv/bin/ansible-playbook main.yml --syntax-check
	bash -n scripts/bootstrap.sh scripts/deps.sh scripts/run.sh

test:
	.venv/bin/python -m unittest discover -s tests -v
