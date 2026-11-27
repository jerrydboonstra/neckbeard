# neckbeard. `make` runs the self-check.

PYTHON  ?= python3
# Every remote a release goes to: origin (GitHub, whose Actions run the self-check) and any MIRRORS. A fixed
# list, never `git remote`, which would also push main into whatever else the checkout has (a work queue, say).
# This machine's own setup lives in local.mk, which git ignores: MIRRORS (more remotes a release pushes to) and
# HOSTS (machines `make deploy` reaches over plain ssh, besides this one), PRIVATE_WORDS (a file of words, one a line, that
# `make release` refuses to push a tree holding; see tools/guard.sh) and POST_DEPLOY (a command `make deploy` runs
# once every host has deployed; empty by default, and with $(VERSION) available to it).
MIRRORS :=
HOSTS :=
PRIVATE_WORDS :=
POST_DEPLOY :=
# deploy runs post-deploy through this variable, not a literal $(MAKE): make runs a recipe line holding $(MAKE) even under -n,
# and that line would then deploy for real.
RUN_POST_DEPLOY = $(MAKE) --no-print-directory post-deploy VERSION=$(VERSION)
-include local.mk
REMOTES := origin $(MIRRORS)
# The public GitHub repo: the published report and the slim plugin copy's README link to it.
GITHUB_REPO := jerrydboonstra/neckbeard
VERSION := $(shell $(PYTHON) -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")

.DEFAULT_GOAL := check
.PHONY: \
	check \
	deploy \
	excerpts \
	guard \
	help \
	mutate \
	post-deploy \
	release \
	release-notes \
	report \
	report-check \
	slim-push

help: ## list targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

check: ## run the self-check (every case has been seen to fail), and check README and CASE-STUDIES quote the reports as they are
	tools/check-no-bin
	$(PYTHON) skills/neckbeard/selfcheck.py
	$(PYTHON) tools/excerpts --check
	@for t in tools/test_*.py; do echo "$$t"; $(PYTHON) $$t || exit 1; done

mutate: ## break the inventory*.py modules a few hundred ways and list the self-check cases no break makes fail (heavy: run it under testslot on a test host)
	$(PYTHON) tools/mutate-selfcheck --jobs 10
	$(PYTHON) tools/mutate-selfcheck --targeted

excerpts: ## rewrite the report excerpts in README.md and CASE-STUDIES.md from the reports they quote
	$(PYTHON) tools/excerpts

report: ## regenerate docs/neckbeard-report.md, neckbeard's own published report (no reader, no verdict, no model call), and print its badge line (and refresh the README excerpt of it)
	tools/vet . docs/neckbeard-report.md --facts --release-tag v$(VERSION) --repo https://github.com/$(GITHUB_REPO)
	@$(PYTHON) tools/excerpts >/dev/null   # the README's excerpt of this report, so the badge line stays the last output

report-check: ## fail unless the report in the tagged tree names the tagged version (a tag set before the report commit is refused); REF=HEAD checks the tree before the tag exists
	@if [ -z "$(REF)" ]; then git rev-parse -q --verify "refs/tags/v$(VERSION)" >/dev/null || { echo "report-check: no tag v$(VERSION)"; exit 1; }; fi
	@d=$$(mktemp -d) && trap '[ -n "$$d" ] && rm -rf "$$d"' EXIT && git archive "$(or $(REF),v$(VERSION))" | tar -x -C "$$d" && \
	  tools/vet --check "$$d/docs/neckbeard-report.md" "$$d" && \
	  { grep -E '^`[0-9]{4}-[0-9]{2}-[0-9]{2}` · .* · made by neckbeard ' "$$d/docs/neckbeard-report.md" | head -1 | grep -qF ' @ `v$(VERSION)`' || { echo "report-check: the header of the tagged report must name the tag, @ \`v$(VERSION)\`, not a commit or another tag"; exit 1; }; }

release-notes: ## print this version's CHANGELOG entry, the notes its GitHub Release will carry
	@awk '/^## $(VERSION) /{f=1;next} /^## /{f=0} f' CHANGELOG.md | sed '/./,$$!d' | grep . >/dev/null || { echo "release: CHANGELOG.md has no entry for $(VERSION)" >&2; exit 1; }
	@awk '/^## $(VERSION) /{f=1;next} /^## /{f=0} f' CHANGELOG.md | sed '/./,$$!d'

guard: ## refuse when a tracked file holds a word from the PRIVATE_WORDS list (empty list: skip; `make release` requires one)
	@GUARD_WORDS="$(PRIVATE_WORDS)" bash tools/guard.sh

release: check ## push release/v<version> to GitHub, wait for CI on it, then tag, push main and the tag to every remote (fast-forward only) and delete release/v<version>, then publish the GitHub Release and the slim `plugin` branch
	@$(MAKE) --no-print-directory release-notes >/dev/null
	@test -z "$$(git status --porcelain --untracked-files=no)" || { echo "release: tracked files are modified; commit first"; exit 1; }
	@test "$$(git branch --show-current)" = main || { echo "release: not on main"; exit 1; }
	@grep -q '"version": "$(VERSION)"' .claude-plugin/marketplace.json || { echo "release: marketplace.json does not say $(VERSION)"; exit 1; }
	@if git rev-parse -q --verify "refs/tags/v$(VERSION)" >/dev/null; then \
	  git merge-base --is-ancestor "v$(VERSION)" HEAD || { echo "release: v$(VERSION) is not on main"; exit 1; }; \
	  $(MAKE) --no-print-directory report-check || { echo "release: the report in v$(VERSION) is stale; make report, commit, and release again"; exit 1; }; \
	else \
	  $(MAKE) --no-print-directory report-check REF=HEAD || { echo "release: the report is stale; make report, commit, and release again"; exit 1; }; \
	fi
	@GUARD_REQUIRE_WORDS=1 $(MAKE) --no-print-directory guard
	@VERSION=$(VERSION) REMOTES="$(REMOTES)" bash tools/release-push
	@# A pushed tag is not a GitHub Release; the repo page shows the newest Release as Latest.
	@if gh release view "v$(VERSION)" >/dev/null 2>&1; then echo "== GitHub Release v$(VERSION) already exists"; \
	else $(MAKE) --no-print-directory release-notes | gh release create "v$(VERSION)" --verify-tag --latest \
	       --title "neckbeard $(VERSION)" --notes-file - && echo "== GitHub Release v$(VERSION) published" || \
	     { echo "release: the GitHub Release failed; main and the tag stand. Create it, then run: make slim-push TAG=v$(VERSION)"; exit 1; }; fi
	@# The plugin directory's branch. Without --strict it only warns: the release above stands either way.
	@REMOTES="$(REMOTES)" $(PYTHON) tools/slim-tree publish v$(VERSION) --repo $(GITHUB_REPO)

slim-push: ## publish TAG's slim plugin copy (default: this version's) as branch `plugin` on every release remote
	@REMOTES="$(REMOTES)" $(PYTHON) tools/slim-tree publish $(or $(TAG),v$(VERSION)) --repo $(GITHUB_REPO) --strict

deploy: ## bring the plugin export (~/.claude/plugin-src/neckbeard) on this machine and every host in HOSTS to main as released, then print what each one runs
	@test "$$(git branch --show-current)" = main || { echo "deploy: not on main"; exit 1; }
	@sha=$$(git rev-parse HEAD); \
	for r in $(REMOTES); do \
	  test "$$(git ls-remote "$$r" refs/heads/main | cut -f1)" = "$$sha" || { echo "deploy: $$r's main isn't $$sha; run make release first"; exit 1; }; \
	done; \
	fail=0; \
	bash tools/deploy-host.sh "$(VERSION)" "$$sha" "$$(git remote get-url origin)" || fail=1; \
	for h in $(HOSTS); do \
	  ssh "$$h" bash -s -- "$(VERSION)" "$$sha" < tools/deploy-host.sh || fail=1; \
	done; \
	if [ $$fail -eq 0 ]; then \
	  $(RUN_POST_DEPLOY) || { echo "deploy: post-deploy failed"; fail=1; }; \
	fi; \
	exit $$fail

post-deploy: ## run POST_DEPLOY (set in local.mk; empty by default) and do nothing when it is empty; `make deploy` runs it last
	$(if $(strip $(POST_DEPLOY)),@$(POST_DEPLOY),@:)
