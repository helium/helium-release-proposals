---
name: vote-close
description: >-
  Record the result of a Helium Release Proposal community vote. Updates the HRP status to
  Approved (or back to Proposed if the vote failed), adds the vote URL, updates the README
  with the result, and posts a Reddit comment. Use when the user says "the vote passed",
  "record the vote result", "close the vote", "the vote is done", "update the HRP with
  the vote result", or mentions a heliumvote.com URL for an HRP. Also handles cancelling
  a vote that never started (reverting Frozen back to Proposed).
user_invocable: true
---

# HRP Vote Close Skill

You record the outcome of a Helium Release Proposal community vote and update all the
tracking surfaces — the release file, the README, and the Reddit thread.

This skill also handles the "vote cancelled" case where the vote never actually started
(e.g. the helium-vote PR was rejected or the multisig didn't sign).

## Steps

### 1. Identify the target HRP

- Find the HRP with `status: Frozen` — this is the one with an active or recently completed vote
- If the user specifies a month, find that specific HRP file
- Read the full release file

**Status guard:** This skill only operates on `Frozen` HRPs. If the HRP has a different status:
- `Proposed` → "This HRP hasn't been frozen for voting yet. Run `/hrp:vote-open` first."
- `Approved` → "This HRP's vote result has already been recorded."
- `Released` → "This HRP has already been released."

### 2. Look up vote results from chain

Run the lookup script to get the vote URL and results directly from the on-chain proposal:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/lookup-vote-url.sh" --month "{YYYY-MM}" --results
```

This returns JSON with `url`, `publicKey`, `forPercent`, `againstPercent`, and `totalVeHNT`.

**If the script returns an error** (proposal not found or RPC failure), fall back to asking the user for the vote URL and percentage manually.

**If the frontmatter already has a `vote-url`**, use that instead of querying the chain.

### 3. Determine the outcome

Use the on-chain results to determine the outcome automatically:
- **forPercent >= 67** → vote passed (meets the approval threshold)
- **forPercent < 67** → vote failed

Present the results to the user for confirmation: "The on-chain vote shows {forPercent}% approval ({totalVeHNT} veHNT). Record this as [passed/failed]?"

If the user says the vote was **cancelled** (never went live), skip to step 4c.

### 4a. If vote passed

The vote URL and percentage come from the lookup script. The date defaults to today unless the user specifies otherwise.

Update frontmatter:
- `status: Approved`
- `vote-url: {heliumvote.com URL}`

Update README — insert a new line into the vote history list. The list lives between the intro paragraph and the "How to Contribute" section. Insert at the top of the list (newest first), matching the existing format exactly:

```
- HRP {YYYY-MM} passed with [{X}% of the vote]({vote-url}) on {Month Dth Year}
```

Nudge the user to post a Reddit comment (if `reddit-post-id` exists). Provide:
1. A direct link to the thread: `https://www.reddit.com/comments/{id}/` (strip `t3_` prefix from the post ID)
2. The comment text in a fenced code block so they can copy-paste it:

```
**HRP {Month Year} passed!**

The community approved this release with {X}% of the vote. Deployment is expected within the next few days.

Thanks to everyone who participated in the vote!

[Vote results]({vote-url})
```

### 4b. If vote failed

Same data sources as 4a (URL, percentage from lookup script).

Update frontmatter:
- `status: Proposed` (reverts to allow further changes)
- `vote-url: {heliumvote.com URL}` (kept for historical record)
- Remove `vote-summary-url` and `vote-pr` fields

Update README — same insertion point as 4a:

```
- HRP {YYYY-MM} failed with [{X}% of the vote]({vote-url}) on {Month Dth Year}
```

Nudge the user to post a Reddit comment (same pattern as 4a):

```
**HRP {Month Year} did not pass**

The community vote concluded with {X}% approval. The proposal has been reverted to Proposed status for further discussion and revision.

[Vote results]({vote-url})
```

### 4c. If vote cancelled

No vote URL, percentage, or date needed.

Update frontmatter:
- `status: Proposed` (reverts to allow further changes)
- Remove `vote-summary-url` and `vote-pr` fields

Do **not** update the README — nothing to record if no vote happened.

No Reddit comment — unless the user specifically asks for one.

### 5. Commit and report

Commit directly to `main` (the release file should already be on main by this point). Include both the release file and README (if changed) in a single commit:

- Passed: `Record HRP {Month Year} vote result: approved with {X}%`
- Failed: `Record HRP {Month Year} vote result: failed with {X}%`
- Cancelled: `Revert HRP {Month Year} to Proposed (vote cancelled)`

Tell the user:
- What was updated
- Reddit comment posted (or skipped)
- Next step:
  - Passed: "Deploy the release, then run `/hrp:release` to record the deployment date."
  - Failed: "The HRP is back in Proposed status. You can revise it and run `/hrp:vote-open` again when ready."
  - Cancelled: "The HRP is back in Proposed status. The vote artifacts (gist, helium-vote PR) may need manual cleanup."
