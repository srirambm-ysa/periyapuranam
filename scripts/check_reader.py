"""Reader display-controls regression pack.

Static audit of site/periya_puranam_index.html: every display control
(theme / font-size / weight / language), its selected-state highlight,
persistence + boot restore, the mobile bottom-sheet relocation, and the
auto-hide chrome. Run after ANY reader tweak:

    python scripts/check_reader.py

Exit 0 = all green, 1 = failures listed. Style follows scripts/check.py
(plain stdlib asserts collected into an error list).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PRODUCT = REPO / "site" / "periya_puranam_index.html"
PREVIEW = REPO / "site" / "preview.html"

fails = []
passes = []


def check(name, cond):
    (passes if cond else fails).append(name)


def main():
    t = PRODUCT.read_text(encoding="utf-8")

    # 1. Control buttons: id + handler, exactly once each.
    buttons = [
        ("theme-btn-parchment", "setTheme('parchment')"),
        ("theme-btn-sepia", "setTheme('sepia')"),
        ("theme-btn-dark", "setTheme('dark')"),
        ("font-btn-sm", "setFontSize('sm')"),
        ("font-btn-md", "setFontSize('md')"),
        ("font-btn-lg", "setFontSize('lg')"),
        ("font-btn-xl", "setFontSize('xl')"),
        ("weight-btn-regular", "setWeight('regular')"),
        ("weight-btn-bold", "setWeight('bold')"),
        ("lang-btn-en", "setLang('en')"),
        ("lang-btn-ta", "setLang('ta')"),
    ]
    for bid, onclick in buttons:
        check(f"button {bid} present once",
              t.count(f'id="{bid}"') == 1)
        check(f"button {bid} wired to {onclick}",
              t.count(f'onclick="{onclick}"') == 1)
    check("display-sheet gear button present",
          t.count('id="display-sheet-btn"') == 1
          and 'onclick="openDisplaySheet()"' in t)

    # 2. Selected-state parity: every set* handler highlights its buttons.
    for prefix, fname in [("theme-btn", "setTheme"), ("font-btn", "setFontSize"),
                          ("weight-btn", "setWeight"), ("lang-btn", "setLang")]:
        m = re.search(r"function %s\(.*?\{.*?\n        \}" % fname, t, re.S)
        body = m.group(0) if m else ""
        hit = any(q in body for q in (f"getElementById(`{prefix}-",
                                      f'getElementById("{prefix}-',
                                      f"getElementById('{prefix}-"))
        check(f"{fname} highlights {prefix}*",
              m is not None and hit and "bg-templeGold/30" in body)

    # 3. CSS rules backing the controls.
    for cls in ["body.theme-parchment", "body.theme-sepia", "body.theme-dark",
                ".story-text-sm", ".story-text-md", ".story-text-lg",
                ".story-text-xl", "#post-chapters-container.story-bold"]:
        check(f"CSS rule {cls}", cls in t)
    check("mobile chrome CSS (reader-active/chrome-hidden)",
          "body.reader-active.chrome-hidden" in t
          and "#reader-toolbar" in t)
    check("sheet CSS (#display-sheet.open + sheet-row)",
          "#display-sheet.open" in t and ".sheet-row" in t)

    # 4. Persistence: set + boot restore for all four settings.
    for key in ["periya_puranam_theme", "periya_puranam_fontsize",
                "periya_puranam_fontweight", "pp_lang"]:
        check(f"localStorage persists {key}",
              f"localStorage.setItem('{key}'" in t)
        check(f"boot restores {key}",
              f"localStorage.getItem('{key}')" in t)

    # 5. Relocation parity: every ctl-* group has a slot + is moved.
    ctls = sorted(set(re.findall(r'id="(ctl-[a-z]+)"', t)))
    check("control groups found", len(ctls) >= 4)
    for c in ctls:
        slot = c.replace("ctl-", "slot-")
        check(f"slot {slot} exists", f'id="{slot}"' in t)
        check(f"relocate moves {c}",
              f"getElementById('{c}')" in t
              and f"getElementById('{slot}')" in t)

    # 6. ID uniqueness across the whole file.
    ids = re.findall(r'id="([^"]+)"', t)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    check("no duplicate IDs", not dupes)

    # 7. Mobile chrome JS hooks.
    for token in ["function updateChromeVisibility",
                  "function revealChrome",
                  "function openDisplaySheet",
                  "relocateDisplayControls()",
                  "addEventListener('mousemove'",
                  "body.classList.add('reader-active')",
                  "classList.remove('reader-active'"]:
        check(f"chrome JS: {token}", token in t)

    # 8. Header gallery button removed (breadcrumb + Nayanmar Home +
    # brand logo remain the home paths; Saved stays functional).
    check("header gallery button gone",
          'id="btn-nav-gallery"' not in t
          and 'id="nav-gallery-label"' not in t)
    check("home paths intact (logo, breadcrumb, Nayanmar Home)",
          t.count('showGalleryView()"') + t.count('showGalleryView(); return false;') >= 3
          and "Nayanmar Home" in t)
    check("Saved Stories button intact",
          'onclick="toggleBookmarksDrawer()"' in t)

    # 9. Mobile inline TOC hidden (drawer covers chapters below lg).
    m = re.search(r'id="toc-inline"[^>]*class="([^"]+)"', t)
    check("toc-inline present once", t.count('id="toc-inline"') == 1)
    check("toc-inline hidden below lg, sticky on desktop",
          m is not None and "hidden" in m.group(1)
          and "lg:block" in m.group(1) and "sticky" in m.group(1))

    # 9. Last-read resume: persist on chapter activation + gallery banner.
    check("saveLastRead persists periya_puranam_lastread",
          "localStorage.setItem('periya_puranam_lastread'" in t)
    check("setActiveToc saves position", "saveLastRead();" in t)
    for fname in ["function readLastRead", "function renderResumeBanner",
                  "function resumeLastRead", "function dismissResume"]:
        check(f"resume JS: {fname}", fname in t)
    check("resume banner markup",
          t.count('id="resume-banner"') == 1
          and t.count('id="resume-text"') == 1
          and 'onclick="resumeLastRead()"' in t
          and 'onclick="dismissResume()"' in t)
    check("banner rendered on gallery + boot",
          t.count("renderResumeBanner();") >= 2)

    # 10. Preview regenerated from product, banner-free, correct DATA_BASE.
    if PREVIEW.exists():
        p = PREVIEW.read_text(encoding="utf-8")
        check("preview has display-sheet",
              'id="display-sheet"' in p)
        check("preview has setWeight",
              "function setWeight" in p)
        check("preview banner removed",
              "NOT FOR DEPLOY" not in p)
        check("preview reads content/preview",
              'const DATA_BASE = "../content/preview"' in p)
    else:
        check("preview.html exists", False)

    print(f"check_reader: {len(passes)} passed, {len(fails)} failed")
    for f in fails:
        print(f"  FAIL: {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
