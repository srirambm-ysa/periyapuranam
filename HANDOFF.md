# HANDOFF — Periyapuranam Storefront (D:\periapuranam)

> **Last updated:** 2026-10-14 close · **State:** LIVE 73-story gallery on
> `https://periyapuranam.srirambm.workers.dev` (Worker `periyapuranam`).
> Factory approval retired — owner blanket sign-off ships all 73 as
> `english_done`. Repo: `https://github.com/srirambm-ysa/periyapuranam`
> (branch `main`, public, pushed). Custom domain `periyapuranam.nalvar.in`
> NOT wired (human step). CI workflow file held locally (needs
> workflow-scope token).
> **Session (2026-10-13 · model deepseek-v4.1-flash · ses_eca2d1587ff…):**
> REAL billed 1,738,205 tokens (raw 13.5M, 97.5% cache-hit, 87.1% efficiency).
> **Session (2026-10-14 · Muse Spark · ses_ec6d8be71ffe…): closed.**
> REAL billed 4,395,784 tokens (raw 26.3M, 92.9% cache-hit, 83.3% efficiency).
> **Resume prompt for next session:** read `docs/CONTRACT.md`, `docs/COPY_LOG.md`,
> `docs/SCHEMA_V1.md`, then this file. Own `D:\periapuranam` ONLY — never
> write under `D:\nalvar`; factory needs come as files in `content/`.
> **Preview:** double-click `preview.bat` (serves repo root on :8934, opens
> `site/preview.html`). Factory is dead — no more transcriptions coming.

## Frozen contract (do not renegotiate)

- Prose chapters + full canonical Verses-drawer; NO verse auto-detection.
- Golden: `scripts/build_tirukkurippu_experiment.py` + `reference/tiruk_kurippu_experiment.html`
  — byte-identical, read-only, diff oracle. `site/shell.html` reference frozen.
- Story JSON v1 per `docs/SCHEMA_V1.md`; verse record `{n, lines, yappuKey, ref, kind}`;
  raw unescaped Tamil in JSON, escape at render (G8 gate enforces).
- Statuses: `transcribed` (never listed) → `tamil_verified` → `english_done`.
  Factory closed 2026-10-14: per-story verification retired; owner blanket
  sign-off ships the full 73-story corpus as `english_done` (both languages
  as-is). `content/build/` lists all 73; `content/preview/` keeps the
  transcribed dev overlay.

## What is built (all green, local-only)

- `scripts/build.py` (TK default, `--all` full 73-product corpus + preview,
  `--check` oracle diff, `--preview` local-only): chapter splitter +
  drawer-verse loader + registry + `mirror_product` owner-sign-off path.
- `content/build/` 73 story JSONs (all `english_done`) + `manifest.json`
  (canonical `section_order`, `group`/`isBig4` mirrored) + `scripts/check.py`
  gates (schema, status, chapter contiguity, Tamil/English match, verse_count
  vs drawer incl. giant multi-section map totals, manifest order/mirror,
  preview-leak, G8 escaping, setLang/imgURL/spy presence).
- `site/periya_puranam_index.html` wired to manifest (gallery from manifest, v1 chapter
  render, drawer from `verses[]` via single `formatThirumuraiVerseCard`); 5 regressions
  fixed 2026-09-26 (toggle/spy/images/cards/night-default) — do not regress.
- `scripts/assemble_dist.py` (repo tree → `dist/`, asserts no `preview*`, asserts
  `../content/build` resolves identically); `wrangler.toml` (assets-only `./dist`,
  custom-domain block DRAFT); `.github/workflows/deploy.yml` (PR: diff+gates+preview
  artifact; main: rebuild-from-scratch then deploy).
- Verse preview (the BETA reader): `content/preview/` 73 stories (gitignored) +
  `site/preview.html` (gitignored, bannered). 72/72 verse-populated
  (Manikkavachagar has no drawer section by design), 4012 non-TK drawer
  verses (4140 incl TK), 0 pending. Served via `preview.bat` → 
  `http://localhost:8934/site/preview.html` (repo-root server); product at
  `http://localhost:8933` (`dist/` server).
