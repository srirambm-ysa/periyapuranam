"""Generate site/preview.html (the local all-stories BETA reader) from the
product reader site/periya_puranam_index.html.

The preview reader is the product reader with exactly one delta:
  1. DATA_BASE repointed from ../content/build to ../content/preview.

(The old sticky "LOCAL PREVIEW - NOT FOR DEPLOY" banner was removed
2026-10-15 per owner: it covered the sticky header/controls on mobile.
Preview stays safe without it: the file is gitignored and can only ever
read the local-only content/preview/ tree, never the shippable build.)

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


def main():
    src = PRODUCT.read_text(encoding="utf-8")
    n = len(json.loads(MANIFEST.read_text(encoding="utf-8")))

    assert src.count(BUILD_LINE) == 1, \
        "DATA_BASE product line not found (reader drifted?)"

    out = src.replace(BUILD_LINE, PREVIEW_LINE, 1)
    PREVIEW.write_text(out, encoding="utf-8")
    print(f"wrote {PREVIEW.relative_to(REPO)} ({n} stories, no banner)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
