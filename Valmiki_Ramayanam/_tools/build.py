"""Build every file for one sarga from its data folder.

usage:  python build.py <kanda_dir> <sarga_no>
        e.g. python build.py 1_Bala_Kanda 1

Reads   _tools/data/<kanda_dir>/Sarga_NNN/
          verses.json            śloka text (from parse.py)
          meanings_*.txt         '### N' blocks: ప్రతిపదార్థం / తాత్పర్యం
          narration_*.txt        '### N' blocks: TITLE, H_*, C_VIS, L_*, E_* lines
          flow_*.txt             '### N' blocks: 7 rows 'clip | chars | frame | motion | camera | light'
          thumbnails.txt         'N | headline | highlight word | sub-line'
          pinned_comments.txt    'N | comment'
Writes  <kanda_dir>/Sarga_NNN/Sloka_NNN.md, captions/Sloka_NNN.srt, 00_INDEX.md
        and 00_CHARACTER_REFERENCE_SHEETS.md at the top level.
"""
import glob
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from shorts_style import STYLE, RESPECT, TAIL, CHARS, GROUPS  # noqa: E402
import live_style as LS  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), 'Long_Videos', '_tools'))
import honor  # noqa: E402  (respectful names, shared with the long videos)

LIVE = False   # set per sarga: True when its flow rows use the published page's reference library (live_style)

KANDAS = {
    '1_Bala_Kanda': 'బాలకాండ', '2_Ayodhya_Kanda': 'అయోధ్యకాండ', '3_Aranya_Kanda': 'అరణ్యకాండ',
    '4_Kishkindha_Kanda': 'కిష్కింధకాండ', '5_Sundara_Kanda': 'సుందరకాండ',
    '6_Yuddha_Kanda': 'యుద్ధకాండ', '7_Uttara_Kanda': 'ఉత్తరకాండ',
}

# Typos in the Wikisource text, corrected to the Gita Press reading.
# Key: (kanda_dir, sarga, sloka) -> [(wrong, right)]
FIX = {
    ('1_Bala_Kanda', 1, 9): [('శ్రీమాఞ్ఛ్త్రునిబర్హణః', 'శ్రీమాఞ్ఛత్రునిబర్హణః')],
    ('1_Bala_Kanda', 1, 15): [('తత్త్వజ్ఞో స్మృతిమాన్', 'తత్త్వజ్ఞః స్మృతిమాన్')],
    ('1_Bala_Kanda', 1, 17): [('సర్వ గుణోపేతః', 'సర్వగుణోపేతః')],
    ('1_Bala_Kanda', 1, 43): [('పరమ ప్రీతస్తూణీ', 'పరమప్రీతస్తూణీ')],
    ('1_Bala_Kanda', 1, 57): [('సోఽభ్య గచ్ఛన్', 'సోఽభ్యగచ్ఛన్')],
    ('1_Bala_Kanda', 1, 65): [('చాస్తి', 'చాస్థి')],
    ('1_Bala_Kanda', 1, 84): [('మహాత్మనః ॥', 'మహాత్మనః ।')],
    ('1_Bala_Kanda', 1, 100): [('త్ క్షత్రియో', 'స్యాత్ క్షత్రియో')],
    # Sarga 2: wiki indentation (::) and a hyphen split the two long last ślokas; k for c (चरितं, शिरसश्च); a stray ర్.
    ('1_Bala_Kanda', 2, 38): [('భగవాన్ ర్మునిర్', 'భగవాన్ మునిర్')],
    ('1_Bala_Kanda', 2, 42): [('మనోరమై-\n::స్తదాస్య', 'మనోరమైస్తదాస్య'), ('యశస్వినో\n::యశస్కరం', 'యశస్వినో యశస్కరం')],
    ('1_Bala_Kanda', 2, 43): [('సంధియోగం\n::సమమధురో', 'సంధియోగం సమమధురో'), ('రఘువరకరితం', 'రఘువరచరితం'),
                              ('మునిప్రణీతం\n::దశశిరసశ్క', 'మునిప్రణీతం దశశిరసశ్చ')],
}

# The long episode each sarga's Shorts come from, for YouTube's "Related video" link on every Short.
RELATED = {('బాలకాండ', 1): ('E1.01', 'వాల్మీకి మహర్షి కథ'), ('బాలకాండ', 2): ('E1.02', 'క్రౌంచ పక్షులు')}

HASHTAGS = '#shorts #ramayanam #telugushorts #devotional #shloka #ramayanintelugu #valmikiramayanam'

# 7 clips covering the ~45 s short: (start s, end s, Telugu label)
SLOTS = [(0, 4, 'హుక్'), (4, 10, 'శ్లోక పఠనం – 1'), (10, 15, 'శ్లోక పఠనం – 2'),
         (15, 23, 'తాత్పర్యం – 1'), (23, 31, 'తాత్పర్యం – 2'), (31, 38, 'జీవిత పాఠం'),
         (38, 45, 'ముగింపు & CTA')]


