"""CI gates for story JSON v1 + manifest (SCHEMA_V1 §3).

Safe to run on every factory re-export merge: fails loudly on any
shape, status, count, or drawer-length violation.

Gates:
  G1  every story file: schema_version == 1
  G2  status in (transcribed, tamil_verified, english_done)
  G3  english_done => english_chapters present, english_count == tamil_count > 0,
      Tamil/English n arrays match
  G4  tamil_verified => english_chapters null, english_count == 0
  G5  chapter n contiguous from 1 (both languages when present)
  G6  verse_count == len(verses); verse_count > 0 => section_slug exists and
      verse_count == drawer section length; every yappuKey known
  G7  manifest: listed statuses only, counts match story files,
      every listed file present and vice versa, transcribed never listed

Usage: python scripts/check.py  (exit 0 clean, exit 1 with error list)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from yappu_db import YAPPU_DB_JS  # noqa: E402

BUILD = REPO / "content" / "build"
CORPUS = REPO / "content" / "Thirumurai_12_shaivam_corpus.json"
KNOWN_KEYS = set(re.findall(r'"([\w-]+)":\s*\{', YAPPU_DB_JS))
MANIFEST_FIELDS = {"slug", "id", "titleEn", "titleTa", "status",
                   "schema_version", "image", "type", "isBig4", "group",
                   "category",
                   "tamil_count", "english_count",
                   "verse_count", "section_slug", "section_order",
                   "exported_at"}
LISTED = ("tamil_verified", "english_done")
GROUPS = ("tani", "thogai", "samaya", "external")
FMAP_ORDER = {e["factory_slug"]: e.get("section_order", 999) for e in
              json.loads((REPO / "content" / "factory_section_map.json")
                         .read_text(encoding="utf-8"))["entries"]}
# Expected drawer-verse totals per story (giants span 2 drawer sections,
# so the single-section lookup below cannot apply to them).
FMAP_VERSES = {}
for _e in json.loads((REPO / "content" / "factory_section_map.json")
                     .read_text(encoding="utf-8"))["entries"]:
    if _e.get("giant"):
        FMAP_VERSES[_e["factory_slug"]] = \
            sum(s["n_songs"] for s in _e.get("sections", []))
    else:
        FMAP_VERSES[_e["factory_slug"]] = _e.get("n_songs", 0)
KINDS = ("periyapuranam_root", "thogai", "anthathi")

errors = []


def fail(msg):
    errors.append(msg)


def story_files():
    return sorted(p for p in BUILD.glob("*.json") if p.name != "manifest.json")


def gate_preview_leak():
    """Deploy safety: content/preview/ and site/preview.html are local-only.
    Fails on (a) any preview:true inside content/build/, (b) any preview*
    path under dist/."""
    errs = []
    for path in story_files():
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # G1 territory; reported elsewhere
        if s.get("preview") is True:
            errs.append(f"{path.name}: preview:true leaked into content/build/")
    if (BUILD / "manifest.json").exists():
        m = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
        if any(e.get("preview") is True for e in m):
            errs.append("manifest.json: preview entry leaked into "
                        "content/build/")
    dist = REPO / "dist"
    if dist.exists():
        leaks = sorted(str(p.relative_to(dist))
                       for p in dist.rglob("preview*"))
        for leak in leaks:
            errs.append(f"dist/{leak}: preview path would ship")
    return errs


def gate_escaping():
    """G8: JSON holds raw Tamil, so the deploy shell must escape at insertion.
    Scans site/periya_puranam_index.html only (shell.html is a frozen
    reference copy, never shipped). yappuDatabase strings are trusted static
    data and exempt; parasHTML is the audited sink (escapes internally)."""
    shell = REPO / "site" / "periya_puranam_index.html"
    errs = []
    t = shell.read_text(encoding="utf-8")
    if "function esc(s)" not in t:
        errs.append("G8: esc() missing from shell")
    if "function setLang(l)" not in t or "setLang(localStorage.getItem" not in t:
        errs.append("G8: golden P-f toggle (setLang + boot init) missing")
    if "function imgURL(src)" not in t:
        errs.append("G8: imgURL() resolver missing from shell")
    if "function setActiveToc(index)" not in t or \
            "function initTocSpy()" not in t:
        errs.append("G8: golden P-d scroll spy (setActiveToc + initTocSpy) "
                    "missing")
    if "manifest.json" not in t or "parasHTML" not in t:
        errs.append("G8: shell not manifest-wired (manifest fetch/parasHTML)")
    # Brace-matched ${...} scan (handles nested template literals).
    exprs = []
    i = 0
    while True:
        j = t.find("${", i)
        if j < 0:
            break
        depth, k, instr = 0, j + 2, None
        while k < len(t):
            c = t[k]
            if instr:
                if c == instr and t[k - 1] != "\\":
                    instr = None
            elif c in "\"'`":
                instr = c
            elif c == "{":
                depth += 1
            elif c == "}":
                if depth == 0:
                    break
                depth -= 1
            k += 1
        exprs.append((t.count("\n", 0, j) + 1, t[j + 2:k]))
        i = k + 1
    tok = re.compile(r"\b(chap|devotee|item|entry)\.[A-Za-z]+|\bs\.[A-Za-z]+"
                     r"|\btamilVerse\b|\benglishTranslation\b|\bverseSource\b")
    for ln, ex in exprs:
        code = re.sub(r"""'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*""" +
                      r"""|`(?:[^`\\]|\\.)*`""", "''", ex)
        if tok.search(code) and "esc(" not in ex:
            errs.append(f"G8 line {ln}: unescaped story interpolation: "
                        f"{ex.strip()[:90]}")
    # Concat-style building: raw field appends must route via esc/parasHTML.
    for n, line in enumerate(t.splitlines(), 1):
        if re.search(r"\+\s*(chap|s|devotee|item)\.[A-Za-z]+", line) \
                and "esc(" not in line and "parasHTML(" not in line:
            errs.append(f"G8 line {n}: unescaped concat insert: "
                        f"{line.strip()[:90]}")
    return errs


