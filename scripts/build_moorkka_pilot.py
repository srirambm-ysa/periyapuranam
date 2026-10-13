"""Moorkka pilot builder: real Tamil/English/verses.json -> standalone ppreader HTML.
First instance of the story-by-story batch converter (strategy 2026-09-25)."""
import json, re, glob

OUT = "ppreader"
SLUG = "moorkka_nayanar"
DAY = "day-01"

# ---------- load pipeline data ----------
vpath = f"periapuranam/output/{DAY}/{SLUG}/{SLUG}_verses.json"
vd = json.load(open(vpath, encoding="utf-8"))
verses = {v["id"]: v for v in vd["verses"]}

eng = open(f"periapuranam/output/{DAY}/{SLUG}/{SLUG}_english.txt", encoding="utf-8").read()
paras = [p.strip() for p in re.split(r"\n\s*\n", eng) if p.strip()]
paras = [p for p in paras if not re.match(r"Chapter \d+", p)]  # drop header para

def find_song(api_id):
    for f in glob.glob("periapuranam/canonical/**/*.json", recursive=True):
        if "section_index" in f or "story_sections" in f:
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        songs = d if isinstance(d, list) else d.get("songs", d.get("verses", []))
        if not isinstance(songs, list):
            continue
        for s in songs:
            if isinstance(s, dict) and s.get("api_id") == api_id:
                return s
    raise ValueError(f"api_id {api_id} missing")

songs = {vid: find_song(v["api_id"]) for vid, v in verses.items()}

# ---------- tamil segments via verse offsets (same 10-way split as english) ----------
ta_full = open(f"periapuranam/output/{DAY}/{SLUG}/tamil_real/{SLUG}_tamil.txt", encoding="utf-8").read()
R = {vid: (v["start_char"], v["end_char"]) for vid, v in verses.items()}
ALLSPANS = sorted(R.values())
def deverse_paras(a, b):
    kept, cur = [], a
    for s, e in ALLSPANS:
        if s >= a and e <= b:
            kept.append((cur, s)); cur = e
    kept.append((cur, b))
    text = "".join(ta_full[x:y] for x, y in kept)
    return [re.sub(r"\s+", " ", p).strip()
            for p in re.split(r"\n\s*\n", text) if p.strip()]
TA_BOUNDS = {
    "intro": (0, R["root-01"][0]),
    "first": (R["root-01"][1], R["root-02"][0]),
    "second": (R["root-02"][1], R["root-03"][0]),
    "third": (R["root-03"][1], R["root-04"][0]),
    "fourth": (R["root-04"][1], R["root-05"][0]),
    "fifth": (R["root-05"][1], R["root-06"][0]),
    "sixth": (R["root-06"][0], R["root-08"][0]),
    "eighth": (R["root-08"][0], R["root-10"][0]),
    "tenth": (R["root-10"][0], R["root-12"][0]),
    "twelfth": (R["root-12"][0], len(ta_full)),
}

# ---------- segment english paras by verse cue ----------
ORD_IDS = {
    "first": ["root-01"], "second": ["root-02"], "third": ["root-03"],
    "fourth": ["root-04"], "fifth": ["root-05"],
    "sixth": ["root-06", "root-07"], "eighth": ["root-08", "root-09"],
    "tenth": ["root-10", "root-11"], "twelfth": ["root-12"],
}
TITLES = {
    "intro": "Thogai & Anthathi Testimony",
    "first": "Fertile Thondai Nadu & Thiruverkaadu",
    "second": "Birth in the Velalar Lineage",
    "third": "Sacred Ash as True Essence",
    "fourth": "Daily Feeding of Devotees",
    "fifth": "Wealth Exhausted in Service",
    "sixth": "Poverty & the Turn to Gambling",
    "eighth": "Winning for the Devotees",
    "tenth": "Purity in Service",
    "twelfth": "Attaining the Sacred Feet",
}
CUE = re.compile(r"(?:^|(?<=\. ))(?:Now,\s+)?[Tt]he\s+"
                  r"(first|second|third|fourth|fifth|sixth|eighth|tenth|twelfth)\b.*?\bverses?[\.:]")
segments = [{"key": "intro", "ids": ["thogai-05-L5", "anthathi-38"], "paras": []}]
for p in paras:
    m = CUE.search(p)
    if m and m.group(1).lower() in ORD_IDS:
        key = m.group(1).lower()
        head, tail = p[:m.start()].strip(), p[m.start():].strip()
        if head:
            segments[-1]["paras"].append(head)  # tail of previous topic stays put
        segments.append({"key": key, "ids": ORD_IDS[key], "paras": [tail] if tail else []})
    else:
        segments[-1]["paras"].append(p)
