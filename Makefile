# neckbeard. `make` runs the self-check.

PYTHON  ?= python3
REMOTES ?= $(shell git remote)
VERSION := $(shell $(PYTHON) -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

.DEFAULT_GOAL := check
.PHONY: check excerpts release release-notes help

help: ## list targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

check: ## run the self-check (every case has been seen to fail), and check CASE-STUDIES quotes the gallery as it is
	$(PYTHON) skills/neckbeard/selfcheck.py
	$(PYTHON) bin/excerpts --check

excerpts: ## rewrite the report excerpts in CASE-STUDIES.md from examples/
	$(PYTHON) bin/excerpts

release-notes: ## print this version's CHANGELOG entry, the notes its GitHub Release will carry
	@awk '/^## $(VERSION) /{f=1;next} /^## /{f=0} f' CHANGELOG.md | sed '/./,$$!d' | grep . >/dev/null || { echo "release: CHANGELOG.md has no entry for $(VERSION)" >&2; exit 1; }
	@awk '/^## $(VERSION) /{f=1;next} /^## /{f=0} f' CHANGELOG.md | sed '/./,$$!d'

release: check ## push main and the version tag to every remote, fast-forward only, then publish the GitHub Release
	@$(MAKE) --no-print-directory release-notes >/dev/null
	@test -z "$$(git status --porcelain --untracked-files=no)" || { echo "release: tracked files are modified; commit first"; exit 1; }
	@test "$$(git branch --show-current)" = main || { echo "release: not on main"; exit 1; }
	@grep -q '"version": "$(VERSION)"' .claude-plugin/marketplace.json || { echo "release: marketplace.json does not say $(VERSION)"; exit 1; }
	@git rev-parse -q --verify "refs/tags/v$(VERSION)" >/dev/null || { echo "release: no tag v$(VERSION); run: git tag -a v$(VERSION) -m 'neckbeard $(VERSION)'"; exit 1; }
	@git merge-base --is-ancestor "v$(VERSION)" HEAD || { echo "release: v$(VERSION) is not on main"; exit 1; }
	@for r in $(REMOTES); do \
	  echo "== $$r"; \
	  git push "$$r" main "v$(VERSION)" || { echo "release: $$r refused a fast-forward. Never force from here."; exit 1; }; \
	done
	@# A pushed tag is not a GitHub Release; the repo page shows the newest Release as Latest.
	@if gh release view "v$(VERSION)" >/dev/null 2>&1; then echo "== GitHub Release v$(VERSION) already exists"; \
	else $(MAKE) --no-print-directory release-notes | gh release create "v$(VERSION)" --verify-tag --latest \
	       --title "neckbeard $(VERSION)" --notes-file - && echo "== GitHub Release v$(VERSION) published"; fi
