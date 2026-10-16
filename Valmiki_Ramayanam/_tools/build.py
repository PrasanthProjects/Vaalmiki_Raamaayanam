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
}

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
    out = ["## 5. Google Flow వీడియో క్లిప్‌లు (9:16 · ఒక్కోటి 8 సె)\n",
           "ప్రతి క్లిప్‌కు ఒకే ప్రాంప్ట్. **రిఫరెన్స్** లో ఉన్న ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేయండి "
           "([00_CHARACTER_REFERENCE_SHEETS.md](../../00_CHARACTER_REFERENCE_SHEETS.md)). "
           "క్లిప్‌ను ఇచ్చిన సమయానికి ట్రిమ్ చేయండి.\n"]
    for i, (chars, frame, motion, cam, light) in enumerate(clips):
        a, b, label = SLOTS[i]
        refs = [k for k in keys_of(chars) if k not in GROUPS]
        ref_line = ' · '.join(f'`{k}.png`' for k in refs) if refs else 'అవసరం లేదు'
        out.append(f"### క్లిప్ {i + 1} · {mmss(a)} – {mmss(b)} · {label}\n\n"
                   f"- **నెరేషన్:** {texts[i]}\n"
                   f"- **రిఫరెన్స్:** {ref_line}\n\n"
                   f"```text\n{clip_prompt(chars, frame, motion, cam, light)}\n```\n")
    return '\n'.join(out)


def thumb_md(t, clips, kanda_te, sarga, n):
    main, hl, sub = t
    assert hl in main, f'thumbnail {n}: highlight "{hl}" is not in "{main}"'
    pick = next((c for c in clips if keys_of(c[0])), clips[0])
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


def upload_md(f, sloka_lines, tt, pinned, kanda_te, sarga, n, srt_name):
    title = f['TITLE']
    assert len(title) <= 100, f'title {n} is {len(title)} characters (YouTube limit 100)'
    desc = (f"{title}\n\n" + '\n'.join(sloka_lines) + "\n\n"
            f"తాత్పర్యం:\n{tt}\n\n"
            f"📖 మూలం: శ్రీమద్వాల్మీకి రామాయణం · {kanda_te} · సర్గ {sarga} · శ్లోకం {n}\n"
            "🙏 శ్లోకం శ్లోకంగా వాల్మీకి రామాయణం – అర్థం, జీవిత పాఠంతో.\n\n"
            f"{HASHTAGS}")
    return ("## 7. YouTube అప్‌లోడ్\n\n"
            f"**టైటిల్:**\n\n```text\n{title}\n```\n\n"
            f"**వివరణ (Description):**\n\n```text\n{desc}\n```\n\n"
            f"**పిన్ కామెంట్:**\n\n```text\n{pinned}\n```\n\n"
            f"**క్యాప్షన్ ఫైల్:** [captions/{srt_name}](captions/{srt_name}) – YouTube Studio → Subtitles → Upload file "
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
           "2. దాన్ని `Valmiki_Ramayanam/_reference_images/` ఫోల్డర్‌లో ఇచ్చిన పేరుతో సేవ్ చేయండి (ఉదా: `RAMA_S3.png`).",
           "3. ప్రతి క్లిప్‌లో **రిఫరెన్స్** అని ఉన్న ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేసి, ఆ క్లిప్ ప్రాంప్ట్ ఇవ్వండి.",
           "4. ఒకసారి ఆమోదించిన ఇమేజ్‌ను మార్చవద్దు. మారిస్తే ఆ పాత్ర ఉన్న అన్ని క్లిప్‌లు మళ్ళీ చేయాలి.\n",
           "గుంపులు (ఋషులు, రాక్షస సైన్యం, వానర సైన్యం, దేవతలు, ప్రజలు) కు రిఫరెన్స్ అవసరం లేదు.\n"]
    for k, desc in CHARS.items():
        if k in GROUPS:
            continue
        prompt = ("Character reference image for animation consistency: one character only, full body, standing, "
                  "facing the camera, centred, plain soft warm-grey background, even soft lighting, calm expression, "
                  f"vertical 9:16. Style: {STYLE}. Character: {desc}. {RESPECT} "
                  "No text, letters, logos or watermarks.")
        out.append(f"## `{k}.png`\n\n```text\n{prompt}\n```\n")
    return '\n'.join(out)


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
    thumbs = pipe_lines(os.path.join(data, 'thumbnails.txt'))
    pinned = {n: v[0] for n, v in pipe_lines(os.path.join(data, 'pinned_comments.txt')).items()}

    out_dir = os.path.join(ROOT, kanda_dir, f'Sarga_{sarga:03d}')
    os.makedirs(os.path.join(out_dir, 'captions'), exist_ok=True)
    index = []
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
        name = f'Sloka_{n:03d}'
        md = (f"# {kanda_te} · సర్గ {sarga} · శ్లోకం {n}\n\n"
              "**ఈ ఫైల్‌లో:** 1. శ్లోకం · 2. ప్రతిపదార్థం · 3. తాత్పర్యం · 4. నెరేషన్ · "
              "5. Flow క్లిప్‌లు · 6. థంబ్‌నెయిల్ · 7. YouTube అప్‌లోడ్\n\n"
              "## 1. శ్లోకం\n\n" + '  \n'.join(ls) + "\n\n"
              f"## 2. ప్రతిపదార్థం\n\n{pp}\n\n"
              f"## 3. తాత్పర్యం\n\n{tt}\n\n"
              + narration_md(f, ls) + '\n'
              + flow_md(flow[n], texts) + '\n'
              + thumb_md(thumbs[n], flow[n], kanda_te, sarga, n) + '\n'
              + upload_md(f, ls, tt, pinned[n], kanda_te, sarga, n, name + '.srt'))
        open(os.path.join(out_dir, name + '.md'), 'w', encoding='utf-8', newline='\n').write(md)
        open(os.path.join(out_dir, 'captions', name + '.srt'), 'w', encoding='utf-8', newline='\n').write(srt(texts))
        index.append(f"| {n} | [{thumbs[n][0]}]({name}.md) | {f['TITLE'].split(' | ')[0]} | "
                     f"[srt](captions/{name}.srt) |")
    open(os.path.join(out_dir, '00_INDEX.md'), 'w', encoding='utf-8', newline='\n').write(
        f"# {kanda_te} · సర్గ {sarga} – సూచిక\n\n{len(verses)} శ్లోకాలు. హెడ్‌లైన్ మీద క్లిక్ చేస్తే ఆ శ్లోకం ఫైల్ తెరుచుకుంటుంది.\n\n"
        "| శ్లోకం | థంబ్‌నెయిల్ హెడ్‌లైన్ | YouTube టైటిల్ | క్యాప్షన్ |\n|---|---|---|---|\n"
        + '\n'.join(index) + '\n')
    open(os.path.join(ROOT, '00_CHARACTER_REFERENCE_SHEETS.md'), 'w', encoding='utf-8', newline='\n').write(
        reference_sheets())
    print(f'{kanda_te} sarga {sarga}: {len(verses)} ślokas built')


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