- Gallery order = canonical Thirumurai order (drawer `section_order`:
  Sundarar §6 first … Isaignaniyar §77, Mani external last). Manifest-driven
  groups: `tani` 63 (incl. 3 samaya saints) / `thogai` 9 / `samaya` 3 /
  `external` Mani; Big-4 filter = 3 samaya + Mani. Filter counts are live
  from the manifest. End-of-story shows
  Home + Choose-another-story (prev/next removed); chapter jumps measure the
  sticky header+toolbar live so the chapter top lands clear.
- `scripts/make_preview.py` (new): regenerates `site/preview.html` from the
  product reader (`periya_puranam_index.html`) with exactly 2 deltas — banner +
  `DATA_BASE` → `../content/preview`. Preview was hand-built before and drifted
  (stale yappu DB); now reproducible. Run after `build.py --preview`.
- Factory input: `content/factory_section_map.json` v2 (committed, build input —
  73 entries: 72 + Manikkavachagar external, 4140 verses, 2 placeholder flags).
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
  from catalog, video catalog, and thagar zip entirely. Enriched 2026-10-14 to
  ~959 Tamil / ~1110 English words across the same 8 chapters — LLM+web
  synthesis grounded verse-by-verse in drawer §56 (10 songs) + Sundarar's
  "Nelveli venra" reference; disputed points hedged in-text (Arikesari
  identification, kazhuvertram as tradition). Factory dead → stays the story.
  Ships as `english_done` in product (10 drawer verses). Reconciles:
  63 + 9 Thogai = 72 saint-stories (68 + 3 giants + nedumara) + Manikkavachagar
  external note = 73 gallery cards.

## Next queue (next session)

1. Owner reads stories for fine-tuning → minor refinements (texts, UI).
2. Hook up `periyapuranam.nalvar.in` subdomain (human: dashboard DNS +
   route attach; `wrangler.toml` routes block is DRAFT).
3. Push `.github/workflows/deploy.yml` (held untracked locally — needs a
   token with `workflow` scope, or add via GitHub web UI) to wake CI.
4. Fold in real-mobile feedback from the workers.dev test.

## Repo reality (done 2026-10-14, was "first task on resume")

```powershell
cd D:\periapuranam
git status --short   # MUST show no dist/, no content/preview/, no site/preview.html
```

- Remote: `https://github.com/srirambm-ysa/periyapuranam` (public, branch
  `main`, pushed). `.github/` stays untracked until item 3 above.
- `.gitignore` covers: `dist/`, `content/preview/`, `site/preview.html`,
  `__pycache__/`, `.wrangler/`, `.dev.vars`.
- Committed build inputs: `content/factory_section_map.json` (v2),
  `content/Thirumurai_12_shaivam_corpus.json` (8.1 MB),
  `content/stories/` (70× Tamil+English pairs + giants/, nedumara enriched,
  manikkavachagar note), `content/build/` (73 shippable JSONs + manifest).
- Tokens (GitHub PAT, Cloudflare API token) held in-session only — never in
  files. CI secrets (`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`) still
  unset (human, needed only when CI wakes).

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

## Session log — 2026-10-14 (Muse Spark, closed)

Commits (main, pushed): `f74ead1` reader UI batch · `a30bfc5` 73-story
corpus · `1522ad5` docs · `c83ec25` schema/handoff close (pushed; only
untracked `.github/` remains by design).

- Session resume → 7 preview flags settled with owner (6 cleared, nedumara
  kept preview-only) → nedumara enriched to ~959ta/~1110en words,
  drawer-grounded → `preview.bat` launcher.
- Reader UI: canonical gallery order, manifest-driven group filters (63/9/4),
  Home + Choose-another-story (prev/next removed), live-measured chapter
  scroll, Nalvar verse on main page, footer credits + AI disclaimer, mobile
  audit + missing-utility fallback CSS, favicon/OG/JSON-LD SEO.
- Factory approval retired (owner blanket sign-off): `build.py --all`
  mirrors 73 `english_done` products; manifest canonical + gated.
- GitHub repo created + pushed (public, main); Worker `periyapuranam` LIVE
  at `https://periyapuranam.srirambm.workers.dev` (73 verified live).
- Held: `.github/workflows/deploy.yml` (needs workflow-scope token),
  custom domain, CI secrets, real-mobile feedback, story fine-tuning.
