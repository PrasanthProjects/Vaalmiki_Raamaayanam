"""Text for the Video Maker's వైభవం page (localhost:3333/vaibhavam): the Rama and Krishna elevation Shorts.

  python tools/make_vaibhavam_data.py

Reads Valmiki_Ramayanam/_tools/elevation_build.py (రామాయణ వైభవం) and krishna_build.py (కృష్ణ లీలా వైభవం):
every Short's clips with their planned times, lines, pictures' prompts, loop flag and caption, YouTube title and
description, thumbnail prompt. Writes src/data/vaibhavam_rama.json, vaibhavam_krishna.json and updates index.ts.
The voice-and-music file is picked up automatically from <series>/voice/Short_..._Vagmin_MIX.mp3 when it exists.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
TOOLS = os.path.join(os.path.dirname(MAKER), 'Valmiki_Ramayanam', '_tools')
sys.path.insert(0, TOOLS)
os.chdir(TOOLS)
import elevation_build as EB  # noqa: E402
import krishna_build as KB  # noqa: E402

SERIES = [
    ('rama', 'రామాయణ వైభవం', 'Ramayana_Vaibhavam', EB, lambda n: f'Short_{n:02d}', lambda n: f'{n:02d}'),
    ('krishna', 'కృష్ణ లీలా వైభవం', 'Krishna_Vaibhavam', KB, lambda n: f'Short_K{n}', lambda n: f'K{n}'),
]


# Scene sounds (tools/make_vsfx.py, SFX/elevation/): which clip gets which, from what the clip shows.
# (pattern, sound, where in the clip 0-1, volume over the voice-and-music mix); first matches win, at most 3 per clip.
import re  # noqa: E402
SFX_RULES = [
    (r'snapping in the middle|bow snapping|snaps in the middle|bow (?:snaps|breaks)', 'big_break', 0.45, 0.85),
    (r'thunderbolt|lightning', 'thunder_crack', 0.1, 0.6),
    (r'thunderbolt|lightning', 'lightning', 0.05, 0.45),
    (r'rain of (?:glowing )?arrows|streams of (?:glowing )?arrows|one blazing divine astra after another', 'arrow_rain', 0.2, 0.6),
    (r'swallowed|spirals? into', 'astra_blast', 0.45, 0.7),
    (r'drawing (?:the|a|his) (?:string|bowstring|blazing|glowing|huge)|drawing the bowstring|drawn on his bow|setting (?:the )?(?:glowing|blazing).{0,30}on (?:his|the) bow|stringing', 'bow_draw', 0.05, 0.55),
    (r'releas', 'bow_release', 0.15, 0.65),
    (r'releas', 'arrow_fly', 0.25, 0.55),
    (r'strikes|striking|pierces|blinding burst|burst of light', 'arrow_hit', 0.6, 0.7),
    (r'brahmastra|astra|thunderbolt', 'astra_charge', 0.0, 0.45),
    (r'trees? (?:crash|fall|topple|crack)|falling to either side|fallen trees|crashing down', 'tree_crash', 0.45, 0.8),
    (r'roof cracking|cracking and breaking|crumbl|tower top|chariot breaks apart|breaking apart|shatters|stamping', 'rock_crash', 0.4, 0.7),
    (r'boulder', 'boulder_splash', 0.4, 0.65),
    (r'blazing tail|tail blazing|flames bloom|tail catches fire|burning city|fire glow on gold', 'fire_roar', 0.05, 0.45),
    (r'ocean (?:heaving|churns)|stormy sea|boils|huge (?:stormy )?waves|waves rise', 'ocean_storm', 0.0, 0.45),
    (r'eagle|wingbeat|wings spread', 'wings', 0.1, 0.6),
    (r'driving .{0,40}chariot|chariot (?:descends|speeds|rushes)|chariot with green horses', 'chariot_rumble', 0.0, 0.4),
    (r'leaping|leaps? (?:up|off|over|into)|springs? (?:off|into)|springing|launch|shoots into the sky|dives? out of the clouds', 'leap_launch', 0.1, 0.6),
    (r'fly-through|flying|flies|soaring|streaks across|races through|flung far', 'fly_wind', 0.0, 0.45),
    (r'shockwave|trembles|tremble|shaking|mountain trembles', 'ground_rumble', 0.25, 0.6),
    (r'gasps?|amazement|in wonder|in awe', 'crowd_gasp', 0.3, 0.45),
    (r'cheer', 'cheer', 0.3, 0.5),
    (r'curd pot|broken (?:curd )?pot|pot breaks', 'pot_break', 0.3, 0.6),
    (r'runs? |running', 'ankle_bells', 0.1, 0.45),
    (r'rope', 'rope_tug', 0.35, 0.55),
    (r'glow|divine|shining|stars? |blessing|light spreads|radiant', 'divine_shimmer', 0.2, 0.3),
]


def sfx_for(row, climax, hook, krishna, loop=False):
    text = (row[1] + ' ' + row[2]).lower()
    out = []
    for pat, name, at, vol in SFX_RULES:
        if len(out) == 3:
            break
        if name == 'ankle_bells' and not krishna:
            continue
        if name == 'rock_crash' and any(x[0] == 'tree_crash' for x in out):
            continue   # one crash is enough
        if name == 'divine_shimmer' and out:
            continue   # a soft shimmer only where nothing else sounds
        if re.search(pat, text) and name not in [x[0] for x in out]:
            out.append([name, at, round(min(1.0, vol * (1.15 if climax else 1.0)), 2)])
    if loop:   # a loop has no voice and repeats: soft accents under its music, and no swish (it would play every repeat)
        return [[n, at, round(min(v, 0.35), 2)] for n, at, v in out if n != 'whoosh_fast'][:2]
    if hook and not any(x[0] in ('fly_wind', 'leap_launch') for x in out):
        out.insert(0, ['whoosh_fast', 0.0, 0.5])   # the Short opens with a swish
    return out[:3]


def build(key, te, folder, B, stem, short_id):
    out = []
    for sh in B.SHORTS:
        page = B.short_page(sh)
        total, slots = B.timing(sh)
        clips = []
        for c, (a, b), row in zip(page['clips'], slots, sh['rows']):
            clips.append({'no': c['no'], 'start': a, 'end': b, 'label': c['label'], 'say': row[5], 'shows': row[1],
                          'climax': len(row) > 6, 'refs': c['refs'], 'move': c['move'],
                          'sfx': sfx_for(row, len(row) > 6, c['no'] == 1, key == 'krishna', bool(sh.get('loop'))),
                          'img': c['imagePrompt'], 'end2': c['endImagePrompt'], 'vid': c['videoPrompt']})
        music = getattr(B, 'MUSIC', {}).get(sh['n']) if hasattr(B, 'MUSIC') else None
        out.append({'id': f"{key.capitalize()}-{short_id(sh['n'])}", 'n': sh['n'], 'label': short_id(sh['n']),
                    'headline': sh['headline'], 'hl': sh['hl'], 'sub': sh['sub'], 'src': sh['src'],
                    'loop': bool(sh.get('loop')), 'caption': sh.get('caption', ''), 'planLength': total, 'clips': clips,
                    'title': page['title'], 'desc': page['desc'], 'pinned': page['pinned'], 'thumb': page['thumbPrompt'],
                    'thumbRefs': page['thumbRefs'], 'musicPrompt': B.music_prompt(sh), 'kit': music or '',
                    'voiceScript': B.voice_script(sh) if not sh.get('loop') else '',
                    'auto': f"{folder}/voice/{stem(sh['n'])}_Vagmin_MIX.mp3",
                    # a loop's ready music (krishna_music.py), picked up when none is dropped
                    'autoMusic': f"{folder}/music/K{sh['n']}_loop.mp3" if sh.get('loop') else ''})
    return {'series': key, 'seriesTe': te, 'folder': folder, 'shorts': out}


def main():
    out_dir = os.path.join(MAKER, 'src', 'data')
    for key, te, folder, B, stem, sid in SERIES:
        d = build(key, te, folder, B, stem, sid)
        json.dump(d, open(os.path.join(out_dir, f'vaibhavam_{key}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f"vaibhavam_{key}: {len(d['shorts'])} Shorts")
    from make_movie_data import write_index
    write_index(out_dir)


if __name__ == '__main__':
    main()
