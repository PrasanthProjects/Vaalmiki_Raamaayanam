"""Scene sounds for the వైభవం Shorts (user, 2026-11-12): short, punchy effects that match each moment (bow draw, arrow
flight and hit, divine astra charge and blast, thunder and lightning, speed whooshes, the bow breaking, crashes,
splashes, fire, wings, cheers, and Krishna's bells, rope and pot) instead of plain music alone.

  python tools/make_vsfx.py            -> SFX/elevation/<name>.mp3 (only the missing ones; --all remakes)

ElevenLabs Sound Effects (eleven_text_to_sound_v3), levelled to -16 LUFS. make_vaibhavam_data.py decides which
clip gets which sound from what the clip shows; Vaibhavam.tsx plays them over the voice-and-music mix.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_sfx import check, level, load_env  # noqa: E402

OUT = os.path.join(MAKER, 'SFX', 'elevation')
NM = ', no music, no voices'
SOUNDS = {
    'bow_draw': (2.0, 'A heavy wooden war bow being drawn back slowly, the string creaking under great tension, close and powerful' + NM),
    'bow_release': (1.5, 'A powerful bow string released with a deep twang and a sharp snap, cinematic' + NM),
    'arrow_fly': (2.0, 'A glowing arrow flying fast past the listener, a sharp rising whistle then a whoosh fading into the distance, cinematic' + NM),
    'arrow_hit': (2.0, 'A divine arrow striking with a deep powerful impact boom and a shimmering burst of energy, cinematic' + NM),
    'arrow_rain': (3.0, 'Hundreds of arrows whistling through the air in a dense volley, then many rapid impacts, epic battle' + NM),
    'astra_charge': (3.0, 'A divine weapon charging with energy: a rising humming glow and crackling power building to a peak, cinematic' + NM),
    'astra_blast': (3.0, 'A colossal divine energy blast: a deep thunderous boom, a bright shimmering shockwave and a long rumble, cinematic' + NM),
    'thunder_crack': (4.0, 'A sudden close thunder crack, sharp and violent, then a long rolling rumble, no rain' + NM),
    'lightning': (2.0, 'Electric lightning crackling and sizzling with a sharp bright zap, raw storm energy' + NM),
    'whoosh_fast': (1.0, 'A very fast whoosh of something rushing past at high speed, clean and cinematic' + NM),
    'fly_wind': (3.0, 'Flying high and fast through the sky, strong rushing wind past the ears and through clouds' + NM),
    'leap_launch': (2.0, 'A mighty leap: a heavy thump of feet pushing off rock, then a powerful rising whoosh into the sky' + NM),
    'big_break': (3.0, 'A gigantic bow snapping in the middle with a thunderous crack and a deep boom echoing in a great stone hall' + NM),
    'tree_crash': (3.0, 'Two giant trees cracking at the roots and crashing down to the ground with branches and leaves, heavy impact' + NM),
    'rock_crash': (3.0, 'Huge rocks and stone breaking and crumbling down, a heavy crash with falling debris' + NM),
    'boulder_splash': (3.0, 'A huge boulder thrown into the sea: a massive deep splash and spray raining back down' + NM),
    'fire_roar': (3.0, 'A large fire whooshing up and roaring, flames rushing across wooden roofs, crackling' + NM),
    'ocean_storm': (4.0, 'A stormy ocean: huge waves rising and crashing, roaring water and wind' + NM),
    'wings': (2.0, 'Huge bird wings flapping powerfully and fast, feathers and wind' + NM),
    'ground_rumble': (3.0, 'A deep earth rumble and the ground shaking, a low powerful tremor' + NM),
    'crowd_gasp': (2.0, 'A large royal court crowd gasping in amazement all at once, then a hushed murmur, no words'),
    'cheer': (3.0, 'A big crowd of warriors cheering and roaring in victory, no words' + ', no music'),
    'divine_shimmer': (2.0, 'A soft divine shimmer of temple bells and glittering light, magical and holy' + NM),
    'chariot_rumble': (3.0, 'An ancient war chariot rushing past, heavy wheels rumbling and horses galloping' + NM),
    'pot_break': (1.5, 'A clay pot falling and shattering on a stone floor with a splash of curd' + NM),
    'ankle_bells': (2.0, 'Little silver ankle bells jingling as a small child runs on a stone floor, cute and light' + NM),
    'rope_tug': (1.5, 'A thick rope pulled tight with a creak and a soft stretch, then a playful slip' + NM),
}


def main(args):
    load_env()
    from elevenlabs import ElevenLabs
    client = ElevenLabs()
    os.makedirs(OUT, exist_ok=True)
    want = [a for a in args if not a.startswith('--')]
    names = want or [n for n in SOUNDS if '--all' in args or not os.path.exists(os.path.join(OUT, n + '.mp3'))]
    for n in names:
        sec, prompt = SOUNDS[n]
        audio = client.text_to_sound_effects.convert(text=prompt, model_id='eleven_text_to_sound_v3', duration_seconds=sec,
                                                     prompt_influence=0.7, output_format='mp3_44100_192')
        path = os.path.join(OUT, n + '.mp3')
        with open(path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)
        level(path)
        dur, lufs, silent = check(path)
        print(f"{n:15s} {dur:4.1f}s  {lufs} LUFS  silent {silent:.1f}s" + ('  ⚠ mostly silent' if silent > dur / 2 else ''), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
