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

### 2. Check if a Reddit post already exists for this HRP

Check the frontmatter for a `reddit-post-id` field, or use:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/reddit-post.py" lookup --file releases/YYYYMMDD-core-devs.md
```

- If `found: true` → this is an **update** (comment on existing post)
- If `found: false` → this is a **new announcement** (create post)

### 3. Format the content

#### New announcement (no existing post)

Title: `Helium Release Proposal {Month Year} — Open for Community Review`

Body:
```
The Helium Release Proposal for {Month Year} has been published and is open for community review.

**Release Date:** {release-date}
**Vote Date:** {vote-date}

## Proposed Features

{numbered list of features with 1-2 sentence summary of each from the motivation section}

---

Full proposal: https://github.com/helium/helium-release-proposals/blob/main/releases/{filename}

The vote will open around {vote-date formatted naturally}. Review the proposal and share your feedback before then.
```

#### Update comment (existing post found)

Determine what changed — ask the user if unclear. Format as a comment:

For a new feature added:
```
**Update: {Feature Name} added to HRP {Month Year}**

{Brief summary from the feature's motivation section}

Full proposal: https://github.com/helium/helium-release-proposals/blob/main/releases/{filename}
```

For a vote reminder:
```
**Reminder: Voting opens {vote-date}**

The community vote for this release opens on {vote-date}. Proposed features:

{numbered list}

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
