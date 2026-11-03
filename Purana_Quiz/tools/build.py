"""Quiz Shorts "పురాణ ప్రశ్నలు – తాతయ్య, చిన్ని": one kit per Short and one phone page.

usage:  python Purana_Quiz/tools/build.py

Reads   Purana_Quiz/data/quiz.txt          the Shorts (4 questions each, with the source of every answer)
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
            sid, title, book = (x.strip() for x in line[6:].split('|'))
            shorts.append({'id': sid, 'title': title, 'book': book, 'qs': []})
        elif line.startswith('Q '):
            f = [x.strip() for x in line[2:].split('|')]
            assert len(f) == 9, f'{shorts[-1]["id"]}: a Q line needs 9 fields: {line[:60]}'
            who, q, a, b, c, ans, src, why, pic = f
            assert ans in 'ABC' and who in WHO
            shorts[-1]['qs'].append({'who': who, 'q': q, 'opts': [a, b, c], 'ans': ans, 'src': src, 'why': why, 'pic': pic})
    for s in shorts:
        assert 3 <= len(s['qs']) <= 5, f"{s['id']}: 3 to 5 questions"
    return shorts


def mmss(t):
    return f'{t // 60}:{t % 60:02d}'


def timeline(s, n):
    """Hook → each question (ask 4 s, options 4 s, countdown 3 s, answer + source 5 s) → score and the next Short."""
    rows, t = [], 0
    rows.append((t, 3, 'హుక్', 'C' if n % 2 else 'T', f"{BOOK[s['book']]} క్విజ్! ఈ {len(s['qs'])} ప్రశ్నలకు మీకు జవాబు తెలుసా?",
                 f"{s['title']} · {len(s['qs'])} ప్రశ్నలు", 'presenters'))
    t += 3
    for i, q in enumerate(s['qs'], 1):
        other = 'C' if q['who'] == 'T' else 'T'
        k = 'ABC'.index(q['ans'])
        rows.append((t, 4, f'ప్రశ్న {i}', q['who'], q['q'], f'ప్రశ్న {i}: {q["q"]}', 'presenters'))
        rows.append((t + 4, 4, 'ఆప్షన్లు', q['who'], '; '.join(f'{L}, {o}' for L, o in zip('ABC', q['opts'])) + '.',
                     '  '.join(f'{L}) {o}' for L, o in zip('ABC', q['opts'])), 'options'))
        rows.append((t + 8, 3, 'కౌంట్‌డౌన్', '', '', '3… 2… 1…  (టిక్ టిక్ శబ్దం, మాటలు లేవు)', 'options'))
        rows.append((t + 11, 5, 'జవాబు', other, f"జవాబు {q['ans']}, {q['opts'][k]}! {q['why']}",
                     f"✅ {q['ans']}) {q['opts'][k]}\nమూలం: {q['src']}", q['pic']))
        t += 16
    cta = ' '.join(CTAS[(n + j) % len(CTAS)] for j in range(2))
    rows.append((t, 7, 'ముగింపు', 'T', f'ఎన్ని సరిగ్గా చెప్పారు? {cta}', 'మీ స్కోర్ ఎంత? 👇', 'presenters'))
    return rows, t + 7


def presenters_prompt(row):
    who = row[3] or 'T'
    speaking = CAST['TATAYYA' if who == 'T' else 'CHINNI'][0]
    return (STYLE + f'Setting: {SET}. ' + 'Characters (keep exactly this look in every Short): '
            + ' '.join(f'{v[1]}.' for v in CAST.values())
            + f' Moment: the two sit together on the swing; {speaking} is speaking with a lively expression and a small '
              f'hand gesture while the other listens, curious. ' + RESPECT)


def answer_prompt(pic):
    return STYLE + f'A devotional illustration: {pic}. ' + RESPECT


def video_prompt(row):
    if row[6] == 'presenters':
        return ('Animate the attached start frame as one continuous 4 second vertical shot: the speaking character talks '
                'with natural lip movement, blinks and a small hand gesture; the other listens and nods; the swing sways '
                'very gently, the lamp flame flickers. Characters keep exactly the same faces and clothes; no sudden moves, '
                'no cuts. Audio: soft ambient only.')
    return ('Animate the attached start frame as one continuous 5 second vertical shot: slow, gentle movement only — a '
            'soft push-in, light and cloth moving gently; the figures keep exactly the same look and stay in place; '
            'no sudden moves, no cuts. ' + RESPECT + ' Audio: soft ambient only.')


def kit(s, n):
    rows, total = timeline(s, n)
    voice = '\n'.join(f'[{WHO[r[3]]}]: {r[4]}' for r in rows if r[3] and r[4])
    pics = [r for r in rows if r[6] not in ('presenters', 'options')]
    title = f"{s['title']} | {BOOK[s['book']]} క్విజ్ #{n} | పురాణ ప్రశ్నలు"
    desc = (f"{title}\n\nతాతయ్య, చిన్ని అడిగే {len(s['qs'])} పురాణ ప్రశ్నలు. మీ జవాబులు కామెంట్‌లో రాయండి!\n\n📖 మూలాలు:\n"
            + '\n'.join(f"{i}. {q['src']}" for i, q in enumerate(s['qs'], 1))
            + '\n\n#పురాణప్రశ్నలు #రామాయణం #మహాభారతం #భాగవతం #TeluguQuiz #PuranaQuiz #Shorts')
    md = [f"# {s['id']} · {s['title']}", '', f"{BOOK[s['book']]} · {len(s['qs'])} ప్రశ్నలు · సుమారు {mmss(total)} · నిలువు 9:16 Short", '',
          '## ప్రశ్నలు, జవాబులు, మూలాలు', '', '| # | అడిగేది | ప్రశ్న | జవాబు | మూలం |', '|---|---|---|---|---|']
    for i, q in enumerate(s['qs'], 1):
        md.append(f"| {i} | {WHO[q['who']]} | {q['q']} | **{q['ans']}) {q['opts']['ABC'.index(q['ans'])]}** | {q['src']} |")
    md += ['', '## టైమ్‌లైన్', '', '| సమయం | భాగం | ఎవరు | మాట | తెరపై | దృశ్యం |', '|---|---|---|---|---|---|']
    for t, d, part, who, say, screen, vis in rows:
        shown = 'తాతయ్య, చిన్ని ఊయల మీద' if vis == 'presenters' else 'ప్రశ్న కార్డు + 3 ఆప్షన్లు' if vis == 'options' else 'జవాబు చిత్రం'
        md.append(f"| {mmss(t)}–{mmss(t + d)} | {part} | {WHO.get(who, '–')} | {say or '–'} | {screen.replace(chr(10), ' · ')} | {shown} |")
    md += ['', '## 🔊 వాయిస్ (రెండు గొంతులు)', '', 'ElevenLabs లో తాతయ్య, చిన్ని గొంతులు వేర్వేరుగా చేసి, ఒక్కో లైన్ ఆ గొంతుతో జనరేట్ చేయండి.', '',
           '```text', voice, '```', '', '## 🖼️ ఇమేజ్ / 🎥 వీడియో ప్రాంప్ట్‌లు', '',
           '**సూచన:** తాతయ్య–చిన్ని షాట్లు 🎥 వీడియో మంచిది (మాట్లాడుతున్నట్టు, లిప్‌సింక్ టూల్‌తో ఇంకా బాగుంటుంది). జవాబు చిత్రాలు 🖼️ ఇమేజ్ + నెమ్మది జూమ్ చాలు. ఆప్షన్ కార్డులు ఎడిటర్‌లో టెక్స్ట్‌తో చేయండి.', '',
           '### తాతయ్య–చిన్ని (ఒకే ఇమేజ్ అన్ని ప్రశ్నలకూ వాడవచ్చు)', '', '```text', presenters_prompt(rows[0]), '```', '',
           '```text', video_prompt(rows[0]), '```', '']
    for i, r in enumerate(pics, 1):
        md += [f'### జవాబు {i} చిత్రం', '', '```text', answer_prompt(r[6]), '```', '', '```text', video_prompt(r), '```', '']
    md += ['## 📤 అప్‌లోడ్', '', '```text', title, '```', '', '```text', desc, '```', '']
    page = {'id': s['id'], 'title': s['title'], 'book': BOOK[s['book']], 'len': mmss(total), 'voice': voice, 'ytitle': title,
            'desc': desc, 'qs': s['qs'], 'pres': presenters_prompt(rows[0]), 'presVideo': video_prompt(rows[0]),
            'answers': [{'img': answer_prompt(r[6]), 'vid': video_prompt(r)} for r in pics],
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
             'Front view, side view and three-quarter view, full body, consistent look. ' + RESPECT} for k, v in CAST.items()]
    tpl = open(os.path.join(ROOT, 'tools', 'page_template.html'), encoding='utf-8').read()
    blob = json.dumps({'shorts': pages, 'cast': cast}, ensure_ascii=False).replace('</', '<\\/')
    os.makedirs(os.path.join(ROOT, 'tools', 'publish'), exist_ok=True)
    open(os.path.join(ROOT, 'tools', 'publish', 'quiz.html'), 'w', encoding='utf-8', newline='\n').write(tpl.replace('__DATA__', blob))
    print(f'{len(shorts)} Shorts, {sum(len(s["qs"]) for s in shorts)} questions')


if __name__ == '__main__':
    main()
