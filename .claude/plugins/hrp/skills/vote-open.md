---
name: vote-open
description: Start the voting process for a Helium Release Proposal. Creates the vote summary gist, opens a PR against helium/helium-vote, updates the HRP status to Voting, and posts a vote reminder to Reddit. Use when the user says "open voting", "start the vote", "create the vote", "put it to vote", "kick off voting", or it's time to submit an HRP for community vote.
user_invocable: true
---

# HRP Vote Open Skill

You help start the community vote for a Helium Release Proposal by creating the vote summary gist, opening a PR against helium/helium-vote, and updating the HRP status.

## Prerequisites

- The HRP must have `status: Proposed` and at least one real feature
- hiptron GitHub token must be configured (see Credential setup below)
- The user must be ready to finalize — once voting opens, the HRP content is frozen

## GitHub commands

All GitHub API commands (gists, PRs, pushes) run as the **hiptron** user via the wrapper script:

```
${CLAUDE_PLUGIN_ROOT}/scripts/gh-hiptron.sh
```

Use this instead of bare `gh` for every GitHub operation in this skill.

## Steps

### 1. Identify the target HRP

- Find the active HRP (status: Proposed, upcoming vote-date) or use the month the user specifies
- Read the full release file
- Confirm with the user: "Ready to open voting for HRP {Month Year}? Once the vote PR is merged, the HRP content will be frozen."

### 2. Generate the vote summary

Create a markdown document summarizing the HRP for voters. This is what voters see on heliumvote.com. The format is concise — just a summary paragraph, the feature list, and boilerplate sections.

**Template for releases with features:**

```markdown
# Helium Release Proposal: {YYYY-MM}

## Summary
This proposal defines the {Month Year} Helium release that will be deployed after a successful outcome of this vote. The linked release notes have context and explicit details on implementation.

- Authors: Helium Core Developers
- Full release note text: [{YYYY-MM}](https://github.com/helium/helium-release-proposals/blob/main/releases/{filename})

## Roadmap Features
{numbered list of feature names — just the names, no descriptions}

## Approval Requirements

* This HRP is considered approved if 67% of the voting power is reached.
* This HRP must reach the quorum of 100,000,000 veHNT to be considered valid.

***

## Governance

To participate in governance, please join the Community for live events on [X](https://x.com/helium) and ongoing discussion on [Reddit](https://reddit.com/r/HeliumNetwork/). Governance related events will be the monthly Deployers roundtable on 3rd Thursday of each month and the quarterly tokenholder updates.
```

**Template for no-change releases:**

```markdown
# Helium Release Proposal: {YYYY-MM} - No Changes

## Summary
This proposal defines the {Month Year} Helium release which contains no changes to the Helium protocol. There will be no planned deployment this month but this vote is a placeholder to allow proxies to continue to provide an active vote status.

## Roadmap Features
"There will be no protocol updates in the {Month Year} Release."

## Approval Requirements

* This HRP is considered approved if 67% of the voting power is reached.
* This HRP must reach the quorum of 100,000,000 veHNT to be considered valid.

***

## Governance

To participate in governance, please join the Community for live events on [X](https://x.com/helium) and ongoing discussion on [Reddit](https://reddit.com/r/HeliumNetwork/). Governance related events will be the monthly Deployers roundtable on 3rd Thursday of each month and the quarterly tokenholder updates.
```

**Concrete example** — here's what the April 2026 vote summary would look like:

```markdown
# Helium Release Proposal: 2026-04

## Summary
This proposal defines the April 2026 Helium release that will be deployed after a successful outcome of this vote. The linked release notes have context and explicit details on implementation.

- Authors: Helium Core Developers
- Full release note text: [2026-04](https://github.com/helium/helium-release-proposals/blob/main/releases/20260401-core-devs.md)

## Roadmap Features
1. Staked HNT Position Transfers

## Approval Requirements

* This HRP is considered approved if 67% of the voting power is reached.
* This HRP must reach the quorum of 100,000,000 veHNT to be considered valid.

***

## Governance

To participate in governance, please join the Community for live events on [X](https://x.com/helium) and ongoing discussion on [Reddit](https://reddit.com/r/HeliumNetwork/). Governance related events will be the monthly Deployers roundtable on 3rd Thursday of each month and the quarterly tokenholder updates.
```

**Show the generated summary to the user for confirmation before creating the gist.**

### 3. Create the gist

Create a public gist with the vote summary:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/gh-hiptron.sh" gist create --public --desc "HRP {YYYY-MM} Vote Summary" --filename "HRP-{YYYY-MM}-Vote-Summary.md" /path/to/summary.md
```

Note the raw URL of the gist — you'll need it for the proposal entry.

### 4. Open PR against helium/helium-vote

Use the `vote-pr.sh` script — it handles everything via the GitHub API as hiptron (no local clone needed):

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/vote-pr.sh" \
  --month "{YYYY-MM}" \
  --gist-url "{raw gist URL}" \
  --hrp-file "releases/{filename}"
```

The script fetches `helium-proposals.json`, appends the vote entry, creates a branch, commits, and opens the PR. It prints the PR URL on success.

Note the PR URL from the output.

### 5. Update the HRP frontmatter

Add tracking fields and update status:

- `status: Frozen`
- `vote-summary-url: {raw gist URL}`
- `vote-pr: {PR URL or helium/helium-vote#NN}`

Commit this change to the release-proposals repo with message: `Freeze HRP {Month Year} for voting`

### 6. Post Reddit update

If the HRP has a `reddit-post-id`, post a vote reminder comment on the existing thread:

```
**Heads up: voting is opening for HRP {Month Year}**

The vote proposal has been submitted and is pending approval. Once the multisig signs off, voting will go live at [heliumvote.com](https://www.heliumvote.com).

Quick recap of what's in this release:

{numbered feature list in plain language}

We'll update this thread when voting is officially live.
```

If no `reddit-post-id`, suggest running `/hrp:post` first.

### 7. Report

Tell the user:
- Gist created (with URL)
- PR opened against helium/helium-vote (with URL)
- HRP status updated to Frozen
- Reddit update posted (or reminder to post)
- Next step: a maintainer reviews and merges the vote PR, then the multisig signers approve the on-chain proposal

