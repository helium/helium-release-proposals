---
name: post
description: Post or update a Helium Release Proposal on r/HeliumNetwork as HeliumConsoleTeam. Use when the user wants to announce a new HRP, post an update about feature additions, or notify the community about an HRP.
user_invocable: true
---

# HRP Reddit Post Skill

You help post Helium Release Proposals to r/HeliumNetwork. Each HRP gets **one Reddit post** (the announcement). All subsequent updates (new features, vote reminders, etc.) are posted as **comments on that original post**.

The Reddit post ID is tracked in the release file's YAML frontmatter (`reddit-post-id` field), so it's visible in the repo and accessible to all users.

## Script location

`${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py`

## Steps

### 1. Identify the target HRP

- Look at files in `releases/` to find the active HRP (status: Proposed, with a future or recent vote-date)
- If the user specifies a month, find that specific HRP file
- Read the full HRP file contents
- Note the release filename (e.g. `releases/20260401-core-devs.md`)

### 2. Determine new post vs update

Check the release file's frontmatter for a `reddit-post-id` field:

- **No `reddit-post-id`** → this is a **new HRP** that hasn't been announced yet. Create a new Reddit post.
- **Has `reddit-post-id`** → a post already exists. Post a **comment** on the existing thread.

You can also verify programmatically:
```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py" lookup --file releases/YYYYMMDD-core-devs.md
```

### 3. Format the content

**Tone: casual and community-friendly.** This is a subreddit, not a boardroom. Keep it conversational — explain features in plain language, avoid jargon, and sound like a person talking to the community. No corporate-speak.

#### New announcement (no `reddit-post-id`)

Title: `HRP {Month Year} is up — here's what's in it`

Body:
```
Hey everyone, the {Month Year} Helium Release Proposal is out and ready for your review.

**What's in this release:**

{For each feature: a plain-language 2-3 sentence explanation of what it does and why it matters. Write this like you're explaining it to a community member, not a developer. Pull from the Motivation section but rephrase conversationally.}

**Key dates:**
- Vote opens: ~{vote-date formatted naturally, e.g. "March 20th"}
- Target release: {release-date formatted naturally, e.g. "April 1st"}

Check out the full proposal here: https://github.com/helium/helium-release-proposals/blob/main/releases/{filename}

Questions or feedback? Drop them in the comments — we want to hear from you before the vote goes live.
```

#### Update comment (has `reddit-post-id`)

Determine what changed — ask the user if unclear. Format as a comment:

For a new feature added:
```
**Update: {Feature Name} added**

{Plain-language 2-3 sentence explanation of the feature and why it matters.}

Updated proposal: https://github.com/helium/helium-release-proposals/blob/main/releases/{filename}
```

For a vote reminder:
```
**Heads up: voting opens {vote-date}**

Quick recap of what's in this release:

{numbered list in plain language}

Cast your vote at https://www.heliumvote.com
```

### 4. Confirm with user

**Always show the full formatted title (if new) and body to the user and ask for confirmation before posting.** The user may want to adjust wording.

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

If credentials are missing, tell the user:

1. Log in to Reddit as **HeliumConsoleTeam**
2. Go to https://www.reddit.com/prefs/apps/ → create a **script** type app
3. Create `~/.config/hrp/reddit.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=HeliumConsoleTeam
   REDDIT_PASSWORD=your_password
   ```
