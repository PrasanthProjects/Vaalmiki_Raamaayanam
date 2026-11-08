"""Valmiki Cinema: one movie-style video per sarga, built from a plain script in source/.

Script format (one file per video, see source/1_Bala_Kanda/S000_prologue.txt):
    TITLE: ...            video title (Telugu)
    COVERS: ...           which sargas and ślokas the video tells
    NEXT: ...             what the next video is
    ## <scene title> | <ślokas> | <place, in English>
    SHOT <ślokas> | <EP> | <picture, English> | <what moves, English> | <camera, English>
      N: ...              narrator (కథకుడు)
      D <KEY>: ...        a character speaks (KEY = VALMIKI, NARADA, BRAHMA, RAMA, ...)
      SONG <KEY>: ...     sung or chanted lines (the śloka itself)
      M: ...              music cue
      FX: ...             sound effects
      CAP: ...            small on-screen caption
      SEC: n              length in seconds (otherwise from the spoken words)
      VIDEO / STILL       force a real video clip or a still image
Pictures follow the long videos' character bible and reference images, photoreal 16:9.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CINEMA = os.path.dirname(HERE)
ROOT = os.path.dirname(CINEMA)
sys.path.insert(0, os.path.join(ROOT, 'Long_Videos', '_tools'))
sys.path.insert(1, os.path.join(ROOT, 'Valmiki_Ramayanam', '_tools'))
import long_style as LS   # noqa: E402
from soften import soft    # noqa: E402

VOICES = {   # who speaks: Telugu name and the voice to cast (same voice in every video)
    'N': ('కథకుడు', 'warm, steady middle-aged male storyteller; clear everyday Telugu, never rushed'),
    'VALMIKI': ('వాల్మీకి మహర్షి', 'old sage, soft and deep, full of feeling'),
    'NARADA': ('నారద మహర్షి', 'bright, joyful voice of a grown man of about twenty-five, musical lilt'),
    'BRAHMA': ('బ్రహ్మదేవుడు', 'very deep, calm, slow, with a light echo'),
    'DISCIPLE': ('భరద్వాజుడు (శిష్యుడు)', 'young man, gentle and respectful'),
    'RAMA': ('శ్రీరాములవారు', 'calm, warm, kingly baritone; never loud'),
    'BHARATA': ('భరతుడు', 'young prince, earnest and tearful, pleading softly'),
    'MARICHA': ('మారీచుడు', 'old rakshasa, low and fearful, warning'),
    'KABANDHA': ('కబంధుడు (దివ్యరూపంలో)', 'freed celestial voice, grateful and clear, light echo'),
    'HANUMAN': ('హనుమంతుడు', 'strong, humble, joyful young voice'),
    'CHORUS': ('కోరస్', 'mixed devotional chorus, men and women, clear Sanskrit'),
    'KUSHALAVA':('కుశలవులు', 'two young boys singing together, sweet, clear, in tune'),
    'SAGES': ('మునులు', 'a few old sages together, joyful'),
}
TE = {   # Telugu names for the cast list (respectful forms in narration style)
    'NARADA': 'నారద మహర్షి', 'VALMIKI': 'వాల్మీకి మహర్షి', 'RAMA': 'శ్రీరాములవారు', 'SITA': 'సీతమ్మవారు',
    'LAKSHMANA': 'లక్ష్మణుడు', 'BHARATA': 'భరతుడు', 'DASHARATHA': 'దశరథ మహారాజు', 'KAUSALYA': 'కౌసల్యాదేవి',
    'KAIKEYI': 'కైకేయి', 'GUHA': 'గుహుడు', 'SUMANTRA': 'సుమంత్రుడు', 'VASHISHTHA': 'వసిష్ఠ మహర్షి',
    'VIRADHA': 'విరాధుడు', 'AGASTYA': 'అగస్త్య మహర్షి', 'SHURPANAKHA': 'శూర్పణఖ', 'KHARA': 'ఖరుడు',
    'RAVANA': 'రావణుడు – ఒకే తల (మామూలు సన్నివేశాలు)', 'RAVANA_TEN': 'రావణుడు – పది తలలు (కోపం, యుద్ధం, ముఖ్య ఘట్టాలు)', 'MARICHA': 'మారీచుడు', 'JATAYU': 'జటాయువు', 'KABANDHA': 'కబంధుడు', 'SHABARI': 'శబరి',
    'HANUMAN': 'హనుమంతుడు', 'SUGRIVA': 'సుగ్రీవుడు', 'DUNDUBHI': 'దుందుభి (కళేబరం)', 'VALI': 'వాలి', 'TARA': 'తార',
    'SAMPATI': 'సంపాతి', 'AKSHAKUMARA': 'అక్షకుమారుడు', 'NALA': 'నలుడు', 'VIBHISHANA': 'విభీషణుడు',
    'PUSHPAKA_VIMANA': 'పుష్పక విమానం', 'BHARADWAJA': 'భరద్వాజ మహర్షి', 'BRAHMA': 'బ్రహ్మదేవుడు',
}
STAGE_TE = {'S1': 'బాల్యం', 'S2': 'అయోధ్యలో యువరాజు', 'S3': 'వనవాసం మొదలు (నారచీరలు)',
            'S4': 'దండకారణ్యం నుండి లంక వరకు', 'S5': 'లంక తర్వాత, పట్టాభిషేకం'}
SPEAKS = {'NARADA': 'NARADA', 'VALMIKI': 'VALMIKI', 'BHARATA': 'BHARATA', 'MARICHA': 'MARICHA',
          'KABANDHA': 'KABANDHA', 'HANUMAN': 'HANUMAN', 'RAMA': 'RAMA', 'BRAHMA': 'BRAHMA'}


@soft
def ref_image_prompt(key, ep):
    look = LS.character(key, ep)
    if key in LS.OBJECTS:
        return ("Object reference image for film continuity: the object only, no people, the whole of it in view, "
                "centred, plain soft warm-grey studio background, even soft lighting, 16:9 frame. "
                f"Style: {LS.STYLE}. Object: {look}. {LS.RESPECT} No text, letters, logos or watermarks.")
    return ("Character reference image for film continuity: one character only, full body, standing, facing the "
            "camera, centred, plain soft warm-grey studio background, even soft lighting, calm expression, 16:9 frame. "
            f"Style: {LS.STYLE}. Character: {look}. {LS.RESPECT} No text, letters, logos or watermarks.")


def cast_sheet(v):
    """Every reference image the video needs, in order of first appearance, with scenes, shots and voice."""
    seen, n = {}, 0
    for si, sc in enumerate(v['scenes'], 1):
        for shot in sc['shots']:
            n += 1
            for k in cast(shot)[0]:
                r = ref_name(k, shot['ep'])
                c = seen.setdefault(r, {'ref': r, 'key': k, 'ep': shot['ep'], 'scenes': [], 'shots': []})
                if si not in c['scenes']:
                    c['scenes'].append(si)
                c['shots'].append(n)
    out = []
    for r, c in seen.items():
        stage = r[len(c['key']) + 1:] if r != c['key'] else ''
        sp = SPEAKS.get(c['key'])
        out.append({'ref': r, 'te': TE.get(c['key'], c['key'].title()) + (f" · {STAGE_TE.get(stage, stage)}" if stage else ''),
                    'scenes': c['scenes'], 'shots': c['shots'], 'prev': '',
                    'voice': f"{VOICES[sp][0]} – {VOICES[sp][1]}" if sp else '',
                    'prompt': ref_image_prompt(c['key'], c['ep'])})
    for c in out:   # a later look of the same person is made from the earlier one
        base = c['ref'].rsplit('_S', 1)[0]
        earlier = [x['ref'] for x in out if x['ref'] != c['ref'] and x['ref'].rsplit('_S', 1)[0] == base
                   and x['ref'] < c['ref'] and '_S' in c['ref']]
        if earlier:
            c['prev'] = earlier[-1]
        if c['ref'] == 'RAVANA_TEN':   # the ten heads carry the one-headed Ravana's face
            c['prev'] = 'RAVANA'
    order = {c['ref']: i for i, c in enumerate(out)}
    if 'RAVANA_TEN' in order and 'RAVANA' in order:   # make the one-headed look first
        out.insert(order['RAVANA_TEN'], out.pop(order['RAVANA']))
    return out


def cast_md(cs):
    rows = []
    for i, c in enumerate(cs, 1):
        rows.append(f"### {i}. {c['te']} · `{c['ref']}.png`\n\n"
                    f"- 🎬 దృశ్యాలు: {', '.join(map(str, c['scenes']))} · షాట్‌లు: {', '.join(map(str, c['shots']))}\n"
                    + (f"- 🗣 గొంతు: {c['voice']}\n" if c['voice'] else "- 🗣 మాటలు లేవు (కనిపిస్తారు మాత్రమే)\n")
                    + (f"- 📎 ముందు `{c['prev']}.png` జత చేసి \"same person, same face\" అని చెప్పండి; దుస్తులు, రూపం మార్పు మాత్రమే.\n"
                       if c['prev'] else '')
                    + f"\n```text\n{c['prompt']}\n```\n")
    return ("ముందు పాత్రలు, తర్వాత గొంతులు, ఆ తర్వాత కథ. ప్రతి పాత్రకు ఒక్కసారి రిఫరెన్స్ ఇమేజ్ చేసి "
            "`Long_Videos/_reference_images/` లో ఇచ్చిన పేరుతో సేవ్ చేయండి; ప్రతి షాట్‌లో 📎 ఉన్న ఇమేజ్‌లు జత చేయండి. "
            "ఆమోదించిన ఇమేజ్‌ను మార్చవద్దు.\n\n" + '\n'.join(rows))


MOTION = ('fly', 'flies', 'flying', 'descend', 'leap', 'arrow', 'run', 'fall', 'burn', 'fight', 'battle', 'rise',
          'rising', 'vanish', 'walk', 'charg', 'swoop', 'storm', 'flame', 'build', 'carry', 'glide', 'sing', 'weep')
def ref_name(key, ep):
    stage = LS.stage_of(key, ep) if key in LS.STAGES else None
    return f'{key}_{stage}' if stage else key


def speak_secs(text):
    return max(3, round(len(text.split()) / 2.1 + 0.8))


def mmss(s):
    return f'{s // 60}:{s % 60:02d}'


def parse(path):
    vid = {'scenes': []}
    scene = shot = None
    for raw in open(path, encoding='utf-8').read().split('\n'):
        line = raw.strip()
        if not line or line.startswith('#!'):
            continue
        if line.startswith('## '):
            title, refs, loc = [x.strip() for x in line[3:].split(' | ')]
            scene = {'title': title, 'refs': refs, 'loc': loc, 'shots': []}
            vid['scenes'].append(scene)
            shot = None
        elif line.startswith(('SUNO: ', 'SONGSTYLE: ')) and shot is None:   # scene-level music for Suno
            k, v = line.split(': ', 1)
            scene[k.lower()] = v
        elif line.startswith('SHOT '):
            refs, ep, pic, move, cam = [x.strip() for x in line[5:].split(' | ')]
            shot = {'refs': refs, 'ep': ep, 'pic': pic, 'move': move, 'cam': cam, 'audio': [], 'force': None}
            scene['shots'].append(shot)
        elif line in ('VIDEO', 'STILL'):
            shot['force'] = line.lower()
        elif re.match(r'^(TITLE|COVERS|NEXT|SONGNOTE): ', line):
            k, v = line.split(': ', 1)
            vid[k.lower()] = v
        else:
            key, text = line.split(': ', 1)
            if key == 'SEC':
                shot['sec'] = int(text)
            else:
                shot['audio'].append((key, text))
    return vid


def kind_of(shot):
    if shot['force']:
        return 'video' if shot['force'] == 'video' else 'image'
    text = (shot['pic'] + ' ' + shot['move']).lower()
    return 'video' if sum(text.count(w) for w in MOTION) >= 2 else 'image'


def cast(shot):
    keys = [k for k in LS.names_in(shot['pic']) if LS.character(k, shot['ep'])]
    return keys, [LS.character(k, shot['ep']) for k in keys]


@soft
def image_prompt(shot, loc):
    keys, looks = cast(shot)
    return ("Cinematic 16:9 film still, 1920x1080, main subject well framed with room around it. "
            f"Style: {LS.STYLE}. Setting: {loc}. "
            + (f"Characters (keep exactly this look; attach their reference images): {' '.join(x + '.' for x in looks)} " if looks else '')
            + f"Scene: {shot['pic']} Rich cinematic colour, real light and atmosphere, high detail. "
            "Correct anatomy and natural hands; no extra characters, limbs or faces beyond those described. "
            f"{LS.RESPECT} No text, letters, subtitles, logos or watermarks.")


@soft
def video_prompt(shot, loc, kind):
    keys, looks = cast(shot)
    act = (f"Action, slow and cinematic: 0–2 s hold the start frame; 2–6 s {shot['move']}; 6–8 s settle and hold."
           if kind == 'video' else
           f"Only gentle life: {shot['move']}; breathing, a slow blink, cloth and leaves stirring in the breeze.")
    return ("Animate the attached start frame as one continuous 8 second cinematic 16:9 shot. The start frame is the "
            "exact look of the whole video: keep its style, colours, light, faces, clothes and framing; do not "
            "redesign anything and do not add or remove anyone; only bring it to life with motion. "
            f"Style: {LS.STYLE}. Setting: {loc}. "
            + (f"Characters (keep exactly this look): {' '.join(x + '.' for x in looks)} " if looks else '')
            + f"The frame shows: {shot['pic']} {act} Camera: {shot['cam']}; smooth, no shake, no sudden zoom. "
            "Every character keeps the same face, hair, clothes, ornaments and size for the whole shot; one "
            "continuous shot, no cuts; physically consistent motion with no morphing or flicker. Correct anatomy and "
            f"natural hands. {LS.RESPECT} {LS.TAIL}")


ICON = {'N': '🎙', 'D': '🗣', 'SONG': '🎶', 'M': '🎵', 'FX': '🔊', 'CAP': '🔤'}


def audio_md(key, text):
    if key == 'N':
        return f"🎙 **కథకుడు:** {text}"
    if key.startswith('D '):
        return f"🗣 **{VOICES[key[2:]][0]}:** {text}"
    if key.startswith('SONG '):
        return f"🎶 **పాట – {VOICES[key[5:]][0]}:** {text}"
    return f"{ICON[key]} **{dict(M='సంగీతం', FX='శబ్దాలు', CAP='తెరపై')[key]}:** {text}"


def build(src):
    v = parse(src)
    t, n, out, voice, music, prompts, page = 0, 0, [], [], [], [], []
    for si, sc in enumerate(v['scenes'], 1):
        out.append(f"\n### దృశ్యం {si} · {sc['title']} · {sc['refs']}\n")
        for shot in sc['shots']:
            n += 1
            spoken = [speak_secs(x) * (3 if k.startswith('SONG ') else 1)   # a sung śloka is slow
                      for k, x in shot['audio'] if k == 'N' or k.startswith(('D ', 'SONG '))]
            sec = shot.get('sec') or (sum(spoken) if spoken else 6)
            kind = kind_of(shot)
            keys, _ = cast(shot)
            mode = ('🎶 పాట' if any(k.startswith('SONG') for k, _ in shot['audio']) else
                    '🗣 మాటలు' if any(k.startswith('D ') for k, _ in shot['audio']) else
                    '🎙 కథనం' if any(k == 'N' for k, _ in shot['audio']) else '🎵 సంగీతం మాత్రమే')
            head = f"**షాట్ {n}** · {mmss(t)}–{mmss(t + sec)} · {mode} · {'🎥 వీడియో' if kind == 'video' else '🖼️ ఇమేజ్ + కదలిక'} · శ్లో. {shot['refs']}"
            out.append(head + '\n\n' + '\n'.join(f"- {audio_md(k, x)}" for k, x in shot['audio'])
                       + f"\n- 🎬 **దృశ్యం:** {shot['pic']}\n")
            for k, x in shot['audio']:
                if k == 'N' or k.startswith(('D ', 'SONG ')):
                    who = 'N' if k == 'N' else k.split(' ', 1)[1]
                    voice.append(f"[{mmss(t)}] {VOICES[who][0]}{' (పాట)' if k.startswith('SONG') else ''}: {x}")
                elif k in ('M', 'FX'):
                    music.append(f"| {mmss(t)} | {'సంగీతం' if k == 'M' else 'శబ్దం'} | {x} |")
            refs = ' · '.join(f'`{ref_name(k, shot["ep"])}.png`' for k in keys) or 'అవసరం లేదు'
            prompts.append(f"#### షాట్ {n} · {mmss(t)} · {'🎥 వీడియో' if kind == 'video' else '🖼️ ఇమేజ్'}\n\n"
                           f"- **రిఫరెన్స్ (Long_Videos/_reference_images):** {refs}\n\n"
                           f"**🖼️ ఇమేజ్ ప్రాంప్ట్:**\n\n```text\n{image_prompt(shot, sc['loc'])}\n```\n\n"
                           f"**🎥 వీడియో ప్రాంప్ట్** (Frames to Video – పై ఇమేజ్ మొదటి ఫ్రేమ్):\n\n"
                           f"```text\n{video_prompt(shot, sc['loc'], kind)}\n```\n")
            if not page or page[-1]['si'] != si:
                page.append({'si': si, 'title': f"{si}. {sc['title']}", 'sr': sc['refs'], 'start': mmss(t),
                             'suno': sc.get('suno', ''), 'songstyle': sc.get('songstyle', ''), 'shots': []})
            page[-1]['shots'].append({
                         'no': n, 'time': f'{mmss(t)}–{mmss(t + sec)}', 'sec': sec,
                         'mode': mode, 'kind': kind, 'refs': shot['refs'], 'pic': shot['pic'],
                         'lines': [{'who': VOICES['N' if k == 'N' else k.split(' ', 1)[1]][0], 'text': x,
                                    'song': k.startswith('SONG ')}
                                   for k, x in shot['audio'] if k == 'N' or k.startswith(('D ', 'SONG '))],
                         'music': [x for k, x in shot['audio'] if k == 'M'],
                         'fx': [x for k, x in shot['audio'] if k == 'FX'],
                         'cap': [x for k, x in shot['audio'] if k == 'CAP'],
                         'img': image_prompt(shot, sc['loc']), 'vid': video_prompt(shot, sc['loc'], kind),
                         'ref': [ref_name(k, shot['ep']) for k in keys]})
            t += sec
    name = os.path.splitext(os.path.basename(src))[0]
    kanda = os.path.basename(os.path.dirname(src))
    cast_lines = sorted({line.split(': ', 1)[0].split('] ', 1)[1].replace(' (పాట)', '') for line in voice})
    cs = cast_sheet(v)
    md = (f"# {v['title']}\n\n"
          f"**కథ:** {v['covers']} · **నిడివి:** సుమారు {mmss(t)} · **షాట్‌లు:** {n} · **తరువాత:** {v['next']}\n\n"
          "**ఈ ఫైల్‌లో:** 1. పాత్రలు (రిఫరెన్స్ ఇమేజ్‌లు) · 2. గొంతులు & వాయిస్ స్క్రిప్ట్ · 3. స్క్రీన్‌ప్లే (కథ, షాట్ వారీగా) · "
          "4. సంగీతం & శబ్దాల క్యూ షీట్ · 5. ఇమేజ్ & వీడియో ప్రాంప్ట్‌లు\n\n"
          f"## 1. పాత్రలు ({len(cs)} రిఫరెన్స్ ఇమేజ్‌లు)\n\n" + cast_md(cs) + "\n\n"
          "## 2. గొంతులు & వాయిస్ స్క్రిప్ట్ (రికార్డింగ్ కోసం)\n\n"
          "**గొంతులు:**\n\n" + '\n'.join(f"- **{VOICES[k][0]}:** {VOICES[k][1]}" for k in VOICES if VOICES[k][0] in cast_lines)
          + "\n\n```text\n" + '\n\n'.join(voice) + "\n```\n\n"
          "## 3. స్క్రీన్‌ప్లే (కథ)\n" + '\n'.join(out) + "\n\n"
          "## 4. సంగీతం & శబ్దాల క్యూ షీట్\n\n" + (f"{v['songnote']}\n\n" if v.get('songnote') else '')
          + "| సమయం | రకం | క్యూ |\n|---|---|---|\n" + '\n'.join(music) + "\n\n"
          "## 5. ఇమేజ్ & వీడియో ప్రాంప్ట్‌లు (16:9)\n\n"
          "ముందు 🖼️ ఇమేజ్ చేయండి (రిఫరెన్స్ ఇమేజ్‌లు జత చేసి). 🎥 షాట్‌లకు ఆ ఇమేజ్‌ను Flow → Frames to Video లో "
          "మొదటి ఫ్రేమ్‌గా పెట్టి వీడియో ప్రాంప్ట్ వాడండి; 🖼️ షాట్‌లకు ఇమేజ్ + ఎడిటర్‌లో నెమ్మది జూమ్/ప్యాన్ చాలు "
          "(కావాలంటే వీడియో కూడా చేయవచ్చు).\n\n" + '\n'.join(prompts))
    dst = os.path.join(CINEMA, kanda, name + '.md')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8', newline='\n').write(md)
    data = {'title': v['title'], 'covers': v['covers'], 'next': v['next'], 'length': mmss(t), 'songnote': v.get('songnote', ''),
            'voices': [[VOICES[k][0], VOICES[k][1]] for k in VOICES if VOICES[k][0] in cast_lines],
            'voice': '\n\n'.join(voice), 'cast': cs, 'scenes': page}
    tpl = open(os.path.join(HERE, 'page_template.html'), encoding='utf-8').read()
    html = tpl.replace('__TITLE__', v['title'].split(' | ')[0]).replace(
        '__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    pub = os.path.join(CINEMA, 'publish', f'{kanda}_{name}.html')
    os.makedirs(os.path.dirname(pub), exist_ok=True)
    open(pub, 'w', encoding='utf-8', newline='\n').write(html)
    with open(pub.replace('.html', '_open_on_pc.html'), 'w', encoding='utf-8', newline='\n') as f:   # double-click copy
        f.write('<!DOCTYPE html><html lang="te"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + html + '</body></html>')
    print(f'{os.path.relpath(dst, CINEMA)}: {n} shots, {mmss(t)}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        build(p)
