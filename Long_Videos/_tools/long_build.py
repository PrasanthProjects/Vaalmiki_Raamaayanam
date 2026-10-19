"""Add the long-video production kit to episode files.

usage:  python long_build.py <data file>          e.g. python long_build.py data/0_1_Parichayam_Baala.txt

For every '### E<k>.<nn>' block in the data file it reads the episode's scene table and writes:
  - a "లాంగ్ వీడియో కిట్" section at the end of the episode .md (between LONG_VIDEO_KIT markers;
    rebuilding replaces it, the rest of the file is never touched)
  - Long_Videos/captions/<kaanda>/<ep>.srt
  - one clip-helper page per kaanda (Long_Videos/<kaanda>_CLIPS_HELPER.html) and its claude.ai copy
  - Long_Videos/00_CHARACTER_REFERENCES.md (realistic reference prompts for every character used)
The scene tables themselves stay the single source: edit a scene there, then rebuild.
"""
import glob
import json
import math
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
LONG = os.path.dirname(TOOLS)
ROOT = os.path.dirname(LONG)
sys.path.insert(0, TOOLS)
from long_style import STYLE, RESPECT, TAIL, VN, SN, KUM, character, names_in, stage_of, STAGES, ep_key  # noqa: E402

KAANDAS = {0: ('00_Parichayam', 'పరిచయం'), 1: ('1 - Baala Khaanda', 'బాలకాండ'), 2: ('2 - Ayodhya Khaanda', 'అయోధ్యకాండ'),
           3: ('3 - Aranya Khaanda', 'అరణ్యకాండ'), 4: ('4 - Kishkinda Khaanda', 'కిష్కింధకాండ'),
           5: ('5 - Sundhara Khaanda', 'సుందరకాండ'), 6: ('6 - Yudha Khaanda', 'యుద్ధకాండ')}
BUMPER, OUTRO = 4, 20          # bumper from 00_INTRO_OUTRO_TEMPLATES.md; outro = YouTube's 20 s end screen
START, END = '<!-- LONG_VIDEO_KIT_START -->', '<!-- LONG_VIDEO_KIT_END -->'
HASHTAGS = '#ramayanam #ramayanamintelugu #valmikiramayanam #telugudevotional #puranakathasravanam'

GROUPS = [  # crowd words in a scene -> one consistent crowd description
    (r'\b(sages|rishis|maharshis|maharshi-group|hermits)\b',
     'a group of venerable sages with white beards and matted hair, ochre and white robes, kamandalus; '
     'about two thirds with the white Vishnu namam and one third with three ash-white Shiva lines; every face different'),
    (r'\bvanara (army|soldiers|host|troops)|\bvanaras\b',
     'an army of vanara warriors (muscular, upright, human-proportioned bodies with monkey faces and tails), '
     'varied fur tones and builds, dhotis and sashes, white Vishnu namam'),
    (r'\brakshasa (army|soldiers|host|troops)|\brakshasas\b',
     'rakshasa soldiers with varied builds, skin tones and dark ornate armour, some with moustaches, '
     'three ash-white Shiva lines; fierce but not horror'),
    (r'\b(devas|devatas|gods|celestials)\b',
     'radiant devas in silk and gold crowns on clouds, each with a small red kumkum dot'),
    (r'\b(citizens|crowd|townspeople|people of ayodhya|courtiers|ministers)\b',
     'people of the kingdom in traditional South Indian dress (veshti and angavastram, single-wrap drapes), '
     'every forehead with a red kumkum dot or namam'),
]
MOTION = ('leap', 'fly', 'flies', 'flying', 'descend', 'arrow', 'running', 'runs ', 'charg', 'fight', 'battle',
          'swing', 'crash', 'pierc', 'burn', 'gallop', 'dive', 'ascend', 'emerg', 'transform', 'storm', 'lightning',
          'throw', 'hurl', 'roar', 'rising', 'rises', 'flow', 'pour', 'collapse', 'falls', 'shatter', 'breaks',
          'snaps', 'explod', 'flames', 'rain', 'walk', 'procession', 'chariot', 'dance')
MOVES = ['నెమ్మదిగా జూమ్-ఇన్ (100% → 110%)', 'ఎడమ నుండి కుడికి నెమ్మదిగా ప్యాన్',
         'నెమ్మదిగా జూమ్-అవుట్ (112% → 100%)', 'కుడి నుండి ఎడమకి నెమ్మదిగా ప్యాన్']


def mmss(s):
    return f'{s // 60}:{s % 60:02d}' if s < 3600 else f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}'


def episode_file(ep):
    k = int(ep[1:].split('.')[0])
    hits = glob.glob(os.path.join(ROOT, KAANDAS[k][0], f'{ep}_*.md'))
    assert len(hits) == 1, f'{ep}: found {hits}'
    return hits[0]


def read_data(path):
    eps = {}
    for blk in re.split(r'^### ', open(path, encoding='utf-8').read(), flags=re.M)[1:]:
        ep, body = blk.split('\n', 1)
        f = dict(l.split(': ', 1) for l in body.strip().split('\n') if ': ' in l)
        head = [x.strip() for x in f['HEAD'].split(' | ')]
        assert len(head) == 3 and head[1] in head[0], f'{ep}: HEAD needs "headline | highlight | sub-line"'
        chapters = []
        for part in f['CH'].split(' ; '):
            n, title = part.strip().split(' ', 1)
            chapters.append((int(n), title.strip()))
        eps[ep.strip()] = {'head': head, 'sum': f['SUM'], 'chapters': chapters, 'pin': f['PIN']}
    return eps


