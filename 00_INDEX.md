# శ్రీమద్రామాయణం — YouTube & Shorts Production Plan
### Master Index

**Source:** "చిత్రరూపంలో సంపూర్ణ వాల్మీకి రామాయణము" (Chitra Roopamlo Sampoorna Valmiki Ramayanamu) — 717 pages, illustrated Telugu edition. Covers Parichayam (introduction) + 6 Khaandas (Baala, Ayodhya, Aranya, Kishkindha, Sundara, Yudha). Ends at Rama's coronation; does not include Uttara Khaanda.

**Core production rule:** Every episode covers its source pages **paragraph by paragraph — nothing skipped, nothing summarized away.** This is a hard requirement, confirmed with the user, and is why this series runs to roughly **250+ long-form episodes** rather than a ~60-episode condensed retelling. Episodes stay 8-10 minutes by narrowing each episode's page-span (roughly 2.5-3 source pages per episode), not by cutting content.

---

## Channel name — decided

**పురాణామృతం (Puranamrutham)** — "the nectar of the Puranas." See `00_INTRO_OUTRO_TEMPLATES.md` for the channel's fixed opening bumper and closing card (used on every long-form video and every short — never redesigned per episode).

## ⚠️ Read before generating anything

1. **`00_CHARACTER_BIBLE.md`** — Visual Lock + Voice Profile for every character, plus the era/region style baseline (Treta Yuga, South Indian). Copy locks verbatim into every prompt.
2. **`00_STYLE_GUIDE.md`** — architecture, clothing, and palette by location register (Ayodhya, forest-exile, Kishkindha, Lanka).
3. **`00_INTRO_OUTRO_TEMPLATES.md`** — the fixed పురాణామృతం opening/closing bumper every video and short wraps around.
   - **`00_NARRATOR_VISUAL_PROFILE.md`** — optional companion file: the Narrator's visual appearance (for trailers/thumbnails only — he stays off-screen inside actual episodes, see rule below).
4. **Source-fidelity + verse-accuracy rule** — every stotram/shloka/padyam in the source must be recited correctly, character-by-character verified, before an episode script is marked final. See "Text pipeline status" below — no episode is finalized on text that hasn't cleared this check yet.
5. **No character speaks on-mic except the Narrator.** Everyone else moves, acts, and is described in third person. (See Character Bible → Narrator.)

---

## Text pipeline status (why this file doesn't yet have 250 filled-in episodes)

The source PDF's embedded text layer is corrupted (its font's internal character map substitutes wrong symbols for ~100 different conjuncts, and silently reorders vowel-signs in others — confirmed independently against two extraction engines and against OCR of the actual rendered pages). Fixing this properly, rather than guessing, requires:

1. ✅ Raw text extracted verbatim, page-by-page, all 717 pages (`raw_source_text.txt` per Khaanda folder)
2. ✅ ~104 corrupted symbols decoded and fixed via cross-referencing known names/verses (`corrected_text.txt` per Khaanda folder)
3. 🔄 **In progress:** full-corpus OCR pass (reads the actual rendered page images, sidesteps the font-encoding bug entirely) — running in the background, khaanda-by-khaanda. Vignapti and Parichayam are done; Baala Khaanda is in progress.
4. ⏳ **Not started:** reconciling OCR output against the corrected extraction (catches anything either method got wrong alone), then a manual verse-by-verse check of every shloka/stotram/padyam against the reconciled text
5. ⏳ **Not started:** paragraph-by-paragraph episode scripting, Khaanda by Khaanda, only once a Khaanda's text has cleared step 4

**An episode is only added to this index once its source text has cleared step 4.** This is slower than writing from the raw extraction directly, but a wrong syllable in a stotram is treated as a hard blocker, not a minor issue, per your standing instruction.

---

## Files in this project

- `00_CHARACTER_BIBLE.md` — required reading, every episode
- `00_INDEX.md` — this file
- `00 - Vignapti (Foreword)` / `00 - Parichayam (Introduction)` — text files (raw / corrected / OCR), verification pending
- `1 - Baala Khaanda/` through `6 - Yudha Khaanda/` — each folder holds that Khaanda's `raw_source_text.txt`, `corrected_text.txt`, and (as OCR completes) `ocr_text.txt`; episode scripts land here once written, as `1.01_<title>.md` etc.

## Episode & shorts numbering