def mmss(s):
    return f'{s // 60}:{s % 60:02d}'


def blocks(path_glob):
    """Yield (n, body) for every '### N' block in the matching files."""
    for path in sorted(glob.glob(path_glob)):
        for blk in re.split(r'^### ', open(path, encoding='utf-8').read(), flags=re.M)[1:]:
            n, body = blk.split('\n', 1)
            yield int(n), body.strip()


def pipe_lines(path):
    out = {}
    for line in open(path, encoding='utf-8').read().strip().split('\n'):
        parts = [p.strip() for p in line.split(' | ')]
        out[int(parts[0])] = parts[1:]
    return out


def keys_of(chars):
    return [c.strip() for c in chars.split(',') if c.strip() and c.strip() != '-']


def sentences(text):
    return [s.strip() for s in re.findall(r'[^.!?]+[.!?]*', text) if s.strip()]


def split3(text):
    """Split the lesson voiceover into 3 roughly equal runs of whole sentences."""
    sents = sentences(text)
    total = sum(len(s) for s in sents)
    parts, cur, acc = [], [], 0
    for s in sents:
        cur.append(s)
        acc += len(s)
        if len(parts) < 2 and acc >= total * (len(parts) + 1) / 3:
            parts.append(' '.join(cur))
            cur = []
    parts.append(' '.join(cur))
    return (parts + ['', ''])[:3]


def slot_texts(f, sloka_lines):
    half = (len(sloka_lines) + 1) // 2
    lesson = split3(f['L_VO'])
    return [f['H_VO'], ' / '.join(sloka_lines[:half]), ' / '.join(sloka_lines[half:]),
            lesson[0], lesson[1], lesson[2], f['E_VO']]


# Sanskrit nasal + consonant clusters as they are usually read and printed in Telugu (మునిపుఙ్గవమ్ → మునిపుంగవమ్).
NASALS = [('ఙ్', 'కఖగఘ'), ('ఞ్', 'చఛజఝ'), ('ణ్', 'టఠడఢ'), ('న్', 'తథదధ'), ('మ్', 'పఫబభ')]


def reading(line):
    for nasal, cons in NASALS:
        line = re.sub(nasal + f'([{cons}])', r'ం\1', line)
    return line.replace('ఽ', '')


def youtube_title(f, kanda_dir, sarga, n):
    title = f"{f['TITLE'].split(' | ')[0]} | Ramayanam {kanda_dir.split('_')[0]}.{sarga}.{n}"
    assert len(title) <= 100, f'title {n} is {len(title)} characters (YouTube limit 100)'
    return title


def canva_csv(rows):
    """Canva Bulk Create: one row per śloka; headline split so the highlight word gets its own text box."""
    import csv
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['sloka', 'headline', 'before_highlight', 'highlight', 'after_highlight', 'sub_line', 'badge',
                'background_image'])
    for n, (main, hl, sub), badge in rows:
        before, after = main.split(hl, 1)
        w.writerow([n, main, before.strip(), hl, after.strip(), sub, badge, f'Sloka_{n:03d}_thumb.png'])
    return '﻿' + buf.getvalue()  # BOM so Excel and Canva read Telugu correctly


# ---------- sections ----------

def narration_md(f, sloka_lines):
    chant = '\n'.join('> ' + l + '  ' for l in sloka_lines)
    return ("## 4. నెరేషన్ స్క్రిప్ట్ (~45 సెకన్లు)\n\n"
            "### 0:00 – 0:04 · హుక్\n\n"
            f"- **విజువల్:** {f['H_VIS']}\n"
            f"- **వాయిస్ (నాటకీయంగా):** {f['H_VO']}\n"
            f"- **తెరపై టెక్స్ట్:** {f['H_TXT']}\n\n"
            "### 0:04 – 0:15 · శ్లోక పఠనం\n\n"
            f"- **విజువల్:** {f['C_VIS']}\n"
            "- **వాయిస్ (శ్రావ్యంగా, స్పష్టంగా):**\n\n"
            f"{chant}\n\n"
            "### 0:15 – 0:38 · తాత్పర్యం & జీవిత పాఠం\n\n"
            f"- **విజువల్:** {f['L_VIS']}\n"
            f"- **వాయిస్ (సంభాషణ శైలిలో):** {f['L_VO']}\n"
            f"- **తెరపై టెక్స్ట్:** {f['L_TXT']}\n\n"
            "### 0:38 – 0:45 · ముగింపు & CTA\n\n"
            f"- **విజువల్:** {f['E_VIS']}\n"
            f"- **వాయిస్ (వేగంగా, ముగింపు స్వరం లేకుండా):** {f['E_VO']}\n")


MOTION_WORDS = ('leap', 'fly', 'flies', 'flying', 'descend', 'arrow', 'running', 'runs ', 'charg', 'fight',
                'battle', 'swing', 'crash', 'pierc', 'burn', 'gallop', 'dive', 'ascend', 'emerg', 'transform',
                'storm', 'lightning', 'throw', 'hurl', 'flick', 'roar', 'rising', 'rises', 'glides', 'flow')
