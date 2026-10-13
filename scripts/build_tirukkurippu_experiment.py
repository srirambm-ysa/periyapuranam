"""Tiruk Kurippu pager experiment: 36 prose chapters + 128-verse drawer.

First consumer of the prose-only + Verses-drawer contract (2026-09-26 pivot).
No verse detection in the build path; metre keys map straight from shaivam
labels via ppreader/yappu_db.py. Tests: pager-vs-scroll hybrid, drawer TOC at
36 chapters, 128-verse drawer, offline shell.
Output: ppreader/tiruk_kurippu_experiment.html (template + data, no detection).
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from yappu_db import YAPPU_DB_JS, label_to_key  # noqa: E402

OUT = "ppreader"
SLUG = "tiruk_kurippu_tonda_nayanar"
DAY = "day-07"
SECTION_SLUG = ("periya-puranam-mummaiyal-ulakanda-charukkam-"
                "thiruk-kuripputh-thonta-nayanar-puranam")

CHAP_RE = re.compile(r"^Chapter (\d+)\s*[-–—:]?\s*(.*)$")


def split_chapters(text):
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
        chapters.append({"no": int(m.group(1)), "paras": paras})
    chapters.sort(key=lambda c: c["no"])
    assert [c["no"] for c in chapters] == list(range(1, len(chapters) + 1)), \
        "chapter sequence broken"
    return chapters


ta_full = open(f"periapuranam/output/{DAY}/{SLUG}/tamil_real/{SLUG}_tamil.txt",
               encoding="utf-8").read()
en_full = open(f"periapuranam/output/{DAY}/{SLUG}/{SLUG}_english.txt",
               encoding="utf-8").read()
ta_ch = split_chapters(ta_full)
en_ch = split_chapters(en_full)
assert len(ta_ch) == 36, len(ta_ch)
assert len(en_ch) == 36, len(en_ch)

# ---------- verses_all: full canonical section, metre keys mapped ----------
t12 = {c["slug"]: c for c in json.load(open(
    "periapuranam/canonical/Thirumurai_12_Periyapuranam/"
    "Thirumurai_12_shaivam_corpus.json", encoding="utf-8"))}
songs = t12[SECTION_SLUG]["songs"]
assert len(songs) == 128, len(songs)
verses_all, unmapped, linecounts = [], [], {}
for s in songs:
    n = int(str(s.get("song_no")).strip())
    label = s.get("metre") or s.get("type_inherited") or ""
    key = label_to_key(label)
    if key is None:
        unmapped.append((n, label))
    raw = (s.get("raw_song") or s.get("tamil_split") or "")
    lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
    linecounts[len(lines)] = linecounts.get(len(lines), 0) + 1
    verses_all.append({
        "n": n,
        "lines": [html.escape(ln) for ln in lines],
        "yappuKey": key,
        "ref": "திருக்குறிப்புத்தொண்ட புராணம்",
    })
print("verse line-count distribution:", linecounts)
print("unmapped metre labels:", unmapped if unmapped else "none")
assert not unmapped, "drawer has verses with no card key"

chapters = []
for ta, en in zip(ta_ch, en_ch):
    assert ta["no"] == en["no"]
    chapters.append({
        "title": "Chapter %02d" % ta["no"],
        "content_en": [html.escape(p) for p in en["paras"]],
        "content_ta": [html.escape(p) for p in ta["paras"]],
    })

read_mins = max(15, round(len(ta_full) / 1100))
read_label = ("~%d hrs" % round(read_mins / 60)) if read_mins >= 90 \
    else ("~%d mins" % read_mins)
story = {
    "id": "tiruk-kurippu-tonda-nayanar",
    "nameEn": "Tiruk Kurippu Tonda Nayanar",
    "nameTa": "திருக்குறிப்புத்தொண்ட நாயனார்",
    "type": "tani", "isBig4": False,
    "category": "Service by discerning devotion",
    "place": "Kanchipuram (Thondai Nadu)",
    "grace": "Read devotees' intentions; washed their clothes",
    "readTime": read_label,
    "image": "./chola_bronze_320.png",
    "prev": {"id": "", "nameEn": "Tirunalaippovar Nayanar",
             "nameTa": "திருநாளைப்போவார் நாயனார்", "published": False},
    "next": None,
    "summary": ("Born in Kanchipuram to a washerman family, Tirukkurippu "
                "Tondar served Shiva's devotees by washing their clothes — "
                "reading and fulfilling their unspoken intentions (kurippu). "
                "Tested by Shiva with a soiled garment and unceasing rain, "
                "he held firm and attained Shiva Loka."),
    "subtitle": "Thondai Nadu sung in 110 verses; the saint's steadfast service in 17",
    "chapters": chapters,
    "verses_all": verses_all,
}

# ---------- patch template ----------
tpl = open(f"{OUT}/periya_puranam_index.html", encoding="utf-8").read()

# P-a: 6-card PP yappu DB (shared module)
tpl2, n1 = re.subn(r"const yappuDatabase = \{.*?\n        \};",
                   lambda _: YAPPU_DB_JS, tpl, count=1, flags=re.DOTALL)
assert n1 == 1, "yappuDB patch failed"

# P-b: story data (prose chapters + verses_all)
story_js = json.dumps([story], ensure_ascii=False, indent=12)
tpl2, n2 = re.subn(r"const devoteesData = \[.*?function formatThirumuraiVerseCard",
                   lambda _: "const devoteesData = " + story_js
                   + ";\n\n        function formatThirumuraiVerseCard",
                   tpl2, count=1, flags=re.DOTALL)
assert n2 == 1, "devoteesData patch failed"

# P-c: pager + windowed-scroll engine (replaces template render-all)
PAGER_CODE = """// Render Post Chapters (pager + windowed scroll, giants path)
            window._ppMode = localStorage.getItem('pp_mode') || 'pager';
            window._ppWin = 2;
            window._ppChapters = devotee.chapters;
            window._ppPagerIdx = (typeof chapterIdx === 'number' ? chapterIdx : 0) || 0;
            window._chapterHTML = (chap, index) => {
                const L = localStorage.getItem('pp_lang') || 'en';
                const enCls = 'text-justify leading-relaxed lang-en' + (L === 'en' ? '' : ' hidden');
                const taCls = 'font-tamil text-justify leading-relaxed lang-ta' + (L === 'ta' ? '' : ' hidden');
                const enPs = (chap.content_en || [chap.content]).map((p, pi) =>
                    '<p class="' + (pi === 0 ? 'drop-cap ' : '') + enCls + '">' + p + '</p>').join('');
                const taPs = (chap.content_ta || []).map(t =>
                    '<p class="' + taCls + '">' + t + '</p>').join('');
                return '<section id="chapter-' + index + '" class="space-y-4 pt-4 border-b border-templeGold/20 pb-8">'
                    + '<h2 class="font-heading font-bold text-2xl sm:text-3xl text-amber-300 flex items-center gap-3">'
                    + '<span class="text-saffron font-sans text-sm border border-saffron px-2.5 py-1 rounded-md">Chapter ' + (index + 1) + '</span></h2>' + enPs + taPs + '</section>';
            };
            window._shellHTML = (chap, index) =>
                '<section id="chapter-' + index + '" data-ph="1" data-i="' + index + '" class="space-y-4 pt-4 border-b border-templeGold/20 pb-8 min-h-[30vh]">'
                + '<h2 class="font-heading font-bold text-2xl sm:text-3xl text-amber-300 flex items-center gap-3">'
                + '<span class="text-saffron font-sans text-sm border border-saffron px-2.5 py-1 rounded-md">Chapter ' + (index + 1) + '</span></h2>'
                + '<p class="text-sm text-gray-500">Loading chapter…</p></section>';
            window._renderWindow = (center) => {
                const chs = window._ppChapters || [];
                for (let i = Math.max(0, center - window._ppWin); i <= Math.min(chs.length - 1, center + window._ppWin); i++) {
                    const el = document.getElementById('chapter-' + i);
                    if (el && el.hasAttribute('data-ph')) {
                        const tmp = document.createElement('div');
                        tmp.innerHTML = window._chapterHTML(chs[i], i);
                        const real = tmp.firstElementChild;
                        el.replaceWith(real);
                        if (window._tocObserver) window._tocObserver.observe(real);
                    }
                }
            };
            window._renderPagerBar = () => {
                const chs = window._ppChapters || [];
                const i = window._ppPagerIdx || 0;
                const host = document.getElementById('post-chapters-container');
                let bar = document.getElementById('pp-pagerbar');
                if (!bar) {
                    bar = document.createElement('div');
                    bar.id = 'pp-pagerbar';
                    host.parentNode.insertBefore(bar, host);
                }
                let bottom = document.getElementById('pp-bottombar');
                if (!bottom) {
                    bottom = document.createElement('div');
                    bottom.id = 'pp-bottombar';
                    document.body.appendChild(bottom);
                }
                const opts = chs.map((c, k) => '<option value="' + k + '"' + (k === i ? ' selected' : '') + '>Chapter ' + (k + 1) + ' / ' + chs.length + '</option>').join('');
                const modeBtn = window._ppMode === 'pager'
                    ? '<button onclick="setPpMode(\\'scroll\\')" class="min-h-[44px] px-3 rounded-lg border border-templeGold/50 text-xs font-bold text-amber-200 hover:bg-templeGold/10">Scroll mode</button>'
                    : '<button onclick="setPpMode(\\'pager\\')" class="min-h-[44px] px-3 rounded-lg border border-templeGold/50 text-xs font-bold text-amber-200 hover:bg-templeGold/10">Pager mode</button>';
                bar.className = 'flex flex-wrap items-center gap-2 mb-6 p-2 rounded-xl bg-parchment/95 dark:bg-darkBg/95 border border-templeGold/30';
                bar.innerHTML = '<select onchange="ppJump(this.value)" class="min-h-[44px] flex-1 min-w-[140px] px-2 rounded-lg bg-parchmentDark/60 dark:bg-zinc-800 text-xs font-bold text-charcoal dark:text-amber-100 border border-templeGold/30">' + opts + '</select>'
                    + modeBtn
                    + '<span class="text-[11px] text-gray-500">' + chs.length + '-chapter scale test</span>';
                if (window._ppMode === 'pager') {
                    bottom.style.display = '';
                    bottom.className = 'fixed bottom-0 inset-x-0 z-30 border-t border-templeGold/40 bg-parchment/95 dark:bg-darkBg/95 backdrop-blur-md';
                    bottom.style.paddingBottom = 'env(safe-area-inset-bottom)';
                    bottom.innerHTML = '<div class="max-w-7xl mx-auto px-4 py-2 flex items-center gap-2">'
                        + '<button onclick="ppStep(-1)" class="min-h-[44px] flex-1 rounded-lg bg-templeRed text-templeGold text-sm font-bold">‹ Prev</button>'
                        + '<button onclick="openTocDrawer()" class="min-h-[44px] flex-1 rounded-lg border border-templeGold/50 text-xs font-bold text-amber-200">' + (i + 1) + ' / ' + chs.length + '</button>'
                        + '<button onclick="ppStep(1)" class="min-h-[44px] flex-1 rounded-lg bg-templeRed text-templeGold text-sm font-bold">Next ›</button></div>';
                    host.style.paddingBottom = '76px';
                } else {
                    bottom.style.display = 'none';
                    bottom.innerHTML = '';
                    host.style.paddingBottom = '';
                }
            };
            window.ppStep = (d) => {
                const chs = window._ppChapters || [];
                const n = Math.min(chs.length - 1, Math.max(0, (window._ppPagerIdx || 0) + d));
                scrollToChapter(n);
            };
            window.ppJump = (v) => { scrollToChapter(parseInt(v, 10) || 0); };
            window.setPpMode = (m) => {
                window._ppMode = m;
                try { localStorage.setItem('pp_mode', m); } catch (e) {}
                bootChapters(window._ppPagerIdx || 0);
            };
            window._renderPager = (i) => {
                const chs = window._ppChapters || [];
                window._ppPagerIdx = Math.min(chs.length - 1, Math.max(0, i));
                const host = document.getElementById('post-chapters-container');
                host.innerHTML = window._chapterHTML(chs[window._ppPagerIdx], window._ppPagerIdx);
                window._renderPagerBar();
                setActiveToc(window._ppPagerIdx);
                renderEndNav(devotee);
            };
            function bootChapters(center) {
                const host = document.getElementById('post-chapters-container');
                if (window._ppMode === 'pager') {
                    window._renderPager(center);
                } else {
                    const old = document.getElementById('pp-pagerbar');
                    host.innerHTML = window._ppChapters.map((chap, k) => window._shellHTML(chap, k)).join('');
                    window._renderWindow(center);
                    window._renderPagerBar();
                    if (window._ppObserver) window._ppObserver.disconnect();
                    if ('IntersectionObserver' in window) {
                        window._ppObserver = new IntersectionObserver((es) => {
                            es.forEach(e => {
                                if (e.isIntersecting && e.target.hasAttribute('data-ph')) {
                                    const k = parseInt(e.target.getAttribute('data-i'), 10);
                                    const tmp = document.createElement('div');
                                    tmp.innerHTML = window._chapterHTML(window._ppChapters[k], k);
                                    const real = tmp.firstElementChild;
                                    e.target.replaceWith(real);
                                    if (window._tocObserver) window._tocObserver.observe(real);
                                }
                            });
                        }, { rootMargin: '900px 0px' });
                        host.querySelectorAll('section[data-ph]').forEach(s => window._ppObserver.observe(s));
                    }
                    initTocSpy();
                    setActiveToc(center);
                    renderEndNav(devotee);
                }
            }
            bootChapters(window._ppPagerIdx);"""
w1 = tpl2.find("// Render Post Chapters")
w2 = tpl2.find("`).join('');", w1)
assert w1 != -1 and w2 != -1, "window render span not found"
tpl2 = tpl2[:w1] + PAGER_CODE + tpl2[w2 + len("`).join('');"):]

# P-d: pager-aware scrollToChapter + TOC highlight (sidebar + drawer) + spy
OLD_SCROLL2 = """        function scrollToChapter(index) {
            activeChapterIndex = index;
            const target = document.getElementById(`chapter-${index}`);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""
NEW_SCROLL = """        let tocObserver = null;
        function setActiveToc(index) {
            activeChapterIndex = index;
            ['toc-chapter-list', 'toc-drawer-list'].forEach((id) => {
                document.querySelectorAll('#' + id + ' button').forEach((b, i) => {
                    const on = i === index;
                    b.classList.toggle('bg-templeGold/30', on);
                    b.classList.toggle('text-templeRed', on);
                    b.classList.toggle('dark:text-amber-200', on);
                    b.classList.toggle('font-bold', on);
                });
            });
            try { history.replaceState(null, '', '#story=' + activeStoryId + '&chapter=' + index); } catch (e) {}
        }
        function initTocSpy() {
            if (tocObserver) tocObserver.disconnect();
            const secs = document.querySelectorAll('#post-chapters-container section[id^="chapter-"]');
            if (!('IntersectionObserver' in window) || !secs.length) return;
            tocObserver = new IntersectionObserver((entries) => {
                entries.forEach(e => {
                    if (e.isIntersecting) {
                        const idx = parseInt(e.target.id.replace('chapter-', ''), 10);
                        if (!isNaN(idx)) setActiveToc(idx);
                    }
                });
            }, { rootMargin: '-30% 0px -60% 0px' });
            secs.forEach(s => tocObserver.observe(s));
            window._tocObserver = tocObserver;
        }
        function scrollToChapter(index) {
            const chs = window._ppChapters || [];
            index = Math.min(chs.length - 1, Math.max(0, index));
            window._ppPagerIdx = index;
            if (window._ppMode === 'pager') {
                window._renderPager(index);
            } else {
                if (window._renderWindow) window._renderWindow(index);
                setActiveToc(index);
            }
            renderEndNav(devotee);
            requestAnimationFrame(() => {
                const target = document.getElementById(`chapter-${index}`);
                if (target && window._ppMode !== 'pager') target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                else window.scrollTo({ top: 0 });
            });
        }"""
assert OLD_SCROLL2 in tpl2, "scrollToChapter anchor missing"
tpl2 = tpl2.replace(OLD_SCROLL2, NEW_SCROLL)

# P-f: EN/TA toggle (lang-ta-gated Verses button needs setLang)
OLD_FONT = ">A++</button>\n                </div>"
NEW_FONT = """>A++</button>
                </div>

                <!-- Language Toggle -->
                <div class="flex items-center border border-templeGold/30 rounded-lg p-1 bg-parchmentDark/60 dark:bg-zinc-800">
                    <button id="lang-btn-en" onclick="setLang('en')" title="Read in English" class="min-h-[44px] min-w-[44px] px-2.5 py-0.5 text-xs font-bold rounded hover:text-templeRed">EN</button>
                    <button id="lang-btn-ta" onclick="setLang('ta')" title="தமிழில் படிக்க" class="min-h-[44px] min-w-[44px] px-2.5 py-0.5 text-xs font-bold rounded font-tamil hover:text-templeRed">தமிழ்</button>
                </div>"""
assert tpl2.count(OLD_FONT) == 1, "font anchor ambiguous"
tpl2 = tpl2.replace(OLD_FONT, NEW_FONT)

OLD_BM = "        function toggleBookmarksDrawer() {"
NEW_BM = """        function setLang(l) {
            document.querySelectorAll('.lang-en').forEach(e => e.classList.toggle('hidden', l !== 'en'));
            document.querySelectorAll('.lang-ta').forEach(e => e.classList.toggle('hidden', l !== 'ta'));
            const be = document.getElementById('lang-btn-en');
            const bt = document.getElementById('lang-btn-ta');
            if (be) be.classList.toggle('bg-templeGold/30', l === 'en');
            if (bt) bt.classList.toggle('bg-templeGold/30', l === 'ta');
            localStorage.setItem('pp_lang', l);
        }

        function toggleBookmarksDrawer() {"""
assert OLD_BM in tpl2, "bookmark anchor missing"
tpl2 = tpl2.replace(OLD_BM, NEW_BM)

# P-g: dark-only reader
assert '<body class="theme-parchment font-body' in tpl2, "body anchor missing"
tpl2 = tpl2.replace('<body class="theme-parchment font-body',
                    '<body class="theme-dark font-body', 1)
tpl2, nrm = re.subn(r"                <!-- Reading Mode Themes -->\n.*?\n                </div>\n",
                    "", tpl2, count=1, flags=re.DOTALL)
assert nrm == 1, "theme switcher removal failed"
OLD_SAVED = """            const savedTheme = localStorage.getItem('periya_puranam_theme');
            if (savedTheme) setTheme(savedTheme);"""
assert OLD_SAVED in tpl2, "theme init anchor missing"
tpl2 = tpl2.replace(OLD_SAVED, "            setTheme('dark'); // dark-only reader")
OLD_THEME = """        function setTheme(theme) {
            document.body.classList.remove('theme-parchment', 'theme-sepia', 'theme-dark');
            document.body.classList.add(`theme-${theme}`);
            localStorage.setItem('periya_puranam_theme', theme);
        }"""
NEW_THEME = """        function setTheme(theme) {
            document.body.classList.remove('theme-parchment', 'theme-sepia', 'theme-dark');
            document.body.classList.add(`theme-${theme}`);
            document.documentElement.classList.toggle('dark', theme === 'dark');
            localStorage.setItem('periya_puranam_theme', theme);
        }"""
assert OLD_THEME in tpl2, "setTheme anchor missing"
tpl2 = tpl2.replace(OLD_THEME, NEW_THEME)

# P-h: yappuPillars (drawer cards) + story-end footer + read checkmark
PILLARS = """        function yappuPillars(yappuKey) {
            const yappu = yappuDatabase[yappuKey] || {
                nameEn: "Metre Unidentified",
                nameTa: "யாப்பு அறியப்படவில்லை",
                math: { anatomy: "Pending classification", syllables: "—", rhyme: "—" },
                mood: { cadence: "—", effect: "—" },
                craft: { difficulty: "—", challenge: "—" },
                singing: { pann: "—", raga: "—", pause: "—" }
            };
            const row = (l, v) => '<p class="text-gray-700 dark:text-gray-200"><strong>' + l + ':</strong> ' + v + '</p>';
            const panel = (t, inner) => '<div class="p-4 rounded-xl bg-amber-50/80 dark:bg-zinc-800/80 border border-templeGold/30 space-y-1.5">'
                + '<div class="font-heading font-bold uppercase tracking-wider">' + t + '</div>' + inner + '</div>';
            return '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">'
                + panel('1. The Mathematics', row('Anatomy', yappu.math.anatomy) + row('Syllables', yappu.math.syllables) + row('Rhyme', yappu.math.rhyme))
                + panel('2. Mood & Rasa', row('Cadence', yappu.mood.cadence) + row('Effect', yappu.mood.effect))
                + panel('3. Poetic Rigor', row('Difficulty', yappu.craft.difficulty) + row('Challenge', yappu.craft.challenge))
                + panel('4. How to Sing', row('Pann', yappu.singing.pann) + row('Raga', yappu.singing.raga) + row('Pause', yappu.singing.pause))
                + '</div>';
        }

        function renderEndNav(devotee) {
            const host = document.getElementById('story-end-nav');
            if (!host) return;
            const songs = devotee.verses_all || [];
            const metres = [...new Set(songs.map(s => s.yappuKey).filter(Boolean))];
            const mnames = metres.map(k => ((typeof yappuDatabase !== 'undefined' && yappuDatabase[k] ? yappuDatabase[k].nameTa : k))).join(' · ');
            host.innerHTML = `
                <div class="p-5 sm:p-6 rounded-2xl bg-zinc-900/90 border border-templeGold/40 shadow-inner mb-6">
                    <h3 class="font-heading font-bold text-base text-amber-200 mb-1">இக்கதையின் யாப்பு · Prosody in this story</h3>
                    <p class="text-xs sm:text-sm text-gray-300">📜 ${songs.length} root verses · 🎵 ${metres.length} metres${mnames ? ` (${mnames})` : ''} · ⏱ ${devotee.readTime || ''}</p>
                    <p class="text-xs sm:text-sm text-gray-400 mt-1 font-tamil">மூல பாடல்கள் அனைத்தும் மேலே உள்ள மூல பாடல்கள் பொத்தான் வழியே.</p>
                </div>
                <div class="flex flex-col sm:flex-row items-stretch gap-3 font-sans">
                    <button onclick="showGalleryView()" class="min-h-[44px] flex-1 px-5 py-3 rounded-xl border border-templeGold/50 hover:bg-templeGold/10 text-xs sm:text-sm font-semibold text-amber-200">🛕 Saint Gallery</button>
                </div>`;
            if ('IntersectionObserver' in window) {
                const mo = new IntersectionObserver((es) => {
                    es.forEach(e => {
                        if (e.isIntersecting) {
                            if (typeof savedReads !== 'undefined' && savedReads.indexOf(devotee.id) < 0) {
                                savedReads.push(devotee.id);
                                try { localStorage.setItem('pp_read', JSON.stringify(savedReads)); } catch (err) {}
                            }
                            mo.disconnect();
                        }
                    });
                }, { threshold: 0.3 });
                mo.observe(host);
            }
        }

        let activeFilter = 'all';"""
OLD_ACTF = "        let activeFilter = 'all';"
assert tpl2.count(OLD_ACTF) == 1, "activeFilter anchor ambiguous"
tpl2 = tpl2.replace(OLD_ACTF, PILLARS)

i1 = tpl2.find("<!-- Bottom Chapter Navigation -->")
i2 = tpl2.find("</article>", i1)
assert i1 != -1 and i2 != -1 and i1 < i2, "end-nav span not found"
tpl2 = (tpl2[:i1] + "<!-- Story End: summary + story navigation (rendered per story) -->\n"
        "                <div id=\"story-end-nav\" class=\"pt-8 border-t-2 border-templeGold/30\"></div>\n"
        "                " + tpl2[i2:])

OLD_SAVED2 = "let savedBookmarks = JSON.parse(localStorage.getItem('periya_puranam_bookmarks') || '[]');"
assert tpl2.count(OLD_SAVED2) == 1, "bookmarks anchor ambiguous"
tpl2 = tpl2.replace(OLD_SAVED2, OLD_SAVED2 + "\n        let savedReads = JSON.parse(localStorage.getItem('pp_read') || '[]');")

OLD_INIT2 = "            if (savedFontSize) setFontSize(savedFontSize);"
NEW_INIT2 = """            if (savedFontSize) setFontSize(savedFontSize);

            setLang(localStorage.getItem('pp_lang') || 'en');"""
assert OLD_INIT2 in tpl2, "init anchor missing"
tpl2 = tpl2.replace(OLD_INIT2, NEW_INIT2)

# P-j: hide pager bottom bar when returning to gallery
OLD_GAL = """        function showGalleryView() {
            document.getElementById('view-gallery').classList.remove('hidden');"""
NEW_GAL = """        function showGalleryView() {
            var bb = document.getElementById('pp-bottombar');
            if (bb) bb.style.display = 'none';
            document.getElementById('view-gallery').classList.remove('hidden');"""
assert OLD_GAL in tpl2, "gallery anchor missing"
tpl2 = tpl2.replace(OLD_GAL, NEW_GAL)

OLD_INIT = "handleHashRouting();\n        });"
assert tpl2.count(OLD_INIT) == 1, "init anchor ambiguous"
tpl2 = tpl2.replace(OLD_INIT,
    "if (window.location.hash && window.location.hash !== '#gallery') handleHashRouting(); else loadStory('tiruk-kurippu-tonda-nayanar');\n        });")

out = f"{OUT}/tiruk_kurippu_experiment.html"
open(out, "w", encoding="utf-8").write(tpl2)
print(f"wrote {out} ({len(tpl2)//1024}KB): {len(chapters)} chapters, "
      f"{len(verses_all)} drawer verses")