# intro cue check: first para must be the intro (Thogai/Anthathi); closing praise lands on last segment
assert "Thirutthondathogai" in segments[0]["paras"][0], "intro para mismatch"

YAPPU = {
    "root-01": "aruseer-viruttham", "root-02": "aruseer-viruttham",
    "root-03": "aruseer-viruttham", "root-04": "aruseer-viruttham",
    "root-05": "aruseer-viruttham", "root-06": "aruseer-viruttham",
    "root-07": "aruseer-viruttham", "root-08": "kochakam-kalippa",
    "root-09": "kochakam-kalippa", "root-10": "kochakam-kalippa",
    "root-11": "kochakam-kalippa", "root-12": "kochakam-kalippa",
    "thogai-05-L5": "ezhucir-viruttham", "anthathi-38": "ezhucir-viruttham",
}

def clean_para(p):
    return re.sub(r"\s+", " ", p).strip()

def card_for(vid, seg_paras, qidx=0):
    v = verses[vid]
    song = songs[vid]
    tamil = "\n".join(ln.strip() for ln in song["raw_song"].strip().split("\n") if ln.strip())
    if vid == "thogai-05-L5":  # highlight the single quoted line of 8
        lines = tamil.split("\n")
        for i, ln in enumerate(lines):
            if "மூர்க்க" in ln and "அடியேன்" in ln:
                lines[i] = "<mark>" + ln + "</mark>"
        tamil = "\n".join(lines)
    n = v.get("verse_no")
    if v["kind"] == "periyapuranam_root":
        ref = f"மூர்க்க புராணம் · பாடல் {n}"
        via = f"shaivam label ({v['metre_source']})"
    elif v["kind"] == "thogai":
        ref = "திருத்தொண்டத்தொகை 07.039 · வரி 5"
        via = f"Gemini offline (conf {v.get('metre_confidence')}, single-source)"
    else:
        ref = "திருவந்தாதி · பாடல் 38"
        via = f"Gemini offline (conf {v.get('metre_confidence')}, engine-corroborated)"
    prov = f"யாப்பு: {v['metre']} · {via} · transcript match {v['match_score']}%"
    return {"vid": vid, "tamil": tamil, "kind": v["kind"],
            "yappuKey": YAPPU[vid], "ref": ref, "prov": prov}

chapters = []
for seg in segments:
    verses_list = [card_for(vid, seg["paras"], qidx=i) for i, vid in enumerate(seg["ids"])]
    chapters.append({
        "title": TITLES[seg["key"]],
        "content_en": [clean_para(p) for p in seg["paras"]],
        "content_ta": deverse_paras(*TA_BOUNDS[seg["key"]]),
        "verses": verses_list,
    })

story = {
    "id": "moorkka-nayanar", "nameEn": "Moorkka Nayanar",
    "nameTa": "மூர்க்க நாயனார்", "type": "tani", "isBig4": False,
    "category": "Service through Sacrifice (Maheswara Puja)",
    "place": "Thiruverkaadu", "grace": "Fed devotees with gambling winnings",
    "readTime": "15 mins", "image": "./chola_bronze_320.png",
    "prev": {"id": "", "nameEn": "Thandiyadigal Nayanar", "nameTa": "தண்டியடிகள் நாயனார்", "published": False},
    "next": {"id": "", "nameEn": "Somasi Mara Nayanar", "nameTa": "சோமாசிமாற நாயனார்", "published": False},
    "summary": "The gambler-saint of Thiruverkaadu who fed Shiva's devotees with his winnings and attained the sacred feet.",
    "subtitle": "From Skillful Gambler to Eternal Devotee — Maheswara Puja at Thiruverkaadu & Kumbakonam",
    "chapters": chapters,
}

# ---------- patch template ----------
tpl = open(f"{OUT}/periya_puranam_index.html", encoding="utf-8").read()

