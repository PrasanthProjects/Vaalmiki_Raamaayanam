"""Text for the Video Maker, taken from the Shorts kit (nothing typed twice).

  python tools/make_data.py 1_Bala_Kanda 1

Reads Valmiki_Ramayanam/<kanda>/Sarga_NNN/Sloka_NNN.md (hook, narration, on-screen text, clips) and the
śloka data the on-screen cards use (Telugu reading form, Devanagari, IAST, word meanings in three languages).
Writes src/data/<kanda>_S<NNN>.json and src/data/index.ts (the list of sargas the studio shows).
Run it again whenever the Shorts kit is rebuilt.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
TOOLS = os.path.join(os.path.dirname(MAKER), 'Valmiki_Ramayanam', '_tools')
sys.path.insert(0, TOOLS)
import build as B  # noqa: E402
import overlays as O  # noqa: E402

KANDA_EN = {'1_Bala_Kanda': 'Bala', '2_Ayodhya_Kanda': 'Ayodhya', '3_Aranya_Kanda': 'Aranya',
            '4_Kishkindha_Kanda': 'Kishkindha', '5_Sundara_Kanda': 'Sundara', '6_Yuddha_Kanda': 'Yuddha',
            '7_Uttara_Kanda': 'Uttara'}


def section(md, title_start, next_start):
    a = md.index(title_start)
    b = md.index(next_start, a)
    return md[a:b]


def field(block, name):
    m = re.search(r'- \*\*' + name + r'[^*]*:\*\*\s*(.*)', block)
    return m.group(1).strip() if m else ''


def parse_md(path):
    md = open(path, encoding='utf-8').read()
    nar = section(md, '## 4.', '## 5.')
    parts = re.split(r'\n### ', nar)[1:]
    assert len(parts) == 4, f'{path}: expected 4 narration parts, found {len(parts)}'
    hook, _, meaning, end = parts
    clips = []
    for m in re.finditer(r'### క్లిప్ (\d+) · [^·]+ · ([^·]+) · (🎥|🖼️)[^\n]*\n(.*?)(?=\n### |\n## |\Z)', md, re.S):
        body = m.group(4)
        shows = re.search(r'The frame shows: (.*?)(?<!\b[A-Z])\.\s', body)
        clips.append({'label': m.group(2).strip(), 'video': m.group(3) == '🎥',
                      'shows': shows.group(1).strip() if shows else '', 'says': field(body, 'నెరేషన్') or ''})
    assert len(clips) == 7, f'{path}: expected 7 clips, found {len(clips)}'
    return {
        'hook': {'voice': field(hook, 'వాయిస్'), 'screen': field(hook, 'తెరపై టెక్స్ట్')},
        'meaning': {'voice': field(meaning, 'వాయిస్'), 'screen': field(meaning, 'తెరపై టెక్స్ట్')},
        'end': {'voice': field(end, 'వాయిస్')},
        'clips': clips,
    }


# ElevenLabs (Eleven v3) reads the square-bracket tags as how to say the line; the words stay exactly as in the kit.
HOOK_TAG = {'calm': '[intrigued, warm]', 'sad': '[softly, emotional]', 'heroic': '[dramatic, powerful]',
            'mystery': '[mysterious, hushed]', 'joyful': '[excited, bright]'}


# Each picture gets its own music mood (user, 2026-11-11): the hook, the chanting, the story, the lesson and the
# ending feel different, so the music follows each part instead of one track for the whole Short.
CLIP_MOODS = {
    # English words match whole words only (2026-11-12: "toward" had matched "war"); Telugu stems as before
    'sad': r'\b(?:longing|alone|lonely|tears?|tearful|weep\w*|grie\w*|sorrow\w*|mourn\w*|lament\w*|crying|funeral|pyre|dying|parting|anguish|heartbroken|wail\w*)\b|దుఃఖ|ఏడ్|బాధ|కన్నీ|విలప|వేదన|శోక',
    'heroic': r'\b(?:heroe?s?|first time|battle|fight\w*|arrows?|bow drawn|draws? (?:his )?bow|drawing his bow|army|charg\w+|strikes?|duel|war|victor\w*|leap\w*|attack\w*|roar\w*|valou?r|smashing)\b|వీరు|యుద్ధ|బాణ|సంహర|పరాక్రమ|వధ|ధ్వంసం',
    'mystery': r'\b(?:shadows?|eerie|curse\w*|disguis\w*|secret|maya|illusion|mysterious|abduct\w*|carrying sita away|demons?|monstrous|red eyes|looming)\b|శాప|మాయ|రహస్య|ఎత్తుకు|వింత',
    'joyful': r'\b(?:happ(?:y|ily|iness)|laugh\w*|glowing like devas|wedding|celebrat\w*|festival|joy\w*|smil\w*|garlands?|coronation|birth|embrac\w*|reunion|rejoic\w*|blessing)\b|సుఖంగా|సంతోష|ఆనంద|పెళ్ళి|కల్యాణ|ఉత్సవ',
}
# clips whose words say the opposite of what the word lists read ("no sorrow, no disease" is joy, not sadness)
MOOD_FIXES = {('1_Bala_Kanda', 1): {
    (74, 4): 'heroic', (90, 4): 'joyful', (96, 5): 'calm',        # the words say the opposite of the word lists
    (3, 7): 'mystery', (4, 7): 'mystery',                           # teasers: gathering storm clouds, "one last question"
    (49, 7): 'mystery', (52, 7): 'mystery',                         # Ravana at Maricha's hut, Ravana disguised before Sita
    (56, 4): 'calm', (58, 6): 'joyful', (87, 1): 'joyful'},         # a blessing, a friendship joined, good news sent
    # Sarga 2: the hunter's arrow is tension and grief, never heroic; "శోకం → శ్లోకం" and Brahma's visit are awe and joy
    ('1_Bala_Kanda', 2): {
    (9, 7): 'mystery', (10, 1): 'mystery', (10, 4): 'sad', (10, 5): 'sad', (10, 7): 'sad', (15, 1): 'mystery',
    (18, 1): 'calm', (18, 4): 'joyful', (18, 5): 'joyful', (18, 6): 'calm', (18, 7): 'calm',
    (23, 1): 'mystery', (23, 4): 'calm', (23, 5): 'joyful', (23, 7): 'mystery', (28, 4): 'sad', (28, 7): 'mystery',
    (30, 4): 'calm', (30, 5): 'calm', (30, 6): 'joyful', (32, 1): 'mystery', (32, 4): 'joyful', (32, 5): 'calm',
    (32, 7): 'mystery', (40, 1): 'mystery', (40, 4): 'calm', (40, 5): 'calm', (40, 6): 'joyful', (40, 7): 'mystery'},
    # Sarga 3: Valmiki's vision of the whole story
    ('1_Bala_Kanda', 3): {
    (10, 6): 'calm', (12, 1): 'mystery', (12, 7): 'sad', (13, 1): 'sad', (14, 4): 'joyful', (17, 5): 'heroic',
    (19, 4): 'mystery', (21, 1): 'sad', (22, 1): 'joyful', (22, 7): 'joyful', (23, 1): 'joyful', (24, 7): 'heroic',
    (38, 5): 'joyful'},
    # Sarga 4: the sages' tears are tears of joy; Rama honouring the boys is warmth, not battle
    ('1_Bala_Kanda', 4): {
    (15, 1): 'joyful', (15, 4): 'joyful', (15, 5): 'joyful', (15, 7): 'joyful',
    (30, 1): 'joyful', (30, 4): 'joyful', (30, 5): 'calm', (30, 7): 'calm'}}


def clip_mood(text, fallback):
    score = {m: len(re.findall(rx, text, re.I)) for m, rx in CLIP_MOODS.items()}
    best = max(score, key=score.get)
    return best if score[best] else fallback


def set_moods(s, mood):
    """mood: the śloka's own mood (music_moods.json). Box 0 hook, 1–2 chanting (always calm, devotional), 3–4 story,
    5 lesson, 6 ending (the teaser: it follows the story's mood, or curiosity when the story is calm)."""
    for i, c in enumerate(s['clips']):
        text = f"{c['shows']} {c.get('says', '')}"
        if i in (1, 2):
            c['mood'] = 'calm'
        elif i == 0:
            c['mood'] = clip_mood(text, mood if mood != 'calm' else 'mystery')
        elif i == 5:
            c['mood'] = clip_mood(text, 'calm')
        elif i == 6:
            story = s['clips'][3].get('mood', 'calm') if len(s['clips']) > 3 else 'calm'
            c['mood'] = clip_mood(text, story if story != 'calm' else 'mystery')
        else:
            c['mood'] = clip_mood(text, mood)


# The closing call to action is one of four fixed lines, recorded once in the user's own voice (user, 2026-11-11:
# a human voice in every Short). ElevenLabs reads only the teaser before it; the Video Maker plays the recording.
CTA_LINES = ['మీ కుటుంబంతో షేర్ చేసి, ఛానల్‌ని సబ్‌స్క్రైబ్ చేయండి!',
             'కామెంట్‌లో "జై శ్రీరామ్" అని రాసి, లైక్ చేయండి!',
             'లైక్ చేసి, ఇలాంటి శ్లోకాల కోసం సబ్‌స్క్రైబ్ చేయండి!',
             '"జై శ్రీరామ్" అని కామెంట్ చేసి, సబ్‌స్క్రైబ్ చేయండి!']


def split_cta(end):
    v = end['voice'].strip()
    for i, line in enumerate(CTA_LINES, 1):
        if v.endswith(line):
            end['teaser'], end['cta'] = v[:-len(line)].strip(), i
            return
    end['teaser'], end['cta'] = v, 0


def eleven(s, mood):
    """The four voice parts as text to paste into ElevenLabs, one file each (voice1 … voice4)."""
    # easy-reading form, the danda and verse number dropped (a voice would read them out), a pause at each half
    sloka = ' ... '.join(re.sub(r'\s*[।॥].*$', '', l['te']).strip() for l in s['lines']) if s['lines'] else ''
    return {
        'voice1': f"{HOOK_TAG.get(mood, HOOK_TAG['calm'])} {s['hook']['voice']}",
        'voice2': f"[slowly, reverently, like a temple chant] {sloka} ..." if sloka else '',
        'voice3': f"[warm, storytelling] {s['meaning']['voice']}",
        # the full ending, so a Short without the user's own recording still ends properly; when the recording is in
        # the Video Maker, it cuts this file at the pause after the teaser and plays the user's voice instead
        'voice4': f"[curious, upbeat] {s['end']['voice']}",
    }


def main(kanda_dir, sarga):
    folder = os.path.join(B.ROOT, kanda_dir, f'Sarga_{sarga:03d}')
    cards = {s['n']: s for s in O.data_for(kanda_dir, sarga)}
    try:
        moods = json.load(open(os.path.join(MAKER, 'src', 'data', 'music_moods.json'), encoding='utf-8')).get(f'{kanda_dir}_S{sarga:03d}', {})
    except FileNotFoundError:
        moods = {}
    slokas = []
    for path in sorted(glob.glob(os.path.join(folder, 'Sloka_*.md'))):
        n = int(re.search(r'Sloka_(\d+)', path).group(1))
        s = parse_md(path)
        c = cards.get(n)
        if c:
            # 'orig' = the śloka as written in section 1 of the śloka file (the verse number is in the heading)
            s['lines'] = [{'orig': re.sub(r'\s*॥\s*\d+\s*॥$', ' ॥', l), 'te': B.reading(l), 'dev': B.te2dev(l), 'iast': B.te2iast(l)}
                          for l in c['lines']]
            s['words'] = [{'key': k, 'te': B.reading(k), 'dev': B.te2dev(k), 'iast': B.te2iast(k), 'mte': te, 'mhi': hi, 'men': en}
                          for k, te, hi, en in c['words']]
        else:
            s['lines'], s['words'] = [], []
        s['n'] = n
        split_cta(s['end'])
        s['eleven'] = eleven(s, moods.get(str(n), 'calm'))
        set_moods(s, moods.get(str(n), 'calm'))
        for (sn, ci), m in MOOD_FIXES.get((kanda_dir, sarga), {}).items():
            if sn == n and len(s['clips']) >= ci:
                s['clips'][ci - 1]['mood'] = m
        slokas.append(s)
    out_dir = os.path.join(MAKER, 'src', 'data')
    os.makedirs(out_dir, exist_ok=True)
    name = f'{kanda_dir}_S{sarga:03d}'
    data = {'kanda': kanda_dir, 'kandaEn': KANDA_EN[kanda_dir], 'kandaTe': B.KANDAS[kanda_dir],
            'sarga': sarga, 'slokas': slokas}
    json.dump(data, open(os.path.join(out_dir, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.path.insert(0, HERE)
    from make_movie_data import write_index   # one list of Shorts sargas and movies for the studio
    write_index(out_dir)
    missing = [s['n'] for s in slokas if not s['lines']]
    print(f'{name}: {len(slokas)} ślokas' + (f' (no on-screen śloka data yet: {missing})' if missing else ''))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
