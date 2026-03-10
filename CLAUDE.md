## Repository

Helium Release Proposals (HRPs) — monthly release documents for the Helium network,
governed by community vote per HIP-141. This is a content repo, not a code repo.

## Structure

- `releases/YYYYMMDD-core-devs.md` — Release proposal files (one per month)
- `xxxx-template.md` — Template for new HRP files
- `.claude/plugins/hrp/` — Claude Code plugin for HRP lifecycle automation

## HRP Lifecycle

Status flow: Proposed → Frozen → Approved → Released

- **Proposed**: Active development, features added via PRs
- **Frozen**: Content locked permanently from this point forward
- **Approved**: Vote passed, awaiting deployment
- **Released**: Deployed to network

## Frontmatter

Required fields: release-date, vote-date, authors, status
Optional fields: reddit-post-id, vote-url, vote-summary-url, vote-pr, released-date

## Bot Accounts

- **hiptron** (GitHub) — opens PRs, creates gists
- **HeliumConsoleTeam** (Reddit) — posts announcements
