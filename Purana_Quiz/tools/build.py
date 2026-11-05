"""Quiz Shorts "పురాణ ప్రశ్నలు – తాతయ్య, చిన్ని": one kit per Short and one phone page.

usage:  python Purana_Quiz/tools/build.py

Reads   Purana_Quiz/data/quiz.txt          the Shorts (2-3 questions each + a comment question, with the source of every answer)
Writes  Purana_Quiz/Shorts/<id>.md          the kit: timeline, voice lines, on-screen text, image/video prompts, upload text
        Purana_Quiz/tools/publish/quiz.html the phone page (published to claude.ai)
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHO = {'T': 'తాతయ్య', 'C': 'చిన్ని'}
BOOK = {'ramayana': 'రామాయణం', 'bharatam': 'మహాభారతం', 'bhagavatam': 'భాగవతం'}
BOOK_EN = {'ramayana': 'Ramayanam', 'bharatam': 'Mahabharatam', 'bhagavatam': 'Bhagavatam'}
STYLE = ('Vertical 9:16, 1080x1920, warm premium 3D animated film look, soft cinematic light, rich Indian colours, '
         'the main subject in the centre third (top and bottom kept calm for on-screen text). ')
RESPECT = ('Sacred Hindu devotional subject: every deity and sage shown with deep reverence and traditional iconography; '
           'everyone fully and modestly dressed; no blood, gore, horror or mockery. No text, letters or logos in the image.')
CAST = {
    'TATAYYA': ('తాతయ్య', 'A kind Telugu grandfather about 70 years old, slim, silver hair combed back, short white beard, '
                'thin gold-rim glasses, white cotton dhoti and kurta with a cream angavastram on one shoulder, a small '
                'vibhuti line and red dot on the forehead, warm twinkling eyes and a gentle smile'),
    'CHINNI': ('చిన్ని', 'His granddaughter Chinni, about 10 years old, bright curious eyes, long black hair in two braids '
               'with small jasmine strings, a yellow pattu pavada (long skirt and blouse) with a green border, a small '
               'bindi, holding a tablet, lively and smiling'),
}
# ElevenLabs → Voices → "Voice Design": paste the description, paste the Telugu sample as the preview text, pick the
# preview that sounds most like the person, save it under the name, then use these settings for every line.
VOICE_DESIGN = {
    'TATAYYA': ('Tatayya', 'An elderly, warm and kind male voice speaking native Telugu with a natural Andhra accent. '
                'Smooth, mellow and slightly deep, with the soft gentle texture of age, yet every word is crisp and '
                'clear. A natural, human storyteller: relaxed pace, soft breaths, small thoughtful pauses, rising '
                'curiosity when asking a question, a warm chuckle in the voice when teasing, gentle pride when the '
                'answer is right. Expressive and engaging, never flat, monotone or robotic. No shaking, no cough, no '
                'rasp, no shouting. Studio quality, close and warm, no background noise.',
                'చిన్నీ, ఇలా రా అమ్మా, నా పక్కన కూర్చో. ఈ రోజు నీకు ఒక మంచి ప్రశ్న అడుగుతాను. '
                'వాల్మీకి మహర్షికి రాముడి కథ మొదట ఎవరు చెప్పారో తెలుసా? ఆలోచించి చెప్పు. '
                'భలే! సరిగ్గా చెప్పావు, నా బంగారు తల్లి. జవాబు నారద మహర్షి!',
                'Stability 35–40% (తక్కువ అయితే సహజంగా, రోబోలా ఉండదు) · Similarity 75% · Style 30% · Speed 0.92 · '
                'Speaker boost ON · v3 లో [warmly], [chuckles], [curious] ట్యాగ్‌లు'),
    'CHINNI': ('Chinni', 'A bright, cheerful, energetic female voice speaking native Telugu with a natural Andhra '
               'accent. Light and clear tone, friendly and expressive, a quick and lively pace, with natural '
               'excitement when asking questions and happy pride when answering right. Every Telugu word pronounced '
               'clearly. Studio quality, close and clean, no background noise.',
               'రండి రండి! ఈ రోజు మీకోసం ఒక మంచి ప్రశ్న తెచ్చాను. '
               'తమసా నది ఒడ్డున వాల్మీకి మహర్షి చూసిన పక్షుల జంట ఏది? మీకు తెలుసా? '
               'హహ, నాకు తెలుసు! క్రౌంచ పక్షులు! భలే ఉంది కదా ఈ కథ?',
               'Stability 45% · Similarity 75% · Style 30% · Speed 1.0 · Speaker boost ON'),
}
VOICE_HOW = ('ElevenLabs → Voices → Create a Voice → Voice Design. (1) "Prompt" లో వివరణ పేస్ట్ చేయండి. '
             '(2) "Text to preview" లో తెలుగు శాంపిల్ పేస్ట్ చేయండి. (3) వచ్చిన 3 గొంతుల్లో ఆ పాత్రకు బాగా సరిపోయింది ఎంచుకుని '
             'ఆ పేరుతో సేవ్ చేయండి. (4) ప్రతి లైన్‌కు అదే గొంతు, కింది సెట్టింగ్‌లు; మోడల్ Eleven v3 (లేదా Multilingual v2). '
             'రెండు గొంతులూ ఒక్కసారి చేస్తే అన్ని Shorts కీ సరిపోతాయి. ElevenLabs పిల్లల గొంతు తయారు చేయనివ్వదు, '
             'అందుకే చిన్నికి ఉత్సాహమైన, తేలికైన ఆడ గొంతు (కార్టూన్ డబ్బింగ్‌లో లాగా). 3 ప్రివ్యూల్లో అన్నిటికంటే తేలికగా, '
             'చలాకీగా ఉన్నది ఎంచుకోండి; లేకపోతే మళ్ళీ Generate నొక్కండి. Style ఎక్కువ పెడితే ఇంకా చలాకీగా వస్తుంది. '
             'చిన్ని ఇంకా చిన్నపిల్లలా వినిపించాలంటే: (1) ఆమె లైన్లలో ఆశ్చర్యం, నవ్వు పెట్టండి — Eleven v3 లో [excited], '
             '[giggles] లాంటి ట్యాగ్‌లు; Speed 1.05–1.1. (2) ఎడిటర్‌లో (CapCut / Audacity) చిన్ని ఆడియో పిచ్ +2 నుండి +3 '
             'సెమిటోన్లు పెంచండి. (3) ఇంట్లో ఒక పాప గొంతు తల్లిదండ్రుల ఒప్పుకోలుతో రికార్డ్ చేయండి, లేదా కార్టూన్ డబ్బింగ్ '
             'చేసే గాయని/డబ్బింగ్ ఆర్టిస్ట్‌తో చెప్పించండి — ఇది అన్నిటికంటే సహజంగా ఉంటుంది.')
SET = ('a cosy Telugu home verandah in the evening: a wooden swing (oonjal) with brass chains, a tulasi pot, a glowing '
       'brass lamp, a bookshelf with old palm-leaf bundles and a few books')
CTAS = ['"జై శ్రీరామ్" అని కామెంట్ చేసి, మీ స్కోర్ కూడా రాయండి.', 'నచ్చితే లైక్ చేసి, మీ ఇంట్లో పిల్లలకు షేర్ చేయండి.',
        'రోజూ ఒక పురాణ క్విజ్ కోసం సబ్‌స్క్రైబ్ చేయండి.', 'మీ కుటుంబంలో ఎవరు ఎక్కువ స్కోర్ చేశారో కామెంట్‌లో చెప్పండి.']


def parse():
    shorts = []
    for line in open(os.path.join(ROOT, 'data', 'quiz.txt'), encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('SHORT '):
            f = [x.strip() for x in line[6:].split('|')]
            sid, title, book = f[:3]
            shorts.append({'id': sid, 'title': title, 'book': book, 'hook': f[3] if len(f) > 3 else '', 'qs': []})
        elif line.startswith(('Q ', 'NEXT ')):
            kind, rest = line.split(' ', 1)
            f = [x.strip() for x in rest.split('|')]
            assert len(f) == 9, f'{shorts[-1]["id"]}: a {kind} line needs 9 fields: {line[:60]}'
            who, q, a, b, c, ans, src, why, pic = f
            assert ans in 'ABC' and who in WHO
            item = {'who': who, 'q': q, 'opts': [a, b, c], 'ans': ans, 'src': src, 'why': why, 'pic': pic}
            if kind == 'Q':
                shorts[-1]['qs'].append(item)
            else:
                shorts[-1]['next'] = item
    for i, s in enumerate(shorts):
        assert 2 <= len(s["qs"]) <= 4, f"{s['id']}: 2 to 4 questions"
        s['prev'] = shorts[i - 1].get('next') if i else None   # last Short's comment question, answered here
        s['prev_id'] = shorts[i - 1]['id'] if i else ''
    return shorts


def mmss(t):
    return f'{t // 60}:{t % 60:02d}'


def secs(text, least):
    """Seconds the line takes to say: Telugu syllables / 5.5 a second, plus a breath; never under `least`."""
    syl = len(re.findall(r'[అ-ఔ]|[క-హ](?!్)|[A-Za-z]+|\d+', text))
    return max(least, round(syl / 5.5 + 0.8))


def timeline(s, n):
    """Hook → each question (ask, options, 3 s countdown, answer + source) → score. Each part lasts as long as its line."""
    rows, t = [], 0

    def add(part, who, say, screen, vis, least):
        nonlocal t
        d = secs(say, least) if say else least
        rows.append((t, d, part, who, say, screen, vis))
        t += d

    # open on a story teaser from these sargas, not on "N questions"
    add('హుక్', 'C' if n % 2 else 'T', s['hook'] or f"{BOOK[s['book']]} క్విజ్! మీకు జవాబు తెలుసా?",
        s['title'], 'presenters', 3)
    p = s.get('prev')
    if p:
        k = 'ABC'.index(p['ans'])
        add('గత ప్రశ్న జవాబు', 'T', f"క్రితం ప్రశ్నకు జవాబు: {p['ans']}, {p['opts'][k]}! {p['why']}",
            f"గత ప్రశ్న: {p['q']}\n✅ {p['ans']}) {p['opts'][k]}\nమూలం: {p['src']}", p['pic'], 6)
    for i, q in enumerate(s['qs'], 1):
        other = 'C' if q['who'] == 'T' else 'T'
        k = 'ABC'.index(q['ans'])
        add(f'ప్రశ్న {i}', q['who'], q['q'], f'ప్రశ్న {i}: {q["q"]}', 'presenters', 4)
        add('ఆప్షన్లు', q['who'], '; '.join(f'{L}, {o}' for L, o in zip('ABC', q['opts'])) + '.',
            '  '.join(f'{L}) {o}' for L, o in zip('ABC', q['opts'])), 'options', 4)
        add('కౌంట్‌డౌన్', '', '', '3… 2… 1…  (టిక్ టిక్ శబ్దం, మాటలు లేవు)', 'options', 3)
        add('జవాబు', other, f"జవాబు {q['ans']}, {q['opts'][k]}! {q['why']}",
            f"✅ {q['ans']}) {q['opts'][k]}\nమూలం: {q['src']}", q['pic'], 5)
    x = s.get('next')
    if not x:
        cta = ' '.join(CTAS[(n + j) % len(CTAS)] for j in range(2))
        add('ముగింపు', 'T', f'ఎన్ని సరిగ్గా చెప్పారు? {cta}', 'మీ స్కోర్ ఎంత? 👇', 'presenters', 6)
        return rows, t
    # the comment question is the second call to action; the first is like/share or subscribe, in turn
    add('ముగింపు', 'T', f'ఎన్ని సరిగ్గా చెప్పారు? {CTAS[1 + n % 2]}', 'మీ స్కోర్ ఎంత? 👇', 'presenters', 4)
    add('కామెంట్ ప్రశ్న', x['who'], f"ఇప్పుడు మీకోసం ఒక ప్రశ్న! {x['q']}", f"💬 కామెంట్ ప్రశ్న: {x['q']}", 'presenters', 4)
    add('కామెంట్ ఆప్షన్లు', x['who'], '; '.join(f'{L}, {o}' for L, o in zip('ABC', x['opts']))
        + '. మీ జవాబు కామెంట్‌లో రాయండి — తరువాతి Short లో జవాబు చెప్తాం!',
        '  '.join(f'{L}) {o}' for L, o in zip('ABC', x['opts'])) + '\n💬 జవాబు కామెంట్‌లో! తరువాతి Short లో జవాబు 👀', 'options', 6)
    return rows, t


KEY = {'T': 'TATAYYA', 'C': 'CHINNI'}
FRONT = ('Facing the camera straight on and looking directly into the lens: a full front view of the face, no side '
         'or profile view, eyes clear and bright, a clear happy expression and a warm natural smile. ')
ONE = ('Only this one person in the whole image: no other people, no second face, no reflections or posters of '
       'faces, so a lip-sync tool can only animate this face. ')
# (start frame, end frame, the motion between them) for every common shot; the end frame always closes the mouth
SOLO = {
    ('TATAYYA', 'hook'): (
        'leaning a little forward with a twinkle in his eyes, one finger raised as if about to share a wonderful '
        'secret, eyebrows lifted, smiling, mouth slightly open',
        'sitting back relaxed with the finger lowered, a big warm smile, mouth closed, eyes twinkling',
        'he tells the secret with small natural mouth movements and a lively face, then sits back smiling'),
    ('TATAYYA', 'talk'): (
        'sitting relaxed, hands resting on his lap, a gentle smile, mouth slightly open as if speaking',
        'the same relaxed pose, a slightly wider kind smile, a small nod, mouth closed',
        'he talks calmly with small natural mouth movements, soft blinks and one small hand gesture'),
    ('CHINNI', 'hook'): (
        'leaning towards the camera with wide excited eyes, both hands raised near her face in wonder, a big bright '
        'smile, mouth slightly open',
        'hands lowered and clasped happily, a big bright smile, mouth closed, eyes sparkling',
        'she speaks excitedly with small natural mouth movements, then clasps her hands and smiles'),
    ('CHINNI', 'talk'): (
        'sitting up straight holding her tablet on her lap, a bright smile, mouth slightly open as if speaking',
        'the same pose with a small happy head tilt, a bright smile, mouth closed',
        'she talks brightly with small natural mouth movements, soft blinks and one small hand gesture'),
}
BOTH = {
    'think': ('both look at the camera with thoughtful smiles as if solving a puzzle, the grandfather stroking his '
              'beard, Chinni with a finger on her chin',
              'both smile broadly at the camera with bright "I know it!" faces, Chinni raising one finger',
              'both think for a moment, then their faces light up with a smile'),
    'wave': ('both smile at the camera and wave, Chinni pointing down as if saying "write in the comments"',
             'both smile at the camera with joined palms in a namaste',
             'both wave happily, Chinni points down once, then both join their palms in a namaste'),
}


def solo_frame(key, kind, end=False):
    """Start or end picture for one character alone: front view, one face only, for lip sync."""
    pose = SOLO[(key, kind)][1 if end else 0]
    return (STYLE + f'Setting: {SET}. Medium close-up, {CAST[key][1]}. Sitting alone on the swing, {pose}. ' + FRONT
            + 'Face large and evenly lit, the lamp glowing softly behind, background softly blurred. ' + ONE + RESPECT)


def solo_clip(key, kind):
    who = 'The grandfather' if key == 'TATAYYA' else 'Chinni'
    return (f'Animate from the attached start frame to the attached end frame as one continuous 10 second vertical '
            f'shot: {who} faces the camera the whole time; {SOLO[(key, kind)][2]}. Small, slow, natural movements, soft '
            'blinks, the swing sways only a little, the lamp flame flickers. The face and clothes stay exactly the '
            'same, the face never turns sideways, the camera does not move, no cuts. Audio: none.')


def both_frame(mood, end=False):
    """Start or end picture with both on the swing, for moments with no speech on screen (mouths closed)."""
    return (STYLE + f'Setting: {SET}. Characters (keep exactly this look): ' + ' '.join(f'{v[1]}.' for v in CAST.values())
            + f' Medium two-shot, the two sit together on the swing; {BOTH[mood][1 if end else 0]}. Both mouths closed. '
            + FRONT.replace('the face', 'both faces') + RESPECT)


def both_clip(mood):
    return (f'Animate from the attached start frame to the attached end frame as one continuous 8 second vertical '
            f'shot: {BOTH[mood][2]}. Both face the camera the whole time and keep their mouths closed (no talking), '
            'soft blinks, the swing sways gently, the lamp flame flickers. Small slow movements, same faces and '
            'clothes, the camera does not move, no cuts. Audio: none.')


def answer_prompt(pic):
    return STYLE + f'A devotional illustration: {pic}. Faces clear and front-facing where shown, calm and gentle. ' + RESPECT


def answer_end(pic):
    return (STYLE + f'The same devotional illustration as the start frame: {pic}. The same figures in the same places, '
            'seen a little closer, the light warmer and brighter like a soft divine glow, faces calm and smiling. ' + RESPECT)


def video_prompt(d):
    return (f'Animate from the attached start frame to the attached end frame as one continuous {d} second vertical '
            'shot: a slow, gentle push-in, light and cloth moving softly; the figures keep exactly the same look and '
            'stay in place; no sudden moves, no cuts. ' + RESPECT + ' Audio: soft ambient only.')


LIPSYNC = ('ఒక్కసారి: పాత్రలు పేజీలోని మొదటి/చివరి ఇమేజ్‌లతో ElevenLabs లో 6 వీడియోలు చేసి ఉంచండి (TATAYYA_hook.mp4, '
           'TATAYYA_talk.mp4, CHINNI_hook.mp4, CHINNI_talk.mp4, BOTH_think.mp4, BOTH_wave.mp4). ప్రతి Short కి: (1) ప్రతి లైన్‌ను '
           'ఆ గొంతుతో ElevenLabs లో చేసి, నంబర్‌తో సేవ్ చేయండి (ఉదా: 03_chinni.mp3). (2) 👄 షాట్: ఆ ఒక్కరి వీడియో + ఆ ఆడియో '
           'లిప్‌సింక్ టూల్‌లో (ElevenLabs / Kling Lip Sync / Hedra / HeyGen) – వీడియోలో ఒక్కరే ఉంటారు కాబట్టి ఆ నోరే కదులుతుంది; '
           'లైన్ వీడియో కంటే పొడవైతే వీడియోను ఎడిటర్‌లో కొంచెం నెమ్మది చేయండి. (3) 🔊 షాట్: ఇద్దరి వీడియో / జవాబు వీడియో మీద '
           'ఆడియో మాత్రమే. (4) ఎడిటర్‌లో నంబర్ వరుసలో పెట్టి, కార్డుల టెక్స్ట్ పెట్టండి.')


def kit(s, n):
    rows, total = timeline(s, n)
    voice = '\n'.join(f'[{WHO[r[3]]}]: {r[4]}' for r in rows if r[3] and r[4])
    pics = [r for r in rows if r[6] not in ('presenters', 'options')]
    title = f"{s['title']} | {BOOK[s['book']]} క్విజ్ #{n} | పురాణ ప్రశ్నలు"
    x, p = s.get('next'), s.get('prev')
    nl = '\n'
    abc = (lambda q: '  '.join(f'{L}) {o}' for L, o in zip('ABC', q['opts'])))
    ask = (f"{nl}{nl}💬 ఈ రోజు కామెంట్ ప్రశ్న: {x['q']}{nl}{abc(x)}{nl}మీ జవాబు కామెంట్‌లో రాయండి — జవాబు తరువాతి Short లో!"
           if x else '')
    desc = (f"{title}{nl}{nl}తాతయ్య, చిన్ని అడిగే {len(s['qs'])} పురాణ ప్రశ్నలు. మీ జవాబులు కామెంట్‌లో రాయండి!{ask}{nl}{nl}📖 మూలాలు:{nl}"
            + nl.join(f"{i}. {q['src']}" for i, q in enumerate(s['qs'], 1))
            + f'{nl}{nl}#పురాణప్రశ్నలు #{BOOK[s['book']]} #{BOOK_EN[s['book']]} #TeluguQuiz #PuranaQuiz #Shorts')
    # pin this as the first comment so people answer under it
    pin = (f"💬 కామెంట్ ప్రశ్న: {x['q']}{nl}{abc(x)}{nl}A, B, C లో మీ జవాబు కింద రాయండి 👇 జవాబు తరువాతి Short లో!"
           if x else '')
    # after the next Short is up, reply under the pinned comment with the answer and the link
    reveal = (f"✅ జవాబు: {x['ans']}) {x['opts']['ABC'.index(x['ans'])]} — {x['why']} (మూలం: {x['src']}){nl}"
              'పూర్తి జవాబు తరువాతి Short లో: <లింక్>' if x else '')
    labels = (['గత ప్రశ్న జవాబు'] if p else []) + [f'జవాబు {i}' for i in range(1, len(s['qs']) + 1)]
    md = [f"# {s['id']} · {s['title']}", '', f"{BOOK[s['book']]} · {len(s['qs'])} ప్రశ్నలు · సుమారు {mmss(total)} · నిలువు 9:16 Short", '',
          '## ప్రశ్నలు, జవాబులు, మూలాలు', '', '| # | అడిగేది | ప్రశ్న | జవాబు | మూలం |', '|---|---|---|---|---|']
    for i, q in enumerate(s['qs'], 1):
        md.append(f"| {i} | {WHO[q['who']]} | {q['q']} | **{q['ans']}) {q['opts']['ABC'.index(q['ans'])]}** | {q['src']} |")
    if p:
        md.append(f"| మొదట | తాతయ్య (గత ప్రశ్న, {s['prev_id']} నుండి) | {p['q']} | **{p['ans']}) {p['opts']['ABC'.index(p['ans'])]}** | {p['src']} |")
    if x:
        md.append(f"| చివర 💬 | {WHO[x['who']]} (కామెంట్ ప్రశ్న — జవాబు తరువాతి Short లో) | {x['q']} | **{x['ans']}) {x['opts']['ABC'.index(x['ans'])]}** | {x['src']} |")
    # the shot list: one clip per line, each with the one picture it needs and whether it is lip-synced
    shots, pi = [], 0
    for i, (t, d, part, who, say, screen, vis) in enumerate(rows, 1):
        if vis == 'presenters':          # someone speaks on screen: only that person in the picture, lip-synced
            base = f"{KEY[who]}_{'hook' if part == 'హుక్' else 'talk'}"
            img = f'{base}_start.png → {base}_end.png'
            kind, cast, vid = 'lip', 'ఒక్కరే', f'{base}.mp4 (ఒక్కసారి చేసినది) + ఈ ఆడియో → లిప్‌సింక్ → {i:02d}.mp4'
        elif vis == 'options':           # card on screen, nobody talks on screen: both, mouths closed
            mood = 'wave' if part == 'కామెంట్ ఆప్షన్లు' else 'think'
            img = f'BOTH_{mood}_start.png → BOTH_{mood}_end.png, పైన ఆప్షన్ కార్డు'
            kind, cast, vid = 'vo' if say else 'none', 'ఇద్దరూ', f'BOTH_{mood}.mp4 (ఒక్కసారి చేసినది), లిప్‌సింక్ వద్దు'
        else:                            # the answer: the story picture with the voice over it
            img = f'{labels[pi]} చిత్రం'
            img = f'{labels[pi]} – మొదటి → చివరి ఇమేజ్'
            kind, cast, vid = 'vo', 'చిత్రం', f'{labels[pi]} వీడియో (మొదటి → చివరి ఇమేజ్‌లతో), లిప్‌సింక్ వద్దు'
            pi += 1
        shots.append({'n': i, 't': f'{mmss(t)}–{mmss(t + d)}', 'd': d, 'part': part, 'who': WHO.get(who, ''),
                      'key': KEY.get(who, ''), 'say': say, 'img': img, 'vid': vid, 'cast': cast, 'kind': kind,
                      'screen': screen, 'file': f"{i:02d}_{KEY[who].lower()}.mp3" if who else ''})
    DO = {'lip': '👄 లిప్‌సింక్', 'vo': '🔊 ఆడియో మాత్రమే', 'none': '⏱️ మాటలు లేవు – టిక్ టిక్ శబ్దం'}
    md += ['', '## 🎬 షాట్ లిస్ట్ (వరుసగా)', '', LIPSYNC, '',
           '| # | సమయం | భాగం | తెరపై ఎవరు | ఇమేజ్ | వీడియో | గొంతు | లైన్ (ElevenLabs) | ఆడియో ఫైల్ |',
           '|---|---|---|---|---|---|---|---|---|']
    md += [f"| {x_['n']} | {x_['t']} | {x_['part']} | {x_['cast']} | {x_['img']} | {x_['vid']} | {DO[x_['kind']]}"
           f"{' – ' + x_['who'] if x_['who'] else ''} | {x_['say'] or '–'} | {x_['file'] or '–'} |" for x_ in shots]
    md += ['', '## 🔊 వాయిస్ (రెండు గొంతులు)', '', VOICE_HOW, '']
    for k, (name, desc_, sample, sets) in VOICE_DESIGN.items():
        md += [f'### {CAST[k][0]} గొంతు ({name})', '', '```text', desc_, '```', '', '```text', sample, '```', '', f'సెట్టింగ్‌లు: {sets}', '']
    md += ['', '## 🖼️ జవాబు చిత్రాలు', '',
           '**తాతయ్య, చిన్ని, ఇద్దరి ఇమేజ్‌లు, వీడియోలు ఒక్కసారే చేయాలి – పాత్రలు పేజీలో.** '
           'ఇక్కడ ఈ Short కి మాత్రమే కావలసిన జవాబు చిత్రాలు. ఆప్షన్ కార్డులు ఎడిటర్‌లో టెక్స్ట్‌తో చేయండి.', '']
    for lab, r in zip(labels, pics):
        md += [f'### {lab} – మొదటి ఇమేజ్', '', '```text', answer_prompt(r[6]), '```', '', f'### {lab} – చివరి ఇమేజ్', '',
               '```text', answer_end(r[6]), '```', '', f'### {lab} – వీడియో', '', '```text', video_prompt(r[1]), '```', '']
    md += ['## 📤 అప్‌లోడ్', '', '```text', title, '```', '', '```text', desc, '```', '']
    if x:
        md += ['### 📌 పిన్ కామెంట్ (అప్‌లోడ్ అయిన వెంటనే)', '', '```text', pin, '```', '',
               '### ✅ జవాబు రిప్లై (తరువాతి Short వచ్చాక, పిన్ కామెంట్ కింద)', '', '```text', reveal, '```', '']
    page = {'id': s['id'], 'title': s['title'], 'book': BOOK[s['book']], 'len': mmss(total), 'voice': voice, 'ytitle': title,
            'desc': desc, 'qs': s['qs'], 'shots': shots, 'lipHow': LIPSYNC,
            'byVoice': {k: '\n'.join(f"{x_['n']:02d}. {x_['say']}" for x_ in shots if x_['key'] == KEY[k]) for k in 'TC'},
            'answers': [{'label': lab, 'img': answer_prompt(r[6]), 'end': answer_end(r[6]), 'vid': video_prompt(r[1])}
                        for lab, r in zip(labels, pics)],
            'prev': p, 'prevId': s['prev_id'], 'next': x, 'pin': pin, 'reveal': reveal,
            'rows': [{'t': f'{mmss(t)}–{mmss(t + d)}', 'part': part, 'who': WHO.get(who, ''), 'say': say, 'screen': screen}
                     for t, d, part, who, say, screen, vis in rows]}
    return '\n'.join(md), page


def main():
    shorts = parse()
    os.makedirs(os.path.join(ROOT, 'Shorts'), exist_ok=True)
    pages = []
    for n, s in enumerate(shorts, 1):
        md, page = kit(s, n)
        open(os.path.join(ROOT, 'Shorts', f"{s['id']}.md"), 'w', encoding='utf-8', newline='\n').write(md + '\n')
        pages.append(page)
    cast = [{'key': k, 'name': v[0], 'prompt': STYLE + f'Character reference sheet on a plain light background: {v[1]}. '
             'Front view, side view and three-quarter view, full body, consistent look. ' + RESPECT,
             'shots': [{'kind': kd, 'start': solo_frame(k, kd), 'end': solo_frame(k, kd, True), 'vid': solo_clip(k, kd)}
                       for kd in ('hook', 'talk')]} for k, v in CAST.items()]
    tpl = open(os.path.join(ROOT, 'tools', 'page_template.html'), encoding='utf-8').read()
    voices = [{'name': CAST[k][0], 'en': v[0], 'desc': v[1], 'sample': v[2], 'sets': v[3]} for k, v in VOICE_DESIGN.items()]
    both = [{'key': f'BOTH_{m}', 'label': lab, 'start': both_frame(m), 'end': both_frame(m, True), 'vid': both_clip(m)}
            for m, lab in (('think', 'ఇద్దరూ ఆలోచిస్తూ – ఆప్షన్లు, కౌంట్‌డౌన్ కింద'), ('wave', 'ఇద్దరూ చేయి ఊపుతూ – కామెంట్ ప్రశ్న ఆప్షన్ల కింద'))]
    blob = json.dumps({'shorts': pages, 'cast': cast, 'both': both, 'voices': voices, 'voiceHow': VOICE_HOW}, ensure_ascii=False).replace('</', '<\\/')
    os.makedirs(os.path.join(ROOT, 'tools', 'publish'), exist_ok=True)
    open(os.path.join(ROOT, 'tools', 'publish', 'quiz.html'), 'w', encoding='utf-8', newline='\n').write(tpl.replace('__DATA__', blob))
    print(f'{len(shorts)} Shorts, {sum(len(s["qs"]) for s in shorts)} questions')


if __name__ == '__main__':
    main()