# Shots AI video handles badly (crowds, many arms or heads): always a still image.
STILL_ONLY = {'RAVANA', 'KHARA', 'KABANDHA'} | GROUPS
STILL_ONLY |= {'RAVANA_TEN', 'KHARA_SOLO', 'RAKSHASA_ARMY', 'VANARA_ARMY', 'AYODHYA_PEOPLE', 'RISHIS_GROUP'} | set(LS.GROUP_TEXT)


def motion_score(clip):
    text = (clip[1] + ' ' + clip[2]).lower()
    return sum(text.count(w) for w in MOTION_WORDS)


def clip_kinds(clips):
    """Pick 2–3 clips per Short that really need video; the rest are stills animated in the editor."""
    kinds = ['image'] * len(clips)
    ok = [not (set(keys_of(c[0])) & STILL_ONLY) for c in clips]
    if ok[0]:
        kinds[0] = 'video'  # the hook always moves
    ranked = sorted((i for i in range(1, len(clips)) if ok[i] and motion_score(clips[i]) > 0),
                    key=lambda i: -motion_score(clips[i]))
    for i in ranked[:3 - kinds.count('video')]:
        kinds[i] = 'video'
    return kinds


def editor_move(cam):
    c = cam.lower()
    if 'pull-back' in c or 'pull back' in c:
        return 'నెమ్మదిగా జూమ్-అవుట్ (115% → 100%)'
    if 'tilt up' in c or 'upward' in c or 'crane up' in c:
        return 'కింద నుండి పైకి నెమ్మదిగా ప్యాన్'
    if 'tilt down' in c or 'crane down' in c or 'downward' in c:
        return 'పై నుండి కిందకు నెమ్మదిగా ప్యాన్'
    if any(w in c for w in ('orbit', 'dolly', 'tracking', 'side')):
        return 'ఎడమ నుండి కుడికి నెమ్మదిగా ప్యాన్ + కొద్దిగా జూమ్-ఇన్'
    return 'నెమ్మదిగా జూమ్-ఇన్ (100% → 112%)'


def still_prompt(chars, frame, light):
    who = '; '.join(CHARS[k] for k in keys_of(chars))
    return ("Vertical 9:16 cinematic still image, 1080x1920, main subject in the centre safe area. "
            f"Style: {STYLE}. "
            + (f"Characters: {who}. " if who else '')
            + f"Scene: {frame} Lighting and atmosphere: {light} "
            "Correct anatomy and natural hands; no extra characters, limbs or faces beyond those described. "
            f"{RESPECT} No text, letters, logos or watermarks.")


def clip_prompt(chars, frame, motion, cam, light):
    who = '; '.join(CHARS[k] for k in keys_of(chars))
    return ("Vertical 9:16 cinematic shot, 8 seconds, main subject in the centre safe area. "
            f"Style: {STYLE}. "
            + (f"Characters (keep exactly this look for the whole shot): {who}. " if who else '')
            + f"Opening frame: {frame} Then: {motion} Camera: {cam} Lighting and effects: {light} "
            "Correct anatomy and natural hands; no extra characters, limbs or faces beyond those described; "
            "smooth, physically consistent motion with no morphing or flicker. "
            f"{RESPECT} {TAIL}")


def flow_md(clips, texts):
    kinds = clip_kinds(clips)
    out = ["## 5. క్లిప్‌లు (9:16)\n",
           f"ఈ Short లో **🎥 వీడియో: {kinds.count('video')}** · **🖼️ ఇమేజ్ + కదలిక: {kinds.count('image')}**\n",
           "- **🎥 వీడియో:** Flow (Veo) లో ప్రాంప్ట్ పెట్టండి. ముందు ఇదే ప్రాంప్ట్‌తో ఇమేజ్ చేసి, నచ్చితే "
           "*Frames to Video* లో మొదటి ఫ్రేమ్‌గా వాడితే తప్పులు తక్కువ. 8 సెకన్ల క్లిప్‌ను ఇచ్చిన సమయానికి ట్రిమ్ చేయండి.\n"
           "- **🖼️ ఇమేజ్ + కదలిక:** ప్రాంప్ట్‌తో ఒక ఇమేజ్ మాత్రమే చేయండి. ఎడిటర్‌లో (CapCut / Resolve) ఇచ్చిన కదలిక పెట్టండి.\n"
           "- **రిఫరెన్స్** లో ఉన్న ఇమేజ్‌లను జత చేయండి (Flow లో *Ingredients*) – "
           "[00_CHARACTER_REFERENCE_SHEETS.md](../../00_CHARACTER_REFERENCE_SHEETS.md).\n"]
    for c in clip_cards(clips, texts):
        ref_line = ' · '.join(f'`{k}.png`' for k in c['refs']) if c['refs'] else 'అవసరం లేదు'
        head = '🎥 వీడియో' if c['kind'] == 'video' else '🖼️ ఇమేజ్ + కదలిక'
        extra = f"- **ఎడిటర్‌లో కదలిక:** {c['move']}\n" if c['move'] else ''
        out.append(f"### క్లిప్ {c['no']} · {c['time']} · {c['label']} · {head}\n\n"
                   f"- **నెరేషన్:** {c['narration']}\n"
                   f"- **రిఫరెన్స్:** {ref_line}\n{extra}\n"
                   f"```text\n{c['prompt']}\n```\n")
    return '\n'.join(out)


