---
name: post
description: Post or update a Helium Release Proposal on Reddit (r/HeliumNetwork) as HeliumConsoleTeam. Use this skill whenever the user mentions posting to Reddit, announcing an HRP, updating the subreddit, sending a vote reminder, or notifying the community about a release proposal — even if they just say "post it" or "let people know". Also triggers for "announce on Reddit", "update the thread", "Reddit post", or "subreddit".
user_invocable: true
---

# HRP Reddit Post Skill

You help post Helium Release Proposals to r/HeliumNetwork. Each HRP gets **one Reddit post** (the initial announcement). All subsequent updates (new features added, vote reminders, etc.) are posted as **comments on that original post** to keep discussion in one thread.

The Reddit post ID is tracked in the release file's YAML frontmatter (`reddit-post-id` field), so it's visible in the repo and any contributor can post follow-ups.

## Script location

`${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py`

## Steps

### 1. Identify the target HRP

- Look at files in `releases/` to find the active HRP (status: Proposed, with a future or recent vote-date)
- If the user specifies a month, find that specific HRP file
- Read the full HRP file contents
- Note the release filename (e.g. `releases/20260401-core-devs.md`)

**If the HRP has no real features** (empty Roadmap Features, or only placeholder text like "no protocol updates"), tell the user there's nothing to announce yet and stop. Don't post an empty announcement.

### 2. Determine new post vs update

Check the release file's frontmatter for a `reddit-post-id` field:

- **No `reddit-post-id`** → this is a **new HRP** that hasn't been announced yet. Create a new Reddit post.
- **Has `reddit-post-id`** → a post already exists. Post a **comment** on the existing thread.

You can also verify programmatically:
```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py" lookup --file releases/YYYYMMDD-core-devs.md
```

### 3. Format the content

**Tone: casual and community-friendly.** This is a subreddit, not a boardroom. Write like a team member talking to the community — conversational, plain language, no jargon or corporate-speak.

#### New announcement (no `reddit-post-id`)

Title format: `HRP {Month Year} is up — here's what's in it`

Body structure:

```
Hey everyone, the {Month Year} Helium Release Proposal is out and ready for your review.

**What's in this release:**

{For each feature, write a plain-language 2-3 sentence explanation. Pull from the Motivation section but rephrase it like you're explaining to a community member, not a developer.}

**Key dates:**
- Vote opens: ~{vote-date formatted naturally}
- Target release: {release-date formatted naturally}

Check out the [full proposal](https://github.com/helium/helium-release-proposals/blob/main/releases/{filename})

Questions or feedback? Drop them in the comments — we want to hear from you before the vote goes live.
```

**Concrete example** — here's what the April 2026 HRP post would look like:

Title: `HRP April 2026 is up — here's what's in it`

Body:
```
Hey everyone, the April 2026 Helium Release Proposal is out and ready for your review.

**What's in this release:**

**1. Staked HNT Position Transfers** — Right now, if you've staked HNT and need to move your position to a different wallet (say, because your wallet got compromised or you want to move to a cold wallet), you're stuck waiting for the full unlock period. This release adds the ability to transfer staked positions directly between wallets without unstaking. Your lock duration, staked amount, and rewards all stay exactly the same — only the owning wallet changes.

**Key dates:**
- Vote opens: ~March 20th
- Target release: April 1st

Check out the [full proposal](https://github.com/helium/helium-release-proposals/blob/main/releases/20260401-core-devs.md)

Questions or feedback? Drop them in the comments — we want to hear from you before the vote goes live.
```

#### Update comment (has `reddit-post-id`)

Ask the user what changed if it's not obvious from context. Format as a comment on the existing thread:

For a new feature added:
```
**Update: {Feature Name} added**

{Plain-language 2-3 sentence explanation of the feature and why it matters.}

[Updated proposal](https://github.com/helium/helium-release-proposals/blob/main/releases/{filename})
```

For a vote reminder:
```
**Heads up: voting opens {vote-date}**

Quick recap of what's in this release:

{numbered list in plain language}

Cast your vote at [heliumvote.com](https://www.heliumvote.com)
```

### 4. Confirm with user

**Always show the full formatted title (if new) and body to the user and get explicit confirmation before posting.** The user may want to adjust wording, add context, or change tone.

### 5. Post or comment

For a **new announcement**:
```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py" post \
  --file "releases/YYYYMMDD-core-devs.md" \
  --title "the title" \
  --body "the body"
```

This writes the `reddit-post-id` into the release file's frontmatter. **After posting, commit the frontmatter change** so the post ID is tracked in the repo.

For an **update** (comment on existing post):
```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py" update \
  --file "releases/YYYYMMDD-core-devs.md" \
  --body "the comment body"
```

The script reads the `reddit-post-id` from frontmatter and posts a comment on that thread.

### 6. Report result and commit

After posting:
- Report the URL back to the user
- If this was a new post, the release file was modified (frontmatter now has `reddit-post-id`). Ask the user if they want to commit this change.

## Credential setup

If credentials are missing, the script will error with details. Tell the user:

1. Log in to Reddit as **HeliumConsoleTeam**
2. Go to https://www.reddit.com/prefs/apps/ → create a **script** type app
3. Create `~/.config/hrp/reddit.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=HeliumConsoleTeam
   REDDIT_PASSWORD=your_password
   ```