def main():
    if not BUILD.is_dir():
        fail("content/build/ missing — run scripts/build.py first")
        raise SystemExit(1)
    sections = {c["slug"]: c for c in
                json.loads(CORPUS.read_text(encoding="utf-8"))}
    stories = {}
    for path in story_files():
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{path.name}: invalid JSON ({e})")
            continue
        stories[s.get("slug", path.stem)] = (path, s)

        if s.get("schema_version") != 1:  # G1
            fail(f"{path.name}: schema_version != 1")
        status = s.get("status")  # G2
        if status not in ("transcribed", *LISTED):
            fail(f"{path.name}: bad status {status!r}")

        ta = s.get("tamil_chapters") or []
        if [c.get("n") for c in ta] != list(range(1, len(ta) + 1)):  # G5
            fail(f"{path.name}: tamil chapter n not contiguous from 1")
        if s.get("group") not in GROUPS:
            fail(f"{path.name}: bad group {s.get('group')!r}")
        if not isinstance(s.get("isBig4"), bool):
            fail(f"{path.name}: isBig4 must be bool")
        if s.get("tamil_count") != len(ta):
            fail(f"{path.name}: tamil_count != len(tamil_chapters)")

        en = s.get("english_chapters")
        if status == "english_done":  # G3
            if not en:
                fail(f"{path.name}: english_done with null english_chapters")
            elif ([c.get("n") for c in en] != [c.get("n") for c in ta]
                    or len(en) != len(ta) or not ta):
                fail(f"{path.name}: english/tamil chapter mismatch")
            if s.get("english_count") != (len(en) if en else 0) or \
                    s.get("english_count", 0) <= 0:
                fail(f"{path.name}: english_count must equal tamil_count > 0")
        if status == "tamil_verified":  # G4
            if en is not None or s.get("english_count", -1) != 0:
                fail(f"{path.name}: tamil_verified must have null "
                     f"english_chapters and english_count 0")
        if en and [c.get("n") for c in en] != list(range(1, len(en) + 1)):
            fail(f"{path.name}: english chapter n not contiguous from 1")

        verses = s.get("verses", [])  # G6
        if s.get("verse_count") != len(verses):
            fail(f"{path.name}: verse_count != len(verses)")
        slug = s.get("section_slug")
        if len(verses) > 0:
            want = FMAP_VERSES.get(s.get("slug"))
            if want is not None:
                if len(verses) != want:
                    fail(f"{path.name}: verse_count {len(verses)} != "
                         f"mapped drawer total {want}")
            elif slug not in sections:
                fail(f"{path.name}: section_slug not in drawer")
            elif len(verses) != sections[slug]["n_songs"]:
                fail(f"{path.name}: verse_count {len(verses)} != drawer "
                     f"section length {sections[slug]['n_songs']}")
            for v in verses:
                if v.get("yappuKey") not in KNOWN_KEYS:
                    fail(f"{path.name}: verse {v.get('n')} bad yappuKey "
                         f"{v.get('yappuKey')!r}")
                if v.get("kind") not in KINDS:
                    fail(f"{path.name}: verse {v.get('n')} bad kind "
                         f"{v.get('kind')!r}")

    mpath = BUILD / "manifest.json"  # G7
    if not mpath.exists():
        fail("content/build/manifest.json missing")
        raise SystemExit(1)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    seen = set()
    for e in manifest:
        if set(e) != MANIFEST_FIELDS:
            fail(f"manifest entry {e.get('slug')}: fields "
                 f"{sorted(set(e))} != expected")
        if e.get("schema_version") != 1:
            fail(f"manifest {e.get('slug')}: schema_version != 1")
        if e.get("status") not in LISTED:
            fail(f"manifest {e.get('slug')}: status {e.get('status')!r} "
                 f"must be listed-only (transcribed never listed)")
        key = e.get("slug")
        seen.add(key)
        if key not in stories:
            fail(f"manifest {key}: no matching story file")
            continue
        _, s = stories[key]
        for f in ("tamil_count", "english_count", "verse_count",
                  "section_slug", "exported_at"):
            if e.get(f) != s.get(f):
                fail(f"manifest {key}: {f} {e.get(f)!r} != story {s.get(f)!r}")
        if e.get("section_order") != FMAP_ORDER.get(key, 999):
            fail(f"manifest {key}: section_order "
                 f"{e.get('section_order')!r} not canonical")
        if e.get("id") != s.get("id") or \
                e.get("titleEn") != s.get("nameEn") or \
                e.get("titleTa") != s.get("nameTa") or \
                e.get("image") != s.get("image") or \
                e.get("type") != s.get("type") or \
                e.get("isBig4") != s.get("isBig4") or \
                e.get("group") != s.get("group") or \
                e.get("category") != s.get("category"):
            fail(f"manifest {key}: id/title/image/type/isBig4/group/"
                 f"category drift vs story file")
    for key, (path, s) in stories.items():
        if s.get("status") in LISTED and key not in seen:
            fail(f"{path.name}: listed status but missing from manifest")
        if s.get("status") == "transcribed" and key in seen:
            fail(f"{path.name}: transcribed must never be listed")
    order = [(e.get("section_order", 999), e.get("slug")) for e in manifest]
    if order != sorted(order):
        fail("manifest not in canonical (section_order, slug) order")

    for e in gate_escaping():  # G8
        fail(e)
    for e in gate_preview_leak():  # preview must never ship
        fail(e)

    if errors:
        print(f"GATES FAILED ({len(errors)}):")
        for e in errors:
            print("  -", e)
        return 1
    listed = sum(1 for _, s in stories.values() if s.get("status") in LISTED)
    print(f"gates clean: {len(stories)} stories, {listed} listed, "
          f"{len(manifest)} manifest entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
