---
name: vote-open
description: Start the voting process for a Helium Release Proposal. Creates the vote summary gist, opens a PR against helium/helium-vote, updates the HRP status to Voting, and posts a vote reminder to Reddit. Use when the user says "open voting", "start the vote", "create the vote", "put it to vote", "kick off voting", or it's time to submit an HRP for community vote.
user_invocable: true
---

# HRP Vote Open Skill

You help start the community vote for a Helium Release Proposal by creating the vote summary gist, opening a PR against helium/helium-vote, and updating the HRP status.

## Prerequisites

- The HRP must have `status: Proposed` and at least one real feature
- `gh` CLI must be authenticated with access to `helium/helium-vote`
- The user must be ready to finalize — once voting opens, the HRP content is frozen

## Steps

### 1. Identify the target HRP

- Find the active HRP (status: Proposed, upcoming vote-date) or use the month the user specifies
- Read the full release file
- Confirm with the user: "Ready to open voting for HRP {Month Year}? Once the vote PR is merged, the HRP content will be frozen."

### 2. Generate the vote summary

Create a markdown document summarizing the HRP for voters. This is what voters see on heliumvote.com.

Follow this structure (derived from existing vote summaries):

```markdown
# Helium Release Proposal: {YYYY-MM} Summary

{1-2 paragraph summary of what this release contains. For each feature, explain in plain language what it does and why. Keep it accessible — voters aren't all developers.}

## Roadmap Features

{For each feature:}

### {Feature Name}

{2-3 sentence plain-language summary pulled from the Motivation and Implementation sections.}

## Approval Requirements

* This HRP is considered approved if 67% of the voting power is reached.
* This HRP must reach the quorum of 100,000,000 veHNT to be considered valid.

## Governance

To participate in governance, stakeholders can engage through the Community for live events on X and ongoing discussion on Reddit. Monthly Deployers roundtables occur on the third Thursday, with quarterly tokenholder updates also scheduled.
```

For no-change releases, use this shorter form:

```markdown
# Helium Release Proposal: {YYYY-MM} - No Changes

## Summary
This proposal defines the {Month Year} Helium release which contains no changes to the Helium protocol. There will be no planned deployment this month but this vote is a placeholder to allow proxies to continue to provide an active vote status.

## Roadmap Features
"There will be no protocol updates in the {Month Year} Release."

## Approval Requirements

* This HRP is considered approved if 67% of the voting power is reached.
* This HRP must reach the quorum of 100,000,000 veHNT to be considered valid.

## Governance

To participate in governance, stakeholders can engage through the Community for live events on X and ongoing discussion on Reddit. Monthly Deployers roundtables occur on the third Thursday, with quarterly tokenholder updates also scheduled.
```

**Show the generated summary to the user for confirmation before creating the gist.**

### 3. Create the gist

Create a public gist with the vote summary:

```bash
gh gist create --public --desc "HRP {YYYY-MM} Vote Summary" --filename "HRP-{YYYY-MM}-Vote-Summary.md" /path/to/summary.md
```

Note the raw URL of the gist — you'll need it for the proposal entry.

### 4. Generate the helium-proposals.json entry

The entry follows this exact structure:

```json
{
  "name": "Helium Release Proposal: {YYYY-MM}",
  "uri": "{raw gist URL}",
  "maxChoicesPerVoter": 1,
  "tags": ["Release"],
  "choices": [
    {
      "uri": null,
      "name": "For Helium Release {YYYY-MM}"
    },
    {
      "uri": null,
      "name": "Against Helium Release {YYYY-MM}"
    }
  ]
}
```

### 5. Open PR against helium/helium-vote

- Fork or clone `helium/helium-vote` if needed
- Append the new entry to `helium-proposals.json` (add to the end of the array)
- Open a PR:
  - Title: `Add HRP {YYYY-MM} vote proposal`
  - Body: Link to the HRP file and the gist

```bash
gh pr create --repo helium/helium-vote --title "Add HRP {YYYY-MM} vote proposal" --body "$(cat <<'PREOF'
## Summary
Adds the community vote proposal for [HRP {Month Year}](https://github.com/helium/helium-release-proposals/blob/main/releases/{filename}).

Vote summary gist: {gist URL}
PREOF
)"
```

Note the PR number/URL.

### 6. Update the HRP frontmatter

Add tracking fields and update status:

- `status: Frozen`
- `vote-summary-url: {raw gist URL}`
- `vote-pr: {PR URL or helium/helium-vote#NN}`

Commit this change to the release-proposals repo with message: `Freeze HRP {Month Year} for voting`

### 7. Post Reddit update

If the HRP has a `reddit-post-id`, post a vote reminder comment on the existing thread:

```
**Heads up: voting is opening for HRP {Month Year}**

The vote proposal has been submitted and is pending approval. Once the multisig signs off, voting will go live at [heliumvote.com](https://www.heliumvote.com).

Quick recap of what's in this release:

{numbered feature list in plain language}

We'll update this thread when voting is officially live.
```

If no `reddit-post-id`, suggest running `/hrp:post` first.

### 8. Report

Tell the user:
- Gist created (with URL)
- PR opened against helium/helium-vote (with URL)
- HRP status updated to Voting
- Reddit update posted (or reminder to post)
- Next step: a maintainer reviews and merges the vote PR, then the multisig signers approve the on-chain proposal
