# SLSA provenance for neckbeard: research and recommendation

Researched 2026-11-19 for the question: could neckbeard use SLSA provenance, from the OpenSSF "SLSA Generic generator" or from GitHub's own attestations, to add certainty to its inspections? This is research only. No workflow or code changed.

**Recommendation: neither adopt for inspections nor for our own releases now.** One cheap follow-up is worth doing: report, from the target's checked-in workflow files, whether it declares a provenance step. Revisit the rest when Claude Code can check provenance at install time.

## What each tool produces

- **The generic generator** ([slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator)): a signed in-toto statement with a SLSA provenance predicate, in a DSSE envelope, for files your own workflow built. You call its reusable workflow in a separate job and hand it the artifacts' sha256 sums. It signs with the workflow's GitHub OIDC identity through Sigstore and posts every build to the public Rekor transparency log.
- **Its status:** its README says the project is no longer actively maintained and points new users to GitHub artifact attestations. The item was written without that fact.
- **GitHub artifact attestations** ([actions/attest-build-provenance](https://github.com/actions/attest-build-provenance), a wrapper around [actions/attest](https://github.com/actions/attest) since v4, where new work should start): a signed SLSA v1 provenance statement for a file or container image, signed with a short-lived Sigstore certificate and stored in GitHub's attestations API. A reader checks it with `gh attestation verify PATH -R OWNER/REPO`. The job needs `id-token: write`, `contents: read` and `attestations: write`.
- **npm provenance** ([docs](https://docs.npmjs.com/generating-provenance-statements)): `npm publish --provenance` from a GitHub Actions or GitLab CI job on a cloud-hosted runner, with `id-token: write`. It signs through the same Sigstore and OIDC path, links a package to its source and build, and a reader checks it with `npm audit signatures`. It covers only packages published to npm. Neckbeard is not published to npm, so it does not apply to our releases. It applies to a target only when that target ships an npm package, and then it is evidence about that package, not about the plugin's git tree.
- **Which to prefer:** for a file we build and publish ourselves outside npm, GitHub artifact attestations. For an npm package, npm provenance, because `npm audit signatures` is the check npm users already have. The generic generator last, since it is unmaintained.
- **Not confirmed:** which SLSA Build level each one claims. The generator's README calls its output "SLSA3+" without a separate statement, and the GitHub pages I read name no level. Do not quote a level without checking the current SLSA spec and GitHub's docs.

## Cost for a repo like ours

- **Public repos:** both work. Attestations are free on every current plan for a public repo, and the public Sigstore instance is used.
- **Private repos:** GitHub attestations need GitHub Enterprise Cloud and use GitHub's own Sigstore instance. The generic generator refuses a private repo unless you set `private-repository: true`, and then it publishes the repo's name in the public Rekor log. A private repo that must stay unnamed cannot use it.
- **Pinning:** the generator must be referenced by a full tag (`@vX.Y.Z`), not a short tag or a hash, or the build fails.
- **Our release path:** `make release` runs locally. It pushes `release/v<version>` to GitHub, waits for CI on that commit, then pushes `main` and the tag to every remote, deletes the release branch, then creates a GitHub Release with the CHANGELOG notes and no attached files. Both tools need a GitHub Actions job to sign, and need files to attest. We would add a workflow on tag push that builds a source archive of the tag, attests it, and attaches both to the Release. That workflow races with the `gh release create` step at the end of `make release`, so the order of the two would have to be settled first.

## Inspecting other people's releases

- **What neckbeard reads:** a local checkout, or a shallow clone of a git URL (`skills/neckbeard/SKILL.md`, the "Target" bullet under Step 3). A provenance attestation names a built file and its digest. A plugin installed from git has no built file, so there is nothing for the attestation to name, unless the author also publishes a source archive of the tag.
- **Linking the two:** to say "the tree I read is the tree that was attested", neckbeard would download the release archive, run `gh attestation verify` (or `slsa-verifier`) against it, and compare the archive's tree with the checkout. That needs network access, a `gh` login and a new failure mode. It also crosses the line that neckbeard's default reads files and runs nothing (`SECURITY.md`, "The default never executes the target").
- **How common it is:** I found no sign that Anthropic's own marketplace signs or attests plugins. A few community projects (an attested marketplace, supply-chain skills) and several open requests for plugin signing or install-time verification came up in search, and no adoption numbers. Treat it as rare, and unmeasured.
- **When it is missing:** say nothing new. The report already names the commit it read. A missing attestation is the normal case, so it must not colour or lower anything.

## Our own releases

- **Value:** for a plugin that is installed by cloning a tag, the commit is already the identity. An attestation on a tag archive adds a binding from that archive to the workflow that built it, which no installer checks today.
- **Cost:** one workflow file, a release-order change, an extra Release asset, and a standing habit of checking the attestation works.
- **Cat Herder:** the same verdict. The reasoning does not depend on the repo: a Claude Code plugin is installed from a git tag, no installer checks an attestation, and the plugin has no built file to attest. Where a repo is private, attestations also need GitHub Enterprise Cloud, which only strengthens the case for waiting. I did not read Cat Herder's release workflow for this report.
- **Verdict:** low value today. If Claude Code or a marketplace starts verifying provenance at install, adopt GitHub's `actions/attest` (not the generic generator) at that point, for neckbeard first, since it is public.

## Follow-up items for the queue

1. **Report a declared provenance step as a fact.** Read the target's `.github/workflows/*.yml` and say whether any job uses `actions/attest`, `actions/attest-build-provenance` or `slsa-framework/slsa-github-generator`. It is a static read like every other fact in "What it adds": no network, no verification, no colour. Size s.
2. **Revisit attestations for our own releases** when Claude Code or a marketplace verifies provenance at install, or when a release needs an artifact that is not just a tag. Park it with a note, not a date.

## Sources

- [slsa-github-generator generic builder README](https://github.com/slsa-framework/slsa-github-generator/blob/main/internal/builders/generic/README.md): output, tag pinning, private repositories, maintenance status.
- [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance): output, signing, private repositories, plan requirement, `gh attestation verify`.
- [GitHub: using artifact attestations](https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds): permissions and verification commands.
- [attested-delivery/claude-code-plugins](https://github.com/attested-delivery/claude-code-plugins), [a plugin signing request on a third-party mirror of Claude Code's issues](https://claudeissues.com/issue/40775-feature-request-plugin-code-signing-for-supply-chain-integrity) and [an install-time verification request](https://claudeissues.com/issue/77989-feature-request-install-time-verification-hook-for-plugins-skills-content-re-val): what plugin authors and users ask for.
