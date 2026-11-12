"""Build publish/sundarakanda_parayanam.html: the Sundarakanda Parayanam section page.

Reads the Suno song file(s) in Sundarakanda_Parayanam/songs/ and shows, for each song,
copy-ready lyrics + style (exactly the SUNO_*.txt text), the chanted Valmiki slokas with
their sources, which slokas each charanam follows, and the parayanam credit plan.
Run:  python sundara_page.py
"""
import json, re
from pathlib import Path

import live_style as LS
from soften import soften

HERE = Path(__file__).resolve().parent
# the long videos' 9:16 -> 16:9 swap (Long_Videos/_tools/long_build.py WIDE)
WIDE = [('Vertical 9:16 cinematic still image, 1080x1920, main subject in the centre safe area.',
         'Cinematic 16:9 still image, 1920x1080, main subject well framed.'),
        ('Vertical 9:16 YouTube Shorts thumbnail key art, single still image, 1080x1920.',
         '16:9 YouTube video thumbnail key art, single still image, 1920x1080.'),
        ('Keep the top 35% of the frame a clean dark gradient or soft sky with no important detail (space for a '
         'headline) and the bottom 12% calm and plain (space for a small line).',
         'Keep the left 40% of the frame a clean dark gradient or soft sky with no important detail (space for a '
         'headline); the main subject on the right.'),
        ('vertical 9:16', '16:9'), ('Vertical 9:16', '16:9'), ('9:16', '16:9'), ('1080x1920', '1920x1080'),
        ('centre safe area', 'frame')]
SONG_CAM = 'very slow, steady push-in'


def wide(text):
    for a, b in WIDE:
        text = text.replace(a, b)
    return text


def keys_of(s):
    return [k.strip() for k in s.split(',') if k.strip()]


def pictures(scenes, thumbpic):
    """Each song section's picture in the Shorts' own prompt style: a 16:9 still for the full song video, a 9:16
    still for song Shorts, and a gentle video prompt that animates that picture (the video follows the image)."""
    out, used = [], set()
    for sec, keys, frame, light in scenes:
        ks = keys_of(keys)
        used.update(LS.ref_keys(ks))
        frame, light = frame.rstrip('. ') + '.', light.rstrip('. ') + '.'
        tall = soften(LS.still(ks, frame, light, motion='', cam=SONG_CAM))
        vid = soften(LS.start_video(ks, frame, 'gentle natural movement', SONG_CAM, light, False))
        out.append({'sec': sec, 'refs': LS.ref_keys(ks), 'frame': frame,
                    'wide': wide(tall), 'tall': tall, 'video': wide(vid), 'videoTall': vid})
    thumb = None
    if thumbpic:
        tk, tf, tl = thumbpic
        t, trefs = LS.thumb(keys_of(tk), tf.rstrip('. ') + '.', tl.rstrip('. ') + '.')
        thumb = {'wide': soften(wide(t)), 'tall': soften(t), 'refs': trefs}
        used.update(trefs)
    return {'scenes': out, 'thumb': thumb, 'refs': LS.library(used)}
SONGS = HERE.parent / 'Sundarakanda_Parayanam' / 'songs'
OUT = HERE / 'publish' / 'sundarakanda_parayanam.html'


def read_song(path):
    src = path.read_text(encoding='utf-8')
    head, lyr = src.split('\n---\n', 1)
    meta, sources, scenes, thumbpic = {}, [], [], None
    for l in head.splitlines():
        k, _, v = l.partition(': ')
        if k == 'SOURCE':
            sources.append([x.strip() for x in v.split('|', 2)])
        elif k == 'SCENE':
            scenes.append([x.strip() for x in v.split('|', 3)])
        elif k == 'THUMBPIC':
            thumbpic = [x.strip() for x in v.split('|', 2)]
        elif k:
            meta[k] = v
    chants = []
    for m in re.finditer(r'\[శ్లోక గానం \|[^|]*\| (\d+) \|[^\]]*\]\n(.+?)\n(.+?)\n', lyr):
        ref = f"సుందరకాండ {meta['SARGA']}.{m.group(1)}"
        mean = next((s[2] for s in sources if s[0].startswith('శ్లోక గానం') and s[1] == ref), '')
        chants.append({'ref': ref, 'l1': m.group(2), 'l2': m.group(3), 'mean': mean})
    # the copy-ready SUNO_*.txt files belong to song 1 only; later songs use their own text
    first = path.name == 'sundara_sarga_001_song.txt'
    lyrics_file = SONGS / ('SUNO_lyrics.txt' if first else '_none_')
    style_file = SONGS / ('SUNO_style.txt' if first else '_none_')
    lyrics = lyrics_file.read_text(encoding='utf-8').strip() if lyrics_file.exists() else lyr.strip()
    style = style_file.read_text(encoding='utf-8').strip() if style_file.exists() else meta['STYLE']
    return {'title': meta['TITLE'], 'sarga': meta['SARGA'], 'gist': meta['GIST'], 'raga': meta['RAGA'],
            'tala': meta['TALA'], 'bpm': meta['BPM'], 'length': meta['LENGTH'], 'style': style,
            'exclude': meta['EXCLUDE'], 'lyrics': lyrics, 'chants': chants, 'pics': pictures(scenes, thumbpic),
            'sources': [s for s in sources if not s[0].startswith('శ్లోక గానం')]}


# the page design lives in sundara_template.html (the long-video pages' workbench layout, 2026-11-12)
TEMPLATE = (HERE / 'sundara_template.html').read_text(encoding='utf-8')


def main():
    songs = [read_song(p) for p in sorted(SONGS.glob('sundara_sarga_*_song.txt'))]
    blob = json.dumps(songs, ensure_ascii=False).replace('</', '<\\/')
    OUT.write_text(TEMPLATE.replace('__DATA__', blob), encoding='utf-8', newline='\n')
    for s in songs:
        print(s['title'], '| chants', [c['ref'] for c in s['chants']], '| meanings', all(c['mean'] for c in s['chants']),
              '| sources', len(s['sources']), '| lyrics', len(s['lyrics']))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
