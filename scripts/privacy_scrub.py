#!/usr/bin/env python3
"""Privacy scrub: block commits that would publish private details.

Runs from the git hooks in .githooks/ (enable with `git config core.hooksPath .githooks`).

  privacy_scrub.py --staged        scan lines added in the staged diff (pre-commit)
  privacy_scrub.py --message FILE  scan a commit message (commit-msg)
  privacy_scrub.py --tree          scan every tracked file
  privacy_scrub.py --history       scan every commit (diffs, messages, authors)

What it looks for:
  * exact strings from a local denylist that is never committed:
    .git/privacy-denylist (one per line, # comments) and
    ~/.config/privacy-scrub/denylist. Your git identity's real email,
    if it is not a noreply address, is added automatically.
  * generic patterns: email addresses (noreply and example domains are allowed),
    home-directory paths, API tokens and private keys, Cloudflare account ids
    written next to the word "account".
  * a commit author or committer email that is not a noreply address.

Bypass a false positive for one line by adding `privacy-scrub: allow` to it.
Python 3.9+, standard library only.
"""
import os
import re
import subprocess
import sys

ALLOW_MARK = "privacy-scrub: allow"
ALLOWED_EMAIL = re.compile(
    r"(noreply|no-reply)@|@users\.noreply\.github\.com$|@example\.(com|org|net)$"
    r"|@localhost$|@anthropic\.com$|^git@github\.com$",
    re.I,
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PATTERNS = [
    ("home directory path", re.compile(r"/(Users|home)/(?!runner\b|user\b|me\b|you\b|<)[A-Za-z0-9._-]+/")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}")),
    ("Anthropic/OpenAI key", re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}")),
    ("AWS key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Cloudflare account id", re.compile(r"account[_ -]?id[\"'\s:=]+[\"']?[0-9a-f]{32}\b", re.I)),
    ("secret assignment", re.compile(
        r"\b[A-Z0-9_]*(API_TOKEN|API_KEY|SECRET|PASSWORD)\s*[=:]\s*[\"']?[A-Za-z0-9_\-/+]{16,}")),
]
SKIP_FILES = re.compile(r"\.(woff2?|png|jpe?g|gif|ico|pdf)$|^data/awesome/")
# Generated from public GitHub metadata: repo descriptions can contain email-like text.
# Denylist, token and path checks still apply there; only the generic email check is off.
PUBLIC_DATA = re.compile(r"^data/.*\.json$")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def denylist():
    words = set()
    paths = [os.path.join(git("rev-parse", "--git-common-dir").strip() or ".git", "privacy-denylist"),
             os.path.expanduser("~/.config/privacy-scrub/denylist")]
    for p in paths:
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#"):
                    words.add(line)
    real = git("config", "--global", "user.email").strip()
    if real and not ALLOWED_EMAIL.search(real):
        words.add(real)
    return sorted(words, key=len, reverse=True)


def check_line(text, deny, path=""):
    if ALLOW_MARK in text:
        return []
    hits = []
    low = text.lower()
    for w in deny:
        if w.lower() in low:
            hits.append("denylisted string")
    for m in EMAIL.finditer(text):
        if not PUBLIC_DATA.search(path) and not ALLOWED_EMAIL.search(m.group(0)):
            hits.append("email address")
    for name, rx in PATTERNS:
        if rx.search(text):
            hits.append(name)
    return sorted(set(hits))


def mask(text):
    text = text.strip()
    return text if len(text) <= 100 else text[:97] + "..."


def report(findings, where):
    if not findings:
        return 0
    print(f"privacy scrub: {len(findings)} problem(s) in {where}", file=sys.stderr)
    for loc, kinds, text in findings[:50]:
        print(f"  {loc}: {', '.join(kinds)}\n      {mask(text)}", file=sys.stderr)
    print("Fix these, or mark a false positive with 'privacy-scrub: allow' on that line.", file=sys.stderr)
    return 1


def scan_diff(diff, deny, label=""):
    out, path, ln = [], None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
            continue
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            ln = int(m.group(1)) if m else 0
            continue
        if path is None or SKIP_FILES.search(path):
            continue
        if line.startswith("+"):
            kinds = check_line(line[1:], deny, path)
            if kinds:
                out.append((f"{label}{path}:{ln}", kinds, line[1:]))
            ln += 1
        elif not line.startswith("-"):
            ln += 1
    return out


def check_identity():
    out = []
    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        ident = git("var", var)
        m = re.search(r"<([^>]*)>", ident)
        if m and not ALLOWED_EMAIL.search(m.group(1)):
            out.append((var.lower(), ["non-noreply email"], "use your GitHub noreply address (git config user.email)"))
    return out


def main(argv):
    deny = denylist()
    mode = argv[1] if len(argv) > 1 else "--staged"
    if mode == "--staged":
        diff = git("diff", "--cached", "--no-color", "-U0", "--no-ext-diff")
        return report(check_identity() + scan_diff(diff, deny), "staged changes")
    if mode == "--message":
        text = open(argv[2], encoding="utf-8").read()
        found = [(f"message:{i}", k, l) for i, l in enumerate(text.splitlines(), 1)
                 if not l.startswith("#") and (k := check_line(l, deny))]
        return report(found, "commit message")
    if mode == "--tree":
        found = []
        for path in git("ls-files").splitlines():
            if SKIP_FILES.search(path):
                continue
            try:
                lines = open(path, encoding="utf-8").read().splitlines()
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for i, l in enumerate(lines, 1):
                kinds = check_line(l, deny, path)
                if kinds:
                    found.append((f"{path}:{i}", kinds, l))
        return report(found, "tracked files")
    if mode == "--history":
        found = []
        for sha in git("rev-list", "--all").split():
            meta = git("show", "-s", "--format=%ae%n%ce%n%B", sha)
            for l in meta.splitlines():
                kinds = check_line(l, deny)
                if kinds:
                    found.append((f"{sha[:7]} meta", kinds, l))
            found += scan_diff(git("show", "--no-color", "-U0", "--format=", sha), deny, f"{sha[:7]} ")
        return report(found, "history")
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
