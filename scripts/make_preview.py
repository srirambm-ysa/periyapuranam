"""Generate site/preview.html (the local all-stories BETA reader) from the
product reader site/periya_puranam_index.html.

The preview reader is the product reader with exactly two deltas:
  1. a sticky "LOCAL PREVIEW - NOT FOR DEPLOY" banner after </head>;
  2. DATA_BASE repointed from ../content/build to ../content/preview.

Kept as a script (was previously hand-built and drifted) so the reader's
yappu DB and render logic never diverge between product and preview.
Output is gitignored (never ships). Run after `python scripts/build.py
--preview`.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PRODUCT = REPO / "site" / "periya_puranam_index.html"
PREVIEW = REPO / "site" / "preview.html"
MANIFEST = REPO / "content" / "preview" / "manifest.json"

BUILD_LINE = '        const DATA_BASE = "../content/build"; ' \
             '// repo-served layout; deploy remaps'
PREVIEW_LINE = '        const DATA_BASE = "../content/preview"; ' \
               '// LOCAL PREVIEW ONLY - never ships'
BANNER_STYLE = ("position:sticky;top:0;z-index:100;background:#7A0016;"
                "color:#FCF6BA;text-align:center;font-weight:700;"
                "padding:8px 12px;font-size:13px;letter-spacing:.04em;")


def main():
    src = PRODUCT.read_text(encoding="utf-8")
    n = len(json.loads(MANIFEST.read_text(encoding="utf-8")))

    assert src.count(BUILD_LINE) == 1, \
        "DATA_BASE product line not found (reader drifted?)"
    assert src.count("</head>") == 1, "expected exactly one </head>"

    banner = (f'<div style="{BANNER_STYLE}">LOCAL PREVIEW - UNVERIFIED, '
              f'NOT FOR DEPLOY - {n} stories, no sign-off implied</div>')

    out = src.replace(BUILD_LINE, PREVIEW_LINE, 1)
    out = out.replace("</head>", "</head>\n" + banner, 1)
    PREVIEW.write_text(out, encoding="utf-8")
    print(f"wrote {PREVIEW.relative_to(REPO)} (banner: {n} stories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
