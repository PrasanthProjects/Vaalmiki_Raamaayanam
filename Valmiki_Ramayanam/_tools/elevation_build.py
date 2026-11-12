# -*- coding: utf-8 -*-
"""రామాయణ వైభవం – a separate Shorts series of the Ramayana's mightiest, best-known moments (user, 2026-11-11):
no śloka on screen, 20–30 seconds each, high visuals and action (drone, fly-through, follow-the-arrow, zoom, crane),
for Rama, Hanuman, Vishwamitra, Jatayu, Angada, Lakshmana and others, and each Short's own high-energy music.

Every fact is checked against Valmiki (sarga named per Short; Gita Press numbers may differ by a few).
No folk additions (no names on the setu stones, no Angada's-foot challenge, no Hanuman's chest), no morph or
growth shots (characters are already in their form at the start of a clip), soft prompt words only.

    python elevation_build.py   ->  ../Ramayana_Vaibhavam/Short_NN.md  and  publish/ramayana_vaibhavam.html
"""
import json
import re
import os

import live_style as LS
from soften import soften

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'Ramayana_Vaibhavam')
CTA = {'r': '"జై శ్రీరామ్" అని కామెంట్ చేసి, షేర్ చేయండి!', 'h': '"జై హనుమాన్" అని కామెంట్ చేసి, షేర్ చేయండి!',
       'l': 'లైక్ చేసి, సబ్‌స్క్రైబ్ చేయండి!', 's': 'మీ వాళ్ళకి షేర్ చేసి, సబ్‌స్క్రైబ్ చేయండి!'}
EXCLUDE = 'vocals, singing, lyrics, choir words, rap, EDM, dubstep, western pop, film song, trailer voice'
from elevation_data import MUSIC, SHORTS

RATE = 11.37    # Telugu letters per second: Vagmin (ElevenLabs v3), gaps cut to 0.12 s, tempo 1.05; Short 4 = 35.1 s


def letters(text):
    return len(re.sub(r'[^ఀ-౿]', '', text))


def spoken(sh):
    """Each row's spoken line."""
    return [r[5] for r in sh['rows']]      # no CTA in the voice (user, 2026-11-12): it ends on the punch line


def timing(sh):
    """Length from the lines (30-50 s) and each clip's slot in proportion to its line, so pictures follow the voice."""
    lines = spoken(sh)
    need = [letters(x) / RATE for x in lines]
    total = max(25, round(sum(need)))
    assert total <= 50, (sh['n'], total)
    cuts, acc = [0], 0.0
    for x in need:
        acc += x
        cuts.append(round(acc * total / sum(need)))
    return total, [(cuts[i], cuts[i + 1]) for i in range(len(lines))]


def label(i, n):
    return 'హుక్' if i == 0 else ('పంచ్ & ముగింపు' if i == n - 1 else f'దృశ్యం – {i}')


def music_prompt(sh):
    total, slots = timing(sh)
    peak = next((slots[i][0] for i, r in enumerate(sh['rows']) if len(r) > 6), slots[-2][0])
    return ('High-energy instrumental hero-elevation background score in the style of big South Indian mythological action '
            'films (original music, no copying of any film), no vocals and no words: massive dhol, thavil and war-drum hits, '
            'heavy cinematic brass, a fierce heroic nadaswaram and shehnai lead, punchy sub-bass hits and risers, a fast '
            f'driving string ostinato; energetic from the very first second, no slow or sad intro; {sh["music"]}; '
            f'the biggest drop and hit at about {peak} seconds; about {total} seconds long, ending on a huge heroic hit.')


def short_page(sh):
    rows, n = sh['rows'], len(sh['rows'])
    total, slots = timing(sh)
    sh['L'] = total
    clips = []
    for i, ((a, b), row, said) in enumerate(zip(slots, rows, spoken(sh))):
        keys, frame, motion, cam, light = row[:5]
        ks = [k.strip() for k in keys.split(',') if k.strip()]
        frame, hook, lab = frame.rstrip('.') + '.', i == 0, label(i, n)
        light = light.rstrip('. ') + '.'
        vid = soften(LS.two_frame_video(ks, frame, motion, cam, light, True, hook=hook))
        clips.append({
            'no': i + 1, 'time': f'{a // 60}:{a % 60:02d} – {b // 60}:{b % 60:02d}', 'label': lab, 'kind': 'video',
            'narration': said,
            'refs': LS.ref_keys(ks), 'move': cam,
            'imagePrompt': soften(LS.still(ks, frame, light, lab, motion=motion, cam=cam)),
            'endImagePrompt': soften(LS.end_still(ks, frame, motion, cam, light, True, lab, hook=hook)),
            'videoPrompt': vid, 'prompt': vid})
    tk, tf, tl = sh['thumb']
    tprompt, trefs = LS.thumb([k.strip() for k in tk.split(',') if k.strip()], tf.rstrip('.') + '.', tl)
    title = f"{sh['title']} | రామాయణ వైభవం"
    assert len(title) <= 100, (sh['n'], len(title))
    tags = '#రామాయణవైభవం #JaiShreeRam ' + ('#JaiHanuman ' if sh['cta'] == 'h' else '') + '#ValmikiRamayanam #TeluguShorts'
    desc = (f"{sh['title']}\n\n" + '\n'.join(r[5] for r in rows) +
            f"\n\n📖 మూలం: వాల్మీకి రామాయణం, {sh['src']}\n🎼 దృశ్యాలు, సంగీతం AI సాయంతో; కథ వాల్మీకి రామాయణం ప్రకారం.\n{tags}")
    return {'n': sh['n'], 'headline': sh['headline'], 'hl': sh['hl'], 'sub': sh['sub'],
            'badge': f"రామాయణ వైభవం · {sh['n']} · {sh['L']} సెకన్లు · {sh['src']}", 'title': title, 'sloka': [], 'reading': None,
            'clips': clips, 'thumbPrompt': soften(tprompt), 'thumbRefs': list(trefs), 'desc': desc,
            'pinned': 'రామాయణంలో మీకు ఏ ఘట్టం ఇష్టం? కామెంట్‌లో రాయండి, తరువాతి Shorts లో చూపిస్తాం! 🙏', 'srt': ''}


