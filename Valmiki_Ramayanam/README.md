# శ్రీమద్వాల్మీకి రామాయణం – శ్లోకం ఒక్కోటిగా

Original Vālmīki Rāmāyaṇam in Telugu script, one file per śloka, each a ready-to-make YouTube Short.

**New here? Open [START_HERE.md](START_HERE.md).**

## Layout

```
Valmiki_Ramayanam/
  START_HERE.md                      step-by-step: how to make a Short
  00_SHORTS_PRODUCTION_GUIDE.md      rules: audio, Flow, devotion, captions, thumbnails, growth
  00_CHARACTER_REFERENCE_SHEETS.md   one image prompt per character (make once)
  _reference_images/                 your approved character images go here
  1_Bala_Kanda/ … 7_Uttara_Kanda/  one folder per kaanda (Gita Press sarga counts:
                                     Bala 77, Ayodhya 119, Aranya 75, Kishkindha 67, Sundara 68, Yuddha 128, Uttara 111)
    00_SARGAS.md                     every sarga of the kaanda with its status
    Sarga_001/ … Sarga_077/          one folder per sarga (empty ones say "not made yet")
      00_INDEX.md                    all ślokas of the sarga with links
      Sloka_001.md … Sloka_100.md    everything for one Short
      captions/Sloka_001.srt …       Telugu captions per Short
      thumbnails_canva.csv           all thumbnail texts for Canva Bulk Create
  _tools/                            build scripts and source data
```

## Each śloka file

1. శ్లోకం – Telugu script
2. ప్రతిపదార్థం – word-by-word meaning
3. తాత్పర్యం – meaning in everyday Telugu
4. నెరేషన్ – timed ~45 s voice script
5. క్లిప్‌లు – 7 prompts (9:16): 2–3 🎥 video clips for Flow, the rest 🖼️ still images with an editor zoom/pan; narration and reference images for each
6. థంబ్‌నెయిల్ – headline, sub-line, badge and a text-free background prompt
7. YouTube అప్‌లోడ్ – title, description, pinned comment, caption file

## Source of the text

- Southern (dākṣiṇātya) recension, as in the Gita Press edition.
- Sanskrit Wikisource `रामायणम्/<काण्डम्>/सर्गः N`, converted letter-for-letter to Telugu script by `_tools/parse.py`.
- Typing mistakes in the source are corrected to the Gita Press reading; every correction is listed in `FIX` in `_tools/build.py`.

## Rebuilding (for maintainers)

All written content lives in `_tools/data/<kanda>/Sarga_NNN/` (`meanings_*`, `narration_*`, `flow_*`, `thumbnails.txt`, `pinned_comments.txt`, `verses.json`). Never edit the generated `Sloka_*.md` files by hand; change the data or `_tools/shorts_style.py`, then run:

```
cd _tools
python build.py 1_Bala_Kanda 1
```

## Progress

| Kāṇḍa | Sargas done |
|---|---|
| బాలకాండ | 1 (100 ślokas) |
