# -*- coding: utf-8 -*-
"""Presenter videos (user, 2026-11-11): the user on camera explaining, with the pictures beside, around or behind
them, like a well-edited explainer. First use: the special "films vs Valmiki" parts.

Reads Long_Videos/_tools/data/special/07_cinema_vs_valmiki.py (through special_build) and its built page (for the
three prompts of each clip) and writes src/data/presenter_<id>.json, one per part. Each clip of the part becomes a
segment: what is said, what shows on screen, the suggested layout of the camera box, the music mood and the prompts.

    python tools/make_presenter_data.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
ROOT = os.path.dirname(MAKER)
sys.path.insert(0, os.path.join(ROOT, 'Long_Videos', '_tools'))
import special_build as SB   # noqa: E402
sys.path.insert(0, HERE)
from make_data import clip_mood   # noqa: E402
from make_movie_data import write_index   # noqa: E402

# Where the camera box goes for each kind of segment; the valmiki segments take turns so the screen keeps moving.
AUTO = {'hook': 'pic', 'welcome': 'full', 'intro': 'circle-br', 'title': 'side-left', 'film': 'side-right', 'sloka': 'card-right', 'outro': 'full'}
TURNS = ['circle-br', 'split', 'circle-tl', 'card-right']
ROLE_MOOD = {'hook': 'heroic', 'welcome': 'joyful', 'intro': 'calm', 'title': 'calm', 'film': 'calm', 'sloka': 'calm', 'outro': 'joyful'}


def role_of(it):
    if it['id'].startswith('H'):
        return 'hook'
    if it['id'] == 'G':
        return 'welcome'
    if it['id'] in ('W', 'I'):
        return 'intro'
    if it['id'] == 'C':
        return 'outro'
    if it.get('verse'):
        return 'sloka'
    if it.get('film'):
        return 'film'
    return 'title' if it['id'].startswith('T') and it['id'][1:].isdigit() else 'valmiki'


def main():
    parts = SB.load()
    page = open(os.path.join(ROOT, 'Long_Videos', '_tools', 'publish', 'special_cinema_vs_valmiki.html'), encoding='utf-8').read()
    built = json.loads(re.search(r'<script id="data"[^>]*>(.*?)</script>', page, re.S).group(1).replace('<\\/', '</'))['slokas']
    out_dir = os.path.join(MAKER, 'src', 'data')
    for n, part in enumerate(parts, 1):
        items = [x for x in SB.items_of(part) if x['kind'] != 'intro']   # the channel intro clip comes from Branding/
        cards = [c for c in built[n - 1]['clips'] if 'ఛానల్ ఇంట్రో' not in c['label']]
        assert len(items) == len(cards), (n, len(items), len(cards))
        segs, turn = [], 0
        for k, (it, c) in enumerate(zip(items, cards), 1):
            role = role_of(it)
            if role == 'valmiki':
                layout = TURNS[turn % len(TURNS)]
                turn += 1
            else:
                layout = AUTO[role]
            text = it['text']
            segs.append({
                'no': k, 'role': role, 'label': it['label'], 'text': text, 'onscreen': it.get('onscreen', ''),
                'layout': layout,
                'mood': (clip_mood(f"{it.get('visual', '')} {text}", ROLE_MOOD.get(role, 'calm'))
                         if role in ('hook', 'film', 'valmiki') else ROLE_MOOD[role]),
                'est': max(3, round(len(text.split()) / 2.2 + 1)),
                'imagePrompt': c.get('imagePrompt', ''), 'endImagePrompt': c.get('endImagePrompt', ''),
                'videoPrompt': c.get('videoPrompt', ''), 'refs': c.get('refs', []),
            })
        d = {'id': f'Presenter-CinemaVsValmiki-P{n}', 'kind': 'presenter', 'title': part['title'],
             'headline': part['headline'], 'badge': f"సినిమాలు vs వాల్మీకి · {part['n']}", 'segments': segs}
        json.dump(d, open(os.path.join(out_dir, f'presenter_cinema_vs_valmiki_P{n}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(d['id'], len(segs), 'segments')
    write_index(out_dir)


if __name__ == '__main__':
    main()
