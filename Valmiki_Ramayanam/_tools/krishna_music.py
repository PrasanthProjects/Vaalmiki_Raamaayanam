# -*- coding: utf-8 -*-
"""Music for the కృష్ణ లీలా వైభవం Shorts (user, 2026-11-12: K1 came out with no background music).

A LOOP Short gets a seamless loop of exactly its length: ElevenLabs Music makes a little more than needed, then the
extra tail is blended into the start (0.6 s), so the last beat flows into the first and the Short repeats with no seam.

    python krishna_music.py 1      -> ../Krishna_Vaibhavam/music/K1_loop.mp3 (the Video Maker picks it up by itself)
"""
import os
import subprocess
import sys

import requests

import elevation_voice as V
import krishna_build as KB

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Krishna_Vaibhavam', 'music')
BLEND = 0.6


# styles: 'playful' (the first try) or the peaceful flute the user asked for (2026-11-12: "good music, flute, proper
# peaceful music"): Krishna's bansuri in Vrindavan, soft tanpura, gentle shimmer, no heavy drums, 90 bpm (16 s = 6 bars)
STYLES = {
    'playful': (['instrumental', 'playful sweet Indian devotional', 'bansuri flute melody', 'light mridangam',
                 'tiny ankle bells and hand cymbals', 'soft tanpura', 'cute and cheerful', 'steady 120 bpm',
                 'loopable, same groove start to end'], ['a light boing-like accent every two bars']),
    'peaceful': (['instrumental', 'peaceful soothing Indian devotional', "Lord Krishna's bansuri flute in Vrindavan",
                  'sweet flowing flute melody in the lead', 'soft tanpura drone', 'gentle swarmandal shimmer', 'very soft hand bells',
                  'warm, loving, lullaby-like', 'slow 90 bpm', 'loopable, same mood start to end'],
                 ['one calm, sweet flute phrase that keeps flowing', 'no drums or only a whisper of soft tabla']),
    'peaceful_veena': (['instrumental', 'peaceful soothing Indian devotional', 'bansuri flute and soft veena together',
                        'flute melody answered by gentle veena', 'soft tanpura drone', 'light breeze-like shimmer',
                        'warm and tender', 'slow 90 bpm', 'loopable, same mood start to end'],
                       ['flute and veena in a calm dialogue', 'no drums']),
}


def loop_music(sh, style='peaceful', name=None):
    L = float(sh['L'])
    os.makedirs(OUT, exist_ok=True)
    raw = os.path.join(OUT, f"K{sh['n']}_{style}_raw.mp3")
    glob_styles, local = STYLES[style]
    plan = {'positive_global_styles': glob_styles,
            'negative_global_styles': ['vocals', 'singing', 'choir', 'words', 'fade-in', 'fade-out', 'ending', 'intro', 'drums solo',
                                       'heavy drums', 'EDM', 'western pop', 'scary', 'sad'],
            'sections': [{'section_name': 'Loop', 'positive_local_styles': local,
                          'negative_local_styles': ['build-up', 'big ending'], 'duration_ms': int((L + 2) * 1000), 'lines': []}]}
    r = requests.post(f'{V.API}/v1/music?output_format=mp3_44100_192', headers=V.key(), timeout=600,
                      json={'composition_plan': plan, 'model_id': 'music_v1'})
    if r.status_code != 200:
        sys.exit(f'music {r.status_code}: {r.text[:300]}')
    open(raw, 'wb').write(r.content)
    out = os.path.join(OUT, name or f"K{sh['n']}_loop.mp3")
    # start 0.5 s in (skip any soft first note), take L seconds; the next BLEND seconds fade into the start
    s0 = 0.5
    fc = (f'[0:a]atrim={s0}:{s0 + L},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={BLEND}:curve=tri[main];'
          f'[0:a]atrim={s0 + L}:{s0 + L + BLEND},asetpts=PTS-STARTPTS,afade=t=out:st=0:d={BLEND}:curve=tri[tail];'
          f'[main][tail]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-filter_complex', fc, '-ar', '44100', '-b:a', '192k', out], check=True)
    print(out, V.stats(out)[0], 's')


if __name__ == '__main__':
    n = int(sys.argv[1])
    sh = next(s for s in KB.SHORTS if s['n'] == n)
    KB.short_page(sh)
    style = sys.argv[2] if len(sys.argv) > 2 else 'peaceful'
    loop_music(sh, style, sys.argv[3] if len(sys.argv) > 3 else None)
