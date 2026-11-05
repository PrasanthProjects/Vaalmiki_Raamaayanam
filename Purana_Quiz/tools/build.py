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


SPEAKER = {'T': ('the grandfather', 'Chinni'), 'C': ('Chinni', 'the grandfather')}


def presenters_prompt(who):
    """One start frame per speaker: the speaker turned a little toward the camera, face clear and well lit, mouth
    slightly open; the listener's mouth closed. Lip-sync tools animate the face that is clearest, so this matters."""
    sp, ls = SPEAKER[who]
    return (STYLE + f'Setting: {SET}. ' + 'Characters (keep exactly this look in every Short): '
            + ' '.join(f'{v[1]}.' for v in CAST.values())
            + f' Moment: medium two-shot, the two sit together on the swing; {sp} is speaking, face turned three-quarters '
              f'toward the camera, clearly lit, mouth slightly open, a small hand gesture; {ls} listens with a curious '
              f'smile, lips closed, looking at {sp}. Both faces fully visible, nothing covering the mouths. ' + RESPECT)


def solo_prompt(key):
    """One reusable talking frame per character, alone on the swing, for every Short."""
    return (STYLE + f'Setting: {SET}. Medium close-up of one character only: {CAST[key][1]}. Sitting on the swing, '
            'facing the camera three-quarters, face clear and evenly lit, mouth slightly open as if speaking, a calm '
            'friendly expression, hands resting naturally on the lap. Soft blurred background. ' + RESPECT)


def solo_video(key):
    """One reusable talking loop per character: small mouth movement, small natural motion, starts and ends the same."""
    who = 'the grandfather' if key == 'TATAYYA' else 'Chinni'
    extra = ('a slow gentle nod and a warm smile, one small hand gesture' if key == 'TATAYYA'
             else 'a small lively head tilt and a bright smile, one small hand gesture')
    return (f'Animate the attached start frame as one continuous 10 second vertical shot that can loop: {who} is '
            f'talking calmly with small, natural mouth movements, soft blinks, {extra}, the shoulders breathing '
            'softly; the swing sways only a little, the lamp flame flickers. Movements stay small and slow, the face '
            'and clothes stay exactly the same, the camera does not move, no cuts, and the last frame matches the '
            'first so the clip loops smoothly. Audio: none.')


def talk_prompt(who):
    """For video tools that add lip movement themselves (no audio input): only the speaker's lips move."""
    sp, ls = SPEAKER[who]
    return (f'Animate the attached start frame as one continuous vertical shot, as long as the voice line: only {sp} '
            f'talks, with clear natural lip movement, blinks and a small hand gesture; {ls} keeps the lips closed, '
            'listens, smiles and nods slightly. The swing sways very gently, the lamp flame flickers. Same faces and '
            'clothes, the camera stays still, no cuts. Audio: soft ambient only.')


def answer_prompt(pic):
    return STYLE + f'A devotional illustration: {pic}. ' + RESPECT


def video_prompt(d):
    return (f'Animate the attached start frame as one continuous {d} second vertical shot: slow, gentle movement only — a '
            'soft push-in, light and cloth moving gently; the figures keep exactly the same look and stay in place; '
            'no sudden moves, no cuts. ' + RESPECT + ' Audio: soft ambient only.')


