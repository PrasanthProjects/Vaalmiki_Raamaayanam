# Scene Image Production Plan

This is the canonical workflow for rebuilding or completing the Ramayanam scene images.

## Canonical folder and file names

Use one folder per episode:

```text
assets/
  episodes/
    E0.01_parichayam/
      scene-001_valmiki-introduction.png
      scene-002_ashram-setting.png
      scene-003_...
      manifest.json
    E1.01_valmiki-maharshi-katha/
    E1.02_krauncha-pakshulu/
    E2.01_ramudi-gunamulu/
```

Rules:

- Episode folder: `E<khaanda>.<episode>_<short-kebab-case-title>`.
- Image name: `scene-<three-digit-number>_<short-kebab-case-description>.png`.
- Scene numbers follow the episode script exactly; never renumber an existing scene to hide a gap.
- Use lowercase English kebab-case for machine-safe names. Telugu narration and titles remain in the script files.
- Keep generated source images in the episode folder. Put QA contact sheets and reviews under that same episode's `qa/` folder.
- Never overwrite an existing image. A replacement is saved as `scene-001_name-v2.png`, and the manifest records why.

## Episode status folders

The folder name is the stable identity. Status is tracked in `manifest.json`:

```json
{
  "episode": "E0.01",
  "script": "00_Parichayam/E0.01_parichayam.md",
  "status": "planned",
  "style_lock": ["00_CHARACTER_BIBLE.md", "00_STYLE_GUIDE.md"],
  "scenes": [
    {
      "number": 1,
      "slug": "valmiki-introduction",
      "script_row": 1,
      "status": "missing",
      "file": "scene-001_valmiki-introduction.png",
      "prompt": ""
    }
  ]
}
```

Allowed scene statuses: `planned`, `missing`, `draft`, `approved`, `replaced`, `not-needed`.

## Restart and missed-scene workflow

1. Read the episode markdown and count its scene rows.
2. Build or update the episode `manifest.json` without deleting old assets.
3. Generate only scenes marked `missing` or `replaced`.
4. Review images for character locks, location register, composition, and continuity.
5. Mark approved images in the manifest and record the final prompt.

To restart fully, create a new versioned episode directory such as
`E0.01_parichayam_v2/`; the original remains available for comparison.

## Existing assets

Existing files under `images/`, `assets/images/`, and `production/` are legacy/reference assets. They are not moved automatically. During migration, each file should be copied into the canonical episode folder only after matching it to a script scene.

## Generation order

Start at `E0.01`, then proceed numerically through the scripted episodes. For a faster recovery pass, generate only missing scenes in this order:

1. E0.01 Parichayam
2. E1.01-E1.26 Baala Khaanda
3. E2.01-E2.50 Ayodhya Khaanda
4. E3.01-E3.34 Aranya Khaanda
5. E4.01-E4.04 Kishkindha Khaanda, then continue as scripts are added

All prompts must include the locks in `00_CHARACTER_BIBLE.md` and the relevant location register in `00_STYLE_GUIDE.md`.
