# -*- coding: utf-8 -*-
"""కృష్ణ లీలా వైభవం – Krishna Shorts in the same style as రామాయణ వైభవం (user, 2026-11-12): cute, loving and mighty
moments of Krishna from the Srimad Bhagavatam, high visuals, and LOOP Shorts whose last frame is the first frame,
so the Short repeats seamlessly (the rope that is always two fingers short).

Facts follow the Srimad Bhagavatam (Canto 10; chapter named per Short). Krishna and Yashoda are new references in
data/shorts_refs.json (KRISHNA_BALA, YASHODA, GOKULA_HOME, ULUKHALA, YAMALA_ARJUNA). Cute and devotional, never
slapstick; the mother's anger is loving mock-anger; nothing scary.

    python krishna_build.py   ->  ../Krishna_Vaibhavam/Short_KN.md  and  publish/krishna_vaibhavam.html
"""
import json
import os

import elevation_build as EB
import live_style as LS
from soften import soften

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'Krishna_Vaibhavam')
FAST, PUSH, PULL, ORBIT, CRANE, TRACK = EB.FAST if hasattr(EB, 'FAST') else 'Fast low-angle push-in', \
    'Slow push-in on the face', 'Slow pull-back to a wide view', 'Slow orbit around the child', 'Rising crane up to a high top view', \
    'Side tracking shot at the child\'s eye level'
LOW = 'Low camera at the toddler\'s eye level'
BASE_LOOP = ('Instrumental, no vocals: a playful, sweet Indian devotional loop: bansuri flute melody, light mridangam, tiny '
             'ankle-bell and hand-cymbal rhythm, soft tanpura; cheerful and cute, ')
BASE_STORY = ('Instrumental, no vocals: a joyful, energetic Indian devotional score for a Krishna leela Short: bansuri flute lead, '
              'mridangam and dholak, ankle bells, bright strings, ')
EXCLUDE = 'vocals, singing, lyrics, choir words, rap, EDM, western pop, film song, scary sounds'

