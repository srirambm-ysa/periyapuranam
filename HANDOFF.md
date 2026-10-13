# HANDOFF — Periyapuranam Storefront (D:\periapuranam)

> **Last updated:** 2026-09-26 pm · **State:** shippable on demand, proven locally, NOTHING pushed live.
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
- Verse preview: `content/preview/` 68 stories (gitignored) + `site/preview.html`
  (gitignored, bannered). 62/67 populated, 1737 drawer verses, reconciled to map
  (1737 + 324 pending = 2061). Served at `http://localhost:8934/site/preview.html`
  (repo-root server); product at `http://localhost:8933` (`dist/` server).
- Factory input: `content/factory_section_map.json` v1 (committed, build input —
  68 entries, 2189 verses, 3 flagged mappings inside).

## Next queue (in order)

1. `yappu_db` decision (deliberate, not drive-by) for 5 unmapped labels → rebuild
   preview for: Anaya (42, சந்தக் கலிநிலைத்துறை), Kannappa (186, கலிநிலைத்துறை
   ஐந்து சீர்), Murthi (49, கலித்துறை), Somasi Mara (6, கலித்துறை),
   Pugazh Chozha (41, வஞ்சி விருத்தம்). Full per-story report was delivered
   with the preview session.
2. Flagged-3 scope confirmation arrives factory-side (Gananadhar identity,
   Poyyadimai/Bakthraaip framing scope) — apply + rebuild preview.
3. 67 English/sign-off arrivals → promote `content/build/` + manifest per
   SCHEMA_V1 §3 (factory delivers, human signs off).
4. Ship: git (below) → push → domain attach (human) → deploy.

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
