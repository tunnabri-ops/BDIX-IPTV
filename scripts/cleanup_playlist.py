#!/usr/bin/env python3
"""Clean up BDIX IPTV playlist file(s) in place.

Runs after every upstream sync (see .github/workflows/main.yml) so the
published playlist stays clean even when the upstream source re-introduces
duplicates or merge garbage. Idempotent: running it twice changes nothing
the second time.

What it does (format fixes only — it never judges whether a stream plays):
  1. Moves `#EXTM3U` to line 1 (strict parsers reject it anywhere else),
     keeping any leading comment block verbatim below it.
  2. Drops exact-duplicate entries (same URL string listed 2+ times);
     keeps the first occurrence. Same-name/different-URL entries
     (multi-server) are kept.
  3. Drops orphan URL lines with no `#EXTINF` above them, and `#EXTINF`
     lines with no URL below them.
  4. Fixes the invalid `hls://` URL scheme to `http://`.
  5. Trims leading/trailing whitespace from URL lines, display names and
     `tvg-name` attributes.
  6. Strips repeated merge suffixes from display names, e.g.
     `T Sports (1080p) (1) (2) (2)` -> `T Sports (1080p)`.

It never removes a link for being "dead": no network checks at all, and
mono.ts.m3u8 links are treated like any other URL (exact-duplicate
removal only, which never applies to distinct URLs).

Usage: python3 scripts/cleanup_playlist.py [bdix_dir]  (default: bdix)
"""

import re
import sys
from pathlib import Path

SUFFIX_CHAIN = re.compile(r"( \(\d+\))+$")
TVG_NAME = re.compile(r'tvg-name="([^"]*)"')


def clean_name(name: str) -> str:
    """Trim a display name and strip trailing ' (N) (N)...' merge suffixes."""
    name = name.strip()
    name = SUFFIX_CHAIN.sub("", name).strip()
    return name


def clean_extinf(line: str) -> str:
    """Trim padded tvg-name attributes and the display name after the comma."""
    line = TVG_NAME.sub(lambda m: 'tvg-name="%s"' % m.group(1).strip(), line)
    if "," in line:
        head, name = line.rsplit(",", 1)
        line = head + "," + clean_name(name)
    return line.strip()


def clean_playlist(text: str) -> str:
    lines = text.splitlines()
    header_lines = []  # comment/blank lines before the first #EXTINF, verbatim
    entries = []  # list of (opts, extinf, url)
    pending_opts = []  # #... lines (e.g. #EXTVLCOPT user-agent) belonging to next entry
    seen_urls = set()
    seen_first_extinf = False
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line:
            if not seen_first_extinf:
                header_lines.append("")
            i += 1
            continue
        if line.startswith("#EXTINF"):
            seen_first_extinf = True
            extinf = clean_extinf(line)
            url = ""
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                candidate = lines[j].strip()
                if candidate.startswith(("http://", "https://", "hls://")):
                    url = candidate
                    i = j
            if url:
                url = url.replace("hls://", "http://", 1)
                if url not in seen_urls:
                    seen_urls.add(url)
                    entries.append((pending_opts, extinf, url))
            # else: EXTINF with no URL below it -> dropped, with its opts
            pending_opts = []
        elif line.startswith("#EXTM3U"):
            pass  # re-added at the top
        elif line.startswith("#"):
            if not seen_first_extinf:
                header_lines.append(raw.rstrip())
            else:
                pending_opts.append(raw.rstrip())
        elif line.startswith(("http://", "https://", "hls://")):
            pass  # orphan URL with no EXTINF above it -> dropped
        # any other line is ignored (no such lines in this playlist)
        i += 1

    out = ["#EXTM3U"]
    out.extend(header_lines)
    for opts, extinf, url in entries:
        out.extend(opts)
        out.append(extinf)
        out.append(url)
    out.extend(pending_opts)  # opts with no entry after them: keep, don't lose data
    return "\n".join(out) + "\n"


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bdix")
    files = sorted(target.glob("*.m3u"))
    if not files:
        print("No .m3u files in %s" % target)
        return 0
    for path in files:
        before = path.read_text(encoding="utf-8", errors="replace")
        after = clean_playlist(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            n_before = before.count("#EXTINF")
            n_after = after.count("#EXTINF")
            print("%s: cleaned (%d -> %d entries)" % (path, n_before, n_after))
        else:
            print("%s: already clean" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