CLIPS_NOTE = ('ప్రతి క్లిప్‌కు రెండు ప్రాంప్ట్‌లు: ముందు 🖼️ ఇమేజ్ చేయండి (రిఫరెన్స్ ఇమేజ్‌లు జత చేసి). వీడియో కావాలంటే '
              'ఆ ఇమేజ్‌ను Flow → Frames to Video లో మొదటి ఫ్రేమ్‌గా పెట్టి 🎥 వీడియో ప్రాంప్ట్ వాడండి. "యాక్షన్" క్లిప్‌లు కథలో '
              'కదలిక ఉన్నవి; "మెల్లని కదలిక" క్లిప్‌లకు ఇమేజ్ + ఎడిటర్ కదలిక చాలు, కావాలంటే వీడియో కూడా చేయవచ్చు. '
              'వీడియోలో పాత్రలు అకస్మాత్తుగా కదిలితే: మళ్ళీ Generate చేయండి, లేదా ఇమేజ్ + ఎడిటర్ కదలిక వాడండి.')


def clip_cards(clips, texts):
    """One dict per clip; shared by the Markdown file and the Flow helper page."""
    kinds = clip_kinds(clips)
    cards = []
    for i, (chars, frame, motion, cam, light) in enumerate(clips):
        a, b, label = SLOTS[i]
        video = kinds[i] == 'video'
        if LIVE:
            keys = keys_of(chars)
            refs = LS.ref_keys(keys)
            prompt = LS.video(keys, frame, motion, cam, light) if video else LS.still(keys, frame, light)
            both = {'imagePrompt': LS.still(keys, frame, light),
                    'videoPrompt': LS.start_video(keys, frame, motion, cam, light, video)}
        else:
            refs = [k for k in keys_of(chars) if k not in GROUPS]
            prompt = clip_prompt(chars, frame, motion, cam, light) if video else still_prompt(chars, frame, light)
            both = {'imagePrompt': still_prompt(chars, frame, light),
                    'videoPrompt': clip_prompt(chars, frame, motion if video else LS.GENTLE,
                                               cam if video else 'a very slow, steady push-in', light)
                    + ' ' + LS.STABLE}
        cards.append({
            'no': i + 1, 'time': f'{mmss(a)} – {mmss(b)}', 'label': label, 'kind': kinds[i],
            'narration': texts[i], 'refs': refs, 'move': ('' if video else editor_move(cam) + ' (వీడియో చేయకపోతే)'), 'prompt': prompt, **both,
        })
    return cards


def thumb_md(t, clips, kanda_te, sarga, n):
    main, hl, sub = t
    assert hl in main, f'thumbnail {n}: highlight "{hl}" is not in "{main}"'
    prompt, refs = thumb_prompt(clips)
    return thumb_table(main, hl, sub, kanda_te, sarga, n, refs, prompt)


def thumb_prompt(clips):
    pick = next((c for c in clips if keys_of(c[0])), clips[0])
    if LIVE:
        return LS.thumb(keys_of(pick[0]), pick[1], pick[4])
    who = '; '.join(CHARS[k] for k in keys_of(pick[0]))
    refs = [k for k in keys_of(pick[0]) if k not in GROUPS]
    prompt = ("Vertical 9:16 YouTube Shorts thumbnail key art, single still image, 1080x1920. "
              f"Style: {STYLE}. "
              + (f"Characters: {who}. " if who else '')
              + f"Scene: {pick[1]} Make it a bold, emotional close-up of the main character or symbol in the "
              f"lower-middle of the frame, strong expression, high contrast, glowing rim light. {pick[4]} "
              "Keep the top 35% of the frame a clean dark gradient or soft sky with no important detail "
              "(space for a headline) and the bottom 12% calm and plain (space for a small line). "
              f"{RESPECT} No text, letters, numbers, logos or watermarks in the image.")
    return prompt, refs


