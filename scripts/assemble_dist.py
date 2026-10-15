"""Assemble dist/ for deploy — preserves the repo's relative layout so
DATA_BASE ("../content/build") resolves identically locally and in dist/.

  dist/site/*                 <- site/ (page, css, fonts, fa, images)
  dist/content/build/*.json   <- content/build/ (manifest + story JSONs)

Raw factory inputs (content/stories/), legacy records, the drawer corpus,
scripts, docs, and reference/ never ship.

Usage: python scripts/assemble_dist.py [--clean]
"""
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"

SITE_FILES = ["periya_puranam_index.html", "ppreader.css", "fonts.css",
              "manifest.webmanifest", "sw.js",
              "tailwind.config.js", "fonts", "fa", "images"]


def main(clean=False):
    if clean and DIST.exists():
        shutil.rmtree(DIST)
    build_dir = REPO / "content" / "build"
    if not (build_dir / "manifest.json").exists():
        raise SystemExit("content/build/manifest.json missing — "
                         "run scripts/build.py first")
    manifest = json.loads((build_dir / "manifest.json")
                          .read_text(encoding="utf-8"))

    for name in SITE_FILES:
        src = REPO / "site" / name
        dst = DIST / "site" / name
        if not src.exists():
            print(f"skip (absent): site/{name}")
            continue
        if dst.exists():
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    out_build = DIST / "content" / "build"
    if out_build.exists():
        shutil.rmtree(out_build)
    out_build.mkdir(parents=True, exist_ok=True)
    shipped = []
    for path in sorted(build_dir.glob("*.json")):
        shutil.copy2(path, out_build / path.name)
        shipped.append(path.name)

    # Service worker at the dist ROOT: the page registers '/sw.js', and only
    # a root-level worker controls both /site/* and /content/*. site/sw.js
    # is the source of truth (also copied to dist/site/ above); the root
    # copy is what browsers fetch.
    root_sw = REPO / "site" / "sw.js"
    if root_sw.exists():
        shutil.copy2(root_sw, DIST / "sw.js")
        print("dist/ sw.js at root (scope /)")

    # Deploy safety: preview paths must never ship (mirrors check.py gate).
    leaks = sorted(str(p.relative_to(DIST)) for p in DIST.rglob("preview*"))
    assert not leaks, f"preview paths in dist/: {leaks}"

    # The deploy contract: page-relative ../content/build must resolve.
    probe = (DIST / "site" / "periya_puranam_index.html").parent / \
        ".." / "content" / "build" / "manifest.json"
    assert probe.resolve().exists(), "DATA_BASE does not resolve in dist/"
    listed = json.loads((out_build / "manifest.json")
                        .read_text(encoding="utf-8"))
    assert len(listed) == len(manifest), "manifest mismatch in dist/"

    # Generated root entry (build artifact, not source): the reader lives at
    # /site/… so / redirects there. No fetching happens on this page, so
    # DATA_BASE is unaffected.
    (DIST / "index.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"UTF-8\">\n"
        "<meta http-equiv=\"refresh\" content=\"0; "
        "url=./site/periya_puranam_index.html\">\n"
        "<link rel=\"canonical\" "
        "href=\"./site/periya_puranam_index.html\">\n"
        "<title>Periya Puranam — Sacred Epic Reader</title>\n"
        "</head>\n<body>\n<p><a "
        "href=\"./site/periya_puranam_index.html\">"
        "Open the Periya Puranam reader</a></p>\n</body>\n</html>\n",
        encoding="utf-8")
    print(f"dist/ assembled: {len(shipped)} build JSONs, "
          f"{len(listed)} listed stories, DATA_BASE resolves")


if __name__ == "__main__":
    main("--clean" in sys.argv)
