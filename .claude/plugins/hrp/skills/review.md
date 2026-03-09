---
name: review
description: Review a PR or release file for an active Helium Release Proposal. Checks structural completeness, consistency, content quality, and nudges for Reddit posting. Use when the user wants to review an HRP PR, validate a release file, or asks about HRP quality.
user_invocable: true
---

# HRP Review Skill

You review Helium Release Proposal files for structural completeness, consistency, content quality, and Reddit posting status.

## Steps

### 1. Identify what to review

- If the user specifies a PR number, fetch the PR diff and identify which release file(s) it touches
- If the user specifies a file or month, find the corresponding release file in `releases/`
- If neither, find the active HRP (status: Proposed, future vote-date) and check for open PRs against it
- Read the full release file and the template at `xxxx-template.md` for reference

### 2. Run all checks

Run every check below against the release file. Organize your findings into three severity levels:

- **Error** — must fix before merging (missing sections, broken structure, placeholder text)
- **Warning** — should fix, inconsistent with conventions (heading mismatches, date disagreements)
- **Note** — informational, optional to address (missing optional sections, style suggestions)

---

## Structural Checks

### S1: Roadmap Features list matches feature sections

Every numbered item in the `## Roadmap Features` list must have a corresponding `### (N) Feature Name` section below, and vice versa. Flag:
- Numbered items with no matching section
- Sections with no matching list item
- **Trailing empty list items** like `2.` with no text (this is a known recurring issue — always flag it)
- Mismatched feature names between the list and section headings

Severity: **Error**

### S2: Required sections present for each feature

Each `### (N)` feature section must contain these subsections:
- `#### Motivation`
- `#### Implementation`
- `#### Alternatives Considered`
- `#### Impact` or `#### Impact and Stakeholder Impact`

If `#### Drawbacks` is absent, note it (it's optional per template but good practice to include).

Severity: **Error** for missing required sections, **Note** for missing Drawbacks

### S3: No empty or stub sections

Check that each subsection has actual content — not just:
- Empty (nothing under the heading)
- Stub bullets (`- ` with no text)
- Whitespace only

Exception: "No changes" placeholder releases (where Roadmap Features explicitly says there are no changes) are allowed to have minimal content.

Severity: **Error**

### S4: No leftover template placeholders

Search for any of these patterns in the file:
- `TODO:`
- `fill me in`
- `fill in with`
- `(fill in`
- Content wrapped in triple backticks that matches template placeholder patterns

Severity: **Error**

---

## Consistency Checks

### C1: Section heading consistency

Within a single file, impact section headings should be consistent. The established convention across most HRPs is `#### Impact and Stakeholder Impact`. Flag if a file mixes different forms or uses a non-standard variant.

Also flag any typos in section headings (e.g. `stakeholder` vs `Stakeholder` capitalization).

Severity: **Warning**

### C2: Frontmatter completeness and validity

All of these fields must be present and valid:
- `release-date` — valid YYYY-MM-DD date
- `vote-date` — valid YYYY-MM-DD date, must be before release-date
- `authors` — non-empty list
- `status` — one of: Proposed, Voting, Approved, Released

Flag any extra unexpected fields (except `reddit-post-id` which is expected).

Severity: **Error** for missing/invalid, **Warning** for unexpected fields

### C3: Summary dates match frontmatter

The natural-language dates in the Summary section (e.g. "deployed on or before April 1st 2026", "kick off around March 20th") should agree with the `release-date` and `vote-date` in frontmatter. Flag mismatches.

Severity: **Warning**

### C4: Title matches release month

The `# Helium Release Proposal {Month Year}` heading should match the month and year from `release-date` in frontmatter.

Severity: **Warning**

---

## Content Quality Checks

### Q1: Features don't defer entirely to external docs

Flag features where required sections (especially Alternatives, Impact, Drawbacks) just say "Refer to the HIP" or similar without providing any inline summary. It's fine to reference HIPs, but each section should contain at least a brief standalone summary so readers don't have to leave the document.

Severity: **Warning**

### Q2: Link references defined and used

Check that:
- Any `[reference-style]` links in the body have matching `[reference]: url` definitions at the bottom
- Any definitions at the bottom are actually referenced in the text (no orphaned definitions)

Severity: **Warning** for undefined references, **Note** for orphaned definitions

---

## Reddit Posting Nudge

### R1: Reddit post status

Check the frontmatter for `reddit-post-id`:

- **No `reddit-post-id` and the HRP has at least one real feature**: Include a note at the end of the review:
  > "This HRP hasn't been announced on Reddit yet. After merging, run `/hrp:post` to create the announcement."

- **Has `reddit-post-id` and this PR adds/changes a feature**: Include a note:
  > "This HRP has a Reddit thread. After merging, run `/hrp:post` to post an update about this change."

- **No features yet (empty/skeleton HRP)**: No nudge needed — nothing to announce.

---

## Output Format

Present the review as a clear report:

```
## HRP Review: {Month Year}
File: `releases/{filename}`

### Errors
- **S1**: Trailing empty item `2.` in Roadmap Features list — remove it or add a feature
- **S3**: `#### Alternatives Considered` under feature (1) is empty

### Warnings
- **C3**: Summary says "March 20th" but vote-date is 2026-03-22

### Notes
- **S2**: Feature (1) is missing optional `#### Drawbacks` section
- **R1**: This HRP hasn't been announced on Reddit yet. After merging, run `/hrp:post` to create the announcement.

### Summary
{X} errors, {Y} warnings, {Z} notes
```

If there are no errors: "Looks good to merge."
If there are errors: "Fix the errors above before merging."