def parse_episode(path):
    text = open(path, encoding='utf-8').read()
    title_line = text.split('\n', 1)[0]
    tel = re.match(r'#\s*\S+\s*—\s*(.+?)(?:\s*\(|$)', title_line).group(1).strip()
    src = re.search(r'Source:\s*(pp?\.\s*[\d\-–, ]+)', text)
    script = text.split('## Script', 1)[1].split('\n---', 1)[0]
    header = next(l for l in script.split('\n') if l.startswith('| #'))
    cols = [c.strip() for c in header.strip().strip('|').split('|')]
    i_len, i_vis = cols.index('Clip length'), cols.index('Visual prompt')
    i_nar = cols.index('Telugu narration (verbatim)')
    i_loc = cols.index('Location register') if 'Location register' in cols else None
    scenes = []
    for line in script.split('\n'):
        if re.match(r'\|\s*\d+\s*\|', line):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            scenes.append({'no': int(c[0]), 'secs': int(c[i_len].rstrip('s')), 'visual': c[i_vis],
                           'loc': c[i_loc] if i_loc is not None else '', 'narration': c[i_nar]})
    return text, tel, (src.group(1).strip() if src else ''), scenes


def clean_visual(v):
    v = re.sub(r'\[[^\]]*(?:Lock|Bible|Stage|stage)[^\]]*\]\s*', '', v)
    v = re.sub(r'\s*\((?:see|per|use)[^)]*\)', '', v, flags=re.I)
    v = re.sub(r",?\s*per (?:the )?style guide'?s?[^,.;]*", '', v, flags=re.I)
    return re.sub(r'\s+', ' ', v).strip(' ,;')


def scene_text(scene):
    """The cleaned description; gives it back its subject when a removed [Use X lock] tag held the name."""
    v = clean_visual(scene['visual']).rstrip(' .')
    if v and v[0].islower():
        who = [k.title() for k in names_in(scene['visual'])]
        if who:
            v = ' and '.join(who[:2]) + ' ' + v
    return v


def scene_cast(scene, ep):
    keys = names_in(scene['visual'])
    if ep_key(ep) < (4, 0):   # before Kishkindha "Nila" is the forest of that name, not the vanara
        keys = [k for k in keys if k != 'NALA']
    looks =[x for x in (character(k, ep) for k in keys) if x]
    low = scene['visual'].lower()
    looks += [desc for pat, desc in GROUPS if re.search(pat, low)]
    refs = []
    for k in keys:
        if character(k, ep):
            stage = stage_of('RAMA' if k == 'LAKSHMANA' else k, ep) if k in STAGES else None
            refs.append(f'{k}_{stage}' if stage else k)
    return looks, refs


def kinds_for(scenes):
    """About 3 in 10 scenes get real video: the ones with the most motion. The rest are stills."""
    score = [sum(s['visual'].lower().count(w) for w in MOTION) for s in scenes]
    quota = max(1, math.ceil(0.3 * len(scenes)))
    pick = sorted((i for i in range(len(scenes)) if score[i] > 0), key=lambda i: (-score[i], i))[:quota]
    return ['video' if i in pick else 'image' for i in range(len(scenes))]


def editor_move(visual, i):
    v = visual.lower()
    if any(w in v for w in ('close on', 'close-up', 'closeup', 'close up', 'face')):
        return MOVES[0]
    if any(w in v for w in ('wide', 'aerial', 'landscape', 'panorama', 'city', 'army')):
        return MOVES[1]
    return MOVES[i % 4]


def scene_prompt(scene, kind, looks):
    who = ' '.join(f'{x}.' for x in looks)
    loc = f"Setting: {scene['loc']}. " if scene['loc'] else ''
    body = (f"Style: {STYLE}. {loc}" + (f"Characters (keep exactly this look): {who} " if who else '')
            + f"Scene: {scene_text(scene)}. "
            "Correct anatomy and natural hands; no extra characters, limbs or faces beyond those described. "
            f"{RESPECT} {TAIL}")
    if kind == 'video':
        return ("Cinematic 16:9 shot, 8 seconds, slow and steady, main subject well framed. " + body
                .replace('Correct anatomy', 'Smooth, physically consistent motion with no morphing or flicker. Correct anatomy'))
    return "Cinematic 16:9 still frame, 1920x1080, film still quality. " + body


def thumb_prompt(scenes, ep):
    pick = next((s for s in scenes if names_in(s['visual'])), scenes[0])
    looks, refs = scene_cast(pick, ep)
    who = ' '.join(f'{x}.' for x in looks)
    return (("YouTube thumbnail key art, 16:9, 1280x720, single still image. "
             f"Style: {STYLE}. " + (f"Characters: {who} " if who else '')
             + f"Scene: {scene_text(pick)}. Bold, emotional close-up of the main character on the right "
             "half of the frame, strong expression, high contrast, glowing rim light, rich colour. Keep the left 45% "
             "of the frame a clean darker area with no important detail (space for a Telugu headline). "
             f"{RESPECT} No text, letters, numbers, logos or watermarks in the image."), refs)


# ---------- captions ----------

def chunks(text, limit=42):
    out, line = [], ''
    for w in text.split():
        if line and len(line) + 1 + len(w) > limit:
            out.append(line)
            line = w
        else:
            line = f'{line} {w}'.strip()
    return out + ([line] if line else [])