YAPPU_DB = """const yappuDatabase = {
            "aruseer-viruttham": {
                nameEn: "Aruseer Kazhinediladi Asiriya Viruttham",
                nameTa: "அறுசீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 6 metrical feet per line — 24 feet per stanza",
                    syllables: "Kai-seer feet ending in Naer (நேர்)",
                    rhyme: "2nd-letter ethukai across 4 lines; monai alliteration 1st-4th foot"
                },
                mood: {
                    cadence: "Ahaval Osai — fluid, narrative, deeply devotional",
                    effect: "Majestic epic momentum; Sekkizhar paints vivid drama without slowing narrative speed."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Fitting dense Tamil sandhi into exact 6-foot lines while preserving 2nd-letter rhyme."
                },
                singing: {
                    pann: "Nattapaadai / Thakkakesi",
                    raga: "Nattai / Gambheeranattai or Mayamalavagowla",
                    pause: "Pause after the 3rd foot in each line (3 + 3 = 6)."
                }
            },
            "kochakam-kalippa": {
                nameEn: "Kochchaka Kalippa",
                nameTa: "கொச்சகக் கலிப்பா",
                math: {
                    anatomy: "Mixed Kalippa limbs (taravu opening + thazhisai); Moorkka 8-12 run as 4-line stanzas",
                    syllables: "Kali feet with Thullal Osai rhythm",
                    rhyme: "Ethukai across lines with kalippa-internal limb rhymes"
                },
                mood: {
                    cadence: "Thullal Osai — leaping, dramatic, urgent",
                    effect: "Sekkizhar shifts gear for the gambling drama: pace quickens, moral tension rises, then resolves into grace."
                },
                craft: {
                    difficulty: "Very High",
                    challenge: "Holding mixed taravu/thazhisai limbs together while the story accelerates."
                },
                singing: {
                    pann: "Kolli / Thakkakesi (odhuvan marabu)",
                    raga: "Pantuvarali / Kalyani family",
                    pause: "Break after each limb; chant thazhisai passages briskly."
                }
            },
            "ezhucir-viruttham": {
                nameEn: "Ezhuseer Kazhinediladi Asiriya Viruttham",
                nameTa: "எழுசீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 7 metrical feet per line — 28 feet per stanza",
                    syllables: "Mixed kai-seer feet ending in Naer",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Ahaval Osai — grave, weighty, processional",
                    effect: "Seven-foot lines carry catalogue and praise passages: Thogai's roll-call of saints, Anthathi's compressed hagiography."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Sustaining the long 7-foot line without slack while keeping second-letter rhyme exact."
                },
                singing: {
                    pann: "Nattapaadai / Thakkakesi",
                    raga: "Nattai / Mayamalavagowla family",
                    pause: "Pause after the 4th foot (4 + 3 = 7)."
                }
            },
            "aintucir-kalithurai": {
                nameEn: "Aintucir Kalithurai",
                nameTa: "ஐந்துசீர் கலித்துறை",
                math: {
                    anatomy: "4 lines, 5 metrical feet per line — 20 feet per stanza",
                    syllables: "Kali feet in Thullal Osai rhythm",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Thullal Osai — leaping, energetic, urgent",
                    effect: "Carries fast narrative and fervent devotion; Sekkizhar sustains pace through wonder passages without slack."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Holding exact 5-foot lines with rhyme while the story runs at full speed."
                },
                singing: {
                    pann: "Panchamam",
                    raga: "Ahiri family",
                    pause: "Pause after the 2nd foot (2 + 3 = 5)."
                }
            },
            "encir-viruttham": {
                nameEn: "Encir Kazhinediladi Asiriya Viruttham",
                nameTa: "எண்சீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 8 metrical feet per line — 32 feet per stanza",
                    syllables: "Kai-seer feet ending in Naer, strong mid-line caesura",
                    rhyme: "2nd-letter ethukai across 4 lines; monai alliteration"
                },
                mood: {
                    cadence: "Ahaval Osai — majestic, expansive, contemplative",
                    effect: "Grandeur and detailed praise; Sekkizhar slows time for divine acts and saintly virtues."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Filling 8 long feet per line with imagery that never sags, under strict rhyme."
                },
                singing: {
                    pann: "Indalam",
                    raga: "Kedaragowla family",
                    pause: "Pause after the 4th foot (4 + 4 = 8)."
                }
            },
            "kaliviruttam": {
                nameEn: "Kaliviruttam",
                nameTa: "கலிவிருத்தம் (நான்கு சீர்)",
                math: {
                    anatomy: "4 lines, 4 metrical feet per line — 16 feet per stanza",
                    syllables: "Kali feet in Thullal Osai rhythm",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Thullal Osai — brisk, direct, lively",
                    effect: "Concise turns of event and pointed devotional statement in the shortest Kali gear."
                },
                craft: {
                    difficulty: "Moderate",
                    challenge: "Compression: full meaning and emotion inside 4 short feet per line."
                },
                singing: {
                    pann: "Kurinji",
                    raga: "Harikambhoji family",
                    pause: "Pause after the 2nd foot (2 + 2 = 4)."
                }
            }
        };"""