SHORTS = [
 dict(n=1, loop=True, L=24, headline='రెండు వేళ్ళు తక్కువ!', hl='రెండు వేళ్ళు', sub='దామోదర లీల – లూప్', src='శ్రీమద్భాగవతం, దశమ స్కంధం, అధ్యాయం 9',
  title='ఎన్ని తాళ్ళు కట్టినా… రెండు వేళ్ళు తక్కువే! 😄💙', caption='ఎన్ని తాళ్ళు కట్టినా… రెండు వేళ్ళు తక్కువే! 😄',
  music='a seamless 24-second loop at 120 bpm (exactly 12 bars of 4/4), the last beat flowing straight back into the first, no intro and no ending, a light playful "boing" accent on each tug of the rope',
  thumb=('KRISHNA_BALA, YASHODA, ULUKHALA', 'Mother Yashoda pulling a rope around little Krishna\'s waist beside a wooden mortar, the two rope ends just two fingers apart, Krishna giggling with both hands over his mouth', 'Warm golden morning light'),
  rows=[
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', "Mother Yashoda kneeling in the courtyard pulling a rope around little Krishna's waist as he stands beside the wooden mortar; the two rope ends stop just two fingers apart; Krishna smiling sweetly",
    'she tugs the ends tighter but they stay two fingers apart; Krishna giggles and claps his tiny hands', 'Slow push-in on the small gap, then tilt up to Krishna\'s smile', 'Warm golden morning light',
    ''),
   # 3 clips at full length, in order (user, 2026-11-12): she tries to tie it → she takes another rope and tries again →
   # she picks up a new coil and comes back to the start
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Mother Yashoda picking up another rope, knotting it onto the first and wrapping it around little Krishna again, the ends still two fingers apart; she blinks in surprise',
    'she pulls; the gap stays; Krishna covers his mouth with both hands, eyes twinkling', 'Side close-up on the rope ends, then on both faces', 'Warm golden morning light',
    ''),
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Mother Yashoda laughing softly, picking up a new coil of rope from a pile beside her and turning back to little Krishna',
    'she kneels again and brings the rope around his waist, ending in exactly the pose of the first clip', "Slow push-in, ending on the first clip's framing", 'Warm golden morning light',
    ''),
  ]),
 dict(n=2, headline='తాళ్ళన్నీ తక్కువే!', hl='తాళ్ళన్నీ', sub='దామోదర లీల', src='శ్రీమద్భాగవతం, దశమ స్కంధం, అధ్యాయం 9',
  title='ఇంట్లో తాళ్ళన్నీ తెచ్చినా… కన్నయ్యను కట్టలేకపోయింది! ఎందుకు? 💙', cta='k',
  music='a bright playful flute groove from the first second, a cheeky bouncy rhythm for the butter and the monkeys, a fast chase rhythm, a funny "stretch" motif each time the rope falls short, and a warm, glowing, loving finish',
  thumb=('KRISHNA_BALA, YASHODA, ULUKHALA', 'Mother Yashoda surrounded by coils of rope, pulling a rope around little Krishna\'s waist beside a wooden mortar, the ends just two fingers apart, Krishna giggling', 'Warm golden light, soft glow around Krishna'),
  rows=[
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', "Mother Yashoda pulling a rope around little Krishna's waist beside the wooden mortar, the rope ends just two fingers apart, Krishna giggling",
    'she tugs; the gap stays; Krishna giggles', "Slow push-in on the gap, then tilt up to Krishna's smile", 'Warm golden light',
    'ఇంట్లో తాళ్ళన్నీ తెచ్చినా… రెండు వేళ్ళు తక్కువే! ఎందుకు?', 'i'),
   ('KRISHNA_BALA, YASHODA, GOKULA_HOME', 'Mother Yashoda churning curd in a big pot with a wooden churning rod, little Krishna sitting snugly on her lap and hugging her', 'she churns and smiles down at him', PUSH, 'Soft morning light',
    'యశోదమ్మ పెరుగు చిలుకుతుంటే, కన్నయ్య అమ్మ ఒళ్ళో కూర్చున్నాడు.'),
   ('YASHODA, KRISHNA_BALA, GOKULA_HOME', 'Mother Yashoda setting little Krishna down and hurrying to a clay stove where a pot of milk is boiling over, Krishna pouting', 'she rushes to the stove; Krishna frowns', TRACK, 'Kitchen firelight',
    'పొయ్యి మీద పాలు పొంగుతుంటే, కన్నయ్యను దించి పరుగెత్తింది.'),
   ('KRISHNA_BALA, ULUKHALA, GOKULA_HOME', 'Little Krishna sitting on an upturned wooden mortar, feeding butter from a pot to a row of eager monkeys, butter on his cheeks, a broken curd pot behind him', 'he hands out butter; the monkeys reach and chatter', LOW + ', slow orbit', 'Warm golden light',
    'అంతే! కోపంతో పెరుగు కుండ పగలగొట్టాడు. రోలు మీద కూర్చుని వెన్న కోతులకు పంచాడు!', 'i'),
   ('YASHODA, KRISHNA_BALA, GOKULA_HOME', 'Mother Yashoda running across the courtyard with a small stick, little Krishna running away ahead of her, looking back with a cheeky smile', 'Krishna dodges around pillars; she catches him by the hand', TRACK + ', fast', 'Bright daylight',
    'చిన్న కర్ర పట్టుకుని అమ్మ వెంటపడింది! కన్నయ్య పరుగో పరుగు! చివరికి దొరికిపోయాడు.', 'i'),
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Mother Yashoda knotting rope after rope together, wrapping them around little Krishna by the mortar, the ends always two fingers apart', 'she joins another rope and pulls; the gap stays; Krishna smiles', 'Side close-up on the rope ends', 'Warm golden light',
    'రోలుకు కట్టేద్దామని తాడు చుట్టింది… రెండు వేళ్ళు తక్కువ! ఇంకో తాడు కలిపింది… మళ్ళీ రెండు వేళ్ళు తక్కువ!', 'i'),
   ('YASHODA, KRISHNA_BALA, ULUKHALA, GOKULA_HOME', 'Mother Yashoda tired and sweating among piles of rope, jasmine flowers slipping from her braid, cowherd women at the doorway smiling', 'a flower falls from her braid; she wipes her brow', PULL, 'Warm afternoon light',
    'ఇంట్లో తాళ్ళన్నీ అయిపోయాయి. అమ్మకు చెమటలు పట్టాయి, జడలోని పూలు జారిపడ్డాయి.'),
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Little Krishna looking at his tired mother with a loving smile as the rope finally closes around his waist and is knotted to the mortar, a soft glow around him', 'the rope closes; Yashoda smiles in relief; Krishna beams', PUSH, 'Warm glowing light',
    'అమ్మ అలసట చూసిన కన్నయ్య… తానే కట్టుబడ్డాడు! ప్రేమకు మాత్రమే లొంగే దేవుడు… దామోదరుడు!'),
  ]),
 dict(n=3, headline='రోలుతో చెట్లు కూల్చాడు!', hl='చెట్లు', sub='యమళార్జున భంజనం', src='శ్రీమద్భాగవతం, దశమ స్కంధం, అధ్యాయాలు 9–10',
  title='రోలుకు కట్టేసిన పసివాడు… రెండు మహా వృక్షాలను కూల్చాడు! 🌳💥', cta='k',
  music='a cheeky, tiptoeing flute and mridangam groove from the first second, a mysterious shimmer when the two trees are seen, a rising tension as the mortar gets stuck, a huge crash hit when the trees fall, then a radiant divine theme with bells and a joyful finish',
  thumb=('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Little Krishna tied to a wooden mortar, pulling it between two giant falling Arjuna trees with a big smile, light bursting from the trees', 'Golden light and dust'),
  rows=[
   ('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Little Krishna, tied to a wooden mortar, pulling it between two giant Arjuna trees as they fall apart with a burst of light', 'the trees crash down on both sides; Krishna smiles', LOW + ', fast push-in', 'Golden light, flying dust and leaves',
    'రోలుకు కట్టేసిన పసివాడు… రెండు మహా వృక్షాలను కూల్చేశాడు!', 'i'),
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Little Krishna tied to the wooden mortar, watching his mother Yashoda walk away into the house to her work', 'Yashoda goes inside; Krishna looks around with a twinkle', PUSH, 'Warm daylight',
    'అమ్మ కన్నయ్యను రోలుకు కట్టేసి, ఇంటి పనిలో పడింది.'),
   ('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Little Krishna gazing at two tall twin Arjuna trees at the edge of the courtyard, a faint glow on their trunks', 'he tilts his head and smiles at the trees', 'Over-the-shoulder shot from Krishna to the trees, slow push-in', 'Soft golden light',
    'కన్నయ్య చూపు జంట మద్ది చెట్ల మీద పడింది.'),
   ('NARADA, YAMALA_ARJUNA', 'Sage Narada in the sky raising his hand in a long-ago blessing over two proud young men turning into two tall Arjuna trees by the river, shown as a soft golden memory', 'the two figures fade into tree trunks in a golden mist', CRANE, 'Golden memory haze',
    'నారద మహర్షి శాపంతో చెట్లుగా మారిన కుబేరుడి కొడుకులు… నలకూబరుడు, మణిగ్రీవుడు!'),
   ('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Little Krishna crawling between the two trees, dragging the wooden mortar behind him until it gets stuck crosswise between the trunks', 'the mortar wedges between the trunks; Krishna looks back at it', LOW + ', side tracking shot', 'Warm daylight',
    'పాకుతూ, రోలును లాక్కుంటూ రెండు చెట్ల మధ్య దూరాడు. రోలు అడ్డంగా ఇరుక్కుంది.'),
   ('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Little Krishna giving one strong tug on the rope, the two giant trees cracking at the roots and falling to either side with a mighty crash', 'the trees topple apart in a cloud of leaves and dust', 'Low-angle wide shot, the trees falling past the camera', 'Golden light, dust and leaves',
    'కన్నయ్య ఒక్క లాగు లాగాడు… పెద్ద శబ్దంతో రెండు చెట్లూ కూలిపోయాయి!', 'i'),
   ('KRISHNA_BALA, ULUKHALA, YAMALA_ARJUNA', 'Two shining divine young men rising out of the fallen trees in a glow of light, bowing with joined palms before little Krishna', 'they bow and praise him; the light grows', 'Rising crane from Krishna to the shining figures', 'Radiant divine light',
    'చెట్ల నుండి ఇద్దరు దివ్య పురుషులు వెలుగుతూ బయటికొచ్చారు. కన్నయ్యకు నమస్కరించి స్తుతించారు!', 'i'),
   ('KRISHNA_BALA, YASHODA, ULUKHALA, GOKULA_HOME', 'Mother Yashoda and the cowherds running up in amazement to little Krishna sitting tied to the mortar between the fallen trees, smiling innocently', 'Yashoda scoops him up in her arms', PULL, 'Warm golden light',
    'రోలుకు కట్టేసిన పసివాడే… శాపం తీర్చాడు! అదే కన్నయ్య లీల.'),
  ]),
]


