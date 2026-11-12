# -*- coding: utf-8 -*-
"""ElevenLabs voice for a రామాయణ వైభవం Short (user, 2026-11-11): energetic, warm, young, powerful, never laughing.

One take per voice on Eleven v3 (Telugu, audio tags), the whole Short in one request so the delivery flows.
No [excited] tag (it makes the voice jump in pitch and laugh). Each take is transcribed back with Scribe
and compared word by word with the script, so mispronounced or dropped words show up before you use it.
The key comes from the project's .env.local (never printed).

    python elevation_voice.py 4                 -> Ramayana_Vaibhavam/voice/Short_04_<voice>.mp3 (+ report)
    python elevation_voice.py 4 Sagar           -> one voice only
"""
import difflib
import json
import os
import re
import subprocess
import sys

import requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.dirname(HERE), 'Ramayana_Vaibhavam', 'voice')
API = 'https://api.elevenlabs.io'
VOICES = {'SaiDatta': 'f4UZfBDD7d4QR1DcXAMf', 'Anjan': 's50XhObhvufQgq7POHz0', 'Sagar': '2DRBj9T2XZ7Jmkcm6WCZ',
          'Vagmin': 'ZoV3Y9cqdke2p8nzz7XP'}

# The spoken script per Short: (v3 tag, line). Plain Telugu, story as Valmiki tells it.
SCRIPTS = {
    4: [  # Bala 67: kings could not lift it; 5,000 men pulled the chest; "vatsa rāma dhanuḥ paśya"; lifted as in play;
          # strung, drawn to the ear, broke in the middle with a thunder-like sound, the earth shook.
        ('[confident]', 'ఎంతో మంది రాజులు కదపలేని శివధనుస్సు… ఒక యువకుడి చేతిలో ఏమైంది?'),
        ('[storytelling]', 'ఐదు వేల మంది లాగితేనే కదిలిన ధనుస్సు. నాయనా రామా, చూడు, అన్నారు విశ్వామిత్ర మహర్షి. '
                           'శ్రీరాములవారు దాన్ని ఆటలా పైకెత్తారు.'),
        ('[intense]', 'అల్లెతాడు చెవి దాకా లాగారు… అంతే! పిడుగులాంటి శబ్దంతో ధనుస్సు విరిగిపోయింది! భూమి కంపించింది!'),
        ('[warm]', 'బలం కోసం కాదు… గురువు మాట కోసం! అదే మన శ్రీరాముడు. జై శ్రీరామ్ అని కామెంట్ చేసి, షేర్ చేయండి!'),
    ],
}


def key():
    load_dotenv(os.path.join(ROOT, '.env.local'))
    k = os.environ.get('ELEVENLABS_API_KEY')
    if not k:
        sys.exit('No ElevenLabs key in .env.local')
    return {'xi-api-key': k}


def speak(h, voice_id, text, path):
    r = requests.post(f'{API}/v1/text-to-speech/{voice_id}?output_format=mp3_44100_192', headers=h, timeout=180,
                      json={'text': text, 'model_id': 'eleven_v3', 'language_code': 'te',
                            'voice_settings': {'stability': 0.5, 'similarity_boost': 0.8, 'style': 0.0, 'use_speaker_boost': True}})
    if r.status_code != 200:
        sys.exit(f'TTS {r.status_code}: {r.text[:300]}')
    open(path, 'wb').write(r.content)
    open(path.replace('.mp3', '_raw.mp3'), 'wb').write(r.content)     # the untouched take, to compare


GAP = 0.12      # no gaps between lines (user, 2026-11-12): every pause is cut to this
TEMPO = 1.05    # a touch faster, same pitch (v3 ignores the speed setting)


def level(path):
    """Trim the ends, cut the gaps, tempo, loudness -16 LUFS (the mix lowers it further under the music)."""
    tmp = path + '.tmp.mp3'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', path, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                    f'silenceremove=stop_periods=-1:stop_duration={GAP}:stop_threshold=-42dB:stop_silence={GAP},'
                    f'atempo={TEMPO},loudnorm=I=-16:TP=-1.5:LRA=9', '-ar', '44100', '-b:a', '192k', tmp], check=True)
    os.replace(tmp, path)


def compose(h, prompt, seconds, path):
    """Hero BGM with ElevenLabs Music (instrumental). Returns False if the plan or API refuses."""
    r = requests.post(f'{API}/v1/music?output_format=mp3_44100_192', headers=h, timeout=600,
                      json={'prompt': prompt, 'music_length_ms': int(seconds * 1000), 'model_id': 'music_v1',
                            'force_instrumental': True})
    if r.status_code != 200:
        print(f'   music: {r.status_code} {r.text[:200]}')
        return False
    open(path, 'wb').write(r.content)
    return True


def mix(voice, music, path, voice_lufs=-19, music_lufs=-15, offset=0.0):
    """Preview: loud hero music, the voice a little lower but clear (music dips ~4 dB under the words); the mix ends
    at Shorts level -14 LUFS and the music rings out 1.6 s after the last word."""
    dur = stats(voice)[0]
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', voice, '-ss', f'{offset:.2f}', '-i', music, '-filter_complex',
                    f'[0:a]loudnorm=I={voice_lufs}:TP=-2,adelay=400|400,apad=whole_dur={dur + 1.8},asplit=2[v1][v2];'
                    f'[1:a]afade=t=in:d=0.05,loudnorm=I={music_lufs}:TP=-1.5,afade=t=out:st={dur + 0.4}:d=1.2[m];'
                    '[m][v1]sidechaincompress=threshold=0.04:ratio=2.5:attack=30:release=350[md];'
                    f'[md][v2]amix=inputs=2:duration=first:normalize=0,atrim=0:{dur + 1.6},loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95',
                    '-ar', '44100', '-b:a', '192k', path], check=True)


