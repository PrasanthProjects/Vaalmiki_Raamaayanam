# Parichayam — a complete introductory story

Start with `exports/Parichayam_Story_Short.mp4` after the build completes.

The edit follows the introduction, the epic's structure, human values, the living tradition, Hanuman's presence, and Valmiki. It closes by introducing the next part: **వాల్మీకి మహర్షి కథ — భాగం 1**. All selected spoken verses remain complete. The source episode is abridged by selecting complete scenes; it is not represented as the full E0.01 episode.

`SCRIPT_AND_DIALOGUE.md` contains the exact Telugu dialogue and visual plan. `scene_plan.json` records timing and source assets. The existing Telugu narration is reused locally. Pronunciation and expressive quality require listening review; summary captions are not word-aligned subtitles.

Rebuild from the project root:

```powershell
& production/tools/python/python.exe shorts/S01_Parichayam/build.py
```

Completed scene clips are reused. If changing a scene's artwork, dialogue, or captions, remove only that scene's numbered clip before rebuilding. Final output is a vertical 1080×1920 MP4. The build performs a full decode check and creates a contact sheet. Nothing is uploaded or published.
