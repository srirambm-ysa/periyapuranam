# Periyapuranam Storefront — Frozen Contract (2026-09-26)

Source of truth for these decisions: `D:\nalvar\docs\periyapuranam-verse-spec.md` §0
(read-only reference; this session does NOT edit `D:\nalvar`).

## Reader model: prose-only + canonical Verses-drawer

- NO verse auto-detection. No cue-regex, fuzzy matching, or LLM judging in the build path.
- Each story = prose chapters + its full canonical verse section from the drawer
  (`content/Thirumurai_12_shaivam_corpus.json`, shaivam labels).
- Metre card keys map from shaivam labels via `scripts/yappu_db.py`.
- Golden reference: `reference/tiruk_kurippu_experiment.html`
  (36 prose chapters + 128-verse drawer), built by `scripts/build_tirukkurippu_experiment.py`.
  **Reviewed, frozen, no changes to its shape.**

## Per-story JSON deploy artifact (all agreed 2026-09-26)

1. TK-pilot contract is frozen. Ship English where a verified English text exists
   (`english_done`); Tamil-first with `"english_chapters": null` only where it
   does not (`tamil_verified`); English backfills later via re-export.
2. `"schema_version": 1` in every story JSON (bump on field changes).
3. `"status"` per story: `transcribed` (never listed) → `tamil_verified`
   (launch threshold, per-story human sign-off) → `english_done`.
4. `"tamil_chapters": [{"n": 1, "text": "..."}]` — header line stripped, number in `n`.
5. `"verses": [...]` sourced from the canonical drawer
   (badges: `periyapuranam_root`, `thogai`, `anthathi`); `[]` while pending.
   Char-offset spans into transcripts are NOT produced or consumed.
6. `manifest.json` (slug, title, status, chapter count, export date, schema version)
   drives the reader index and CI gates; never scan directories at runtime.

## Session boundary rules

- This session owns `D:\periapuranam` ONLY. Never read-modify-write anything under `D:\nalvar`.
- Factory exports flow one way: `D:\nalvar` → `content/` (run from the nalvar session).
- Transcription (Sambandhar giants) runs in the nalvar session; don't touch its logs/process.