def srt_time(sec):
    ms = int(round(sec * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def srt(scenes):
    cues, t = [], BUMPER
    for s in scenes:
        lines = chunks(s['narration'])
        total = sum(len(l) for l in lines) or 1
        a = t
        for l in lines:
            b = a + s['secs'] * len(l) / total
            cues.append((a, b, l))
            a = b
        t += s['secs']
    return '\n'.join(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{l}\n' for i, (a, b, l) in enumerate(cues, 1))


# ---------- one episode ----------

CTAS = [
    'రామాయణాన్ని మొదటి నుండి చివరి వరకు భాగం భాగంగా వినడానికి ఛానల్‌ని సబ్‌స్క్రైబ్ చేసి, బెల్ ఐకాన్ నొక్కండి.',
    'ఈ భాగం నచ్చితే లైక్ చేసి, మీ కుటుంబంతో షేర్ చేయండి. ఛానల్‌ని సబ్‌స్క్రైబ్ చేయడం మరచిపోకండి.',
    'మీ అభిప్రాయం కామెంట్‌లో రాయండి. ఏ భాగమూ మిస్ అవ్వకుండా ఇప్పుడే సబ్‌స్క్రైబ్ చేయండి.',
    'రాముడి కథను మీ పిల్లలకూ వినిపించండి. మరిన్ని భాగాల కోసం మన ఛానల్‌లో చేరండి.',
    'ప్రతి భాగం ఒక జీవిత పాఠం. ఒక్కటీ మిస్ అవ్వకుండా బెల్ ఐకాన్ నొక్కండి.',
    'ఈ పుణ్య కథను నలుగురితో పంచుకోండి. సబ్‌స్క్రైబ్ చేసి ఈ ప్రయాణంలో మాతో ఉండండి.',
    '"జై శ్రీరామ్" అని కామెంట్ చేసి, ఛానల్‌ని సబ్‌స్క్రైబ్ చేయండి.',
]
CTA_VISUAL = ('A glowing palm-leaf manuscript of the Ramayana resting on a carved wooden stand beside a lit brass oil '
              'lamp in a quiet temple courtyard at golden hour, marigold petals around it')
TEASER_STARTS = ('తర్వాత', 'తరువాత', 'తర్వాతి', 'ఇది బాలకాండ')


def read_narration(path):
    """Shorts-style spoken layers per episode: hook, one bridge per chapter change, life lesson."""
    out = {}
    if not os.path.exists(path):
        return out
    for blk in re.split(r'^### ', open(path, encoding='utf-8').read(), flags=re.M)[1:]:
        ep, body = blk.split('\n', 1)
        f = dict(l.split(': ', 1) for l in body.strip().split('\n') if ': ' in l)
        out[ep.strip()] = {'hook_from': int(f['HOOK_FROM']), 'hook': f['HOOK'].strip(),
                           'bridges': [b.strip() for b in f['BRIDGES'].split(' ; ')], 'lesson': f['LESSON'].strip()}
    return out


def speak_secs(text):
    """Rough Telugu speaking time: about 2.2 words a second, plus a breath."""
    return max(4, math.ceil(len(text.split()) / 2.2) + 1)


def lesson_item(extra, scenes):
    pick = next((s for s in scenes if names_in(s['visual'])), scenes[0])
    return {'id': 'L', 'label': 'జీవిత పాఠం', 'kind': 'image', 'secs': speak_secs(extra['lesson']),
            'narration': extra['lesson'], 'new': True, 'loc': pick['loc'], 'onscreen': '',
            'visual': f"A quiet, reflective close moment: {pick['visual']}. Soft warm light, calm and contemplative"}


def _words(text):
    return {w.strip('.,!?…"\'—–-') for w in text.split() if len(w) > 3}


def sequence(scenes, d, extra, ep_index):
    """Episode order: hook, scenes (a bridge line before each new chapter), lesson, teaser, subscribe line."""
    seq = []
    bridges, titles = {}, dict(d['chapters'][1:])
    if extra:
        assert len(extra['bridges']) == len(d['chapters']) - 1, \
            f"{d['ep']}: {len(extra['bridges'])} bridge lines for {len(d['chapters']) - 1} chapter changes"
        bridges = dict(zip([n for n, _ in d['chapters'][1:]], extra['bridges']))
        # A bridge must tease, not repeat: refuse one that shares 2+ words with the line it leads into,
        # and a hook that promises "ఈ భాగంలో…" right before a recap that promises the same.
        by_no = {s['no']: s for s in scenes}
        for n, line in bridges.items():
            shared = _words(line) & _words(by_no[n]['narration'][:120])
            assert len(shared) < 2, f"{d['ep']}: bridge before scene {n} repeats it ({', '.join(sorted(shared))}): {line}"
        assert 'ఈ భాగంలో' not in extra['hook'], f"{d['ep']}: end the hook on its peak, not with 'ఈ భాగంలో…'"
        src = next(s for s in scenes if s['no'] == extra['hook_from'])
        seq.append({'id': 'H', 'label': 'హుక్', 'kind': 'video', 'secs': speak_secs(extra['hook']),
                    'narration': extra['hook'], 'new': True, 'loc': src['loc'], 'onscreen': '',
                    'visual': f"Fast, dramatic flash-forward teaser of the episode's biggest moment: {src['visual']}"})
    last = scenes[-1]
    teaser_last = last['narration'].startswith(TEASER_STARTS)
    for s in scenes:
        if s['no'] in bridges:
            seq.append({'id': f"B{s['no']}", 'label': f"బ్రిడ్జ్ → {titles[s['no']]}", 'kind': 'image',
                        'secs': speak_secs(bridges[s['no']]), 'narration': bridges[s['no']], 'new': True,
                        'loc': s['loc'], 'onscreen': titles[s['no']],
                        'visual': f"{s['visual']}. Composed with calm open space on one side for an on-screen chapter title"})
        if extra and s is last and teaser_last:
            seq.append(lesson_item(extra, scenes))
        seq.append({'id': str(s['no']), 'label': f"సీన్ {s['no']}", 'kind': None, 'secs': s['secs'],
                    'narration': s['narration'], 'new': False, 'visual': s['visual'], 'loc': s['loc'],
                    'onscreen': '', 'scene': s})
    if extra and not teaser_last:
        seq.append(lesson_item(extra, scenes))
    if extra:
        cta = CTAS[ep_index % len(CTAS)]
        seq.append({'id': 'C', 'label': 'సబ్‌స్క్రైబ్', 'kind': 'image', 'secs': speak_secs(cta), 'narration': cta,
                    'new': True, 'visual': CTA_VISUAL, 'loc': '', 'onscreen': 'SUBSCRIBE 🔔'})
    return seq


def is_verse(text):
    return '।' in text or '॥' in text


def first_sentence(text, limit=90):
    t = re.split(r'(?<=[.!?])\s', text.strip(), maxsplit=1)[0]
    return t if len(t) <= limit else t[:limit].rsplit(' ', 1)[0] + '…'


def expand(seq, scenes):
    """Retention pass: on-screen card for every verse, a recap-length check, and two stills for long still scenes."""
    nxt = {s['no']: (scenes[i + 1] if i + 1 < len(scenes) else None) for i, s in enumerate(scenes)}
    out = []
    for item in seq:
        item = dict(item)
        if 'scene' in item:
            sc = item['scene']
            if is_verse(sc['narration']):
                n = nxt[sc['no']]
                meaning = first_sentence(n['narration']) if n and not is_verse(n['narration']) else ''
                item['onscreen'] = 'శ్లోకం తెలుగు లిపిలో, అక్షరం అక్షరం కనిపిస్తూ' + (f' · కింద అర్థం: {meaning}' if meaning else '')
            if sc['narration'].startswith('గత భాగ') and sc['secs'] > 8:
                item['tip'] = 'రీక్యాప్‌ను ఎడిట్‌లో 8 సెకన్లలోపు కుదించండి – హుక్ తరువాత వీక్షకులు వెంటనే కొత్త కథ కోరుకుంటారు.'
        if item['kind'] == 'image' and item['secs'] >= 11 and not item['new']:
            a = math.ceil(item['secs'] / 2)
            out.append(dict(item, id=item['id'] + 'a', label=item['label'] + ' (1/2)', secs=a,
                            visual='Wide establishing view: ' + item['visual']))
            out.append(dict(item, id=item['id'] + 'b', label=item['label'] + ' (2/2)', secs=item['secs'] - a,
                            visual='Closer, emotional framing of the same moment: ' + item['visual'],
                            narration='(పై నెరేషన్ కొనసాగుతుంది – చిత్రం మాత్రమే మారుతుంది)', cont=True, tip=''))
        else:
            out.append(item)
    return out


CUES = {
    'H': '[హుక్ · ఉత్సాహంగా, కొంచెం వేగంగా, ప్రశ్న మీద స్వరం పైకి]',
    'B': '[బ్రిడ్జ్ · చిన్న విరామం తరువాత, ఆసక్తి రేకెత్తించేలా]',
    'L': '[జీవిత పాఠం · నెమ్మదిగా, ఆత్మీయంగా, శ్రోతతో మాట్లాడుతున్నట్లు]',
    'C': '[సబ్‌స్క్రైబ్ · చిరునవ్వుతో, సహజంగా]',
    'V': '[శ్లోకం · నెమ్మదిగా, శ్రావ్యంగా, ప్రతి పాదం తరువాత విరామం]',
}


def breath(text, verse=False, limit=70):
    """Split narration into lines a narrator can say in one breath."""
    if verse:
        return [p.strip() + (' ।' if not p.strip().endswith(('।', '॥')) else '')
                for p in re.split(r'(?<=।)', text) if p.strip() and p.strip() != '।']
    out = []
    for sent in re.split(r'(?<=[.!?])\s+', text.strip()):
        while len(sent) > limit:
            cut = max(sent.rfind(', ', 0, limit), sent.rfind(' — ', 0, limit))
            if cut <= 20:
                break
            out.append(sent[:cut + 1].strip())
            sent = sent[cut + 1:].strip()
        if sent:
            out.append(sent)
    return out


def performance_script(spoken):
    """Recording script: a delivery note per part, breath-sized lines, ⏸ where a pause belongs."""
    out = []
    for x in spoken:
        verse = not x['new'] and is_verse(x['narration'])
        cue = CUES[x['id'][0]] if x['new'] else (CUES['V'] if verse else None)
        if cue:
            out.append(cue)
        out += breath(x['narration'], verse)
        if x['new'] or verse:
            out.append('⏸')
    return '\n'.join(out)


def build_episode(ep, d, refs_used, extra, ep_index):
    path = episode_file(ep)
    text, tel, src, scenes = parse_episode(path)
    k = int(ep[1:].split('.')[0])
    folder, kaanda_te = KAANDAS[k]
    d = dict(d, ep=ep)
    scene_kinds = dict(zip([s['no'] for s in scenes], kinds_for(scenes)))
    seq = sequence(scenes, d, extra, ep_index)
    for item in seq:
        if item['kind'] is None:
            item['kind'] = scene_kinds[item['scene']['no']]
    spoken = list(seq)            # what is said, in order (captions, recording script)
    seq = expand(seq, scenes)     # what is shown (clips)
    t = BUMPER
    for item in seq:
        item['start'] = t
        t += item['secs']
    total = t + OUTRO
    body_end = next((x['start'] for x in seq if x['id'] == 'C'), t)

    # chapters: the first at 0:00, the rest where their bridge (or first scene) starts; each at least 10 s
    start_of = {}
    for item in seq:
        if item['id'].startswith('B'):
            start_of[int(item['id'][1:])] = item['start']
        elif 'scene' in item and item['scene']['no'] not in start_of:
            start_of[item['scene']['no']] = item['start']
    chap = []
    for i, (n, title) in enumerate(d['chapters']):
        assert n in start_of, f'{ep}: chapter scene {n} not in the scene table'
        chap.append((0 if i == 0 else start_of[n], title))
    assert len(chap) >= 3, f'{ep}: YouTube needs at least 3 chapters'
    ends = [c[0] for c in chap[1:]] + [total]
    for (a, title), b in zip(chap, ends):
        assert b - a >= 10, f'{ep}: chapter "{title}" is {b - a}s (YouTube minimum is 10s)'

    cards, md_items = [], []
    for i, item in enumerate(seq):
        s = {'visual': item['visual'], 'loc': item['loc']}
        looks, refs = scene_cast(s, ep)
        refs_used.update(refs)
        kind, secs = item['kind'], item['secs']
        note = ''
        if kind == 'video' and secs > 8:
            note = (f"Flow 8 సెకన్లు ఇస్తుంది; మిగిలిన {secs - 8} సె కోసం చివరి ఫ్రేమ్‌ను నెమ్మదిగా జూమ్‌తో "
                    "పట్టుకోండి లేదా క్లిప్‌ను కొద్దిగా స్లో చేయండి.")
        if item['onscreen']:
            note = (note + ' ' if note else '') + f"తెరపై టెక్స్ట్: «{item['onscreen']}»"
        if item.get('tip'):
            note = (note + ' ' if note else '') + item['tip']
        move = '' if kind == 'video' else editor_move(item['visual'], i)
        a = item['start']
        card = {'no': item['id'], 'time': f"{mmss(a)} – {mmss(a + secs)}", 'label': f"{item['label']} · {secs} సె",
                'kind': kind, 'narration': item['narration'], 'refs': refs, 'move': move, 'note': note,
                'prompt': scene_prompt(s, kind, looks)}
        cards.append(card)
        head = '🎥 వీడియో' if kind == 'video' else '🖼️ ఇమేజ్ + కదలిక'
        star = ' · ✨ కొత్తది' if item['new'] else (' · 🔁 అదే నెరేషన్, కొత్త చిత్రం' if item.get('cont') else '')
        nar = item['narration']
        short = nar if item['new'] or len(nar) <= 110 else nar[:110].rsplit(' ', 1)[0] + '…'
        lines = [f"#### {item['label']} · {card['time']} · {secs} సె · {head}{star}\n",
                 f"- **నెరేషన్:** {short}",
                 f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in refs) if refs else 'అవసరం లేదు'}"]
        if move:
            lines.append(f'- **ఎడిటర్‌లో కదలిక:** {move}')
        if note:
            lines.append(f'- **గమనిక:** {note}')
        lines.append(f"\n```text\n{card['prompt']}\n```\n")
        md_items.append('\n'.join(lines))

    recording = performance_script(spoken)

    main, hl, sub = d['head']
    tprompt, trefs = thumb_prompt(scenes, ep)
    refs_used.update(trefs)
    title = f'{tel} | Ramayanam {ep} | రామాయణం తెలుగులో'
    if len(title) > 100:
        title = f'{tel} | Ramayanam {ep}'
    assert len(title) <= 100, f'{ep}: title is {len(title)} characters'
    chapters_txt = '\n'.join(f'{mmss(a)} {t}' for a, t in chap)
    desc = (f"{title}\n\n{d['sum']}\n\n⏱️ అధ్యాయాలు\n{chapters_txt}\n\n"
            f"📖 మూలం: చిత్రరూపంలో సంపూర్ణ వాల్మీకి రామాయణము" + (f", {src}" if src else '') + "\n"
            "🔔 పురాణ కథా శ్రవణం – రామాయణం మొదటి నుండి చివరి వరకు, భాగం భాగంగా.\n\n"
            f"{HASHTAGS} #{kaanda_te.replace(' ', '')}")
    tags = ', '.join(['రామాయణం', 'శ్రీరాముడు', 'వాల్మీకి రామాయణం', kaanda_te, tel, 'Ramayanam in Telugu',
                      'Valmiki Ramayanam', 'Telugu devotional', 'Purana Katha Shravanam'])
    srt_rel = f'Long_Videos/captions/{folder}/{ep}.srt'
    n_video = sum(c['kind'] == 'video' for c in cards)
    n_new = sum(1 for x in seq if x['new'])

    new_md = ''
    if extra:
        new_md = '\n'.join([
            '### 1. 🎙️ కొత్త నెరేషన్ – Shorts శైలిలో (హుక్ · బ్రిడ్జ్‌లు · పాఠం · సబ్‌స్క్రైబ్)\n',
            'పుస్తకంలోని కథనం (సీన్ పట్టిక) ఏమాత్రం మారలేదు. దాని చుట్టూ వీక్షకులను ఆపి ఉంచే ఈ కొత్త భాగాలు జోడించాం:\n',
            f"- **హుక్ (0:{BUMPER:02d} నుండి, సుమారు {speak_secs(extra['hook'])} సె):** {extra['hook']}",
            *[f"- **బ్రిడ్జ్ → {title}:** {line}" for (n, title), line in zip(d['chapters'][1:], extra['bridges'])],
            f"- **జీవిత పాఠం:** {extra['lesson']}",
            f"- **సబ్‌స్క్రైబ్:** {CTAS[ep_index % len(CTAS)]}\n",
            '**పూర్తి రికార్డింగ్ స్క్రిప్ట్** – ఈ వరుసలోనే చదవండి. [ ] లో ఎలా చెప్పాలో సూచన; '
            'ప్రతి లైను ఒక శ్వాసలో; ⏸ దగ్గర ఒక సెకను ఆగండి.\n',
            f'```text\n{recording}\n```\n'])
    n = 2 if extra else 1
    section = '\n'.join([
        START,
        '## 🎬 లాంగ్ వీడియో కిట్ (నెరేషన్ · Flow · థంబ్‌నెయిల్ · అప్‌లోడ్)\n',
        '*ఈ భాగం పై సీన్ పట్టిక, `Long_Videos/_tools/data/` నుండి ఆటోమేటిక్‌గా తయారవుతుంది. '
        'చేత్తో మార్చవద్దు; మార్పులు అక్కడ చేసి మళ్ళీ బిల్డ్ చేయండి.*\n',
        '| | |\n|---|---|',
        f'| వీడియో నిడివి | **{mmss(total)}** (బంపర్ {BUMPER} సె + {len(seq)} క్లిప్‌లు + ఔట్రో {OUTRO} సె) |',
        f'| క్లిప్‌లు | 🎥 వీడియో {n_video} · 🖼️ ఇమేజ్ + కదలిక {len(seq) - n_video}'
        + (f' · ✨ కొత్త నెరేషన్ భాగాలు {n_new}' if extra else '') + ' |',
        f'| క్యాప్షన్లు | `{srt_rel}` |',
        f'| ఎండ్ స్క్రీన్ | చివరి {OUTRO} సె: తరువాతి భాగం, కాండ ప్లేలిస్ట్, సబ్‌స్క్రైబ్ – YouTube Studio → End screen |',
        '| రిఫరెన్స్ ఇమేజ్‌లు | `Long_Videos/_reference_images/` (ప్రాంప్ట్‌లు: `Long_Videos/00_CHARACTER_REFERENCES.md`) |\n',
        new_md,
        f'### {n}. క్లిప్‌లు (16:9 · ఫోటోరియలిస్టిక్)\n',
        '- **🎥 వీడియో:** Flow (Veo) లో. ముందు ఇదే ప్రాంప్ట్‌తో ఇమేజ్ చేసి, నచ్చితే *Frames to Video* లో మొదటి ఫ్రేమ్‌గా వాడండి.',
        '- **🖼️ ఇమేజ్ + కదలిక:** ఇమేజ్ మాత్రమే చేసి, ఎడిటర్‌లో ఇచ్చిన జూమ్/ప్యాన్‌తో క్లిప్ నిడివి అంతా చూపించండి.',
        f'- ప్రతి క్లిప్‌కు **రిఫరెన్స్** ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేయండి. సమయాలు బంపర్ ({BUMPER} సె) తో కలిపి.\n',
        '\n'.join(md_items),
        f'### {n + 1}. థంబ్‌నెయిల్ (1280×720 · 16:9)\n',
        '| భాగం | టెక్స్ట్ | రూపం |\n|---|---|---|',
        f'| హెడ్‌లైన్ (ఎడమ 45%) | **{main}** | తెలుపు, **{hl}** పసుపు (#FFD700), నల్ల అవుట్‌లైన్ + షాడో |',
        f'| కింది లైన్ | {sub} | తెలుపు, సెమీ-బోల్డ్ |',
        f'| బ్యాడ్జ్ (పై ఎడమ) | {kaanda_te} · {ep} | కాషాయ పట్టీ |\n',
        f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in trefs) if trefs else 'అవసరం లేదు'}",
        '- బ్యాక్‌గ్రౌండ్ ఈ ప్రాంప్ట్‌తో చేసి, టెక్స్ట్ Canva లో వేయండి.\n',
        f'```text\n{tprompt}\n```\n',
        f'### {n + 2}. YouTube అప్‌లోడ్\n',
        f'**టైటిల్:**\n\n```text\n{title}\n```\n',
        f'**వివరణ (అధ్యాయాలతో):**\n\n```text\n{desc}\n```\n',
        f"**పిన్ కామెంట్:**\n\n```text\n{d['pin']}\n```\n",
        f'**ట్యాగ్‌లు:**\n\n```text\n{tags}\n```\n',
        f'**క్యాప్షన్ ఫైల్:** `{srt_rel}` – YouTube Studio → Subtitles → Upload file.',
        END])

    if START in text:
        before, rest = text.split(START, 1)
        text = before.rstrip('\n') + '\n\n' + section + rest.split(END, 1)[1]
    else:
        text = text.rstrip('\n') + '\n\n' + section + '\n'
    open(path, 'w', encoding='utf-8', newline='\n').write(text)

    cap_dir = os.path.join(LONG, 'captions', folder)
    os.makedirs(cap_dir, exist_ok=True)
    open(os.path.join(cap_dir, f'{ep}.srt'), 'w', encoding='utf-8', newline='\n').write(srt(spoken))

    plan = {'ep': ep, 'tel': tel, 'sum': d['sum'], 'head': d['head'], 'thumb': tprompt, 'src': src, 'k': k,
            'body': body_end - BUMPER, 'cta': total - OUTRO - body_end, 'chapters': [(a - BUMPER if a else 0, t) for a, t in chap]}
    return k, {'plan': plan, 'n': ep, 'headline': main, 'hl': hl, 'sub': sub, 'badge': f'{kaanda_te} · {ep} · {mmss(total)}',
               'title': title, 'sloka': recording.split('\n') if extra else [], 'reading': None, 'clips': cards,
               'thumbPrompt': tprompt, 'thumbRefs': trefs, 'desc': desc, 'pinned': d['pin'], 'srt': srt_rel}



