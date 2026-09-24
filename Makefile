# neckbeard. `make` runs the self-check.

PYTHON  ?= python3
REMOTES ?= $(shell git remote)
VERSION := $(shell $(PYTHON) -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

.DEFAULT_GOAL := check
.PHONY: check release help

help: ## list targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

check: ## run the self-check (every case has been seen to fail)
	$(PYTHON) skills/neckbeard/selfcheck.py

release: check ## push main and the version tag to every remote, fast-forward only
	@test -z "$$(git status --porcelain --untracked-files=no)" || { echo "release: tracked files are modified; commit first"; exit 1; }
	@test "$$(git branch --show-current)" = main || { echo "release: not on main"; exit 1; }
	@grep -q '"version": "$(VERSION)"' .claude-plugin/marketplace.json || { echo "release: marketplace.json does not say $(VERSION)"; exit 1; }
	@git rev-parse -q --verify "refs/tags/v$(VERSION)" >/dev/null || { echo "release: no tag v$(VERSION); run: git tag -a v$(VERSION) -m 'neckbeard $(VERSION)'"; exit 1; }
	@git merge-base --is-ancestor "v$(VERSION)" HEAD || { echo "release: v$(VERSION) is not on main"; exit 1; }
	@for r in $(REMOTES); do \
	  echo "== $$r"; \
	  git push "$$r" main "v$(VERSION)" || { echo "release: $$r refused a fast-forward. Never force from here."; exit 1; }; \
	done