def thumb_table(main, hl, sub, kanda_te, sarga, n, refs, prompt):
    return ("## 6. థంబ్‌నెయిల్ (1080×1920)\n\n"
            f"| భాగం | టెక్స్ట్ | రూపం |\n|---|---|---|\n"
            f"| హెడ్‌లైన్ (పై 35%) | **{main}** | తెలుపు, **{hl}** పసుపు (#FFD700), నల్ల అవుట్‌లైన్ + షాడో |\n"
            f"| కింది లైన్ (కింది 12%) | {sub} | తెలుపు, సెమీ-బోల్డ్ |\n"
            f"| బ్యాడ్జ్ (పై ఎడమ) | {kanda_te} · సర్గ {sarga} · శ్లోకం {n} | కాషాయ పట్టీ, తెలుపు అక్షరాలు |\n\n"
            "- **ఫాంట్:** Noto Sans Telugu ExtraBold లేదా Gidugu. హెడ్‌లైన్ 2 లైన్లలోపు.\n"
            "- **బొమ్మ:** పాత్ర ముఖం కింది-మధ్యలో, కళ్ళు స్పష్టంగా.\n"
            f"- **రిఫరెన్స్:** {' · '.join(f'`{k}.png`' for k in refs) if refs else 'అవసరం లేదు'}\n"
            "- బ్యాక్‌గ్రౌండ్ ఈ ప్రాంప్ట్‌తో చేసి, టెక్స్ట్ Canva / ఎడిటర్‌లో వేయండి.\n\n"
            f"```text\n{prompt}\n```\n")


def upload_desc(title, sloka_lines, tt, kanda_te, sarga, n):
    return (f"{title}\n\n" + '\n'.join(sloka_lines) + "\n\n"
            f"తాత్పర్యం:\n{tt}\n\n"
            f"📖 మూలం: శ్రీమద్వాల్మీకి రామాయణం · {kanda_te} · సర్గ {sarga} · శ్లోకం {n}\n"
            "🙏 శ్లోకం శ్లోకంగా వాల్మీకి రామాయణం – అర్థం, జీవిత పాఠంతో.\n"
            + (f"📺 పూర్తి కథ: {RELATED[(kanda_te, sarga)][1]} – Ramayanam {RELATED[(kanda_te, sarga)][0]} (మన ఛానల్‌లో)\n"
               if (kanda_te, sarga) in RELATED else '')
            + f"\n{HASHTAGS}")


def upload_md(title, sloka_lines, tt, pinned, kanda_te, sarga, n, srt_name):
    desc = upload_desc(title, sloka_lines, tt, kanda_te, sarga, n)
    return ("## 7. YouTube అప్‌లోడ్\n\n"
            f"**టైటిల్:**\n\n```text\n{title}\n```\n\n"
            f"**వివరణ (Description):**\n\n```text\n{desc}\n```\n\n"
            f"**పిన్ కామెంట్:**\n\n```text\n{pinned}\n```\n\n"
            + (f"**సంబంధిత వీడియో (Related video):** అప్‌లోడ్ చేసేటప్పుడు *Related video* లో "
               f"**{RELATED[(kanda_te, sarga)][0]} – {RELATED[(kanda_te, sarga)][1]}** లాంగ్ వీడియోను ఎంచుకోండి. "
               "Short చూసినవారికి పూర్తి ఎపిసోడ్‌కు లింక్ కనిపిస్తుంది.\n\n" if (kanda_te, sarga) in RELATED else '')
            + f"**క్యాప్షన్ ఫైల్:** [captions/{srt_name}](captions/{srt_name}) – YouTube Studio → Subtitles → Upload file "
            "లో పెట్టండి, లేదా ఎడిటర్‌లో ఇంపోర్ట్ చేయండి.\n")


# ---------- captions ----------

def chunks(text, limit=38):
    """Break text into caption lines of at most `limit` characters on word boundaries."""
    out = []
    for part in [p.strip() for p in text.split(' / ')]:
        line = ''
        for w in part.split():
            if line and len(line) + 1 + len(w) > limit:
                out.append(line)
                line = w
            else:
                line = f'{line} {w}'.strip()
        if line:
            out.append(line)
    return out


