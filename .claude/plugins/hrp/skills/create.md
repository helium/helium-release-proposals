---
name: create
description: Create a new Helium Release Proposal for a given month. Scaffolds the release file with computed dates, creates a branch, and opens a PR. Use when the user wants to create a new HRP, start the next month's release, or scaffold a release proposal.
user_invocable: true
---

# HRP Create Skill

You scaffold a new Helium Release Proposal file and open a PR for it.

## Steps

### 1. Determine the target month

- If the user specifies a month (e.g. "May 2026"), use that
- If not, determine the next month that doesn't have a release file yet by listing `releases/` and finding the gap
- **Always confirm the target month with the user before proceeding**

### 2. Compute dates

**Release date**: First Wednesday of the target month. If that date falls on a US holiday (Jan 1, Jul 4, Dec 25, etc.), use the following Wednesday.

**Vote date**: 10 days before the release date.

**File date**: The release date in YYYYMMDD format, used for the filename.

Show the computed dates to the user and ask for confirmation. They may want to adjust for scheduling reasons.

### 3. Check for conflicts

- Check if `releases/YYYYMMDD-core-devs.md` already exists
- If it does, tell the user and stop — they should use the existing file
- Also check if any other file exists for the same month (different date) to avoid duplicates

### 4. Create the release file

Create `releases/YYYYMMDD-core-devs.md` with this content (no feature sections — those get added by contributors via separate PRs):

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

1.

---
```

Important formatting notes:
- Summary dates should use natural language (e.g. "May 7th, 2026", "April 27th")
- The Roadmap Features list starts with a single empty `1.` — contributors will fill this in
- No feature sections are included — they arrive via separate PRs
- Do NOT include template TODO blocks or placeholder feature sections

### 5. Create branch and PR

- Create a branch named `hrp/{YYYY-MM}` (e.g. `hrp/2026-05`)
- Commit the new file with message: `Add HRP {Month Year} release file`
- Push and open a PR with:
  - Title: `HRP {Month Year}`
  - Body: Summary of the release dates and that the file is ready for feature contributions

### 6. Report

Tell the user:
- The file was created and PR opened
- The release date and vote date
- Next step: contributors can now open PRs adding features to this file