# ---------- upload plan: short episodes combined into 8+ minute videos ----------

MIN_LEN, MAX_LEN = 8 * 60, 16 * 60   # mid-roll ads need 8 min; keep a video under ~16 min


def video_len(group):
    return BUMPER + sum(x['body'] for x in group) + group[-1]['cta'] + OUTRO


def group_episodes(plans):
    """Consecutive episodes of the same kaanda (Parichayam may join E1.01) until each video passes 8 minutes."""
    units, cur = [], []
    for x in plans:
        if cur and x['k'] != cur[-1]['k'] and not (cur[-1]['k'] == 0 and x['k'] == 1):
            units.append(cur)
            cur = []
        cur.append(x)
        if video_len(cur) >= MIN_LEN:
            units.append(cur)
            cur = []
    if cur:
        if units and units[-1][-1]['k'] == cur[0]['k'] and video_len(units[-1] + cur) <= MAX_LEN:
            units[-1] += cur
        else:
            units.append(cur)
    return units


def plan_file(plans, name):
    units = group_episodes(plans)
    lines = ['# అప్‌లోడ్ ప్లాన్ – ' + name + '\n',
             'YouTube **mid-roll ads 8 నిమిషాలు దాటిన వీడియోలకే** వస్తాయి. అందుకే చిన్న ఎపిసోడ్‌లను వరుసగా కలిపి 8–16 నిమిషాల వీడియోలుగా అప్‌లోడ్ చేయండి.\n',
             '**ఎలా కలపాలి:** బంపర్ → మొదటి ఎపిసోడ్ క్లిప్‌లు (దాని సబ్‌స్క్రైబ్ లైన్, ఔట్రో వదిలేయండి) → తరువాతి ఎపిసోడ్ క్లిప్‌లు (దాని హుక్ మధ్యలో "కొత్త ఆసక్తి"గా పనిచేస్తుంది) → ... → చివరి ఎపిసోడ్ సబ్‌స్క్రైబ్ లైన్ → ఎండ్ స్క్రీన్. క్లిప్‌లు, ప్రాంప్ట్‌లు ఆయా ఎపిసోడ్ ఫైల్‌లలోనే ఉన్నాయి.\n',
             '| వీడియో | ఎపిసోడ్‌లు | నిడివి | mid-roll |', '|---|---|---|---|']
    for i, g in enumerate(units, 1):
        n = video_len(g)
        lines.append(f"| V{i} | {' + '.join(x['ep'] for x in g)} | {mmss(n)} | {'✅' if n >= MIN_LEN else '–'} |")
    lines.append('')
    for i, g in enumerate(units, 1):
        n = video_len(g)
        eps = f"{g[0]['ep']}–{g[-1]['ep'].split('.')[-1]}" if len(g) > 1 else g[0]['ep']
        names = ' & '.join(x['tel'] for x in g)
        title = f'{names} | Ramayanam {eps}'
        if len(title) > 100:
            title = f"{g[0]['tel']} … {g[-1]['tel']} | Ramayanam {eps}"
        if len(title) > 100:
            title = f"{g[0]['head'][0]} | Ramayanam {eps}"
        chapters, off = [], 0
        for x in g:
            for t, c in x['chapters']:
                at = 0 if not chapters else BUMPER + off + t
                chapters.append((at, c if len(g) == 1 or t else f"{x['ep']} · {c}"))
            off += x['body']
        desc = (title + '\n\n' + '\n'.join(x['sum'] for x in g) + '\n\n⏱️ అధ్యాయాలు\n'
                + '\n'.join(f'{mmss(a)} {c}' for a, c in chapters)
                + '\n\n📖 మూలం: చిత్రరూపంలో సంపూర్ణ వాల్మీకి రామాయణము\n'
                  '🔔 పురాణ కథా శ్రవణం – రామాయణం మొదటి నుండి చివరి వరకు, భాగం భాగంగా.\n\n' + HASHTAGS)
        lines += [f"## V{i} · {mmss(n)} · {' + '.join(x['ep'] for x in g)}\n",
                  f"- **థంబ్‌నెయిల్:** {g[0]['ep']} థంబ్‌నెయిల్ వాడండి (హెడ్‌లైన్: **{g[0]['head'][0]}**)",
                  f"- **పిన్ కామెంట్, ట్యాగ్‌లు:** {g[0]['ep']} కిట్ నుండి",
                  f'\n**టైటిల్:**\n\n```text\n{title}\n```\n', f'**వివరణ:**\n\n```text\n{desc}\n```\n']
    return '\n'.join(lines), units

