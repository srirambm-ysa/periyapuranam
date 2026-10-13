# HANDOFF — Periyapuranam Storefront (D:\periapuranam)

> **Last updated:** 2026-10-13 pm · **State:** full 72-story preview reader
> green locally; product still TK-only; NOTHING pushed live.
> **Session (2026-10-13 · model deepseek-v4.1-flash · ses_eca2d1587ff…):**
> REAL billed 1,738,205 tokens (raw 13.5M, 97.5% cache-hit, 87.1% efficiency).
> **Resume prompt for next session:** read `docs/CONTRACT.md`, `docs/COPY_LOG.md`,
> `docs/SCHEMA_V1.md`, then this file. Own `D:\periapuranam` ONLY — never
> write under `D:\nalvar`; factory needs come as files in `content/`.

## Frozen contract (do not renegotiate)

- Prose chapters + full canonical Verses-drawer; NO verse auto-detection.
- Golden: `scripts/build_tirukkurippu_experiment.py` + `reference/tiruk_kurippu_experiment.html`
  — byte-identical, read-only, diff oracle. `site/shell.html` reference frozen.
- Story JSON v1 per `docs/SCHEMA_V1.md`; verse record `{n, lines, yappuKey, ref, kind}`;
  raw unescaped Tamil in JSON, escape at render (G8 gate enforces).
- Statuses: `transcribed` (never listed) → `tamil_verified` (launch threshold,
  per-story human sign-off) → `english_done`. Product `content/build/` is TK-only
  until sign-off promotes others.

## What is built (all green, local-only)

- `scripts/build.py` (TK default, `--all` registry, `--check` oracle diff,
  `--preview`): chapter splitter + drawer-verse loader + registry.
- `content/build/tiruk_kurippu_tonda_nayanar.json` (`english_done`, 36/36, 128 verses).
- `content/build/manifest.json` + `scripts/check.py` gates (schema, status, chapter
  contiguity, Tamil/English match, verse_count vs drawer, preview-leak, G8 escaping,
  setLang/imgURL/spy presence).
- `site/periya_puranam_index.html` wired to manifest (gallery from manifest, v1 chapter
  render, drawer from `verses[]` via single `formatThirumuraiVerseCard`); 5 regressions
  fixed 2026-09-26 (toggle/spy/images/cards/night-default) — do not regress.
- `scripts/assemble_dist.py` (repo tree → `dist/`, asserts no `preview*`, asserts
  `../content/build` resolves identically); `wrangler.toml` (assets-only `./dist`,
  custom-domain block DRAFT); `.github/workflows/deploy.yml` (PR: diff+gates+preview
  artifact; main: rebuild-from-scratch then deploy).
- Verse preview (the BETA reader): `content/preview/` 72 stories (gitignored) +
  `site/preview.html` (gitignored, bannered). 71/71 populated, 4012 non-TK drawer
  verses (4140 incl TK), 0 pending. Served at `http://localhost:8934/site/preview.html`
  (repo-root server); product at `http://localhost:8933` (`dist/` server).
- `scripts/make_preview.py` (new): regenerates `site/preview.html` from the
  product reader (`periya_puranam_index.html`) with exactly 2 deltas — banner +
  `DATA_BASE` → `../content/preview`. Preview was hand-built before and drifted
  (stale yappu DB); now reproducible. Run after `build.py --preview`.
- Factory input: `content/factory_section_map.json` v1 (committed, build input —
  72 entries, 4140 verses, 7 flagged mappings inside, incl. the nedumara
  placeholder).
- `yappu_db.py` metres all mapped (2026-10-13): kalithurai-family labels →
  aintucir-kalithurai; new `vanji-viruttam` card (Karigai sey.14) for Pugazh
  Chozha. Golden + `shell.html` untouched.
- Day-08 GIANTS integrated (2026-10-13) via `content/stories/giants/` +
  `build.py --preview` giant path (`giant:true` map entries; `sections[]` list):
  Sundarar (47 chapters = drawer §6 Thaduthatkonda 203 + §78 Vellanai 53 = 256
  verses), Thirunavukkarasu/Appar (215 chapters, §27, 429), Thirugnanasambandha
  (291 chapters, §34, 1256). Preview splitter merges duplicate chapter heads
  (Sambandhar English repeats 250/291). `isBig4:true`.
- Nedumara Nayanar placeholder (the missing 63rd Thani Adiyaar): story absent
  from catalog, video catalog, and thagar zip entirely. 8-chapter web-sourced
  Tamil+English placeholder (`content/stories/nedumara_nayanar_*`,
  `_english_meta.json` `placeholder:true`, sources listed) + map entry. SOURCE
  FILES DO NOT EXIST factory-side → this stays the story. Builds as
  `transcribed` (never listed) — product unaffected. Reconciles: 63 + 9 Thogai
  = 72 saint-stories (68 + 3 giants + nedumara).

## Next queue (in order)

1. Settle the 7 preview flags factory-side (Gananadhar identity,
   Poyyadimai/Bakthraaip framing scope are real; the 3 giants + nedumara
   placeholder flags are informational) → apply + rebuild preview.
2. English/sign-off arrivals → promote `content/build/` + manifest per
   SCHEMA_V1 §3 (factory delivers, human signs off). Product stays TK-only
   until then; giants/nedumara build as `transcribed` in preview only.
3. Ship: git push (human creates repo) → secrets → domain attach → deploy.

## GIT REPO instructions (first task on resume, before any code work)

```powershell
cd D:\periapuranam
git init
git add .                                   # respects .gitignore
git status --short                          # MUST show no dist/, no content/preview/, no site/preview.html
git commit -m "feat(storefront): TK reader shippable on demand (v1 contract, golden-clean)"
# create empty GitHub repo (human or gh), then:
git remote add origin <url>
git branch -M main
git push -u origin main
```

- `.gitignore` already covers: `dist/`, `content/preview/`, `site/preview.html`,
  `__pycache__/`, `.wrangler/`. Verify with `git status` before committing —
  if preview paths appear, STOP and fix ignore rules (deploy-leak class bug).
- Committed build inputs: `content/factory_section_map.json`,
  `content/Thirumurai_12_shaivam_corpus.json` (8.1 MB, fine),
  `content/stories/` (68× Tamil+English+meta, ~21 MB, fine).
- After push: set repo secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`
  (human), attach `periyapuranam.nalvar.in` custom domain (human, dashboard/DNS),
  then first `main` push deploys. PRs get preview artifacts automatically.

## Session log — 2026-10-13 (deepseek-v4.1-flash)

Commits (master, tree clean): `15f5bc4` exported_at refresh · `814dab5`
kalithurai-family yappu mapping · `de5757e` vanji-viruttam card · `69b3b2a`
nedumara placeholder · `ad0ab2b` handoff · `bf800ce` giants + preview reader.

- Git repo initialised + committed locally (branch `master`, NO remote yet —
  push is a human step: create empty GitHub repo, `git remote add origin`,
  `git branch -M main`, `git push -u origin main`).
- yappu_db: all metre labels mapped (4 kalithurai-family → aintucir-kalithurai;
  new vanji-viruttam card). Zero UNMAPPED across corpus.
- Set reconciled to 72 saint-stories: 68 + 3 giants + nedumara (the missing
  63rd Thani Adiyaar). Nedumara source genuinely absent factory-side.
- 3 day-08 giants integrated into preview; preview + beta reader rebuilt
  (72 stories). `make_preview.py` generator added (fixes preview drift).
- Product untouched: golden diff clean, `check.py` gates clean.
