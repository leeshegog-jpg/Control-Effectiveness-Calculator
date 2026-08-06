# ADR-001: Release Tags Are Immutable

**Status:** Accepted (2026-08-05)
**Context:** `v1.1.0-R0` is the first tagged release baseline of the repository — the point R1 and all subsequent work builds from. Without an explicit rule, a tag could later be re-pointed (e.g. `git tag -f`) to "fix" something retroactively, which destroys the audit trail this project has otherwise been careful to maintain (Design Baseline governance, ACR process, R0 exit review).
**Decision:** Once created and pushed, a release tag (`vX.Y.Z-RN` pattern) is never moved, deleted, or re-pointed. Any defect discovered in a tagged commit is fixed forward — a new branch, a normal PR, a new commit — never by rewriting history under the existing tag. If a tag was created in error, it is documented as superseded, not silently corrected.
**Consequences:** Makes tags trustworthy as fixed reference points for audits, comparisons, and rollback decisions. Means a known defect in `v1.1.0-R0` stays visible in that tag's tree until fixed forward in a later commit/tag — this is intentional; hiding it by rewriting the tag would be worse.