- Long-form: `E<khaanda#>.<episode#>` — e.g. `E1.03`. Parichayam is `E0.01`.
- Shorts: `S<khaanda#>.<episode#>.<short#>` — e.g. `S1.03.02`. Shorts are cut FROM an already-scripted episode, never written independently (guarantees they inherit the parent episode's verified text and character locks).
- 2-3 shorts per long-form episode, each one self-contained emotional beat (one exchange, one verse, one action moment) — not a compressed summary of the whole episode.

## Episode file format (once scripted)

**Scene # | Clip length | Visual prompt (location register + character Stage tags from the Character Bible) | Telugu narration (verbatim, source-checked) | Notes (verse-recitation flags, pronunciation flags, transition flags)** — plus a Shorts Hook per short cut from that episode, and a **Total runtime** line at the end of the script table.

Every scene row is a **self-contained clip unit** — generate each one independently (each row already carries its own character locks and location register, so nothing depends on reading a previous row), then concatenate in order. This is the whole point of the scene-by-scene table: it's a literal shot list, not just a script.

**Clip length** is a rounded-up production target in seconds, matched to common AI video tool increments (4/6/8/10/12/14/16/20/25/30s), based on the narration's natural unhurried pace for that row — roughly 2.2 words/sec for plain narration, ~1.2 words/sec for verses (verses always get extra room; never compress a shloka's clip to hit a runtime target). The **Total runtime** is the sum of all clip lengths in that episode.

**Runtime varies naturally by source density — don't force every episode to 8-10 minutes.** Some page-ranges are dialogue-dense and short (E1.01 runs ~4 min), others are description-heavy and long. Padding a short episode with invented visual beats to hit a target would violate the source-fidelity rule; report the real total and move on. `~8-10 min` remains the general design target for the series overall, not a hard floor per episode.

**Retrofit status:** this Clip-length column was added starting mid-project — `E1.01` has it fully filled in as the reference template. The other 25 already-written Baala Khaanda episodes (E0.01, E1.02-E1.26) do not yet have per-scene clip lengths; they'll get retrofitted in a batch pass. Every episode written from here forward includes it from the start.

---

## Provisional episode map

Page numbers are the PDF's own printed page numbers. Counts below are provisional until each Khaanda's text clears verification (step 4) — final counts may shift slightly once real paragraph boundaries are confirmed.

| Khaanda | Source pages | Provisional episode count | Status |
|---|---|---|---|
| Parichayam | 6-7 | 1 (E0.01) | ✅ Scripted |
| 1 — Baala Khaanda | 8-104 (97 pages) | **26 — ✅ COMPLETE** | ✅ Fully scripted, E0.01-E1.26, pp. 6-104 in full |
| 2 — Ayodhya Khaanda | 105-217 (113 pages) | **50 — ✅ COMPLETE** | ✅ Fully scripted, E2.01-E2.50, pp. 105-217 in full (~3 h 3 min) |
| 3 — Aranya Khaanda | 218-331 (114 pages) | **34 — ✅ COMPLETE** | ✅ Fully scripted, E3.01-E3.34, pp. 218-331 in full (~2 h 46 min) |
| 4 — Kishkinda Khaanda | 332-422 (91 pages) | ~30-35 | ✅ OCR done; **4 episodes scripted (E4.01-E4.04, pp. 332-343)**, in progress |
| 5 — Sundhara Khaanda | 423-520 (98 pages) | ~35-40 | 🔄 OCR in progress |
| 6 — Yudha Khaanda | 521-717 (197 pages) | ~65-75 | ⏳ OCR not started |
| **Total** | **717 pages** | **~230-270 long-form + ~550-700 shorts** | |

**🎉 Baala Khaanda is complete — 26 of ~26 episodes fully scripted (E0.01 through E1.26), pp. 6-104 in full, paragraph by paragraph.** Full arc: Valmiki's origin (E0.01-E1.02) → Ayodhya/Dasharatha/Rishyashringa (E1.03-04) → Rama's birth (E1.05) → the journey with Vishwamitra, including his entire 7-episode backstory arc from king to Brahmarshi (E1.06-E1.21) → the Shiva-bow, Sita's birth story, and the wedding of all four princes (E1.22-E1.24) → Parashurama's challenge (E1.25) → the quiet closing coda on Rama and Sita's wordless love (E1.26). Every stotram/shloka/padyam across all 26 episodes is flagged for the manual verse-verification pass before recording.