LIPSYNC = ('లిప్‌సింక్ సరిగ్గా రావాలంటే: (1) ముందు ElevenLabs లో ఒక్కో లైన్ వాయిస్ ఫైల్ చేయండి. (2) మాట్లాడేవారి ఇమేజ్ '
           '(తాతయ్య మాట్లాడుతూ / చిన్ని మాట్లాడుతూ) తీసుకోండి. (3) లిప్‌సింక్ టూల్‌లో (Kling "Lip Sync", Hedra, HeyGen, '
           'Runway లాంటివి) ఆ ఇమేజ్ + ఆ లైన్ ఆడియో పెట్టండి — నోరు ఆడియోకి సరిగ్గా కదులుతుంది. ఒక క్లిప్‌లో ఒక్కరే '
           'మాట్లాడాలి; టూల్ ముఖం అడిగితే మాట్లాడేవారి ముఖం ఎంచుకోండి. ఆప్షన్లు, జవాబు లైన్లు కార్డు/చిత్రం మీద '
           'వాయిస్ మాత్రమే — వాటికి లిప్‌సింక్ అక్కర్లేదు.')


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
    md += ['', '## టైమ్‌లైన్', '', '| సమయం | భాగం | ఎవరు | మాట | తెరపై | దృశ్యం |', '|---|---|---|---|---|---|']
    for t, d, part, who, say, screen, vis in rows:
        shown = 'తాతయ్య, చిన్ని ఊయల మీద' if vis == 'presenters' else 'ప్రశ్న కార్డు + 3 ఆప్షన్లు' if vis == 'options' else 'జవాబు చిత్రం'
        md.append(f"| {mmss(t)}–{mmss(t + d)} | {part} | {WHO.get(who, '–')} | {say or '–'} | {screen.replace(chr(10), ' · ')} | {shown} |")
    lips = [{'t': f'{mmss(r[0])}–{mmss(r[0] + r[1])}', 'part': r[2], 'who': WHO[r[3]], 'frame': r[3], 'say': r[4], 'd': r[1]}
            for r in rows if r[6] == 'presenters' and r[3]]
    md += ['', '## 🔊 వాయిస్ (రెండు గొంతులు)', '', VOICE_HOW, '']
    for k, (name, desc_, sample, sets) in VOICE_DESIGN.items():
        md += [f'### {CAST[k][0]} గొంతు ({name})', '', '```text', desc_, '```', '', '```text', sample, '```', '', f'సెట్టింగ్‌లు: {sets}', '']
    md += ['### లైన్లు', '', '```text', voice, '```', '', '## 👄 లిప్‌సింక్', '', LIPSYNC, '',
           '| సమయం | భాగం | ఎవరు మాట్లాడతారు | ఇమేజ్ | లైన్ |', '|---|---|---|---|---|']
    md += [f"| {l['t']} | {l['part']} | {l['who']} | {l['who']} మాట్లాడుతూ | {l['say']} |" for l in lips]
    md += ['', '## 🖼️ ఇమేజ్ / 🎥 వీడియో ప్రాంప్ట్‌లు', '',
           '**సూచన:** తాతయ్య–చిన్ని రెండు ఇమేజ్‌లు ఒక్కసారి చేస్తే అన్ని ప్రశ్నలకూ సరిపోతాయి. జవాబు చిత్రాలు 🖼️ ఇమేజ్ + నెమ్మది జూమ్ చాలు. ఆప్షన్ కార్డులు ఎడిటర్‌లో టెక్స్ట్‌తో చేయండి.', '']
    for k in 'TC':
        md += [f'### {WHO[k]} మాట్లాడుతూ — ఇమేజ్', '', '```text', presenters_prompt(k), '```', '',
               f'### {WHO[k]} మాట్లాడుతూ — వీడియో (ఆడియో పెట్టలేని టూల్ అయితే మాత్రమే)', '', '```text', talk_prompt(k), '```', '']
    for lab, r in zip(labels, pics):
        md += [f'### {lab} చిత్రం', '', '```text', answer_prompt(r[6]), '```', '', '```text', video_prompt(r[1]), '```', '']
    md += ['## 📤 అప్‌లోడ్', '', '```text', title, '```', '', '```text', desc, '```', '']
    if x:
        md += ['### 📌 పిన్ కామెంట్ (అప్‌లోడ్ అయిన వెంటనే)', '', '```text', pin, '```', '',
               '### ✅ జవాబు రిప్లై (తరువాతి Short వచ్చాక, పిన్ కామెంట్ కింద)', '', '```text', reveal, '```', '']
    page = {'id': s['id'], 'title': s['title'], 'book': BOOK[s['book']], 'len': mmss(total), 'voice': voice, 'ytitle': title,
            'desc': desc, 'qs': s['qs'], 'lips': lips, 'lipHow': LIPSYNC,
            'pres': {k: presenters_prompt(k) for k in 'TC'}, 'talk': {k: talk_prompt(k) for k in 'TC'},
            'answers': [{'label': lab, 'img': answer_prompt(r[6]), 'vid': video_prompt(r[1])} for lab, r in zip(labels, pics)],
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
             'soloImg': solo_prompt(k), 'soloVid': solo_video(k)} for k, v in CAST.items()]
    tpl = open(os.path.join(ROOT, 'tools', 'page_template.html'), encoding='utf-8').read()
    voices = [{'name': CAST[k][0], 'en': v[0], 'desc': v[1], 'sample': v[2], 'sets': v[3]} for k, v in VOICE_DESIGN.items()]
    blob = json.dumps({'shorts': pages, 'cast': cast, 'voices': voices, 'voiceHow': VOICE_HOW}, ensure_ascii=False).replace('</', '<\\/')
    os.makedirs(os.path.join(ROOT, 'tools', 'publish'), exist_ok=True)
    open(os.path.join(ROOT, 'tools', 'publish', 'quiz.html'), 'w', encoding='utf-8', newline='\n').write(tpl.replace('__DATA__', blob))
    print(f'{len(shorts)} Shorts, {sum(len(s["qs"]) for s in shorts)} questions')


if __name__ == '__main__':
    main()
