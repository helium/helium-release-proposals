---
name: release
description: >-
  Mark a Helium Release Proposal as deployed. Updates the HRP status to Released and records
  the deployment date. Use when the user says "the release is deployed", "mark it as released",
  "it's live", "we shipped the release", "deployment is done", or wants to close out an
  approved HRP after the network deployment. Also handles no-change months where no vote
  was needed — use when the user says "no changes this month", "skip this release", or
  "nothing to deploy".
user_invocable: true
---

# HRP Release Skill

You mark a Helium Release Proposal as deployed to the network, recording the actual
release date. Also handles the "no changes this month" shortcut for months that are
skipped without a vote.

## Steps

### 1. Identify the target HRP

- If the user says "no changes" or "skip", find the current skeleton HRP (status: Proposed, no features)
- Otherwise, find the HRP with `status: Approved` (the most recently approved one)
- If the user specifies a month, find that specific HRP file
- Read the full release file

**Status guard:**
- `Proposed` with features → "This HRP hasn't been through the vote process yet. Run `/hrp:vote-open` first."
- `Proposed` without features → this is a no-change month, handle via the skip path (step 2b)
- `Frozen` → "This HRP is still being voted on. Run `/hrp:vote-close` to record the result first."
- `Released` → "This HRP has already been released."

### 2a. Normal release (status: Approved)

Ask the user:
- **Deployment date** — when was the release deployed? Default to today.

Confirm: "Marking HRP {Month Year} as released on {date}. Correct?"

Update frontmatter:
- `status: Released`
- `released-date: {YYYY-MM-DD}`

Post Reddit comment (if `reddit-post-id` exists):
```
**HRP {Month Year} is live**

The {Month Year} release has been deployed to the network.

{one-line summary of what shipped, e.g. "Staked HNT position transfers are now available."}
```

### 2b. No-change month (status: Proposed, no features)

This is a shortcut for months with no protocol changes. Instead of going through the full
vote-open → vote-close → release cycle, you can skip straight to Released.

Confirm: "No changes for HRP {Month Year} — marking as released without a vote. Correct?"

Update frontmatter:
- `status: Released`
- `released-date: {YYYY-MM-DD}` (use the planned release-date or today)

Update README — insert at the top of the vote history list:
```
- HRP {YYYY-MM} had no changes and was not put to vote.
```

No Reddit post — nothing to announce.

### 3. Commit and report

Commit directly to `main`:
- Normal: `Mark HRP {Month Year} as released on {date}`
- No-change: `Mark HRP {Month Year} as released (no changes)`

Include both the release file and README (if changed) in a single commit.

Tell the user:
- HRP status updated to Released
- Released date recorded
- README updated (if no-change month)
- The HRP lifecycle for {Month Year} is complete