**🎉 Ayodhya Khaanda is complete — 50 episodes (E2.01-E2.50), pp. 105-217 in full, ~3 h 3 min.** The closing run E2.45-E2.50 covers Rama's grief and the forest shraddha → the dharma debate with Bharata and the Kekaya promise → Jabali's argument and Rama's answer on truth → Bharata's protest-fast and Rama's vow → the golden sandals enthroned in Ayodhya → Atri and Anasuya, ending exactly where E3.01 begins. Note: the shlokas on pp. 204-211 are printed in a broken transliteration in both extractions; E2.45-E2.49 reconstruct them in standard form, all flagged for extra scrutiny in the verse-audit pass. Production note: single-Narrator-only voice confirmed by the user as the launch plan; per-character voices deferred to a possible later phase.

**🎉 Aranya Khaanda is complete — 34 episodes (E3.01-E3.34), pp. 218-331 in full, ~2 h 46 min.** Full arc: Viradha → Sharabhanga → Sutikshna → Sita's counsel → the ten years among the hermitages → Vatapi-Ilvala → Agastya's weapons and Jatayu → the Panchavati parnashala → winter at Panchavati → Shurpanakha → her mutilation and the fourteen rakshasas → the battle of Janasthana (Khara, Dushana, Trishira and the 14,000) → Ravana in Lanka → Shurpanakha rouses Ravana → Ravana and Maricha → the golden deer → Maricha's death and the false cry → Lakshmana forced to leave → Ravana in disguise → the abduction → Jatayu's battle → the jewels dropped among five vanaras → Sita in the Ashoka grove → the empty hut → Rama's wrath and Lakshmana's counsel → Jatayu's death and last rites → Ayomukhi and Kabandha → Dhanu's counsel to seek Sugriva → Shabari). Sita moves to SITA-S4 (captivity) in E3.25-E3.26. Shurpanakha appears in her true form only (the source has no disguise phase) — Character Bible updated to match. Ravana first appears on screen in E3.14; his look is fixed there as ten heads in a fan with twenty arms, following the source's own description (recorded in the Character Bible). Rama moves from RAMA-S3 to RAMA-S4 at the ten-year montage in E3.05; all later Aranya episodes use RAMA-S4. Baala, Ayodhya and Aranya are now continuous from E0.01 to E3.34. **Kishkindha started:** E4.01-E4.04 (Pampa lament → Hanuman's first appearance → his gift of speech → the friendship sworn before fire). **Review pass (E2.45-E4.04):** a page-by-page and sentence-level coverage check against the OCR text found no missed pages or passages; 65 thin visual prompts were rewritten, and a series-wide "Cinematic & devotional treatment" section was added to `00_STYLE_GUIDE.md` (darshan shots, divine revelations, shloka cards, recaps, end cards, grief, counsel, nature-as-witness). **Review pass (E0.01-E2.44):** p. 17 added to E1.02 (Brahma's boon → Lava-Kusha → Kosala); young Dasharatha's hunt (p. 170) added to E2.27; E1.25's placeholder captions replaced with the p. 97-98 text; nine dropped prose passages restored (E1.11, E1.15, E2.05, E2.09, E2.12, E2.19, E2.22, E2.28, E2.29); four missing shlokas added (p. 109 in E2.02, two from p. 158 in E2.22, p. 175 in E2.28); visual-only and placeholder rows merged or removed (E1.04, E1.20); the pipeline now reads the narration column from the table header, so Baala's Location-register column no longer leaks into the narration parts. Next: E4.05 (p. 344, Sita's jewels).

**Text pipeline is now well ahead of scripting** — 4 of 6 Khaandas are fully OCR'd (Baala, Ayodhya, Aranya, Kishkindha), with Sundara in progress and Yudha still queued. Scripting, not text availability, is now the pacing bottleneck going forward.

## Workflow per episode (once its Khaanda clears verification)

1. Pull that episode's page-range from the verified text
2. Write the narration script paragraph-by-paragraph (nothing skipped), flagging every verse for the manual correctness pass
3. Break the script into visual-prompt scenes, tagging each character with their Character Bible Stage + location register
4. Derive 2-3 Shorts from the finished episode
5. Move to the next episode; a Khaanda file is assembled once all its episodes are done

---

*Next update to this file: once Baala Khaanda's OCR pass finishes and the reconciliation/verse-check pass is done, Khaanda 1's episodes get written out in full and this index's status table updates.*
