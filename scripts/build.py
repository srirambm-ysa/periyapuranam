"""Per-story JSON builder (schema v1) — generalizes the frozen TK pilot.

Golden files stay byte-identical and are NEVER imported here:
  scripts/build_tirukkurippu_experiment.py  (logic copied/adapted below)
  reference/tiruk_kurippu_experiment.html   (diff oracle for --check)

Contract: docs/CONTRACT.md, field list: docs/SCHEMA_V1.md.
Usage:
  python scripts/build.py                       # build TK pilot
  python scripts/build.py --all                 # build every registry entry
  python scripts/build.py --check               # rebuild TK + diff vs golden
Output: content/build/<slug>.json (schema_version 1)
"""
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from yappu_db import label_to_key  # noqa: E402

CONTENT = REPO / "content"
STORIES = CONTENT / "stories"
BUILD = CONTENT / "build"
PREVIEW = CONTENT / "preview"
CORPUS = CONTENT / "Thirumurai_12_shaivam_corpus.json"
GOLDEN_HTML = REPO / "reference" / "tiruk_kurippu_experiment.html"

CHAP_RE = re.compile(r"^Chapter (\d+)\s*[-–—:]?\s*(.*)$")

# Registry: one entry per buildable story. section_slug + ref come from the
# factory session (drawer mapping); display metadata comes from the legacy
# record until the factory supplies another source (SCHEMA_V1 §5).
STORIES_REGISTRY = {
    "tiruk_kurippu_tonda_nayanar": {
        "legacy": CONTENT / "tiruk_kurippu.json",
        "section_slug": ("periya-puranam-mummaiyal-ulakanda-charukkam-"
                         "thiruk-kuripputh-thonta-nayanar-puranam"),
        "ref": "திருக்குறிப்புத்தொண்ட புராணம்",
        "status": "english_done",
        "expect": {"tamil": 36, "english": 36, "verses": 128},
    },
}