def bhagavatam(text):
    return text.replace('the Valmiki Ramayana', 'the Srimad Bhagavatam').replace('Valmiki Ramayana', 'Srimad Bhagavatam')


def timing(sh):
    if sh.get('loop'):
        n, L = len(sh['rows']), sh['L']
        cuts = [round(L * i / n) for i in range(n + 1)]
        return L, [(cuts[i], cuts[i + 1]) for i in range(n)]
    return EB.timing(sh)


def short_page(sh):
    rows, n = sh['rows'], len(sh['rows'])
    total, slots = timing(sh)
    sh['L'] = total
    clips = []
    for i, ((a, b), row) in enumerate(zip(slots, rows)):
        keys, frame, motion, cam, light, said = row[:6]
        ks = [k.strip() for k in keys.split(',') if k.strip()]
        frame, light, hook = frame.rstrip('.') + '.', light.rstrip('. ') + '.', i == 0
        lab = ('లూప్ – ' if sh.get('loop') else '') + EB.label(i, n)
        start = bhagavatam(soften(LS.still(ks, frame, light, lab, motion=motion, cam=cam)))
        end = bhagavatam(soften(LS.end_still(ks, frame, motion, cam, light, True, lab, hook=hook)))
        vid = bhagavatam(soften(LS.two_frame_video(ks, frame, motion, cam, light, True, hook=hook)))
        if sh.get('loop') and i == n - 1:
            end = ('LOOP POINT – do not make a new picture: use the START image of clip 1 as this clip\'s END image, exactly the '
                   'same file, so the last frame of the Short is the first frame and it repeats seamlessly.')
            vid += (' LOOP: this clip ends on exactly the first frame of clip 1 (same pose, same framing, same light), '
                    'a smooth continuous motion with no cut, so the Short loops seamlessly.')
        clips.append({'no': i + 1, 'time': f'{a // 60}:{a % 60:02d} – {b // 60}:{b % 60:02d}', 'label': lab, 'kind': 'video',
                      'narration': said or f"(మాట లేదు – తెరపై: {sh['caption']})", 'refs': LS.ref_keys(ks), 'move': cam,
                      'imagePrompt': start, 'endImagePrompt': end, 'videoPrompt': vid, 'prompt': vid})
    tk, tf, tl = sh['thumb']
    tprompt, trefs = LS.thumb([k.strip() for k in tk.split(',') if k.strip()], tf.rstrip('.') + '.', tl)
    title = f"{sh['title']} | కృష్ణ లీలా వైభవం"
    assert len(title) <= 100, (sh['n'], len(title))
    tags = '#కృష్ణలీల #JaiShriKrishna #Damodara #SrimadBhagavatam #TeluguShorts' + (' #Loop' if sh.get('loop') else '')
    story = sh.get('caption') if sh.get('loop') else '\n'.join(r[5] for r in rows)
    desc = (f"{sh['title']}\n\n{story}\n\n📖 మూలం: {sh['src']}\n🎼 దృశ్యాలు, సంగీతం AI సాయంతో; కథ శ్రీమద్భాగవతం ప్రకారం.\n{tags}")
    return {'n': sh['n'], 'headline': sh['headline'], 'hl': sh['hl'], 'sub': sh['sub'],
            'badge': f"కృష్ణ లీలా వైభవం · K{sh['n']} · {total} సెకన్లు" + (' · లూప్' if sh.get('loop') else '') + f" · {sh['src']}",
            'title': title, 'sloka': [], 'reading': None, 'clips': clips, 'thumbPrompt': bhagavatam(soften(tprompt)),
            'thumbRefs': list(trefs), 'desc': desc, 'pinned': 'కన్నయ్య లీలల్లో మీకు ఏది ఇష్టం? కామెంట్‌లో రాయండి! 💙', 'srt': ''}


