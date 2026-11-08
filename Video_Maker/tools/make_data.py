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
                      'shows': shows.group(1).strip() if shows else ''})
    assert len(clips) == 7, f'{path}: expected 7 clips, found {len(clips)}'
    return {
        'hook': {'voice': field(hook, 'వాయిస్'), 'screen': field(hook, 'తెరపై టెక్స్ట్')},
        'meaning': {'voice': field(meaning, 'వాయిస్'), 'screen': field(meaning, 'తెరపై టెక్స్ట్')},
        'end': {'voice': field(end, 'వాయిస్')},
        'clips': clips,
    }


def main(kanda_dir, sarga):
    folder = os.path.join(B.ROOT, kanda_dir, f'Sarga_{sarga:03d}')
    cards = {s['n']: s for s in O.data_for(kanda_dir, sarga)}
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
        slokas.append(s)
    out_dir = os.path.join(MAKER, 'src', 'data')
    os.makedirs(out_dir, exist_ok=True)
    name = f'{kanda_dir}_S{sarga:03d}'
    data = {'kanda': kanda_dir, 'kandaEn': KANDA_EN[kanda_dir], 'kandaTe': B.KANDAS[kanda_dir],
            'sarga': sarga, 'slokas': slokas}
    json.dump(data, open(os.path.join(out_dir, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    names = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(out_dir, '*_S*.json')))
    with open(os.path.join(out_dir, 'index.ts'), 'w', encoding='utf-8') as f:
        f.write('// Written by tools/make_data.py\n')
        for i, nm in enumerate(names):
            f.write(f"import d{i} from './{nm}.json';\n")
        f.write('export const SARGAS = [' + ', '.join(f'd{i}' for i in range(len(names))) + '];\n')
    missing = [s['n'] for s in slokas if not s['lines']]
    print(f'{name}: {len(slokas)} ślokas' + (f' (no on-screen śloka data yet: {missing})' if missing else ''))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
