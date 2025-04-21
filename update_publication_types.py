#!/usr/bin/env python3
"""
Walk through all `index.md` files under `content/publication/`, normalize publication_types,
replace any `article-journal` entry with the numeric code "2", discover their DOI,
fetch metadata from CrossRef (journal, abstract, URL), and rewrite the frontmatter
with `publication_types`, `publication`, `url_pdf`, `doi`, and `abstract` fields populated.
"""
import pathlib
import re
import requests
import yaml

CROSSREF_API = "https://api.crossref.org/works/{}"


def fetch_metadata(doi: str) -> dict:
    """Fetch CrossRef metadata for a DOI (no URL prefix)."""
    resp = requests.get(CROSSREF_API.format(doi))
    resp.raise_for_status()
    msg = resp.json().get('message', {})
    # Clean JATS markup from abstract if present
    abstract = msg.get('abstract', '')
    abstract = re.sub(r'<.*?>', '', abstract).strip()
    # Container title may be a list
    container = msg.get('container-title', [])
    journal = container[0] if container else ''
    # URL field generally points to the DOI landing page
    url = msg.get('URL', '')
    return {
        'journal': journal,
        'abstract': abstract,
        'url': url
    }


def process_file(md_path: pathlib.Path):
    text = md_path.read_text(encoding='utf-8')
    # Split frontmatter + body
    m = re.match(r'^(---\n)(.*?)(---\n)(.*)$', text, re.S)
    if not m:
        print(f"Skipping (no frontmatter): {md_path}")
        return
    start, fm_text, end, body = m.groups()
    fm = yaml.safe_load(fm_text)

    # Normalize publication_types: replace article-journal with "2"
    if 'publication_types' in fm:
        pts = fm['publication_types'] or []
        # detect string entries equal to article-journal
        if any(str(t) == 'article-journal' for t in pts):
            fm['publication_types'] = ["2"]

    # Locate DOI in frontmatter (with or without full URL)
    raw_doi = fm.get('doi') or fm.get('url_pdf') or fm.get('url')
    if not raw_doi:
        print(f"No DOI found in {md_path}")
        return
    # Normalize DOI string
    doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', str(raw_doi))

    # Fetch metadata
    meta = fetch_metadata(doi)

    # Update frontmatter with fetched metadata
    fm['publication'] = f"*{meta['journal']}*"
    fm['url_pdf'] = meta['url']
    fm['doi'] = f"https://doi.org/{doi}"
    fm['abstract'] = meta['abstract']

    # Dump back to YAML, preserving key order
    new_fm = yaml.dump(fm, sort_keys=False)
    new_text = f"{start}{new_fm}{end}{body}"
    md_path.write_text(new_text, encoding='utf-8')
    print(f"Processed: {md_path}")


def main():
    root = pathlib.Path('content/publication')
    for md_path in root.rglob('index.md'):
        process_file(md_path)


if __name__ == '__main__':
    main()