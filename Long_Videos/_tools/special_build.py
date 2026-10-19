"""Special sloka videos (Long_Videos/Special/): one theme per video, e.g. slokas for expecting mothers.

    cd Long_Videos/_tools && python -X utf8 special_build.py data/special/01_Garbha_Sanskaram.txt

Input: a header (KEY: value lines), then the video's items, then '=== SHORT' and the Short's items. An item:

    @ id | kind | label | ep | on-screen text
    VISUAL: what the clip shows (character names pull in their looks, as in the long videos)
    MEANING: (slokas only) the meaning shown under the sloka card
    the narration, or for kind 'verse' the sloka itself (half-lines end with । or ॥)

kind: video | image | verse | intro. ids starting with B open a YouTube chapter (title = on-screen text).
Output: Long_Videos/Special/<NAME>/VIDEO.md, SHORT.md, VIDEO.srt, tts/VIDEO.txt, tts/SHORT.txt
"""
import os
import re
import sys

import long_build as L
import tts

SPECIAL = os.path.join(L.LONG, 'Special')
CHANT_PACE = 1.8     # a sloka is chanted slower than narration


def read(path):
    head, parts, cur, item = {}, {'VIDEO': [], 'SHORT': []}, 'VIDEO', None
    for line in open(path, encoding='utf-8').read().split('\n'):
        if line.startswith('#') and not line.startswith('##'):
            continue
        if line.strip() == '=== SHORT':
            cur, item = 'SHORT', None
            continue
        if line.startswith('@ '):
            f = [x.strip() for x in line[2:].split('|')]
            f += [''] * (5 - len(f))
            item = {'id': f[0], 'kind': f[1], 'label': f[2], 'ep': f[3] or 'E1.18', 'onscreen': f[4],
                    'visual': '', 'meaning': '', 'text': []}
            parts[cur].append(item)
            continue
        if item is None:
            if ': ' in line:
                k, v = line.split(': ', 1)
                head[k.strip()] = v.strip()
            continue
        if line.startswith('VISUAL: '):
            item['visual'] = line[8:].strip()
        elif line.startswith('MEANING: '):
            item['meaning'] = line[9:].strip()
        elif line.strip():
            item['text'].append(line.strip())
    for items in parts.values():
        for x in items:
            x['narration'] = ('\n' if x['kind'] == 'verse' else ' ').join(x.pop('text'))
            verse = x['kind'] == 'verse'
            x['secs'] = (round(L.speak_secs(x['narration']) * CHANT_PACE) if verse
                         else L.BUMPER if x['kind'] == 'intro' else L.speak_secs(x['narration']))
            x['new'] = True
            x['scene'] = {'verse': verse}
            x['id'] = 'I' if x['kind'] == 'intro' else x['id']
    return head, parts


def prompt(x):
    if x['kind'] == 'intro':
        return 'Use the channel intro clip (already made once for all videos).'
    scene = {'visual': x['visual'], 'loc': ''}
    looks, refs = L.scene_cast(scene, x['ep'])
    kind = 'video' if x['kind'] == 'video' else 'image'
    return L.scene_prompt(scene, kind, looks), refs


def mmss(s):
    return f'{s // 60}:{s % 60:02d}'


def voice(items):
    return tts.pieces(tts.paragraphs(items))


def tts_file(items):
    labels = {'text': '🗣️ నెరేషన్', 'verse': '🕉️ శ్లోకం (నెమ్మదిగా, ప్రశాంతంగా)', 'intro': '🎵 ఇంట్రో (00_INTRO.txt)'}
    return '\n\n'.join(f'===== {i}. {labels[k]} =====\n\n{v}' for i, (k, v) in enumerate(voice(items), 1)) + '\n'


def script_md(items, title):
    out, t = [f'# {title}\n'], 0
    for n, x in enumerate(items, 1):
        x['start'] = t
        t += x['secs']
        if x['kind'] == 'intro':
            out.append(f"### {n}. {mmss(x['start'])} · {x['label']}\n\nఛానల్ ఇంట్రో క్లిప్ ({x['secs']} సె).\n")
            continue
        p, refs = prompt(x)
        card = ''
        if x['kind'] == 'verse':
            card = (f"\n- **తెరపై:** శ్లోకం తెలుగు లిపిలో, అక్షరం అక్షరం కనిపిస్తూ · కింద అర్థం: {x['meaning']}\n"
                    "- **ఆడియో:** ElevenLabs లో ఈ శ్లోకం విడిగా చేయండి (లేదా మీ గొంతులో); ముందు, తరువాత 1 సెకను నిశ్శబ్దం.")
        elif x['onscreen']:
            card = f"\n- **తెరపై టెక్స్ట్:** «{x['onscreen']}»"
        ref = f"\n- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in refs)}" if refs else ''
        body = x['narration'].replace('\n', '  \n')
        out.append(f"### {n}. {mmss(x['start'])} · {x['label']} · {'🎥 వీడియో' if x['kind'] == 'video' else '🖼️ ఇమేజ్'} "
                   f"· {x['secs']} సె\n\n- **నెరేషన్:** {body}{card}{ref}\n\n```text\n{p}\n```\n")
    return '\n'.join(out), t


