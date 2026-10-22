#!/usr/bin/env python3
"""Adds a release to the Sparkle appcast (website/appcast.xml).

Usage:
    update_appcast.py APPCAST VERSION BUILD MIN_OS URL RELEASE_NOTES_URL SIGN_UPDATE_OUTPUT

SIGN_UPDATE_OUTPUT is what Sparkle's sign_update prints, e.g.
    sparkle:edSignature="..." length="12345"
"""
import re
import sys
from email.utils import formatdate
from xml.sax.saxutils import escape, quoteattr


def main() -> None:
    appcast, version, build, min_os, url, notes_url, signed = sys.argv[1:8]

    match = re.search(r'sparkle:edSignature="([^"]+)"\s+length="(\d+)"', signed)
    if not match:
        sys.exit(f"Unexpected sign_update output: {signed!r}")
    signature, length = match.groups()

    with open(appcast, encoding="utf-8") as f:
        xml = f.read()

    if re.search(rf"<sparkle:version>{re.escape(build)}</sparkle:version>", xml):
        sys.exit(f"Build {build} is already in {appcast}")

    item = f"""        <item>
            <title>{escape(version)}</title>
            <pubDate>{formatdate(usegmt=True)}</pubDate>
            <sparkle:version>{escape(build)}</sparkle:version>
            <sparkle:shortVersionString>{escape(version)}</sparkle:shortVersionString>
            <sparkle:minimumSystemVersion>{escape(min_os)}</sparkle:minimumSystemVersion>
            <sparkle:releaseNotesLink>{escape(notes_url)}</sparkle:releaseNotesLink>
            <enclosure url={quoteattr(url)} sparkle:edSignature={quoteattr(signature)} length={quoteattr(length)} type="application/octet-stream"/>
        </item>
"""

    # Newest release first, directly after the channel's own metadata.
    marker = "<!-- releases -->\n"
    if marker not in xml:
        sys.exit(f"Missing {marker.strip()} marker in {appcast}")
    xml = xml.replace(marker, marker + item, 1)

    with open(appcast, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Added {version} ({build}) to {appcast}")


if __name__ == "__main__":
    main()
