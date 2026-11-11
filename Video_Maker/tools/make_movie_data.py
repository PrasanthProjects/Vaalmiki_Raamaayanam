"""Text for the Video Maker's movie mode, taken from a Valmiki Cinema script (nothing typed twice).

  python tools/make_movie_data.py ../Valmiki_Cinema/source/1_Bala_Kanda/S001_sarga1.txt

Uses Valmiki_Cinema/_tools/cinema_build.py for the scenes, shots, voice lines, titles (CAP), music and sound
notes and the image / video prompts, exactly as the movie doc shows them.
Writes src/data/movie_<kanda>_<file>.json and updates src/data/index.ts.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
CINEMA_TOOLS = os.path.join(os.path.dirname(MAKER), 'Valmiki_Cinema', '_tools')
sys.path.insert(0, CINEMA_TOOLS)
import cinema_build as C  # noqa: E402

KANDA_EN = {'1_Bala_Kanda': 'Bala', '2_Ayodhya_Kanda': 'Ayodhya', '3_Aranya_Kanda': 'Aranya',
            '4_Kishkindha_Kanda': 'Kishkindha', '5_Sundara_Kanda': 'Sundara', '6_Yuddha_Kanda': 'Yuddha',
            '7_Uttara_Kanda': 'Uttara'}

# The script's sound notes (FX, Telugu) as ElevenLabs Sound Effects prompts. A note missing here shows without a prompt.
FX_PROMPTS = {
    'పక్షుల కిలకిల, నది సవ్వడి': 'Morning forest by a clear river: many birds chirping and a gentle river flowing over stones, calm, no music',
    'బాణం ఝుంకారం, అడవి కంపించే శబ్దం': 'A great bow string twanging, an arrow released with power, the forest trembling with a deep rumble, cinematic, no music',
    'బాణాల వర్షం, రథాల చప్పుడు': 'A rain of arrows whistling through the air, ancient war chariots rumbling and wheels clattering, battle, no music',
    'రెక్కల చప్పుడు, గాలి హోరు': 'Huge bird wings flapping powerfully, strong wind roaring high in the sky, no music',
    'గాలిని చీల్చే శబ్దం': 'Something huge flying fast, cutting through the air with a deep whoosh, no music',
    'బాణం దూసుకెళ్ళే శబ్దం, చెట్లు చీలిన శబ్దం': 'An arrow shooting fast through the air, then thick trees cracking and splitting one after another, cinematic, no music',
    'సుగ్రీవుడి గర్జన': 'A powerful monkey-king roar and battle cry echoing over rocky hills, no music',
    'గాలి హోరు': 'Strong wind roaring and howling, open sky, no music',
    'రాళ్ళు కూలే శబ్దం': 'Big rocks and stone arches crashing down and tumbling, heavy impact, no music',
    'మంటల చప్పుడు': 'A big fire roaring and crackling, flames rushing across wooden roofs, no music',
    'అలల గర్జన': 'Huge ocean waves roaring and crashing, a stormy sea rising, no music',
    'దివ్యాస్త్రం గర్జన': 'A divine weapon released: a blazing arrow roaring through the sky with a deep thunderous boom and shimmering energy, no music',
}


def who_of(k):
    return 'N' if k == 'N' else k.split(' ', 1)[1]


def main(src):
    src = os.path.abspath(src)
    v = C.parse(src)
    kanda = os.path.basename(os.path.dirname(src))
    name = os.path.splitext(os.path.basename(src))[0]
    t, n, scenes = 0, 0, []
    for si, sc in enumerate(v['scenes'], 1):
        scene = {'si': si, 'title': sc['title'], 'refs': sc['refs'], 'loc': sc['loc'], 'suno': sc.get('suno', ''),
                 'songstyle': sc.get('songstyle', ''), 'shots': []}
        for shot in sc['shots']:
            n += 1
            spoken = [C.speak_secs(x) * (3 if k.startswith('SONG ') else 1)
                      for k, x in shot['audio'] if k == 'N' or k.startswith(('D ', 'SONG '))]
            sec = shot.get('sec') or (sum(spoken) if spoken else 6)
            kind = C.kind_of(shot)
            keys, _ = C.cast(shot)
            scene['shots'].append({
                'no': n, 'planStart': t, 'sec': sec, 'fixedSec': shot.get('sec') or 0, 'kind': kind, 'refs': shot['refs'],
                'pic': shot['pic'],
                'lines': [{'who': who_of(k), 'label': C.VOICES[who_of(k)][0], 'voice': C.VOICES[who_of(k)][1],
                           'text': x, 'song': k.startswith('SONG '), 'est': C.speak_secs(x) * (3 if k.startswith('SONG ') else 1)}
                          for k, x in shot['audio'] if k == 'N' or k.startswith(('D ', 'SONG '))],
                'music': [x for k, x in shot['audio'] if k == 'M'],
                'fx': [{'te': x, 'prompt': FX_PROMPTS.get(x, '')} for k, x in shot['audio'] if k == 'FX'],
                'cap': [x for k, x in shot['audio'] if k == 'CAP'],
                'img': C.image_prompt(shot, sc['loc']), 'end': C.end_prompt(shot, sc['loc'], kind),
                'vid': C.video_prompt(shot, sc['loc'], kind),
                # extra pictures of the same shot (song montages, fight cuts) and the shot's own music
                'alts': [{'pic': a['pic'], 'img': C.image_prompt(C.alt_shot(shot, a), sc['loc']),
                          'end': C.end_prompt(C.alt_shot(shot, a), sc['loc'], 'video'),
                          'vid': C.video_prompt(C.alt_shot(shot, a), sc['loc'], 'video')} for a in shot.get('alts', [])],
                'bgm': shot.get('bgm', ''),
                'ref': [C.ref_name(k, shot['ep']) for k in keys]})
            t += sec
        scenes.append(scene)
    sarga = int(re.search(r'S(\d+)', name).group(1))
    data = {'id': f'{KANDA_EN[kanda]}-{name}', 'kanda': kanda, 'kandaEn': KANDA_EN[kanda], 'file': name, 'sarga': sarga,
            'title': v['title'], 'covers': v.get('covers', ''), 'next': v.get('next', ''), 'songnote': v.get('songnote', ''),
            'voices': {k: {'label': a, 'voice': b} for k, (a, b) in C.VOICES.items()},
            'planLength': t, 'scenes': scenes}
    out_dir = os.path.join(MAKER, 'src', 'data')
    json.dump(data, open(os.path.join(out_dir, f'movie_{kanda}_{name}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    write_index(out_dir)
    print(f"movie_{kanda}_{name}: {len(scenes)} scenes, {n} shots, plan {int(t // 60)}:{int(t % 60):02d}")


def write_index(out_dir):
    shorts = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(out_dir, '*_S[0-9][0-9][0-9].json')))
    movies = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(out_dir, 'movie_*.json')))
    # long videos: the slim copies (no prompts) – the renderer needs only timing, pictures and titles
    movies += sorted('slim/' + os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(out_dir, 'slim', 'long_*.json')))
    with open(os.path.join(out_dir, 'index.ts'), 'w', encoding='utf-8') as f:
        f.write('// Written by tools/make_data.py, make_movie_data.py and make_long_data.py\n')
        for i, nm in enumerate(shorts):
            f.write(f"import d{i} from './{nm}.json';\n")
        for i, nm in enumerate(movies):
            f.write(f"import m{i} from './{nm}.json';\n")
        f.write('export const SARGAS = [' + ', '.join(f'd{i}' for i in range(len(shorts))) + '];\n')
        f.write('export const MOVIES = [' + ', '.join(f'm{i}' for i in range(len(movies))) + '];\n')
        # presenter videos (tools/make_presenter_data.py): the user on camera with the pictures
        presenters = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(out_dir, 'presenter_*.json')))
        for i, nm in enumerate(presenters):
            f.write(f"import p{i} from './{nm}.json';\n")
        f.write('export const PRESENTERS = [' + ', '.join(f'p{i}' for i in range(len(presenters))) + '];\n')


if __name__ == '__main__':
    main(sys.argv[1])
