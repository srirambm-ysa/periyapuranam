# Copy Log — D:\periapuranam seeded 2026-09-26 from D:\nalvar

## site/ (reader shell + static assets)
- `periya_puranam_index.html` ← `ppreader/periya_puranam_index.html` (template shell)
- `shell.html` ← `ppreader/shell.html` (reference)
- `ppreader.css`, `fonts.css`, `tailwind.config.js` ← `ppreader/`
- `fonts/` ← `ppreader/fonts/` (98 files, 2.6 MB)
- `fa/` ← `ppreader/fa/` (fontawesome css + 2 woff2)
- `images/` ← chola_bronze_320/cutout/face/small/small-removebg, Sekkizhar.png,
  sekkizhar_384.jpg, lingam.svg. SKIPPED: `chola_bronze.png` (8.8 MB full-size, unused)

## content/ (drawer + legacy story data, seeded 2026-09-26)
- `moorkka.json`, `tiruk_kurippu.json` ← `ppreader/data/`
- `Thirumurai_12_shaivam_corpus.json` (8.1 MB) ←
  `periapuranam/canonical/Thirumurai_12_Periyapuranam/` (drawer source, all stories)

## content/stories/ (all 68 day-01..day-07 stories, added 2026-09-26 pm)
- Per story: `<slug>_tamil.txt` (from `tamil_real/`, else top level) +
  `<slug>_english.txt` + `<slug>_english_meta.json` ←
  `D:\nalvar\periapuranam\output\day-01..day-07/<slug>/`
- Zero missing: all 68 have Tamil AND English (~14.3 MB Tamil, ~5.2 MB English).
- NOT copied: audio/, chunk txts, logs, instrumentation, bilingual.txt (rebuildable),
  `verses.json`/`review.json` (parked Tier artifacts).
- NOT started (nothing to copy): day-08 giants — Thirunavukkarasu (stub dirs only),
  Thirugnanasambandha (transcribing now).

## scripts/ (builders, to generalize into build.py)
- `build_tirukkurippu_experiment.py` (golden builder), `build_moorkka_pilot.py`,
  `yappu_db.py` ← `ppreader/`

## reference/ (golden outputs, do not edit)
- `tiruk_kurippu_experiment.html` (1.7 MB) ← `ppreader/`

## NOT copied (stay factory-side in D:\nalvar)
- All `output/**/audio/`, chunk txts, `transcribe_*.log`, `*_instrumentation.json`
- `verses.json` / `verses.review.json` (parked Tier-pipeline artifacts)
- moorkka pilot v1–v11 iteration HTMLs, `__pycache__/`, books, xlsx trackers