# ---------- references and helper pages ----------

def reference_file(refs):
    out = ['# పాత్రల రిఫరెన్స్ ఇమేజ్‌లు – లాంగ్ వీడియోలు (ఫోటోరియలిస్టిక్)\n',
           'లాంగ్ వీడియోలు ఫోటోరియలిస్టిక్ కాబట్టి Shorts రిఫరెన్స్‌లకు వేరు. ప్రతి పాత్రకు (వయసు దశతో సహా) ఒక్కసారి చేయండి.\n',
           '1. ప్రాంప్ట్‌తో ఇమేజ్ చేసి ఉత్తమమైనది `Long_Videos/_reference_images/` లో ఇచ్చిన పేరుతో సేవ్ చేయండి.',
           '2. వేరే దశ (ఉదా: `RAMA_S2`) చేసేటప్పుడు ముందు దశ ఇమేజ్‌ను జత చేసి "same person, same face" అని చెప్పి మార్పు మాత్రమే అడగండి.',
           '3. ఆమోదించిన ఇమేజ్‌ను మార్చవద్దు.\n',
           'రూపాలు `00_CHARACTER_BIBLE.md` నుండి వస్తాయి; అక్కడ మార్చి మళ్ళీ బిల్డ్ చేస్తే ఇక్కడ కూడా మారతాయి.\n']
    items = []
    for r in sorted(refs):
        key, _, stage = r.partition('_S')
        ep = 'E6.39'
        if stage:
            ep = next(st for st, s in STAGES['RAMA' if key == 'LAKSHMANA' else key] if s == 'S' + stage)
            ep = ep if ep != 'E0.00' else 'E1.01'
        look = character(key, ep)
        prompt = ("Character reference image for film continuity: one character only, full body, standing, facing "
                  "the camera, centred, plain soft warm-grey studio background, even soft lighting, calm expression, "
                  f"16:9 frame. Style: {STYLE}. Character: {look}. {RESPECT} No text, letters, logos or watermarks.")
        out.append(f'## `{r}.png`\n\n```text\n{prompt}\n```\n')
        items.append({'key': r, 'prompt': prompt})
    return '\n'.join(out), items