def music_prompt(sh):
    total = timing(sh)[0]
    if sh.get('loop'):
        return BASE_LOOP + sh['music'] + '.'
    return BASE_STORY + f"{sh['music']}; about {total} seconds long."


def voice_script(sh):
    """Warm and lively for Krishna stories; the climax lines confident. Never [excited] (it laughs)."""
    return ' '.join(f"{'[confident]' if len(r) > 6 else '[warm]'} {r[5]}" for r in sh['rows'] if r[5])


def main():
    pages = [short_page(sh) for sh in SHORTS]
    music = {'exclude': EXCLUDE, 'moods': {f"k{sh['n']}": {'label': f"💙 K{sh['n']}. {sh['sub']}", 'prompt': music_prompt(sh)} for sh in SHORTS},
             'of': {str(sh['n']): f"k{sh['n']}" for sh in SHORTS}}
    eleven = {str(sh['n']): {'voice1': voice_script(sh)} for sh in SHORTS if not sh.get('loop')}
    used = sorted({r for p in pages for c in p['clips'] for r in c['refs']} | {r for p in pages for r in p['thumbRefs']})
    data = {'key': 'krishna_vaibhavam', 'name': 'కృష్ణ లీలా వైభవం – Shorts', 'slokas': pages,
            'clipsNote': ('శ్రీమద్భాగవతం నుండి కన్నయ్య లీలలు. లూప్ Short లో మాట లేదు: చివరి క్లిప్ చివరి ఇమేజ్ = మొదటి క్లిప్ మొదటి ఇమేజ్ '
                          '(అదే ఫైల్), కాబట్టి వీడియో ఆగకుండా మళ్ళీ మళ్ళీ తిరుగుతుంది. పైన క్యాప్షన్ ఒక్కటే. మిగిలిన Shorts కథతో.'),
            'refs': LS.library(used), 'music': music, 'eleven': eleven,
            'elevenTitle': '🎙 ElevenLabs వాయిస్ – మొత్తం Short ఒకే టేక్',
            'elevenNote': 'గొంతు: Vagmin, Eleven v3. [ ] లోని సూచనలు చదవబడవు. లూప్ Short కి వాయిస్ లేదు.',
            'elevenParts': [['voice1', 'మొత్తం Short – ఒకే టేక్']]}
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    tpl = open(os.path.join(HERE, 'flow_helper_live_template.html'), encoding='utf-8').read()
    frag = tpl.replace('__TITLE__', 'కృష్ణ లీలా వైభవం Shorts').replace('__DATA__', blob)
    open(os.path.join(HERE, 'publish', 'krishna_vaibhavam.html'), 'w', encoding='utf-8', newline='\n').write(frag)
    os.makedirs(OUT, exist_ok=True)
    for sh, p in zip(SHORTS, pages):
        md = [f"# కృష్ణ లీలా వైభవం K{sh['n']} · {sh['headline']} ({sh['L']} సెకన్లు{', లూప్' if sh.get('loop') else ''})", '',
              f"📖 {sh['src']}", '', f"**సంగీతం (Suno, Instrumental):** {music_prompt(sh)}  ", f"**Exclude:** {EXCLUDE}", '']
        if sh.get('loop'):
            md += [f"**తెరపై క్యాప్షన్ (మొత్తం వీడియో):** {sh['caption']}", '']
        for c in p['clips']:
            md += [f"## {c['no']}. {c['label']} · {c['time']}", '', f"**మాట:** {c['narration']}", '', f"**కెమెరా:** {c['move']}", '',
                   f"**రిఫరెన్స్:** {', '.join(c['refs'])}", '', '**1. మొదటి ఇమేజ్**', '```text', c['imagePrompt'], '```',
                   '**2. చివరి ఇమేజ్**', '```text', c['endImagePrompt'], '```', '**3. వీడియో**', '```text', c['videoPrompt'], '```', '']
        md += ['## థంబ్‌నెయిల్', '', f"**{sh['headline']}** ({sh['hl']} పసుపు) · {sh['sub']}", '```text', p['thumbPrompt'], '```', '',
               '## YouTube', '', '```text', p['title'], '```', '```text', p['desc'], '```']
        open(os.path.join(OUT, f"Short_K{sh['n']}.md"), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    print(len(pages), 'Krishna Shorts,', [(sh['n'], sh['L']) for sh in SHORTS], 'unknown refs:',
          sorted({k.strip() for sh in SHORTS for r in sh['rows'] for k in r[0].split(',') if k.strip()} - set(LS.LIB)))


if __name__ == '__main__':
    main()
