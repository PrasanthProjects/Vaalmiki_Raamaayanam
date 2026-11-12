# -*- coding: utf-8 -*-
"""Hero-elevation music kit for రామాయణ వైభవం Shorts (user, 2026-11-12): a few shared 50-second tracks, all with the
same shape, instead of new music for every Short.

Shape (ElevenLabs Music composition plan, exact section lengths):
  0–3 s   HOOK    full power from the first beat (no fade-in)
  3–14 s  DRIVE   driving rhythm, heroic lead
  14–26 s RISE    building tension, drum rolls, risers
  26 s    DROP    the biggest hit; 26–40 s full-power climax
  40–50 s FINALE  triumphant theme, a final hit and a short ring-out
The Video Maker / mix starts the track at (DROP − the Short's climax time), so the drop lands on that Short's climax.

    python elevation_music.py            -> Ramayana_Vaibhavam/music/kit_*.mp3 (skips ones already made)
"""
import os
import sys

import requests

import elevation_voice as V

OUT = os.path.join(os.path.dirname(V.OUT), 'music')
DROP = 26.0
NEG = ['vocals', 'singing', 'choir', 'spoken words', 'lyrics', 'rap', 'EDM', 'dubstep', 'western pop', 'lo-fi',
       'soft piano', 'slow fade-in', 'silence']
BASE = ['instrumental', 'epic Indian cinematic hero-elevation score', 'South Indian mythological action film style',
        'massive dhol and thavil drums', 'heavy cinematic brass', 'punchy sub-bass hits', 'high energy']

KIT = {
    'kit_rama_royal': (['royal and majestic', 'nadaswaram lead', 'temple bells and big temple drums', 'war conch',
                        'noble, proud hero theme', '118 bpm'],
                       'a regal, majestic hero for a righteous prince'),
    'kit_hanuman_flight': (['soaring and fast', 'shehnai lead', 'racing dhol rhythm', 'whoosh risers', 'wind-like strings',
                            'unstoppable flying power', '132 bpm'],
                           'a mighty flying hero leaping across the sky'),
    'kit_war_battle': (['dark and fierce', 'pounding war drums', 'low brass stabs', 'aggressive string ostinato',
                        'war conch blasts', 'battlefield intensity', '128 bpm'],
                       'a fierce battle against a huge army'),
    'kit_divine_astra': (['mystic divine power', 'tanpura drone under huge drums', 'shimmering bells', 'deep brass swells',
                          'cosmic, awe-filled', '110 bpm'],
                         'a sage and a divine weapon of light'),
    'kit_fury_march': (['stomping swagger', 'heavy marching drums', 'bold brass riffs', 'hand claps', 'fearless attitude',
                        '124 bpm'],
                       'a fearless hero striding in with anger and pride'),
}


def plan(styles, who):
    sec = lambda name, ms, local: {'section_name': name, 'positive_local_styles': local, 'negative_local_styles': ['fade-in', 'quiet'],
                                   'duration_ms': ms, 'lines': []}
    return {'positive_global_styles': BASE + styles, 'negative_global_styles': NEG, 'sections': [
        sec('Hook', 3000, ['instant full-power opening hit', 'drum roll', f'grabs attention at once for {who}']),
        sec('Drive', 11000, ['driving rhythm', 'heroic lead melody', 'strong and confident']),
        sec('Rise', 12000, ['building tension', 'rising drum rolls', 'risers getting louder', 'anticipation']),
        sec('Drop', 14000, ['huge drop on the first beat', 'biggest climax of the track', 'everything at full power', 'triumphant']),
        sec('Finale', 10000, ['victorious hero theme', 'ends on one massive final hit', 'short ring-out']),
    ]}


def main(only=None):
    h = V.key()
    os.makedirs(OUT, exist_ok=True)
    for name, (styles, who) in KIT.items():
        path = os.path.join(OUT, f'{name}.mp3')
        if (only and name != only) or os.path.exists(path):
            continue
        r = requests.post(f'{V.API}/v1/music?output_format=mp3_44100_192', headers=h, timeout=900,
                          json={'composition_plan': plan(styles, who), 'model_id': 'music_v1'})
        if r.status_code != 200:
            print(name, 'FAILED', r.status_code, r.text[:300])
            continue
        open(path, 'wb').write(r.content)
        print(name, 'ok', V.stats(path)[0], 's')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)


def rms(path):
    import re
    import subprocess
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'asetnsamples=11025,astats=metadata=1:reset=1,'
                          'ametadata=print:key=lavfi.astats.Overall.RMS_level', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return [max(-90.0, float(x)) if x not in ('-inf', 'inf') else -90.0 for x in re.findall(r'RMS_level=(-?[\d.]+|-?inf)', out)]


def cues(path):
    """(start, climax) in seconds: start = first quarter-second loud enough (cuts a quiet intro);
    climax = onset of the loudest 3-second stretch between 20 and 38 s (where the big hit should meet the Short's climax)."""
    v = rms(path)
    q = 0.25
    start = next((i for i, x in enumerate(v) if x > -24), 0) * q
    win = 12
    sm = [sum(v[i:i + win]) / win for i in range(len(v) - win)]
    lo, hi = int(20 / q), int(38 / q)        # the planned DROP section (26-40 s); the final hit at the end is not the climax
    best = max(range(lo, min(hi, len(sm))), key=lambda i: sm[i]) if len(sm) > lo else 0
    onset = best
    while onset > lo and v[onset - 1] > sm[best] - 3:
        onset -= 1
    return round(start, 2), round(onset * q, 2)