def main(data_path):
    tpl_path = os.path.join(ROOT, 'Valmiki_Ramayanam', '_tools', 'flow_helper_template.html')
    data = read_data(data_path)
    extras = read_narration(data_path.replace('.txt', '_narration.txt'))
    refs_used, by_kaanda = set(), {}
    for i, (ep, d) in enumerate(data.items()):
        k, page = build_episode(ep, d, refs_used, extras.get(ep), i)
        by_kaanda.setdefault(max(k, 1), []).append(page)  # Parichayam shares the Baala page
        print(f"{ep}: {len(page['clips'])} clips, {sum(c['kind'] == 'video' for c in page['clips'])} video, "
              f"{page['badge'].split(' · ')[-1]}")
    ref_md, ref_items = reference_file(refs_used)
    open(os.path.join(LONG, '00_CHARACTER_REFERENCES.md'), 'w', encoding='utf-8', newline='\n').write(ref_md)
    tpl = open(tpl_path, encoding='utf-8').read()
    os.makedirs(os.path.join(TOOLS, 'publish'), exist_ok=True)
    for k, pages in by_kaanda.items():
        folder, kaanda_te = KAANDAS[k]
        label = 'పరిచయం + ' + kaanda_te if any(p['n'].startswith('E0.') for p in pages) else kaanda_te
        payload = {'key': f'long_{k}', 'name': f'{label} – లాంగ్ వీడియోలు', 'slokas': pages, 'refs': ref_items,
                   'unit': 'భాగాలు', 'clipWord': '', 'subtitle': 'ప్రతి సీన్‌కు Flow ప్రాంప్ట్, థంబ్‌నెయిల్, అప్‌లోడ్',
                   'scriptTitle': 'రికార్డింగ్ స్క్రిప్ట్ – [ ] ఎలా చెప్పాలో, ప్రతి లైను ఒక శ్వాస, ⏸ = ఒక సెకను విరామం'}
        blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
        frag = tpl.replace('__TITLE__', f'{kaanda_te} లాంగ్ వీడియోలు').replace('__DATA__', blob)
        name = folder.replace(' - ', '_').replace(' ', '_')
        open(os.path.join(TOOLS, 'publish', f'{name}.html'), 'w', encoding='utf-8', newline='\n').write(frag)
        full = ('<!doctype html><html lang="te"><head><meta charset="utf-8"><meta name="viewport" '
                'content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + frag + '</body></html>')
        open(os.path.join(LONG, f'{name}_CLIPS_HELPER.html'), 'w', encoding='utf-8', newline='\n').write(full)
    plans = [p['plan'] for pages in by_kaanda.values() for p in pages]
    name = os.path.basename(data_path).replace('.txt', '')
    text, units = plan_file(plans, name)
    open(os.path.join(LONG, f'UPLOAD_PLAN_{name}.md'), 'w', encoding='utf-8', newline='\n').write(text)
    print(f'{len(data)} episodes, {len(refs_used)} reference images; upload plan: {len(units)} videos, '
          f'{sum(video_len(g) >= MIN_LEN for g in units)} over 8 minutes')


if __name__ == '__main__':
    main(sys.argv[1])