def srt_time(sec):
    ms = int(round(sec * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def srt(texts):
    cues = []
    for i, ((a, b, _), text) in enumerate(zip(SLOTS, texts)):
        # Śloka lines stay whole (clips 2–3); narration is broken into short caption lines.
        lines = [p.strip() for p in text.split(' / ')] if i in (1, 2) else chunks(text)
        total = sum(len(l) for l in lines) or 1
        t = a
        for l in lines:
            end = t + (b - a) * len(l) / total
            cues.append((t, end, l))
            t = end
    return '\n'.join(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{l}\n' for i, (a, b, l) in enumerate(cues, 1))


# ---------- reference sheets ----------

def reference_sheets():
    out = ["# పాత్రల రిఫరెన్స్ ఇమేజ్‌లు (Character Reference Sheets)\n",
           "Google Flow లో పాత్రలు ప్రతి క్లిప్‌లో ఒకేలా కనిపించడానికి, ముందుగా ప్రతి పాత్రకు **ఒక్కసారి** ఇమేజ్ తయారు చేయండి.\n",
           "1. కింది ప్రాంప్ట్‌తో Flow (లేదా ఏదైనా ఇమేజ్ టూల్) లో ఇమేజ్ తయారు చేయండి. 3–4 వెర్షన్లలో ఉత్తమమైనది ఎంచుకోండి.",
           "2. దాన్ని `Valmiki_Ramayanam/_reference_images/` ఫోల్డర్‌లో ఇచ్చిన పేరుతో సేవ్ చేయండి (ఉదా: `RAMA_PRINCE.png`).",
           "3. ప్రతి క్లిప్‌లో **రిఫరెన్స్** అని ఉన్న ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేసి, ఆ క్లిప్ ప్రాంప్ట్ ఇవ్వండి.",
           "4. ఒకసారి ఆమోదించిన ఇమేజ్‌ను మార్చవద్దు. మారిస్తే ఆ పాత్ర ఉన్న అన్ని క్లిప్‌లు మళ్ళీ చేయాలి.\n",
           "పాత్రలు, గుంపులు, వస్తువులు, ప్రదేశాలు – క్లిప్‌ల్లో **రిఫరెన్స్** లో ఉన్న ప్రతిదానికీ ఒక ఇమేజ్.\n"]
    for k, v in LS.LIB.items():   # the published page's library: the images the clips are made with
        out.append(f"## `{k}.png` · {v['te']}\n\n```text\n{v['refprompt']}\n```\n")
    return '\n'.join(out)


def ref_prompt(desc):
    return ("Character reference image for animation consistency: one character only, full body, standing, "
            "facing the camera, centred, plain soft warm-grey background, even soft lighting, calm expression, "
            f"vertical 9:16. Style: {STYLE}. Character: {desc}. {RESPECT} "
            "No text, letters, logos or watermarks.")


# ---------- Flow helper page ----------

def sloka_refs_md(clips, texts):
    """The reference images one Short needs (clips and thumbnail), with the clips that use each."""
    where = {}
    for c in clip_cards(clips, texts):
        for r in c['refs']:
            where.setdefault(r, []).append(str(c['no']))
    for r in thumb_prompt(clips)[1]:
        where.setdefault(r, []).append('థంబ్‌నెయిల్')
    if not where:
        return ''
    rows = '\n'.join(f"| `{k}.png` | {LS.LIB[k]['te']} | {', '.join(v)} |" for k, v in where.items())
    return ("### ఈ శ్లోకానికి రిఫరెన్స్ ఇమేజ్‌లు\n\n"
            "పాత్రలు, గుంపులు, వస్తువులు, ప్రదేశాలు – అన్నీ. ఇమేజ్ ప్రాంప్ట్‌లు: [00_REFERENCES.md](00_REFERENCES.md).\n\n"
            f"| ఇమేజ్ | ఏమిటి | ఏ క్లిప్‌లలో |\n|---|---|---|\n{rows}\n")


def used_refs(slokas):
    """Every reference image a sarga's clips and thumbnails use."""
    return {k for s in slokas for k in s['thumbRefs'] + [r for c in s['clips'] for r in c['refs']]}


def sarga_references(kanda_te, sarga, slokas):
    """00_REFERENCES.md for one sarga: only the images its Shorts need, with the ślokas that use each."""
    where = {}
    for s in slokas:
        for k in s['thumbRefs'] + [r for c in s['clips'] for r in c['refs']]:
            where.setdefault(k, set()).add(s['n'])
    out = [f"# {kanda_te} · సర్గ {sarga} – రిఫరెన్స్ ఇమేజ్‌లు ({len(where)})\n",
           "ఈ సర్గ Shorts కు కావలసినవి మాత్రమే. ఇంతకు ముందు చేసిన ఇమేజ్ ఉంటే అదే వాడండి, కొత్తవి మాత్రమే చేయండి. "
           "ప్రతి క్లిప్‌లో **రిఫరెన్స్** లో ఉన్నవి Flow లో *Ingredients* గా జత చేయండి.\n",
           "| ఇమేజ్ | ఏమిటి | ఏ శ్లోకాల్లో |\n|---|---|---|"]
    for k in sorted(where, key=lambda k: min(where[k])):
        out.append(f"| `{k}.png` | {LS.LIB[k]['te']} | {', '.join(map(str, sorted(where[k])))} |")
    out.append('')
    for k in sorted(where, key=lambda k: min(where[k])):
        out.append(f"## `{k}.png` · {LS.LIB[k]['te']}\n\n```text\n{LS.LIB[k]['refprompt']}\n```\n")
    return '\n'.join(out)


def helper_page(kanda_dir, kanda_te, sarga, slokas):
    """The clip-by-clip copy page: returns (fragment to publish on claude.ai, full local HTML)."""
    if LIVE:   # the published page's own layout (dialogue, objects and places tabs) and library
        data = {'key': f'{kanda_dir}_s{sarga:03d}', 'name': f'{kanda_te} · సర్గ {sarga}', 'slokas': slokas,
                'clipsNote': CLIPS_NOTE, 'refs': LS.library(used_refs(slokas))}
        blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
        tpl = open(os.path.join(TOOLS, 'flow_helper_live_template.html'), encoding='utf-8').read()
        fragment = tpl.replace('__TITLE__', f'{kanda_te} సర్గ {sarga} క్లిప్‌లు').replace('__DATA__', blob)
        full = ('<!doctype html><html lang="te"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'
                + fragment + '</body></html>')
        return fragment, full
    data = {'key': f'{kanda_dir}_s{sarga:03d}', 'name': f'{kanda_te} · సర్గ {sarga}', 'slokas': slokas,
            'unit': 'శ్లోకాలు', 'clipWord': 'క్లిప్', 'clipsNote': CLIPS_NOTE, 'subtitle': 'Google Flow కోసం క్లిప్ ప్రాంప్ట్‌లు',
            'refs': [{'key': k, 'prompt': ref_prompt(v)} for k, v in CHARS.items() if k not in GROUPS]}
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tpl = open(os.path.join(TOOLS, 'flow_helper_template.html'), encoding='utf-8').read()
    fragment = tpl.replace('__TITLE__', f'{kanda_te} సర్గ {sarga} క్లిప్‌లు').replace('__DATA__', blob)
    full = ('<!doctype html><html lang="te"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'
            + fragment + '</body></html>')
    return fragment, full


# ---------- main ----------

def main(kanda_dir, sarga):
    kanda_te = KANDAS[kanda_dir]
    data = os.path.join(TOOLS, 'data', kanda_dir, f'Sarga_{sarga:03d}')
    verses = json.load(open(os.path.join(data, 'verses.json'), encoding='utf-8'))
    mean = {}
    for n, body in blocks(os.path.join(data, 'meanings_*.txt')):
        pp, tt = body.split('తాత్పర్యం\n', 1)
        mean[n] = (pp.replace('ప్రతిపదార్థం\n', '', 1).strip().replace('• ', '- '),
                   re.sub(r'\n+', '\n\n', tt.strip()))
    narr = {n: dict(l.split(': ', 1) for l in body.split('\n') if ': ' in l)
            for n, body in blocks(os.path.join(data, 'narration_*.txt'))}
    flow = {}
    for n, body in blocks(os.path.join(data, 'flow_*.txt')):
        rows = [r.split(' | ') for r in body.split('\n') if r.strip()]
        assert len(rows) == 7 and all(len(r) == 6 for r in rows), f'flow {n}: need 7 rows of 6 fields'
        flow[n] = [r[1:] for r in rows]
    global LIVE
    LIVE = all(LS.known(keys_of(row[0])) for rows in flow.values() for row in rows)
    thumbs = pipe_lines(os.path.join(data, 'thumbnails.txt'))
    pinned = {n: v[0] for n, v in pipe_lines(os.path.join(data, 'pinned_comments.txt')).items()}
    # Respectful names in everything the viewer hears or reads (the śloka itself stays as Valmiki wrote it).
    honor.DISCIPLE_BHARADWAJA = kanda_dir.startswith('1_')
    hon = lambda t: honor.Honorer(quotes=False)(t)
    mean = {n: (hon(pp), hon(tt)) for n, (pp, tt) in mean.items()}
    def hon_narr(f):    # one voice-aware pass per śloka, in spoken order (a speech may run over two lines)
        h = honor.Honorer()
        return {k: (v if k.endswith('_VIS') else h(v)) for k, v in f.items()}
    narr = {n: hon_narr(f) for n, f in narr.items()}
    def thumb(v):     # the highlight must stay a piece of the headline
        main, hl, rest = hon(v[0]), hon(v[1]), [hon(x) for x in v[2:]]
        if hl not in main:
            hl = v[1] if v[1] in main else next((w for w in main.split() if w.startswith(v[1][:2])), main.split()[-1])
        return [main, hl, *rest]
    thumbs = {n: thumb(v) for n, v in thumbs.items()}
    pinned = {n: hon(v) for n, v in pinned.items()}

    out_dir = os.path.join(ROOT, kanda_dir, f'Sarga_{sarga:03d}')
    os.makedirs(os.path.join(out_dir, 'captions'), exist_ok=True)
    index, canva_rows, helper, n_video, n_image = [], [], [], 0, 0
    for n, lines in verses:
        for part, table in (('meanings', mean), ('narration', narr), ('flow', flow),
                            ('thumbnails', thumbs), ('pinned_comments', pinned)):
            assert n in table, f'śloka {n}: missing {part}'
        text = re.sub(r'  +', ' ', '\n'.join(lines))
        for a, b in FIX.get((kanda_dir, sarga, n), []):
            assert a in text, (n, a)
            text = text.replace(a, b)
        ls = text.split('\n')
        ls[-1] = ls[-1].rstrip(' ।॥') + f' ॥ {n} ॥'
        pp, tt = mean[n]
        f = narr[n]
        texts = slot_texts(f, ls)
        title = youtube_title(f, kanda_dir, sarga, n)
        name = f'Sloka_{n:03d}'
        read = [reading(l) for l in ls]
        read_md = ("\n\n**చదవడానికి సులువుగా (రికార్డింగ్ కోసం):**\n\n" + '  \n'.join(read)) if read != ls else ''
        md = (f"# {kanda_te} · సర్గ {sarga} · శ్లోకం {n}\n\n"
              "**ఈ ఫైల్‌లో:** 1. శ్లోకం · 2. ప్రతిపదార్థం · 3. తాత్పర్యం · 4. నెరేషన్ · "
              "5. క్లిప్‌లు · 6. థంబ్‌నెయిల్ · 7. YouTube అప్‌లోడ్\n\n"
              "## 1. శ్లోకం\n\n" + '  \n'.join(ls) + read_md + "\n\n"
              f"## 2. ప్రతిపదార్థం\n\n{pp}\n\n"
              f"## 3. తాత్పర్యం\n\n{tt}\n\n"
              + narration_md(f, ls) + '\n'
              + flow_md(flow[n], texts) + '\n'
              + (sloka_refs_md(flow[n], texts) + '\n' if LIVE else '')
              + thumb_md(thumbs[n], flow[n], kanda_te, sarga, n) + '\n'
              + upload_md(title, ls, tt, pinned[n], kanda_te, sarga, n, name + '.srt'))
        open(os.path.join(out_dir, name + '.md'), 'w', encoding='utf-8', newline='\n').write(md)
        open(os.path.join(out_dir, 'captions', name + '.srt'), 'w', encoding='utf-8', newline='\n').write(srt(texts))
        kinds = clip_kinds(flow[n])
        index.append(f"| {n} | [{thumbs[n][0]}]({name}.md) | {title.replace('|', '·')} | "
                     f"{kinds.count('video')} 🎥 + {kinds.count('image')} 🖼️ | [srt](captions/{name}.srt) |")
        canva_rows.append((n, thumbs[n], f'{kanda_te} · సర్గ {sarga} · శ్లోకం {n}'))
        tprompt, trefs = thumb_prompt(flow[n])
        helper.append({
            'n': n, 'headline': thumbs[n][0], 'hl': thumbs[n][1], 'sub': thumbs[n][2],
            'badge': f'{kanda_te} · సర్గ {sarga} · శ్లోకం {n}', 'title': title, 'sloka': ls,
            'reading': read if read != ls else None, 'clips': clip_cards(flow[n], texts),
            'thumbPrompt': tprompt, 'thumbRefs': trefs,
            'desc': upload_desc(title, ls, tt, kanda_te, sarga, n), 'pinned': pinned[n], 'srt': name + '.srt',
            **({'speaker': [x.strip() for x in f['SPK'].split(' | ', 1)]} if 'SPK' in f else {})})
        n_video += kinds.count('video')
        n_image += kinds.count('image')
    open(os.path.join(out_dir, '00_INDEX.md'), 'w', encoding='utf-8', newline='\n').write(
        f"# {kanda_te} · సర్గ {sarga} – సూచిక\n\n"
        f"{len(verses)} శ్లోకాలు · మొత్తం {n_video} 🎥 వీడియో క్లిప్‌లు + {n_image} 🖼️ ఇమేజ్‌లు. "
        "హెడ్‌లైన్ మీద క్లిక్ చేస్తే ఆ శ్లోకం ఫైల్ తెరుచుకుంటుంది. "
        "థంబ్‌నెయిల్‌లు అన్నీ ఒకేసారి: [thumbnails_canva.csv](thumbnails_canva.csv) (Canva → Bulk create).\n\n"
        "| శ్లోకం | థంబ్‌నెయిల్ హెడ్‌లైన్ | YouTube టైటిల్ | క్లిప్‌లు | క్యాప్షన్ |\n|---|---|---|---|---|\n"
        + '\n'.join(index) + '\n')
    open(os.path.join(out_dir, 'thumbnails_canva.csv'), 'w', encoding='utf-8', newline='').write(canva_csv(canva_rows))
    fragment, full = helper_page(kanda_dir, kanda_te, sarga, helper)
    if LIVE:
        open(os.path.join(out_dir, '00_REFERENCES.md'), 'w', encoding='utf-8', newline='\n').write(
            sarga_references(kanda_te, sarga, helper))
    open(os.path.join(out_dir, '00_CLIPS_HELPER.html'), 'w', encoding='utf-8', newline='\n').write(full)
    os.makedirs(os.path.join(TOOLS, 'publish'), exist_ok=True)  # claude.ai copy; not committed
    open(os.path.join(TOOLS, 'publish', f'{kanda_dir}_Sarga_{sarga:03d}.html'), 'w', encoding='utf-8',
         newline='\n').write(fragment)
    open(os.path.join(ROOT, '00_CHARACTER_REFERENCE_SHEETS.md'), 'w', encoding='utf-8', newline='\n').write(
        reference_sheets())
    print(f'{kanda_te} sarga {sarga}: {len(verses)} ślokas built')


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