tpl2, n1 = re.subn(r"const yappuDatabase = \{.*?\n        \};", lambda _: YAPPU_DB, tpl, count=1, flags=re.DOTALL)
assert n1 == 1, "yappuDB patch failed"

# P20: windowed chapter rendering (giants-ready) — replaces the render-all
# block BEFORE the paragraph/verse micro-patches below (those become no-ops).
# Initial paint renders shells + active window (±2); placeholders fill on
# approach via observer; explicit nav renders the target window synchronously.
WIN_CODE = """// Render Post Chapters (windowed)
            window._ppWin = 2;
            window._ppChapters = devotee.chapters;
            window._chapterHTML = (chap, index) => {
                const L = localStorage.getItem('pp_lang') || 'en';
                const enCls = 'text-justify leading-relaxed lang-en' + (L === 'en' ? '' : ' hidden');
                const taCls = 'font-tamil text-justify leading-relaxed lang-ta' + (L === 'ta' ? '' : ' hidden');
                const enPs = (chap.content_en || [chap.content]).map((p, pi) =>
                    '<p class="' + (pi === 0 ? 'drop-cap ' : '') + enCls + '">' + p + '</p>').join('');
                const taPs = (chap.content_ta || []).map(t =>
                    '<p class="' + taCls + '">' + t + '</p>').join('');
                const verses = (chap.verses || []).map((v, vi) => formatThirumuraiVerseCard({
                    tamilVerse: v.tamil,
                    yappuKey: v.yappuKey,
                    ref: v.ref,
                    prov: v.prov,
                    vid: (v.vid || ('c' + index + 'v' + vi))
                })).join('');
                return '<section id="chapter-' + index + '" class="space-y-4 pt-4 border-b border-templeGold/20 pb-8">'
                    + '<h2 class="font-heading font-bold text-2xl sm:text-3xl text-amber-300 flex items-center gap-3">'
                    + '<span class="text-saffron font-sans text-sm border border-saffron px-2.5 py-1 rounded-md">Chapter ' + (index + 1) + '</span> '
                    + chap.title + '</h2>' + enPs + taPs + verses + '</section>';
            };
            window._shellHTML = (chap, index) =>
                '<section id="chapter-' + index + '" data-ph="1" data-i="' + index + '" class="space-y-4 pt-4 border-b border-templeGold/20 pb-8 min-h-[30vh]">'
                + '<h2 class="font-heading font-bold text-2xl sm:text-3xl text-amber-300 flex items-center gap-3">'
                + '<span class="text-saffron font-sans text-sm border border-saffron px-2.5 py-1 rounded-md">Chapter ' + (index + 1) + '</span> '
                + chap.title + '</h2>'
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
            const postContainer = document.getElementById('post-chapters-container');
            postContainer.innerHTML = window._ppChapters.map((chap, i) => window._shellHTML(chap, i)).join('');
            window._renderWindow(activeChapterIndex);
            if (window._ppObserver) window._ppObserver.disconnect();
            if ('IntersectionObserver' in window) {
                window._ppObserver = new IntersectionObserver((es) => {
                    es.forEach(e => {
                        if (e.isIntersecting && e.target.hasAttribute('data-ph')) {
                            const i = parseInt(e.target.getAttribute('data-i'), 10);
                            const tmp = document.createElement('div');
                            tmp.innerHTML = window._chapterHTML(window._ppChapters[i], i);
                            const real = tmp.firstElementChild;
                            e.target.replaceWith(real);
                            if (window._tocObserver) window._tocObserver.observe(real);
                        }
                    });
                }, { rootMargin: '900px 0px' });
                postContainer.querySelectorAll('section[data-ph]').forEach(s => window._ppObserver.observe(s));
            }"""
w1 = tpl2.find("// Render Post Chapters")
w2 = tpl2.find("`).join('');", w1)
assert w1 != -1 and w2 != -1, "window render span not found"
tpl2 = tpl2[:w1] + WIN_CODE + tpl2[w2 + len("`).join('');"):]

