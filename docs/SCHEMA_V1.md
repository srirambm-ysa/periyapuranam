# Story JSON v1 + manifest.json — Field List (decision doc, 2026-09-26)

Status: **draft for sign-off**. Unblocks `scripts/build.py`, manifest, CI gates, site wiring.
Guardrails: golden files (`scripts/build_tirukkurippu_experiment.py`,
`reference/tiruk_kurippu_experiment.html`) stay byte-identical; golden HTML
embedded `devoteesData` is the diff oracle for the first artifact.

## 0. Facts established from the repo

- Legacy `content/tiruk_kurippu.json` = frozen TK shape: 36 `chapters`
  (`{title, content_en[], content_ta[]}`) + 128 `verses_all`
  (`{n, lines[], yappuKey, ref}`). `build.py` must reproduce its
  chapters/verses from raw inputs (diff on `n/lines/yappuKey/ref`).
- Factory has delivered 68 stories × (`*_tamil.txt`, `*_english.txt`,
  `*_english_meta.json`) into `content/stories/`. (`*_english_meta.json` is a
  raw LLM API log — **not** verification. `status` is decided here, per-story
  human sign-off, never inferred from factory files.)
- TK factory files: `Chapter NN — <name>` heads, 36/36 chapters; header line
  stripped, number goes in `n`.
- Canonical drawer: `content/Thirumurai_12_shaivam_corpus.json` (78 sections);
  TK section slug `periya-puranam-mummaiyal-ulakanda-charukkam-thiruk-kuripputh-thonta-nayanar-puranam`,
  128 songs. Metre keys via `scripts/yappu_db.py:label_to_key` (assert: zero unmapped).

## 1. Story JSON v1 (`content/build/<slug>.json`)

`"schema_version": 1` in every file. Bump on any field change.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int = 1 | |
| `slug` | string | factory slug, e.g. `tiruk_kurippu_tonda_nayanar` |
| `id` | string | reader id, e.g. `tiruk-kurippu-tonda-nayanar` (matches golden) |
| `status` | enum | `transcribed` (never listed) → `tamil_verified` (launch threshold) → `english_done` |
| `nameEn` / `nameTa` | string | display names (from golden/legacy record) |
| `type` / `isBig4` / `category` / `place` / `grace` | string/bool | passthrough display metadata (reader shell needs them) |
| `readTime` / `image` / `prev` / `next` / `summary` / `subtitle` | various | passthrough from legacy record; `prev/next`: `{id,nameEn,nameTa,published}` |
| `tamil_chapters` | `[{n:int, text:string}]` | header stripped, number in `n`; `text` = body paras joined with `\n\n` |
| `english_chapters` | same shape or `null` | `null` only when no verified English (`tamil_verified`); backfilled later via re-export |
| `verses` | `[verse]` | full canonical section (drawer order); `[]` while pending. Replaces legacy `verses_all` name |
| `section_slug` | string | drawer key, e.g. `periya-puranam-…-nayanar-puranam` |
| `tamil_count` / `english_count` / `verse_count` | int | redundant counts for CI gates |
| `exported_at` | string (UTC date) | e.g. `2026-09-26` |

Rules: `transcribed` stories are never listed in manifest. Chapter sequences
must be exactly `1..N` in both languages; Tamil/English `n` arrays must match
when English ships. No char-offset spans produced or consumed. Verse `lines`
stored **unescaped** (escape at render, not in JSON — golden builder escapes
only for HTML embedding).

## 2. Verse record (frozen — the rework-risk part)

`{n:int, lines:[string…], yappuKey:string, ref:string, kind:string}`

- `n`: int song number (legacy `"1"` string normalizes to `1`).
- `lines`: Tamil lines, whitespace-trimmed, blanks dropped, source
  `raw_song || tamil_split`.
- `yappuKey`: via `label_to_key(metre || type_inherited)`; build **fails**
  on unmapped (golden asserts zero unmapped). Key must exist in `yappu_db`.
- `ref`: Tamil section short name, e.g. `திருக்குறிப்புத்தொண்ட புராணம்`.
- `kind`: badge string, always `periyapuranam_root` for drawer verses
  (drawer = full canonical section = root verses). Field is required by
  CONTRACT §5 badge rule; it is **additive** — the golden diff ignores it
  (diffs on `n/lines/yappuKey/ref` only), so the oracle comparison still holds.
- Order = drawer `song_no` order, not transcript order.

## 3. `manifest.json` (`content/build/manifest.json`)

Array of one entry per **listed** story (`tamil_verified` or `english_done`):

`{slug, id, titleEn, titleTa, status, schema_version, image, type, category,
tamil_count, english_count (0 when null), verse_count, section_slug,
exported_at}`

- `image`/`type`/`category` mirror the story file (gallery cards + type
  filter work on unopened stories; no extra fetch). Added pre-ship, so no
  version bump (`schema_version` stays 1 until first deploy).

- Drives the reader index and CI gates; runtime never scans directories.
- CI gates: every entry `schema_version == 1`; `status in (tamil_verified,
  english_done)`; `english_done ⇒ english_count == tamil_count > 0`;
  `tamil_verified ⇒ english_count == 0`; chapter `n` contiguous from 1;
  `verse_count` equals drawer section length (or 0 while pending).

## 4. First artifact + acceptance test (= work item (2)+(3))

`scripts/build.py` (new file; golden builder copied/adapted, never edited)
emits `content/build/tiruk_kurippu_tonda_nayanar.json` with `status:
english_done`, 36/36 chapters, 128 verses. Acceptance: chapter `n/text`
(para-joined) and verse `n/lines/yappuKey/ref` diff clean against the golden
HTML's embedded `devoteesData`. Only then is (2) done.

## 5. Open questions for the factory session (not this repo)

- Canonical `section_slug` mapping for the other 67 stories (needed before
  their `verses` can be anything but `[]`).
- Display metadata (`nameEn/nameTa/category/place/grace/summary/...`) source
  for non-pilot stories. Until answered, new stories build as
  `transcribed` (never listed, `english_chapters: null`, `verses: []`);
  per-story human sign-off promotes to `tamil_verified` (Tamil lists,
  English backfilled later) or `english_done` (verified English ships).