def stats(path):
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout.strip() or 0)
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=n=-40dB:d=0.6', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    gaps = [round(float(x), 1) for x in re.findall(r'silence_duration: ([\d.]+)', err)]
    return round(dur, 1), gaps


def hear(h, path):
    with open(path, 'rb') as f:
        r = requests.post(f'{API}/v1/speech-to-text', headers=h, timeout=180, files={'file': f},
                          data={'model_id': 'scribe_v1', 'language_code': 'tel', 'tag_audio_events': 'true'})
    if r.status_code != 200:
        return f'(STT {r.status_code})', []
    j = r.json()
    events = [w['text'] for w in j.get('words', []) if w.get('type') == 'audio_event']
    return j.get('text', ''), events


ENGLISH = {'comment': 'కామెంట్', 'share': 'షేర్', 'like': 'లైక్', 'subscribe': 'సబ్‌స్క్రైబ్'}


def words(t):
    """Letters only, spaces ignored (ఎంతోమంది = ఎంతో మంది); English CTA words count as their Telugu spelling."""
    t = re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', t)
    t = re.sub(r'[A-Za-z]+', lambda m: ENGLISH.get(m.group(0).lower(), m.group(0)), t)
    return list(re.sub(r'[^ఀ-౿]', '', t.replace('‌', '')))


def check(plain, heard):
    """Letter-level compare; a real word mistake (a word dropped, added or replaced: 4-5+ letters in one place; spoken forms like మేము/మేం pass) fails the take."""
    a, b = words(plain), words(heard)
    sm = difflib.SequenceMatcher(None, a, b)
    ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
    diffs = [(''.join(a[max(0, i1 - 6):i2 + 6]), ''.join(b[max(0, j1 - 6):j2 + 6])) for _, i1, i2, j1, j2 in ops]
    bad = any(max(i2 - i1, j2 - j1) >= 5 or (op != "replace" and max(i2 - i1, j2 - j1) >= 4) for op, i1, i2, j1, j2 in ops)
    return sm.ratio(), diffs, bad


def main(n, only=None, tries=3, music=True):
    h = key()
    import elevation_build as B
    sh = next(s for s in B.SHORTS if s['n'] == n)
    text, plain = B.voice_script(sh), ' '.join(B.spoken(sh))
    os.makedirs(OUT, exist_ok=True)
    report = []
    for name, vid in VOICES.items():
        if only and name != only:
            continue
        path = os.path.join(OUT, f'Short_{n:02d}_{name}.mp3')
        for k in range(1, tries + 1):
            speak(h, vid, text, path)
            level(path)
            dur, gaps = stats(path)
            heard, events = hear(h, path)
            ratio, diffs, bad = check(plain, heard)
            print(f'{name} take {k}: {dur}s, match {ratio:.1%}, pauses {gaps}, sounds {events or "none"}' + ('  -> RETAKE' if bad or events else ''))
            for x, y in diffs:
                print(f'   script: {x or "-"}   |   heard: {y or "-"}')
            if not bad and not events:
                break
        report.append({'voice': name, 'file': path, 'seconds': dur, 'pauses': gaps, 'match': round(ratio, 3),
                       'events': events, 'diffs': diffs, 'heard': heard, 'ok': not bad and not events})
        if music:
            remix(n, name)      # shared kit track (elevation_music.py), no new music per Short
    json.dump(report, open(os.path.join(OUT, f'Short_{n:02d}_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(OUT, f'Short_{n:02d}_script.txt'), 'w', encoding='utf-8').write(text)


def climax_times(sh, voice):
    """When each climax line ('i') starts in the mix: its share of the letters times the voice length (+0.4 s delay)."""
    import elevation_build as B
    lines = B.spoken(sh)
    total, dur = sum(B.letters(x) for x in lines), stats(voice)[0]
    return [0.4 + dur * sum(B.letters(x) for x in lines[:i]) / total for i, r in enumerate(sh['rows']) if len(r) > 6]


def remix(n, name='Vagmin'):
    """Mix the Short's voice with its kit track; the track's big hit lands on the latest climax line it can reach."""
    import elevation_build as B
    import elevation_data as D
    import elevation_music as M
    sh = next(s for s in B.SHORTS if s['n'] == n)
    voice = os.path.join(OUT, f'Short_{n:02d}_{name}.mp3')
    track = os.path.join(M.OUT, D.MUSIC[n] + '.mp3')
    start, hit = M.cues(track)
    dur = stats(voice)[0]
    room = stats(track)[0] - (dur + 2.0)                 # the track must last to the end of the Short
    lo, hi = hit - room, hit - start                     # where the hit can land in the Short
    times = climax_times(sh, voice) or [dur * 0.7]
    fits = [x for x in times if lo <= x <= hi]
    at = fits[-1] if fits else min(times, key=lambda x: min(abs(x - lo), abs(x - hi)))
    offset = max(start, min(hit - at, room))
    out = os.path.join(OUT, f'Short_{n:02d}_{name}_MIX.mp3')
    mix(voice, track, out, offset=offset)
    print(f'Short {n}: {D.MUSIC[n]} from {offset:.1f}s; big hit at {hit - offset:.1f}s, climax line at {at:.1f}s'
          + ('' if abs(hit - offset - at) < 1.0 else '  (off by %.1fs)' % (hit - offset - at)))


if __name__ == '__main__':
    if sys.argv[1] == 'mix':
        for x in sys.argv[2:]:
            remix(int(x))
    else:
        main(int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
