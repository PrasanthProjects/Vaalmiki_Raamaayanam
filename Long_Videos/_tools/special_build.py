# -*- coding: utf-8 -*-
"""Special long videos (films vs Valmiki): data/special/07_cinema_vs_valmiki.py -> Long_Videos/Special/07_Cinema_vs_Valmiki/
(P1.md, P2.md, tts, captions) and publish/special_cinema_vs_valmiki.html (the clips page).

Each clip gets the same three prompts as the kaanda videos (start image, end image, Frames-to-Video), with the Shorts'
characters and reference images (long_build with SHORTS_LOOKS). Run:  python special_build.py
"""
import importlib.util
import json
import os

import long_build as L
import tts
from long_build import BUMPER, OUTRO, HASHTAGS, mmss

DATA = os.path.join(L.TOOLS, 'data', 'special', '07_cinema_vs_valmiki.py')
OUT = os.path.join(L.ROOT, 'Long_Videos', 'Special', '07_Cinema_vs_Valmiki')
FILM = '🎬 సినిమాల్లో'
VALMIKI = '📜 వాల్మీకి రామాయణంలో'


def load():
    spec = importlib.util.spec_from_file_location('special', DATA)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PARTS


def items_of(part):
    """The part as clips in story order: (id, label, kind, visual, ep, narration, onscreen, verse)."""
    # 2-3 quick hook scenes (pictures only), the channel intro, then the user on camera (welcome), then the story
    out = [dict(id=f'H{j}', label=f'హుక్ {j}', kind='video', visual=h['visual'] + '; ' + h['move'], ep=h['ep'],
                text=h['text'], onscreen=h['text'].split('?')[0] + '?' if '?' in h['text'] else part['headline'])
           for j, h in enumerate(part['hooks'], 1)]
    out += [dict(id='I', label='ఛానల్ ఇంట్రో', kind='intro', text=tts.INTRO),
            dict(id='G', label='స్వాగతం · 📹 మీరు కెమెరాలో', kind='image', visual=part['welcome']['visual'],
                 ep=part['welcome']['ep'], text=part['welcome']['text'], onscreen='', cam=True),
            dict(id='W', label='పరిచయం', kind='image', visual=part['intro']['visual'], ep=part['intro']['ep'],
                 text=part['intro']['text'], onscreen='')]
    for t, top in enumerate(part['topics'], 1):
        out.append(dict(id=f'T{t}', label=f'అంశం {t} · శీర్షిక', kind='image', visual=top['title_visual'], ep=top['ep'],
                        text=top['title'], onscreen=f"{t}. {top['title']}", chapter=top['title']))
        f = top['film']
        out.append(dict(id=f'T{t}F', label=f'అంశం {t} · {FILM}', kind='image', visual=f['visual'], ep=top['ep'],
                        text=f['text'], onscreen=FILM, film=True))
        for j, v in enumerate(top['valmiki'], 1):
            kind = 'video' if v.get('move') else 'image'
            out.append(dict(id=f'T{t}V{j}', label=f'అంశం {t} · {VALMIKI}', kind=kind,
                            visual=v['visual'] + ('; ' + v['move'] if v.get('move') else ''), ep=v.get('ep', top['ep']),
                            text=v['text'], onscreen=f"{VALMIKI} · {top['ref']}" if j == 1 else ''))
        if top.get('sloka'):
            out.append(dict(id=f'T{t}S', label=f"అంశం {t} · 🕉️ శ్లోకం", kind='image',
                            visual='An ancient palm-leaf manuscript open on a carved wooden stand beside a lit brass oil lamp, soft golden light, flower petals and a little incense smoke around it, close-up; no people',
                            ep=top['ep'], text=top['sloka'], verse=True,
                            onscreen=f"🕉️ {top['sloka']} — {top['sloka_ref']}"))
    out.append(dict(id='C', label='ముగింపు', kind='image', visual=part['outro']['visual'], ep=part['outro']['ep'],
                    text=part['outro']['text'], onscreen='', chapter='ముగింపు'))
    return out


