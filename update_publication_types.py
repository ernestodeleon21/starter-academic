#!/usr/bin/env python3
"""
Walk through all `index.md` files under `content/publication/` and replace
any occurrence of `- article-journal` (quoted or unquoted) under
`publication_types:` with `- "2"` (quoted).
"""
import pathlib
import re

def main():
    root = pathlib.Path("content/publication")

    # Regex matches the publication_types block that may list article-journal in any form
    pattern = re.compile(
        r'(publication_types:\s*\n)'                       # the header line
        r'(?:\s*-\s*["\']?article-journal["\']?\s*\n)+' # one or more entries
        ,
        flags=re.MULTILINE
    )

    for md_path in root.rglob("index.md"):
        text = md_path.read_text(encoding="utf-8")
        # Replace matched block with a single numeric code line
        new_text, count = pattern.subn(
            r'\1  - "2"\n',  # keep header, then indent two spaces, dash, space, "2"
            text
        )
        if count > 0:
            md_path.write_text(new_text, encoding="utf-8")
            print(f"Updated {md_path} (replaced {count} block(s))")

if __name__ == "__main__":
    main()