def story_text_path(slug, lang):
    """Factory location first, legacy top-level seed as fallback."""
    for cand in (STORIES / f"{slug}_{lang}.txt",
                 CONTENT / f"{slug}_{lang}.txt"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no {lang} text for {slug}")


def split_chapters(text):
    """Header stripped, number in n; paras whitespace-normalized.
    (Copied from the frozen golden builder — keep logic in sync by hand.)"""
    parts = re.split(r"(?=^Chapter \d+)", text, flags=re.M)
    chapters = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = CHAP_RE.match(p.split("\n", 1)[0])
        assert m, "chapter head mismatch: %r" % p[:60]
        body = p.split("\n", 1)[1] if "\n" in p else ""
        paras = [re.sub(r"\s+", " ", q).strip()
                 for q in re.split(r"\n\s*\n", body) if q.strip()]
        chapters.append({"n": int(m.group(1)),
                         "text": "\n\n".join(paras)})
    chapters.sort(key=lambda c: c["n"])
    assert [c["n"] for c in chapters] == list(range(1, len(chapters) + 1)), \
        "chapter sequence broken"
    return chapters


def load_drawer_verses(section_slug, ref):
    """Full canonical section in drawer order; metre keys mapped, zero unmapped.
    (Copied from the frozen golden builder — keep logic in sync by hand.)"""
    sections = {c["slug"]: c for c in
                json.loads(CORPUS.read_text(encoding="utf-8"))}
    songs = sections[section_slug]["songs"]
    verses, unmapped = [], []
    for s in songs:
        n = int(str(s.get("song_no")).strip())
        label = s.get("metre") or s.get("type_inherited") or ""
        key = label_to_key(label)
        if key is None:
            unmapped.append((n, label))
        raw = (s.get("raw_song") or s.get("tamil_split") or "")
        lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
        verses.append({"n": n, "lines": lines, "yappuKey": key,
                       "ref": ref, "kind": "periyapuranam_root"})
    if unmapped:
        raise ValueError(f"drawer verses with no card key: {unmapped}")
    verses.sort(key=lambda v: v["n"])
    return verses


def load_drawer_verses_preview(section_slug, ref):
    """Preview-only tolerant verse loader: returns (verses, unmapped_labels).
    Unmapped metre labels are collected per story instead of raising (the
    product loader above stays fail-fast and frozen). yappu_db.py untouched."""
    sections = {c["slug"]: c for c in
                json.loads(CORPUS.read_text(encoding="utf-8"))}
    if section_slug not in sections:
        return None, []
    songs = sections[section_slug]["songs"]
    verses, unmapped = [], []
    for s in songs:
        n = int(str(s.get("song_no")).strip())
        label = s.get("metre") or s.get("type_inherited") or ""
        key = label_to_key(label)
        if key is None:
            unmapped.append((n, label))
            continue
        raw = (s.get("raw_song") or s.get("tamil_split") or "")
        lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
        verses.append({"n": n, "lines": lines, "yappuKey": key,
                       "ref": ref, "kind": "periyapuranam_root"})
    verses.sort(key=lambda v: v["n"])
    return verses, sorted(set(label for _, label in unmapped))


def read_time_label(ta_full):
    read_mins = max(15, round(len(ta_full) / 1100))
    return ("~%d hrs" % round(read_mins / 60)) if read_mins >= 90 \
        else ("~%d mins" % read_mins)


def build_story(slug, cfg):
    ta_full = story_text_path(slug, "tamil").read_text(encoding="utf-8")
    ta_ch = split_chapters(ta_full)
    exp = cfg["expect"]
    assert len(ta_ch) == exp["tamil"], (slug, len(ta_ch))

    if cfg["status"] == "english_done":
        en_full = story_text_path(slug, "english").read_text(encoding="utf-8")
        en_ch = split_chapters(en_full)
        assert len(en_ch) == exp["english"], (slug, len(en_ch))
        assert [c["n"] for c in ta_ch] == [c["n"] for c in en_ch], \
            "tamil/english chapter n mismatch"
        english_chapters = en_ch
    else:
        english_chapters = None

    verses = load_drawer_verses(cfg["section_slug"], cfg["ref"])
    assert len(verses) == exp["verses"], (slug, len(verses))

    legacy = json.loads(cfg["legacy"].read_text(encoding="utf-8"))
    if isinstance(legacy, list):
        legacy = legacy[0]

    return {
        "schema_version": 1,
        "slug": slug,
        "id": legacy["id"],
        "status": cfg["status"],
        "nameEn": legacy["nameEn"],
        "nameTa": legacy["nameTa"],
        "type": legacy["type"],
        "isBig4": legacy["isBig4"],
        "category": legacy["category"],
        "place": legacy["place"],
        "grace": legacy["grace"],
        "readTime": read_time_label(ta_full),
        "image": legacy["image"],
        "prev": legacy["prev"],
        "next": legacy["next"],
        "summary": legacy["summary"],
        "subtitle": legacy["subtitle"],
        "tamil_chapters": ta_ch,
        "english_chapters": english_chapters,
        "verses": verses,
        "section_slug": cfg["section_slug"],
        "tamil_count": len(ta_ch),
        "english_count": len(english_chapters) if english_chapters else 0,
        "verse_count": len(verses),
        "exported_at": datetime.now(timezone.utc).date().isoformat(),
    }


LISTED = ("tamil_verified", "english_done")


def write_manifest():
    """Manifest lists listed stories only; transcribed never appears.
    Built from build outputs (plus registry status), never scanned at runtime."""
    entries = []
    for path in sorted(BUILD.glob("*.json")):
        if path.name == "manifest.json":
            continue
        story = json.loads(path.read_text(encoding="utf-8"))
        if story["status"] not in LISTED:
            continue
        entries.append({
            "slug": story["slug"],
            "id": story["id"],
            "titleEn": story["nameEn"],
            "titleTa": story["nameTa"],
            "status": story["status"],
            "schema_version": story["schema_version"],
            "image": story["image"],
            "type": story["type"],
            "category": story["category"],
            "tamil_count": story["tamil_count"],
            "english_count": story["english_count"],
            "verse_count": story["verse_count"],
            "section_slug": story["section_slug"],
            "exported_at": story["exported_at"],
        })
    entries.sort(key=lambda e: e["slug"])
    (BUILD / "manifest.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote content/build/manifest.json: {len(entries)} listed")


def split_chapters_preview(text):
    """Preview-only tolerance: drop any leading preamble (title line,
    Thiruchitrambalam opener) before the first chapter head, then use the
    frozen product splitter. Never used for content/build/."""
    m = re.search(r"(?m)^Chapter \d+", text)
    assert m, "no chapter heads at all"
    return split_chapters(text[m.start():])


def build_preview():
    """Local-only full-scale gallery preview (never ships, never gated as
    product): all 68 factory stories to content/preview/. TK is the full
    signed-off artifact (english_done + drawer verses) plus preview:true,
    rebuilt exactly as-is. The other 67 get both chapter languages plus
    drawer verses via content/factory_section_map.json (map_version 1);
    display names from the map; type/category absent where absent. Stories
    with unmapped metre labels (or verse-count mismatch) build with
    verses [] + verses_pending_reason and land in the report — the run
    never fails. Every file and manifest entry carries preview:true."""
    PREVIEW.mkdir(parents=True, exist_ok=True)
    factory_map = {e["factory_slug"]: e for e in json.loads(
        (CONTENT / "factory_section_map.json").read_text(encoding="utf-8"))
        ["entries"]}
    slugs = sorted(p.name[:-len("_tamil.txt")]
                   for p in STORIES.glob("*_tamil.txt"))
    entries, failed, unmapped_report, flagged = [], [], {}, []
    for slug in slugs:
        try:
            if slug in STORIES_REGISTRY:
                story = build_story(slug, STORIES_REGISTRY[slug])
            else:
                ta_full = story_text_path(slug, "tamil") \
                    .read_text(encoding="utf-8")
                en_full = story_text_path(slug, "english") \
                    .read_text(encoding="utf-8")
                ta_ch = split_chapters_preview(ta_full)
                en_ch = split_chapters_preview(en_full)
                assert [c["n"] for c in ta_ch] == \
                    [c["n"] for c in en_ch], "tamil/english n mismatch"
                entry = factory_map.get(slug)
                assert entry and entry.get("section_slug"), "no map entry"
                verses, unmapped = load_drawer_verses_preview(
                    entry["section_slug"], entry["ref"])
                pending = None
                if verses is None:
                    pending = "section_missing"
                elif unmapped:
                    pending = "unmapped_labels"
                    unmapped_report[slug] = unmapped
                elif len(verses) != entry["n_songs"]:
                    pending = (f"count_mismatch: got {len(verses)}, "
                               f"map n_songs {entry['n_songs']}")
                if pending:
                    verses = []
                if entry.get("flag"):
                    flagged.append((slug, entry["flag"]))
                story = {
                    "schema_version": 1,
                    "slug": slug,
                    "id": entry.get("id") or slug.replace("_", "-"),
                    "status": "transcribed",
                    "nameEn": entry.get("nameEn") or "",
                    "nameTa": entry.get("nameTa") or "",
                    "type": entry.get("type") or "",
                    "isBig4": False,
                    "category": entry.get("category") or "",
                    "place": "",
                    "grace": "",
                    "readTime": read_time_label(ta_full),
                    "image": "",
                    "prev": None,
                    "next": None,
                    "summary": "(Local preview — unverified factory text, "
                               "not for deploy.)",
                    "subtitle": "",
                    "tamil_chapters": ta_ch,
                    "english_chapters": en_ch,
                    "verses": verses,
                    "section_slug": entry["section_slug"],
                    "tamil_count": len(ta_ch),
                    "english_count": len(en_ch),
                    "verse_count": len(verses),
                    "exported_at": datetime.now(timezone.utc).date()
                    .isoformat(),
                }
                if pending:
                    story["verses_pending_reason"] = pending
            story["preview"] = True
            (PREVIEW / f"{slug}.json").write_text(
                json.dumps(story, ensure_ascii=False, indent=2),
                encoding="utf-8")
            entries.append({
                "slug": story["slug"],
                "id": story["id"],
                "titleEn": story["nameEn"],
                "titleTa": story["nameTa"],
                "status": story["status"],
                "schema_version": story["schema_version"],
                "preview": True,
                "image": story["image"],
                "type": story["type"],
                "category": story["category"],
                "tamil_count": story["tamil_count"],
                "english_count": story["english_count"],
                "verse_count": story["verse_count"],
                "section_slug": story["section_slug"],
                "exported_at": story["exported_at"],
            })
        except Exception as e:  # noqa: BLE001 — preview reports, never halts
            failed.append((slug, f"{type(e).__name__}: {e}"))
    entries.sort(key=lambda e: e["slug"])
    (PREVIEW / "manifest.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    populated = sum(1 for e in entries
                    if e["slug"] != "tiruk_kurippu_tonda_nayanar"
                    and e["verse_count"] > 0)
    vtotal = sum(e["verse_count"] for e in entries
                 if e["slug"] != "tiruk_kurippu_tonda_nayanar")
    print(f"preview: {len(entries)} stories, {len(failed)} failed, "
          f"{populated}/67 verse-populated, {vtotal} drawer verses")
    for slug, reason in failed:
        print(f"  FAILED {slug}: {reason}")
    for slug in sorted(unmapped_report):
        print(f"  UNMAPPED {slug}: {unmapped_report[slug]}")
    for slug, flag in flagged:
        print(f"  FLAG {slug}: {flag}")
    return failed


def build_all(slugs):
    BUILD.mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        story = build_story(slug, STORIES_REGISTRY[slug])
        out = BUILD / f"{slug}.json"
        out.write_text(json.dumps(story, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)}: "
              f"{story['tamil_count']} ta / {story['english_count']} en / "
              f"{story['verse_count']} verses [{story['status']}]")
    write_manifest()


