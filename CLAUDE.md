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
Optional fields: reddit-post-id, vote-url, vote-summary-url, vote-pr, vote-live-date, released-date, released-txid

## Bot Accounts

- **hiptron** (GitHub) — opens PRs, creates gists
- **HeliumConsoleTeam** (Reddit) — posts announcements

## HRP Plugin Development

The HRP plugin is distributed as a Claude Code marketplace plugin from this repo.
After pushing changes to plugin files on `main`, the local install does NOT auto-update
(known bug — marketplace clone and cache are never refreshed). To pick up changes:

```bash
git -C ~/.claude/plugins/marketplaces/helium-release-proposals pull origin main
rm -rf ~/.claude/plugins/cache/helium-release-proposals
# then: /plugin install hrp && /reload-plugins
```

### Plugin structure

- Marketplace manifest: `.claude-plugin/marketplace.json` (repo root)
- Plugin manifest: `.claude/plugins/hrp/.claude-plugin/plugin.json`
- Skills: `.claude/plugins/hrp/skills/<name>/SKILL.md` (must be subdirectory + SKILL.md, not flat files)
- Scripts: `.claude/plugins/hrp/scripts/`