def voice_script(sh):
    """The whole Short for ElevenLabs v3 in one take: tone tag per line, never [excited] (it laughs)."""
    out = []
    for i, (r, line) in enumerate(zip(sh['rows'], spoken(sh))):
        tag = '[intense]' if i == 0 or len(r) > 6 else '[confident]'      # energetic throughout; never [excited] (laughs)
        out.append(f'{tag} {line}')
    return ' '.join(out)     # one flowing paragraph: no long gaps between lines


def main():
    pages = [short_page(sh) for sh in SHORTS]
    music = {'exclude': EXCLUDE,
             'moods': {f"e{sh['n']}": {'label': f"🔥 {sh['n']}. {sh['sub']} – వాడేది: Ramayana_Vaibhavam/music/{MUSIC[sh['n']]}.mp3 (కొత్తది కావాలంటే కింది Suno ప్రాంప్ట్)",
                                       'prompt': music_prompt(sh)} for sh in SHORTS},
             'of': {str(sh['n']): f"e{sh['n']}" for sh in SHORTS}}
    eleven = {str(sh['n']): {'voice1': voice_script(sh)} for sh in SHORTS}
    used = sorted({r for p in pages for c in p['clips'] for r in c['refs']} | {r for p in pages for r in p['thumbRefs']})
    data = {'key': 'ramayana_vaibhavam', 'name': 'రామాయణ వైభవం – Shorts', 'slokas': pages,
            'clipsNote': ('శ్లోకం లేదు – రామాయణంలోని గొప్ప ఘట్టాలు, 30–50 సెకన్లు. ప్రతి క్లిప్ వీడియో: మొదటి ఇమేజ్ → చివరి ఇమేజ్ → వీడియో. '
                          'డ్రోన్, ఎగిరే, బాణం వెంట, జూమ్ కెమెరా ప్రతి క్లిప్‌లో రాసి ఉంది. ప్రతి Short కి దాని సొంత సంగీతం (Suno).'),
            'refs': LS.library(used), 'music': music, 'eleven': eleven,
            'elevenTitle': '🎙 ElevenLabs వాయిస్ – మొత్తం Short ఒకే టేక్ (కాపీ చేసి Generate చేయండి)',
            'elevenNote': ('గొంతు: Vagmin (ZoV3Y9cqdke2p8nzz7XP), మోడల్ Eleven v3, Stability: Natural. [ ] లోని ఇంగ్లీష్ సూచనలు చదవబడవు. '
                           'చివర్లో కామెంట్/సబ్‌స్క్రైబ్ మాట లేదు. కంప్యూటర్‌లో: python elevation_voice.py <నంబర్> Vagmin – మాటలన్నీ చెక్ చేసి, '
                           'ఖాళీలు తీసేసి, హీరో మ్యూజిక్‌తో MIX కూడా Ramayana_Vaibhavam/voice/ లో పెడుతుంది.'),
            'elevenParts': [['voice1', 'మొత్తం Short – ఒకే టేక్']]}
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tpl = open(os.path.join(HERE, 'flow_helper_live_template.html'), encoding='utf-8').read()
    frag = tpl.replace('__TITLE__', 'రామాయణ వైభవం Shorts').replace('__DATA__', blob)
    os.makedirs(os.path.join(HERE, 'publish'), exist_ok=True)
    open(os.path.join(HERE, 'publish', 'ramayana_vaibhavam.html'), 'w', encoding='utf-8', newline='\n').write(frag)
    os.makedirs(OUT, exist_ok=True)
    for sh, p in zip(SHORTS, pages):
        md = [f"# రామాయణ వైభవం {sh['n']} · {sh['headline']} ({sh['L']} సెకన్లు)", '', f"📖 {sh['src']}", '',
              f"**సంగీతం (Suno, Instrumental):** {music_prompt(sh)}  ", f"**Exclude:** {EXCLUDE}", '']
        for c in p['clips']:
            md += [f"## {c['no']}. {c['label']} · {c['time']}", '', f"**మాట:** {c['narration']}", '', f"**కెమెరా:** {c['move']}", '',
                   f"**రిఫరెన్స్:** {', '.join(c['refs']) or '– (ప్రాంప్ట్‌లో వర్ణన ఉంది)'}", '',
                   '**1. మొదటి ఇమేజ్**', '```text', c['imagePrompt'], '```', '**2. చివరి ఇమేజ్**', '```text', c['endImagePrompt'], '```',
                   '**3. వీడియో**', '```text', c['videoPrompt'], '```', '']
        md += ['## థంబ్‌నెయిల్', '', f"**{sh['headline']}** ({sh['hl']} పసుపు) · {sh['sub']}", '```text', p['thumbPrompt'], '```', '',
               '## YouTube', '', '```text', p['title'], '```', '```text', p['desc'], '```']
        open(os.path.join(OUT, f"Short_{sh['n']:02d}.md"), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print(len(pages), 'Shorts,', sum(len(p['clips']) for p in pages), 'clips;', 'unknown refs:',
          sorted({k.strip() for sh in SHORTS for r in sh['rows'] for k in r[0].split(',') if k.strip()} - set(LS.LIB)))


if __name__ == '__main__':
    main()
