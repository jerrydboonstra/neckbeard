# neckbeard. `make` runs the self-check.

PYTHON  ?= python3
# Every remote a release goes to: origin (GitHub, whose Actions run the self-check) and any MIRRORS. A fixed
# list, never `git remote`, which would also push main into whatever else the checkout has (a work queue, say).
# This machine's own setup lives in local.mk, which git ignores: MIRRORS (more remotes a release pushes to) and
# HOSTS (machines `make deploy` reaches over plain ssh, besides this one).
MIRRORS :=
HOSTS :=
-include local.mk
REMOTES := origin $(MIRRORS)
VERSION := $(shell $(PYTHON) -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

.DEFAULT_GOAL := check
.PHONY: check excerpts release release-notes deploy help

help: ## list targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

check: ## run the self-check (every case has been seen to fail), and check CASE-STUDIES quotes the gallery as it is
	$(PYTHON) skills/neckbeard/selfcheck.py
	$(PYTHON) tools/excerpts --check
	$(PYTHON) tools/test_deploy.py

excerpts: ## rewrite the report excerpts in CASE-STUDIES.md from examples/
	$(PYTHON) tools/excerpts

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

deploy: ## bring this machine and every host in HOSTS to main as released, then print what each one runs
	@test "$$(git branch --show-current)" = main || { echo "deploy: not on main"; exit 1; }
	@sha=$$(git rev-parse HEAD); \
	for r in $(REMOTES); do \
	  test "$$(git ls-remote "$$r" refs/heads/main | cut -f1)" = "$$sha" || { echo "deploy: $$r's main isn't $$sha; run make release first"; exit 1; }; \
	done; \
	fail=0; \
	bash tools/deploy-host.sh "$(VERSION)" "$$sha" || fail=1; \
	for h in $(HOSTS); do \
	  ssh "$$h" bash -s -- "$(VERSION)" "$$sha" < tools/deploy-host.sh || fail=1; \
	done; \
	exit $$fail