def check_tk():
    """Acceptance test: rebuilt TK JSON diffs clean vs golden devoteesData
    on chapter n/text (para-joined) and verse n/lines/yappuKey/ref.
    `kind` is additive and excluded from the diff (SCHEMA_V1 §2)."""
    build_all(["tiruk_kurippu_tonda_nayanar"])
    ours = json.loads(
        (BUILD / "tiruk_kurippu_tonda_nayanar.json").read_text(
            encoding="utf-8"))
    tpl = GOLDEN_HTML.read_text(encoding="utf-8")
    m = re.search(r"const devoteesData = (\[.*?);\n\n        "
                  r"function formatThirumuraiVerseCard",
                  tpl, flags=re.DOTALL)
    assert m, "devoteesData span not found in golden HTML"
    golden = json.loads(m.group(1))[0]

    errors = []
    g_ch = golden["chapters"]
    if len(g_ch) != len(ours["tamil_chapters"]):
        errors.append(f"chapter count {len(g_ch)} != "
                      f"{len(ours['tamil_chapters'])}")
    for g, o in zip(g_ch, ours["tamil_chapters"]):
        for lang, key in (("content_ta", "tamil_chapters"),
                          ("content_en", "english_chapters")):
            g_text = "\n\n".join(html.unescape(p) for p in g[lang])
            o_text = (o["text"] if key == "tamil_chapters"
                      else ours["english_chapters"][o["n"] - 1]["text"])
            if g_text != o_text:
                errors.append(f"chapter {o['n']} {lang} text differs "
                              f"(golden {len(g_text)}ch vs ours "
                              f"{len(o_text)}ch)")
    g_v = golden["verses_all"]
    if len(g_v) != len(ours["verses"]):
        errors.append(f"verse count {len(g_v)} != {len(ours['verses'])}")
    for g, o in zip(g_v, ours["verses"]):
        if int(g["n"]) != o["n"]:
            errors.append(f"verse n {g['n']} != {o['n']}")
        if [html.unescape(x) for x in g["lines"]] != o["lines"]:
            errors.append(f"verse {o['n']} lines differ")
        if g["yappuKey"] != o["yappuKey"]:
            errors.append(f"verse {o['n']} yappuKey {g['yappuKey']} != "
                          f"{o['yappuKey']}")
        if html.unescape(g["ref"]) != o["ref"]:
            errors.append(f"verse {o['n']} ref differs")
    if errors:
        print("GOLDEN DIFF FAILED:")
        for e in errors[:20]:
            print("  -", e)
        raise SystemExit(1)
    print(f"golden diff clean: {len(ours['tamil_chapters'])} chapters, "
          f"{len(ours['verses'])} verses")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_tk()
    elif "--preview" in sys.argv:
        build_preview()
    elif "--manifest" in sys.argv:
        write_manifest()
    elif "--all" in sys.argv:
        build_all(list(STORIES_REGISTRY))
    else:
        build_all(["tiruk_kurippu_tonda_nayanar"])