OLD_FALLBACK = """const yappu = yappuDatabase[yappuKey] || {
                nameEn: "Aruseer Kazhilaadiasiriya Viruttham",
                nameTa: "அறுசீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: { anatomy: "4 equal lines, 6 feet per line", syllables: "Kai-seer ending in Naer", rhyme: "Ethukai & Monai rhyming" },
                mood: { cadence: "Ahaval Osai", effect: "Evokes epic momentum and devotion." },
                craft: { difficulty: "High", challenge: "Maintaining metrical harmony." },
                singing: { pann: "Nattapaadai", raga: "Nattai / Mayamalavagowla", pause: "Pause after 3rd foot" }
            };"""
NEW_FALLBACK = """const yappu = yappuDatabase[yappuKey] || {
                nameEn: "Metre Unidentified",
                nameTa: "யாப்பு அறியப்படவில்லை",
                math: { anatomy: "Pending offline classification", syllables: "Queued for Gemini metre call", rhyme: "Not yet analysed" },
                mood: { cadence: "—", effect: "This verse awaits offline metre identification before publish." },
                craft: { difficulty: "—", challenge: "Human review required (review.json must clear first)." },
                singing: { pann: "—", raga: "—", pause: "—" }
            };"""
if OLD_FALLBACK in tpl2:  # superseded by P20 windowing; kept for template compat
    tpl2 = tpl2.replace(OLD_FALLBACK, NEW_FALLBACK)

OLD_RENDER = """                    <p class="drop-cap text-justify leading-relaxed">
                        ${chap.content}
                    </p>"""
NEW_RENDER = """                    <p class="drop-cap text-justify leading-relaxed lang-en">
                        ${(chap.content_en || [chap.content]).join('</p><p class="text-justify leading-relaxed lang-en">')}
                    </p>
                    ${(chap.content_ta || []).map(t => `<p class="font-tamil text-justify leading-relaxed lang-ta hidden">` + t + `</p>`).join('')}"""
if OLD_RENDER in tpl2:  # superseded by P20 windowing; kept for template compat
    tpl2 = tpl2.replace(OLD_RENDER, NEW_RENDER)

OLD_VERSES = """${chap.verse ? formatThirumuraiVerseCard({
                        tamilVerse: chap.verse.tamil,
                        englishTranslation: chap.verse.english,
                        yappuKey: chap.verse.yappuKey,
                        verseSource: chap.verse.source
                    }) : ''}"""
NEW_VERSES = """${(chap.verses || (chap.verse ? [chap.verse] : [])).map((v, vi) => formatThirumuraiVerseCard({
                        tamilVerse: v.tamil,
                        yappuKey: v.yappuKey,
                        ref: v.ref,
                        prov: v.prov,
                        vid: (v.vid || ('c' + index + 'v' + vi))
                    })).join('')}"""
if OLD_VERSES in tpl2:  # superseded by P20 windowing; kept for template compat
    tpl2 = tpl2.replace(OLD_VERSES, NEW_VERSES)

# P14: inline-yappu architecture — collapsed verse card + inline yappu
# sub-toggle with 4-pillar grid; no shared section, no navigation.
NEW_CARD_FNS = """function formatThirumuraiVerseCard({ tamilVerse, yappuKey, ref, prov, vid }) {
            const yappu = yappuDatabase[yappuKey] || { nameTa: "யாப்பு அறியப்படவில்லை" };
            return `
                <div id="v-${vid}" class="my-8 p-6 sm:p-8 rounded-3xl thirumurai-verse-card relative overflow-hidden border-2 border-templeGold/50 shadow-lg scroll-mt-28 lang-ta${(localStorage.getItem('pp_lang')||'en')==='ta'?'':' hidden'}">
                    <button onclick="toggleVerse('vb-${vid}')" class="w-full flex items-center justify-between gap-2 text-xs font-bold text-amber-200 font-tamil tracking-wide">
                        <span class="flex items-center gap-1.5">
                            <i class="fa-solid fa-om text-saffron text-base"></i> ${ref}
                        </span>
                        <span id="vb-${vid}-txt" class="text-saffron text-base leading-none">▸</span>
                    </button>
                    <div id="vb-${vid}" class="hidden">
                        <p class="verse-highlight-text text-lg sm:text-xl mt-4 mb-4 leading-relaxed tracking-wide">
                            ${tamilVerse.replace(/\\n/g, '<br>')}
                        </p>
                        <div class="flex justify-start mb-2">
                            <button onclick="toggleVerse('vyb-${vid}')" class="text-xs font-bold px-3 py-1.5 rounded-lg bg-templeGold/20 hover:bg-templeGold/30 text-amber-300 transition-colors flex items-center gap-1 font-tamil">
                                <i class="fa-solid fa-feather-pointed text-saffron"></i> யாப்பு: ${yappu.nameTa} <span id="vyb-${vid}-txt">▸</span>
                            </button>
                        </div>
                        <div id="vyb-${vid}" class="hidden mt-2">${yappuPillars(yappuKey)}</div>
                        <p class="text-[11px] text-gray-500">${prov}</p>
                    </div>
                </div>
            `;
        }

        function toggleVerse(bodyId) {
            const b = document.getElementById(bodyId);
            if (!b) return;
            const closed = b.classList.toggle('hidden');
            const t = document.getElementById(bodyId + '-txt');
            if (t) t.innerText = closed ? '▸' : '▾';
        }

        function yappuPillars(yappuKey) {
            const yappu = yappuDatabase[yappuKey] || {
                nameEn: "Metre Unidentified",
                nameTa: "யாப்பு அறியப்படவில்லை",
                math: { anatomy: "Pending offline classification", syllables: "Queued for Gemini metre call", rhyme: "Not yet analysed" },
                mood: { cadence: "—", effect: "This verse awaits offline metre identification before publish." },
                craft: { difficulty: "—", challenge: "Human review required." },
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

        """