def srt(items):
    cues, t = [], 0
    for x in items:
        if x['narration'] and x['kind'] != 'intro':
            cues.append((t, t + x['secs'], x['narration']))
        t += x['secs']
    return '\n'.join(f'{i}\n{L.srt_time(a)} --> {L.srt_time(b)}\n{s}\n' for i, (a, b, s) in enumerate(cues, 1))


def main(path):
    head, parts = read(path)
    name = head['NAME']
    out = os.path.join(SPECIAL, name)
    os.makedirs(os.path.join(out, 'tts'), exist_ok=True)
    video, short = parts['VIDEO'], parts['SHORT']
    body, total = script_md(video, head['TITLE'])
    chapters = [(0, head.get('FIRST_CHAPTER', 'పరిచయం'))] + [
        (x['start'], x['onscreen']) for x in video if x['id'].startswith('B')]
    for (a, c), (b, _) in zip(chapters, chapters[1:] + [(total, '')]):
        assert b - a >= 10, f'chapter "{c}" is only {b - a}s'
    verses = [x for x in video if x['kind'] == 'verse']
    md = [f"# {head['TITLE']}\n",
          f"**నిడివి:** {mmss(total)} · **శ్లోకాలు:** {len(verses)} · ElevenLabs టెక్స్ట్: `tts/VIDEO.txt` · క్యాప్షన్లు: `VIDEO.srt`\n",
          f"> {head['NOTE']}\n" if head.get('NOTE') else '',
          '## శ్లోకాలు – మూలం, అర్థం\n',
          *[f"**{x['label']}**\n\n```text\n{x['narration']}\n```\n{x['meaning']}\n" for x in verses],
          '## అప్‌లోడ్\n',
          f"- **టైటిల్:** {head['TITLE']}",
          f"- **థంబ్‌నెయిల్ టెక్స్ట్:** {head['HEAD']}",
          f"- **థంబ్‌నెయిల్ ప్రాంప్ట్:**\n\n```text\n{head['THUMB']} Style: {L.STYLE}. {L.RESPECT} "
          'Leave clean space on the left third for a large Telugu title added later. No text in the image.\n```\n',
          '- **వివరణ:**\n\n```text\n' + head['DESC'] + '\n\n' +
          '\n'.join(f'{mmss(a)} {c}' for a, c in chapters) + '\n\n' + head['DISCLAIMER'] + '\n\n' +
          f"{head.get('TAGS', '')} {L.HASHTAGS}\n```\n",
          f"- **పిన్ కామెంట్:** {head['PIN']}\n",
          '## రికార్డింగ్ + క్లిప్‌లు\n', body]
    open(os.path.join(out, 'VIDEO.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    open(os.path.join(out, 'VIDEO.srt'), 'w', encoding='utf-8', newline='\n').write(srt(video))
    open(os.path.join(out, 'tts', 'VIDEO.txt'), 'w', encoding='utf-8', newline='\n').write(tts_file(video))
    sbody, stotal = script_md(short, head['SHORT_TITLE'])
    open(os.path.join(out, 'SHORT.md'), 'w', encoding='utf-8', newline='\n').write(
        f"# {head['SHORT_TITLE']}\n\n**నిడివి:** {mmss(stotal)} (9:16 నిలువుగా కట్ చేయండి) · ElevenLabs: `tts/SHORT.txt`\n\n"
        f"- **వివరణ:** {head['SHORT_DESC']} {head['DISCLAIMER']} #shorts {L.HASHTAGS}\n\n## రికార్డింగ్ + క్లిప్‌లు\n\n" + sbody)
    open(os.path.join(out, 'tts', 'SHORT.txt'), 'w', encoding='utf-8', newline='\n').write(tts_file(short))
    assert stotal <= 60, f'Short is {stotal}s'
    print(f'{name}: video {mmss(total)} ({len(video)} items, {len(verses)} slokas), short {stotal}s')


if __name__ == '__main__':
    main(sys.argv[1])