def secs_of(it):
    if it['kind'] == 'intro':
        return BUMPER
    return L.speak_secs(it['text']) + (3 if it.get('verse') else 0)


def build(n, part, refs_used):
    items = items_of(part)
    t, cards, md_items, chap, srt_rows = 0, [], [], [(0, 'పరిచయం')], []
    for k, it in enumerate(items, 1):
        secs = secs_of(it)
        it['start'] = t
        if it.get('chapter'):
            chap.append((t, it['chapter']))
        if it['kind'] != 'intro':
            srt_rows.append((t, t + secs, tts.clean(it['text']) if not it.get('verse') else it['text']))
        card = {'no': str(k), 'time': f'{mmss(t)} – {mmss(t + secs)}', 'label': f"{it['label']} · {secs} సె",
                'kind': 'video' if it['kind'] in ('video', 'intro') else 'image', 'narration': it['text'], 'refs': [],
                'move': '', 'note': '', 'advice': ''}
        t += secs
        if it['kind'] == 'intro':
            card['note'] = 'ఛానల్ ఇంట్రో క్లిప్ – ఒక్కసారే చేసినది ఇక్కడ పెట్టండి (ప్రాంప్ట్ అవసరం లేదు).'
            cards.append(card)
            md_items.append(f"#### {k}. {it['label']} · {card['time']}\n\n- ఒక్కసారే చేసిన ఇంట్రో క్లిప్ ఇక్కడ.\n")
            continue
        s = {'visual': it['visual'], 'loc': ''}
        looks, refs = L.scene_cast(s, it['ep'])
        if it.get('film'):   # the film's own look (e.g. a "beautiful" rakshasi, a bird with arms): no reference image
            looks, refs = [], []
        refs_used.update(refs)
        kind = card['kind']
        notes = []
        if it['onscreen']:
            notes.append(f"తెరపై టెక్స్ట్: «{it['onscreen']}»")
        if it.get('cam'):
            notes.append('📹 ఈ భాగం మీరు కెమెరాలో చెప్పేది (Video Maker → ప్రెజెంటర్). మీ వీడియో లేకపోతే ఈ చిత్రం + వాయిస్ వస్తాయి.')
        if it.get('film'):
            notes.append('సినిమా వెర్షన్ – అదే 3D శైలిలో చేయండి; మూలలో «🎬 సినిమాల్లో» బ్యాడ్జ్. ఏ సినిమా పేరు, నటుల ముఖాలు వద్దు.')
        if it.get('verse'):
            notes.append('శ్లోకం తెరపై పెద్ద అక్షరాలతో; నెమ్మదిగా, శ్రావ్యంగా చదవండి (కింద తంబుర).')
        if kind == 'video' and secs > 8:
            notes.append(f'Flow 8 సెకన్లు ఇస్తుంది; మిగిలిన {secs - 8} సె చివరి ఫ్రేమ్‌ను నెమ్మది జూమ్‌తో పట్టుకోండి.')
        card.update(refs=refs, note=' '.join(notes),
                    move='' if kind == 'video' else L.editor_move(it['visual'], k) + ' (వీడియో చేయకపోతే)',
                    advice=L.advice(it['visual'], kind, it['id'] if it['id'] in ('W', 'C') else 'x'),
                    imagePrompt=L.scene_prompt(s, 'image', looks, opening=(kind == 'video'), refs=refs),
                    endImagePrompt=L.end_prompt(s, kind, looks, k, refs=refs), videoPrompt=L.video_prompt(s, kind, looks, k, refs=refs))
        cards.append(card)
        head = '🎥 వీడియో' if kind == 'video' else '🖼️ ఇమేజ్ + కదలిక'
        md_items.append('\n'.join([
            f"#### {k}. {it['label']} · {card['time']} · {secs} సె · {head}\n",
            f"- **నెరేషన్:** {it['text']}",
            f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in refs) if refs else 'అవసరం లేదు'}",
            *([f"- **ఎడిటర్‌లో కదలిక:** {card['move']}"] if card['move'] else []),
            *([f"- **గమనిక:** {card['note']}"] if card['note'] else []),
            f"\n**1. మొదటి ఇమేజ్**\n\n```text\n{card['imagePrompt']}\n```\n",
            f"**2. చివరి ఇమేజ్** (మొదటి ఇమేజ్ + రిఫరెన్స్‌లు జత చేసి)\n\n```text\n{card['endImagePrompt']}\n```\n",
            f"**3. వీడియో** (Frames to Video: మొదటి → చివరి)\n\n```text\n{card['videoPrompt']}\n```\n"]))
    total = t + OUTRO
    chap.append((t, 'ఎండ్ స్క్రీన్'))

    paras = []
    for it in items:   # one paragraph per clip; each sloka and the intro their own piece
        if it['kind'] == 'intro':
            paras.append(('intro', tts.INTRO))
        elif it.get('verse'):
            paras.append(('verse', tts.chant(it['text'])))
        else:
            paras.append(('text', tts._close(tts.clean(it['text']))))
    voice = tts.pieces(paras)
    labels = [f'భాగం {j} / {len(voice)}' + {'verse': ' · 🕉️ శ్లోకం', 'intro': ' · 🎬 ఇంట్రో క్లిప్ – ఒక్కసారే చేసినది ఇక్కడ పెట్టండి',
                                              'text': ''}[kd] for j, (kd, _) in enumerate(voice, 1)]

    tprompt, trefs = L.thumb_prompt([{'visual': part['thumb'], 'loc': ''}], part['thumb_ep'])
    refs_used.update(trefs)
    topics = '\n'.join(f"{j}. {x['title']} ({x['ref']})" for j, x in enumerate(part['topics'], 1))
    desc = (f"{part['title']}\n\nసినిమాలు, సీరియల్స్‌లో చూపించే రామాయణానికి, వాల్మీకి మహర్షి రాసిన అసలు రామాయణానికి ఉన్న "
            "తేడాలు, శ్లోకాల ఆధారంతో.\n\n📌 ఈ వీడియోలో\n" + topics + "\n\n⏱️ అధ్యాయాలు\n"
            + '\n'.join(f'{mmss(a)} {c}' for a, c in chap[:-1])
            + "\n\n📖 మూలం: వాల్మీకి రామాయణం (బాల, అయోధ్య, అరణ్య, ఉత్తర కాండలు)\n"
            "🔔 పురాణ కథా శ్రవణం – రామాయణం మొదటి నుండి చివరి వరకు, భాగం భాగంగా.\n\n"
            f"{HASHTAGS} #సినిమాలువాల్మీకి")
    assert len(desc) <= 5000 and len(part['title']) <= 100
    pin = 'మీకు ఇంకా ఏ సన్నివేశంలో సినిమాకూ, వాల్మీకి రామాయణానికీ తేడా తెలుసుకోవాలని ఉంది? కామెంట్‌లో రాయండి, తరువాతి భాగంలో శ్లోకాలతో చూద్దాం. 🙏'
    tags = ', '.join(['రామాయణం', 'వాల్మీకి రామాయణం', 'సినిమాల్లో రామాయణం', 'లక్ష్మణ రేఖ', 'శూర్పణఖ', 'రావణుడి వరం',
                      'అహల్య', 'Ramayanam in Telugu', 'Valmiki Ramayanam', 'Ramayana myths vs facts', 'Purana Katha Shravanam'])
    tts_rel = f'Long_Videos/Special/07_Cinema_vs_Valmiki/tts/P{n}.txt'
    srt_rel = f'Long_Videos/Special/07_Cinema_vs_Valmiki/captions/P{n}.srt'
    n_video = sum(c['kind'] == 'video' for c in cards)
    md = '\n'.join([
        f"# {part['n']} · {part['headline']}\n",
        '*`Long_Videos/_tools/special_build.py` తయారుచేసిన ఫైల్. మార్పులు `_tools/data/special/07_cinema_vs_valmiki.py` లో చేసి మళ్ళీ బిల్డ్ చేయండి.*\n',
        '| | |\n|---|---|',
        f'| వీడియో నిడివి | **{mmss(total)}** ({len(cards)} క్లిప్‌లు + ఎండ్ స్క్రీన్ {OUTRO} సె) |',
        f'| క్లిప్‌లు | 🎥 వీడియో {n_video} · 🖼️ ఇమేజ్ + కదలిక {len(cards) - n_video} |',
        f'| క్యాప్షన్లు | `{srt_rel}` |\n',
        '### ప్రతి అంశం ఎలా',
        f'1. **శీర్షిక** – ప్రశ్న తెరపై.  2. **{FILM}** – సినిమాలు చూపించేది (ఏ సినిమా పేరూ చెప్పకుండా).  '
        f'3. **{VALMIKI}** – శ్లోకం ఆధారంతో అసలు కథ, కాండ·సర్గ·శ్లోకం సంఖ్య తెరపై.  4. **🕉️ శ్లోకం** (ఉన్నచోట).\n',
        '### 1. 🔊 ElevenLabs టెక్స్ట్\n',
        f'అదే టెక్స్ట్ `{tts_rel}` లో కూడా ఉంది. శ్లోకం భాగాలు విడిగా – AI సరిగ్గా పలకకపోతే మీ గొంతుతో రికార్డ్ చేయండి.\n',
        '\n'.join(f'**{lab}** · {len(v)} అక్షరాలు\n\n```text\n{v}\n```\n' for lab, (_, v) in zip(labels, voice)),
        '### 2. క్లిప్‌లు (16:9 · Shorts పాత్రలు, అదే 3D శైలి)\n',
        '- ప్రతి క్లిప్‌కు మూడు ప్రాంప్ట్‌లు: **1. మొదటి ఇమేజ్ → 2. చివరి ఇమేజ్ → 3. వీడియో** (Flow Frames to Video).',
        '- రిఫరెన్స్ ఇమేజ్‌లు Shorts లో చేసినవే (`Ingredients` గా జత చేయండి).\n',
        '\n'.join(md_items),
        '### 3. థంబ్‌నెయిల్ (1280×720)\n',
        f"| హెడ్‌లైన్ | **{part['headline']}** (**{part['hl']}** పసుపు) |\n|---|---|\n| కింది లైన్ | {part['sub']} |\n"
        f"| బ్యాడ్జ్ | సినిమాలు vs వాల్మీకి · {part['n']} |\n",
        f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in trefs) if trefs else 'అవసరం లేదు'}\n",
        f'```text\n{tprompt}\n```\n',
        '### 4. YouTube అప్‌లోడ్\n',
        f"**టైటిల్:**\n\n```text\n{part['title']}\n```\n",
        f'**వివరణ:**\n\n```text\n{desc}\n```\n',
        f'**పిన్ కామెంట్:**\n\n```text\n{pin}\n```\n',
        f'**ట్యాగ్‌లు:**\n\n```text\n{tags}\n```\n'])
    srt = '\n'.join(f'{j}\n{L.srt_time(a)} --> {L.srt_time(b)}\n{txt}\n' for j, (a, b, txt) in enumerate(srt_rows, 1))
    page = {'n': f'P{n}', 'headline': part['headline'], 'hl': part['hl'], 'sub': part['sub'],
            'badge': f"సినిమాలు vs వాల్మీకి · {part['n']} · {mmss(total)}", 'title': part['title'], 'sloka': [],
            'tts': [v for _, v in voice], 'ttsLabels': labels, 'ttsAll': '\n\n'.join(v for k, v in voice if k != 'intro'),
            'ttsAllNote': 'ఇంట్రో క్లిప్ లేకుండా, శ్లోకాలతో సహా మొత్తం వరుసగా. ఒకేసారి తీసుకోకపోతే కింది భాగాలు వాడండి.',
            'reading': None, 'clips': cards, 'thumbPrompt': tprompt, 'thumbRefs': trefs, 'desc': desc, 'pinned': pin,
            'srt': srt_rel}
    return md, srt, page, total, list(zip(labels, [v for _, v in voice]))