i1 = tpl2.find("function formatThirumuraiVerseCard")
i2 = tpl2.find("let activeFilter", i1)
assert i1 != -1 and i2 != -1 and i1 < i2, "card-fns span not found"
tpl2 = tpl2[:i1] + NEW_CARD_FNS + tpl2[i2:]

# P15 retired: yappu now expands inline per verse — no shared section, no hook.
# (Container keeps template default sizing; story default is story-text-md.)

# (P15 hook retired with the shared section — scroll-spy hook below owns this area.)

# P17: hash router must ignore in-page anchors (yappu links) — only route story/gallery
OLD_ELSE = """            } else {
                showGalleryView();
            }"""
NEW_ELSE = """            } else if (hash === '#gallery' || hash === '') {
                showGalleryView();
            }
            // else: in-page anchor (#chapter-*) — leave the reader alone"""
assert tpl2.count(OLD_ELSE) == 1, "hash-router anchor ambiguous"
tpl2 = tpl2.replace(OLD_ELSE, NEW_ELSE)

# P18: scroll-spy TOC highlight + deep-link without reload + TOC button ids
OLD_SCROLL = """        function scrollToChapter(index) {
            activeChapterIndex = index;
            const target = document.getElementById(`chapter-${index}`);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""
NEW_SCROLL = """        let tocObserver = null;
        function setActiveToc(index) {
            activeChapterIndex = index;
            document.querySelectorAll('#toc-chapter-list button').forEach((b, i) => {
                const on = i === index;
                b.classList.toggle('bg-templeGold/30', on);
                b.classList.toggle('text-templeRed', on);
                b.classList.toggle('dark:text-amber-200', on);
                b.classList.toggle('font-bold', on);
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
            if (window._renderWindow) window._renderWindow(index);
            setActiveToc(index);
            requestAnimationFrame(() => {
                const target = document.getElementById(`chapter-${index}`);
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }"""
assert OLD_SCROLL in tpl2, "scrollToChapter anchor missing"
tpl2 = tpl2.replace(OLD_SCROLL, NEW_SCROLL)

OLD_TOCBTN = 'onclick="scrollToChapter(${index})" class='
assert tpl2.count(OLD_TOCBTN) == 1, "toc-button anchor ambiguous"
tpl2 = tpl2.replace(OLD_TOCBTN, 'id="toc-btn-${index}" onclick="scrollToChapter(${index})" class=')

OLD_SPYHOOK = """            updateBookmarkBtnState();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            window.location.hash = `#story=${id}&chapter=${chapterIdx}`;"""
NEW_SPYHOOK = """            initTocSpy();
            setActiveToc(chapterIdx || 0);
            renderEndNav(devotee);
            updateBookmarkBtnState();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            window.location.hash = `#story=${id}&chapter=${chapterIdx}`;"""
assert OLD_SPYHOOK in tpl2, "spy-hook anchor missing"
tpl2 = tpl2.replace(OLD_SPYHOOK, NEW_SPYHOOK)

# P21: end-of-story footer — summary strip + story-level nav (replaces
# chapter prev/next: continuous scroll + TOC already cover chapters).
# Story nav follows canonical order, published stories only.
ENDNAV_JS = """        function renderEndNav(devotee) {
            const host = document.getElementById('story-end-nav');
            if (!host) return;
            let nRoot = 0, nQuote = 0;
            const metres = [];
            (devotee.chapters || []).forEach(ch => (ch.verses || []).forEach(v => {
                if (v.kind === 'periyapuranam_root') nRoot++;
                else nQuote++;
                if (v.yappuKey && !metres.includes(v.yappuKey)) metres.push(v.yappuKey);
            }));
            const mnames = metres.map(k => ((yappuDatabase[k] || {}).nameTa || k)).join(' · ');
            const navBtn = (s, label) => {
                if (s && s.published && s.id) {
                    return `<button onclick="loadStory('${s.id}')" class="flex-1 px-5 py-3 rounded-xl bg-templeRed text-templeGold hover:bg-templeRed/90 text-xs sm:text-sm font-semibold">${label}<br><span class="font-tamil">${s.nameTa}</span><br>${s.nameEn}</button>`;
                }
                const nm = s ? (s.nameEn + ' · விரைவில்') : 'விரைவில்';
                return `<button disabled class="flex-1 px-5 py-3 rounded-xl border border-templeGold/30 text-gray-500 text-xs sm:text-sm font-semibold cursor-not-allowed">${label}<br>${nm}</button>`;
            };
            host.innerHTML = `
                <div class="p-5 sm:p-6 rounded-2xl bg-zinc-900/90 border border-templeGold/40 shadow-inner mb-6">
                    <h3 class="font-heading font-bold text-base text-amber-200 mb-1">இக்கதையின் யாப்பு · Prosody in this story</h3>
                    <p class="text-xs sm:text-sm text-gray-300">📜 ${nRoot} root verses${nQuote ? ` + ${nQuote} thirumurai quotes` : ''} · 🎵 ${metres.length} metres${mnames ? ` (${mnames})` : ''} · ⏱ ${devotee.readTime || ''}</p>
                </div>
                <div class="flex flex-col sm:flex-row items-stretch gap-3 font-sans">
                    ${navBtn(devotee.prev, '← Prev Story')}
                    <button onclick="showGalleryView()" class="flex-1 px-5 py-3 rounded-xl border border-templeGold/50 hover:bg-templeGold/10 text-xs sm:text-sm font-semibold text-amber-200">🛕 Saint Gallery</button>
                    ${navBtn(devotee.next, 'Next Story →')}
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
tpl2 = tpl2.replace(OLD_ACTF, ENDNAV_JS)

i1 = tpl2.find("<!-- Bottom Chapter Navigation -->")
i2 = tpl2.find("</article>", i1)
assert i1 != -1 and i2 != -1 and i1 < i2, "end-nav span not found"
tpl2 = (tpl2[:i1] + "<!-- Story End: summary + story navigation (rendered per story) -->\n"
        "                <div id=\"story-end-nav\" class=\"pt-8 border-t-2 border-templeGold/30\"></div>\n"
        "                " + tpl2[i2:])

# read-checkmark state + gallery badge
OLD_SAVED2 = "let savedBookmarks = JSON.parse(localStorage.getItem('periya_puranam_bookmarks') || '[]');"
assert tpl2.count(OLD_SAVED2) == 1, "bookmarks anchor ambiguous"
tpl2 = tpl2.replace(OLD_SAVED2, OLD_SAVED2 + "\n        let savedReads = JSON.parse(localStorage.getItem('pp_read') || '[]');")
OLD_GBADGE = """${devotee.type === 'thogai' ? 'Group' : 'Nayanmar'}
                        </span>"""
NEW_GBADGE = """${devotee.type === 'thogai' ? 'Group' : 'Nayanmar'}
                        </span>
                        ${(typeof savedReads !== 'undefined' && savedReads.indexOf(devotee.id) >= 0) ? '<span class="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-900 text-emerald-200 mt-1 inline-block">✓ Read</span>' : ''}"""
assert tpl2.count(OLD_GBADGE) == 1, "gallery badge anchor ambiguous"
tpl2 = tpl2.replace(OLD_GBADGE, NEW_GBADGE)
assert tpl2.count("Table of Chapters") == 1, "toc-title anchor ambiguous"
tpl2 = tpl2.replace("Table of Chapters", "Table of Contents")

# P16: dark-only reader — force theme-dark, drop light/sepia switcher
assert '<body class="theme-parchment font-body' in tpl2, "body anchor missing"
tpl2 = tpl2.replace('<body class="theme-parchment font-body', '<body class="theme-dark font-body', 1)
tpl2, nrm = re.subn(r"                <!-- Reading Mode Themes -->\n.*?\n                </div>\n",
                    "", tpl2, count=1, flags=re.DOTALL)
assert nrm == 1, "theme switcher removal failed"
OLD_SAVED = """            const savedTheme = localStorage.getItem('periya_puranam_theme');
            if (savedTheme) setTheme(savedTheme);"""
assert OLD_SAVED in tpl2, "theme init anchor missing"
tpl2 = tpl2.replace(OLD_SAVED, "            setTheme('dark'); // dark-only reader")

# P6: day-mode legibility — grays to near-black on parchment
OLD_CSS = """        body.theme-dark .verse-highlight-text {
            color: #F3E5AB;
        }"""
NEW_CSS = """        body.theme-dark .verse-highlight-text {
            color: #F3E5AB;
        }

        /* Day-mode legibility: body grays forced to near-black on parchment */
        body.theme-parchment .text-gray-400 { color: #5b554b !important; }
        body.theme-parchment .text-gray-500 { color: #2b2620 !important; }
        body.theme-parchment .text-gray-600,
        body.theme-parchment .text-gray-700 { color: #141210 !important; }
        body.theme-parchment #post-chapters-container { color: #141210; }"""
assert OLD_CSS in tpl2, "css anchor missing"
tpl2 = tpl2.replace(OLD_CSS, NEW_CSS)

# P8: EN/TA toggle next to font-size adjuster
OLD_FONT = ">A++</button>\n                </div>"
NEW_FONT = """>A++</button>
                </div>

                <!-- Language Toggle -->
                <div class="flex items-center border border-templeGold/30 rounded-lg p-1 bg-parchmentDark/60 dark:bg-zinc-800">
                    <button id="lang-btn-en" onclick="setLang('en')" title="Read in English" class="px-2.5 py-0.5 text-xs font-bold rounded hover:text-templeRed">EN</button>
                    <button id="lang-btn-ta" onclick="setLang('ta')" title="தமிழில் படிக்க" class="px-2.5 py-0.5 text-xs font-bold rounded font-tamil hover:text-templeRed">தமிழ்</button>
                </div>"""
assert tpl2.count(OLD_FONT) == 1, "font anchor ambiguous"
tpl2 = tpl2.replace(OLD_FONT, NEW_FONT)

# P9: setLang function before toggleBookmarksDrawer
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

# P11 RETIRED (Fix 3 offline): compiled ppreader.css bakes darkMode:'class';
# the inline tailwind.config + Play CDN are gone from the template.

# P12: drive the `dark` class from our own theme switch
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

# P10: restore saved language on init (saved theme already calls setTheme,
# which toggles the `dark` class, so first paint is correct)
OLD_INIT2 = "            if (savedFontSize) setFontSize(savedFontSize);"
NEW_INIT2 = """            if (savedFontSize) setFontSize(savedFontSize);

            setLang(localStorage.getItem('pp_lang') || 'en');"""
assert OLD_INIT2 in tpl2, "init anchor missing"
tpl2 = tpl2.replace(OLD_INIT2, NEW_INIT2)

story_js = json.dumps([story], ensure_ascii=False, indent=12)
tpl2, n2 = re.subn(r"const devoteesData = \[.*?function formatThirumuraiVerseCard",
                   lambda _: "const devoteesData = " + story_js + ";\n\n        function formatThirumuraiVerseCard",
                   tpl2, count=1, flags=re.DOTALL)
assert n2 == 1, "devoteesData patch failed"

OLD_INIT = "handleHashRouting();\n        });"
assert tpl2.count(OLD_INIT) == 1, "init anchor ambiguous"
tpl2 = tpl2.replace(OLD_INIT,
    "if (window.location.hash && window.location.hash !== '#gallery') handleHashRouting(); else loadStory('moorkka-nayanar');\n        });")

out = f"{OUT}/moorkka_nayanar_pilot_v11.html"
open(out, "w", encoding="utf-8").write(tpl2)
n_cards = sum(len(c["verses"]) for c in chapters)
print(f"wrote {out} ({len(tpl2)//1024}KB): {len(chapters)} segments, {n_cards} verse cards")
