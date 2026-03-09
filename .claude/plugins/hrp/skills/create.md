---
name: create
description: Create a new Helium Release Proposal for a given or upcoming month. Scaffolds the release file with computed dates, creates a branch, and opens a PR. Use this skill whenever the user wants to start a new HRP, set up next month's release, create a release proposal, or says things like "new HRP", "start the May release", "set up next month's HRP", or "create a release proposal".
user_invocable: true
---

# HRP Create Skill

You scaffold a new Helium Release Proposal file and open a PR for it. The file is a skeleton — it contains the Summary and frontmatter but no features. Features get added by contributors via separate PRs.

## Steps

### 1. Determine the target month

- If the user specifies a month (e.g. "May 2026"), use that
- If not, list files in `releases/` and find the next month that doesn't have one yet
- **Always confirm the target month with the user before proceeding**

### 2. Compute dates

**Release date**: First Wednesday of the target month.
- If that Wednesday falls on a US holiday (Jan 1, Jul 4, Nov ~fourth Thursday, Dec 25, Jan 2 if New Year's week), use the following Wednesday.
- Examples: May 2026 → Wed May 6, June 2026 → Wed June 3

**Vote date**: 10 days before the release date.
- Example: release May 6 → vote April 26

**Filename date**: The release date in YYYYMMDD format (e.g. `20260506`).

Show the user: "Release date: May 6, 2026. Vote date: April 26, 2026. Look right?"

Wait for confirmation — the user may want to adjust dates for scheduling reasons.

### 3. Check for conflicts

- Check if `releases/YYYYMMDD-core-devs.md` already exists for the computed date
- Also check if any release file exists for the same month (a different date) — e.g. if `20260501-core-devs.md` exists, that month is taken
- If a file exists, tell the user and stop

### 4. Create the release file

Create `releases/YYYYMMDD-core-devs.md` with exactly this structure:

```markdown
---
release-date: {YYYY-MM-DD}
vote-date: {YYYY-MM-DD}
authors:
  - Helium Core Developers
status: Proposed
---

# Helium Release Proposal {Month Year}

## Summary

This document defines the release that will be deployed on or before {Month Dth, Year}. As features are discussed in the community and developed by Helium Core Developers, this release document will be updated with context and explicit details on implementation.

Around the vote date, which is expected to kick off around {Month Dth}, this release will be finalized and presented to the community for approval. Note that all features that are not code complete will be moved to a future release or removed prior to vote.

---

## Roadmap Features

---
```

Formatting rules:
- Summary dates use natural language: "May 6th, 2026", "April 26th"
- Ordinals: 1st, 2nd, 3rd, 4th–20th, 21st, 22nd, 23rd, etc.
- No Roadmap Features list items — the section is empty until contributors add features
- No feature sections, no TODO blocks, no placeholder content
- End with `---` after Roadmap Features

### 5. Create branch and PR

- Always branch from `main`: `git checkout -b hrp/{YYYY-MM} main`
- Commit the new file: `Add HRP {Month Year} release file`
- Push with `-u` flag and open a PR:

Title: `HRP {Month Year}`

Body:
```
## Summary
- Release date: {Month Dth, Year}
- Vote date: {Month Dth, Year}
- Status: Proposed — waiting for feature contributions

This is the skeleton release file for {Month Year}. Contributors can now open PRs to add features.
```

### 6. Report

Tell the user:
- The file path and PR link
- Release date and vote date
- Next step: contributors open PRs adding features to this file, and those PRs can be checked with `/hrp:review`