def main():
    parts = load()
    for sub in ('', 'tts', 'captions'):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    refs_used, pages, index = set(), [], []
    for n, part in enumerate(parts, 1):
        md, srt, page, total, voice = build(n, part, refs_used)
        open(os.path.join(OUT, f'P{n}.md'), 'w', encoding='utf-8', newline='\n').write(md)
        open(os.path.join(OUT, 'captions', f'P{n}.srt'), 'w', encoding='utf-8', newline='\n').write(srt)
        open(os.path.join(OUT, 'tts', f'P{n}.txt'), 'w', encoding='utf-8', newline='\n').write(
            '\n\n'.join(f'===== {lab} =====\n\n{v}' for lab, v in voice) + '\n')
        pages.append(page)
        index.append(f"| [P{n}](P{n}.md) | {part['headline']} | {mmss(total)} | "
                     + ' · '.join(x['title'] for x in part['topics']) + ' |')
        print(f'P{n} {mmss(total):>6}  {len(page["clips"])} clips')
    open(os.path.join(OUT, '00_INDEX.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join([
        '# సినిమాల్లో రామాయణం vs వాల్మీకి రామాయణం\n',
        'ప్రతి అంశం: సినిమాలు చూపించేది → వాల్మీకి మహర్షి రాసినది (కాండ·సర్గ·శ్లోకం సంఖ్యతో). కొత్త అంశాలు '
        '`Long_Videos/_tools/data/special/07_cinema_vs_valmiki.py` లో చేర్చి `python special_build.py` నడపండి.\n',
        '| భాగం | హెడ్‌లైన్ | నిడివి | అంశాలు |', '|---|---|---|---|', *index, '',
        '## పాత్రల రిఫరెన్స్‌లు (Shorts లో చేసినవే)\n', L.reference_file(refs_used)[0]]))
    tpl = open(os.path.join(L.ROOT, 'Valmiki_Ramayanam', '_tools', 'flow_helper_template.html'), encoding='utf-8').read()
    payload = {'key': 'special_cinema_vs_valmiki', 'name': 'సినిమాల్లో రామాయణం vs వాల్మీకి రామాయణం', 'slokas': pages,
               'refs': L.reference_file(refs_used)[1], 'placeKeys': [], 'unit': 'భాగాలు', 'clipWord': '',
               'clipsNote': ('ప్రతి క్లిప్‌కు మూడు ప్రాంప్ట్‌లు: 1. మొదటి ఇమేజ్ (రిఫరెన్స్‌లు జత చేసి) → 2. చివరి ఇమేజ్ (మొదటి ఇమేజ్ '
                             'కూడా జత చేసి) → 3. Flow Frames to Video. 🎬 క్లిప్‌లు సినిమాలు చూపించే విధానం, 📜 క్లిప్‌లు వాల్మీకి '
                             'రామాయణం చెప్పేది.'), 'clipDialog': True,
               'subtitle': 'అంశం వారీగా: 🎬 సినిమాల్లో → 📜 వాల్మీకి రామాయణంలో · ప్రతి క్లిప్‌కు మొదటి/చివరి ఇమేజ్, వీడియో',
               'scriptTitle': '', 'ttsTitle': '🔊 ElevenLabs టెక్స్ట్ – ప్రతి భాగం వరుసగా కాపీ చేసి పేస్ట్ చేయండి'}
    blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    frag = tpl.replace('__TITLE__', 'సినిమాలు vs వాల్మీకి').replace('__DATA__', blob)
    os.makedirs(os.path.join(L.TOOLS, 'publish'), exist_ok=True)
    open(os.path.join(L.TOOLS, 'publish', 'special_cinema_vs_valmiki.html'), 'w', encoding='utf-8', newline='\n').write(frag)


if __name__ == '__main__':
    main()
