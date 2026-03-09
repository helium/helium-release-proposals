# /// script
# requires-python = ">=3.11"
# ///
"""Post or update Helium Release Proposals on Reddit.

Usage:
  reddit-post.py post --file RELEASE_FILE --title TITLE --body BODY [--subreddit SUB]
  reddit-post.py update --file RELEASE_FILE --body BODY
  reddit-post.py lookup --file RELEASE_FILE

The Reddit post ID is stored in the release file's YAML frontmatter as
`reddit-post-id`. This keeps tracking in the repo itself, visible to all users.

Credentials are read from environment variables or ~/.config/hrp/reddit.env:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "hrp" / "reddit.env"
USER_AGENT = "helium-release-proposals/1.0 (by /u/HeliumConsoleTeam)"


def read_frontmatter(filepath):
    """Read YAML frontmatter from a release file. Returns (dict, full_text)."""
    text = Path(filepath).read_text()
    match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if not match:
        print(f"Error: No YAML frontmatter found in {filepath}", file=sys.stderr)
        sys.exit(1)

    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm, text


def write_frontmatter_field(filepath, key, value):
    """Add or update a field in the YAML frontmatter of a release file."""
    text = Path(filepath).read_text()
    match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if not match:
        print(f"Error: No YAML frontmatter found in {filepath}", file=sys.stderr)
        sys.exit(1)

    fm_text = match.group(1)
    rest = text[match.end():]

    # Update existing field or insert before closing ---
    field_pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if field_pattern.search(fm_text):
        fm_text = field_pattern.sub(f"{key}: {value}", fm_text)
    else:
        fm_text = fm_text.rstrip("\n") + f"\n{key}: {value}\n"

    Path(filepath).write_text(f"---\n{fm_text}---\n{rest}")


def load_credentials():
    """Load Reddit API credentials from env vars or .env file."""
    creds = {
        "client_id": os.environ.get("REDDIT_CLIENT_ID"),
        "client_secret": os.environ.get("REDDIT_CLIENT_SECRET"),
        "username": os.environ.get("REDDIT_USERNAME"),
        "password": os.environ.get("REDDIT_PASSWORD"),
    }

    if not all(creds.values()) and ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            env_key = key.lower().replace("reddit_", "")
            if env_key in creds:
                creds[env_key] = creds[env_key] or value

    missing = [k for k, v in creds.items() if not v]
    if missing:
        print(f"Error: Missing credentials: {', '.join(missing)}", file=sys.stderr)
        print(f"\nSet environment variables or create {ENV_FILE} with:", file=sys.stderr)
        print("  REDDIT_CLIENT_ID=...", file=sys.stderr)
        print("  REDDIT_CLIENT_SECRET=...", file=sys.stderr)
        print("  REDDIT_USERNAME=...", file=sys.stderr)
        print("  REDDIT_PASSWORD=...", file=sys.stderr)
        sys.exit(1)

    return creds


def get_access_token(creds):
    """Authenticate with Reddit OAuth2 and return access token."""
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "username": creds["username"],
        "password": creds["password"],
    }).encode()

    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        method="POST",
    )
    req.add_header("User-Agent", USER_AGENT)

    auth = base64.b64encode(
        f"{creds['client_id']}:{creds['client_secret']}".encode()
    ).decode()
    req.add_header("Authorization", f"Basic {auth}")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Error: Auth failed ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)

    if "access_token" not in result:
        print(f"Error: Auth response missing token: {result}", file=sys.stderr)
        sys.exit(1)

    return result["access_token"]


def api_request(token, method, endpoint, data=None):
    """Make an authenticated request to Reddit's OAuth API."""
    url = f"https://oauth.reddit.com{endpoint}"
    encoded = urllib.parse.urlencode(data).encode() if data else None

    req = urllib.request.Request(url, data=encoded, method=method)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Authorization", f"bearer {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Error: API request failed ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)


def cmd_post(args):
    """Submit a new Reddit post and write the post ID into the release file."""
    fm, _ = read_frontmatter(args.file)
    if fm.get("reddit-post-id"):
        print(
            f"Error: {args.file} already has reddit-post-id: {fm['reddit-post-id']}",
            file=sys.stderr,
        )
        print("Use 'update' to comment on the existing post.", file=sys.stderr)
        sys.exit(1)

    creds = load_credentials()
    token = get_access_token(creds)

    result = api_request(token, "POST", "/api/submit", {
        "sr": args.subreddit,
        "kind": "self",
        "title": args.title,
        "text": args.body,
        "sendreplies": "true",
    })

    if result.get("success") is False:
        errors = result.get("jquery", result)
        print(f"Error: Post failed: {json.dumps(errors)}", file=sys.stderr)
        sys.exit(1)

    post_url = None
    post_id = None
    if "json" in result and "data" in result["json"]:
        post_url = result["json"]["data"].get("url")
        post_id = result["json"]["data"].get("name")

    if not post_id:
        print("Error: No post ID returned from Reddit", file=sys.stderr)
        sys.exit(1)

    # Write post ID into the release file frontmatter
    write_frontmatter_field(args.file, "reddit-post-id", post_id)

    output = {"success": True, "post_id": post_id}
    if post_url:
        output["url"] = post_url
    print(json.dumps(output))


def cmd_update(args):
    """Add a comment to the existing Reddit post for this HRP."""
    fm, _ = read_frontmatter(args.file)
    post_id = fm.get("reddit-post-id")
    if not post_id:
        print(f"Error: No reddit-post-id in {args.file}", file=sys.stderr)
        print("Use 'post' first to create the initial announcement.", file=sys.stderr)
        sys.exit(1)

    if not post_id.startswith("t3_"):
        post_id = f"t3_{post_id}"

    creds = load_credentials()
    token = get_access_token(creds)

    result = api_request(token, "POST", "/api/comment", {
        "thing_id": post_id,
        "text": args.body,
    })

    output = {"success": True, "parent_post_id": post_id}
    if "json" in result and "data" in result["json"]:
        things = result["json"]["data"].get("things", [])
        if things:
            output["comment_id"] = things[0].get("data", {}).get("name")

    print(json.dumps(output))


def cmd_lookup(args):
    """Look up the Reddit post ID from the release file frontmatter."""
    fm, _ = read_frontmatter(args.file)
    post_id = fm.get("reddit-post-id")
    if not post_id:
        print(json.dumps({"found": False}))
    else:
        print(json.dumps({"found": True, "post_id": post_id}))


def main():
    parser = argparse.ArgumentParser(description="Post HRPs to Reddit")
    sub = parser.add_subparsers(dest="command", required=True)

    p_post = sub.add_parser("post", help="Create initial HRP announcement")
    p_post.add_argument("--file", required=True, help="Path to release .md file")
    p_post.add_argument("--title", required=True)
    p_post.add_argument("--body", required=True)
    p_post.add_argument("--subreddit", default="HeliumNetwork")

    p_update = sub.add_parser("update", help="Comment on existing HRP post")
    p_update.add_argument("--file", required=True, help="Path to release .md file")
    p_update.add_argument("--body", required=True)

    p_lookup = sub.add_parser("lookup", help="Look up tracked post for an HRP")
    p_lookup.add_argument("--file", required=True, help="Path to release .md file")

    args = parser.parse_args()

    if args.command == "post":
        cmd_post(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "lookup":
        cmd_lookup(args)


if __name__ == "__main__":
    main()
