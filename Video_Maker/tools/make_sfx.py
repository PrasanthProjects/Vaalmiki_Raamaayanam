"""Make the Video Maker's sound effects with ElevenLabs Sound Effects (model v3), from src/data/sfx_prompts.json.

  python tools/make_sfx.py            # the ambience and moment sounds that are missing
  python tools/make_sfx.py --all      # all of them again (old files move to SFX/_old/)
  python tools/make_sfx.py conch roar # only these

The ElevenLabs SDK reads ELEVENLABS_API_KEY; it is loaded from the project's .env.local (set up with
`npx -y @elevenlabs/cli@latest onboard init`, git-ignored, never printed). Ambiences are made as seamless loops.
Each result is levelled to -16 LUFS and checked (length, loudness, silence).
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
ROOT = os.path.dirname(MAKER)
SFX = os.path.join(MAKER, 'SFX')


def load_env():
    """Load ELEVENLABS_API_KEY from the project's .env.local (the key is never printed or stored in code)."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env.local"))


def check(path):
    """Length, loudness and how much of it is near-silent."""
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout.strip() or 0)
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128,silencedetect=n=-45dB:d=0.4', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    lufs = next((l.split('I:')[1].split('LUFS')[0].strip() for l in out.splitlines()[::-1] if 'I:' in l), '?')
    silent = sum(float(l.split('silence_duration:')[1]) for l in out.splitlines() if 'silence_duration:' in l)
    return dur, lufs, silent


def level(path):
    tmp = path + '.tmp.mp3'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', path,
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '44100', '-b:a', '192k', tmp], check=True)
    os.replace(tmp, path)


def main(args):
    load_env()
    if not os.environ.get('ELEVENLABS_API_KEY'):
        sys.exit('No ElevenLabs key: run `npx -y @elevenlabs/cli@latest onboard init` in the project folder.')
    from elevenlabs import ElevenLabs
    client = ElevenLabs()
    sounds = json.load(open(os.path.join(MAKER, 'src', 'data', 'sfx_prompts.json'), encoding='utf-8'))['sounds']
    want = [n for n in args if not n.startswith('--')]
    names = want or [n for n, s in sounds.items() if s['kind'] in ('ambience', 'moment')
                     and ('--all' in args or not os.path.exists(os.path.join(SFX, n + '.mp3')))]
    if not names:
        print('Nothing to make: every sound is already there (use --all to remake).')
        return
    os.makedirs(SFX, exist_ok=True)
    for n in names:
        s = sounds[n]
        loop = s['kind'] == 'ambience'
        audio = client.text_to_sound_effects.convert(
            text=s['prompt'], model_id='eleven_text_to_sound_v3', duration_seconds=float(s['seconds']),
            prompt_influence=0.5 if loop else 0.7, loop=loop, output_format='mp3_44100_192')
        path = os.path.join(SFX, n + '.mp3')
        new = path + '.new.mp3'
        with open(new, 'wb') as f:
            for chunk in audio:
                f.write(chunk)
        if os.path.exists(path):   # keep the old one, never lose a file
            os.makedirs(os.path.join(SFX, '_old'), exist_ok=True)
            shutil.move(path, os.path.join(SFX, '_old', n + '.mp3'))
        os.replace(new, path)
        level(path)
        dur, lufs, silent = check(path)
        flag = '  ⚠ mostly silent' if silent > dur / 2 else ''
        print(f"{n:12s} {dur:5.1f}s  {lufs} LUFS  silent {silent:.1f}s{flag}", flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
