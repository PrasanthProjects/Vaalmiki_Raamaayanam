"""Clip prompts in the format of the published Flow helper page (claude.ai), with its reference library.

data/shorts_refs.json holds every character, crowd, object and place of that page: its English label (as the
prompts name it), its look (the text a prompt repeats), its Telugu label, group, and its reference-image prompt.
A sarga whose flow rows name only keys from this library is built in this format (see build.py).
"""
import json
import os
import re

from soften import soft, soften

TOOLS = os.path.dirname(os.path.abspath(__file__))
LIB = soften(json.load(open(os.path.join(TOOLS, 'data', 'shorts_refs.json'), encoding='utf-8')))   # soft words only

QUALITY_STILL = ("Very high quality: ultra-detailed, sharp and clean 4K-quality render, rich colour depth, "
                 "film-quality lighting, no blur, no noise, no artefacts.")
QUALITY_VIDEO = ("Very high quality: ultra-detailed, sharp and clean cinematic render, rich colour depth, "
                 "film-quality lighting, smooth natural 24fps motion, no blur, no noise, no artefacts.")
STYLE = ("traditional Indian devotional epic art brought to life as premium cinematic 3D animation, inspired by "
         "classical Indian temple murals and traditional devotional paintings of Hindu gods, stylized (not "
         "photorealistic) characters with divine, graceful, dignified features faithful to traditional Hindu "
         "iconography, every character with a clearly individual face (different face shape, eyes, nose, age and "
         "build) so that no two characters ever share the same face, rich jewel-tone colours with temple-gold "
         "accents, ancient South Indian temple-era architecture; forest and ashram settings are lush, green and "
         "serene with flowering trees, clear rivers and streams, deer, peacocks and birds (darker only where the "
         "scene says so); volumetric god rays, soft glowing divine light, high detail, smooth fluid motion, "
         "reverent devotional mood")
RESPECT = ("This is a sacred Hindu devotional scene from the Valmiki Ramayana: depict every deity and character with "
           "deep reverence and faithful traditional Indian iconography. Everyone is fully and modestly dressed in "
           "traditional Indian attire (women in properly draped silk or cotton sarees covering the shoulders and "
           "body, men in dhoti with angavastram or bark-cloth); no revealing, Western, fantasy-armour or modern "
           "clothing; no sexualised or suggestive poses; no blood, wounds, gore or graphic violence; no horror or "
           "jump-scare look; no comedy, cartoon exaggeration or caricature; no distorted, mocking or disrespectful "
           "depiction of gods; no modern objects, buildings, vehicles or technology.")
ANATOMY = "Correct anatomy and natural hands; no extra characters, limbs or faces beyond those described"
MATCH_CHAR = ("match the face, skin colour, hair, clothing and ornaments exactly as in the reference (hand-held "
              "objects only as this scene describes), keep the same art style, and do not redesign")
HANDS_FREE = "Valmiki's hands are free: no palm-leaf manuscripts, no stylus, no books."
# Crowds named in a scene's cast without a reference image of their own (the text the page uses for them).
GROUP_TEXT = {
    'DEVAS': 'radiant celestial devas on clouds in traditional silk and gold crowns, showering flowers',
    'PEOPLE': ('devout people of ancient Ayodhya in traditional South Indian clothing (men in dhoti and angavastram, '
               'women in fully draped sarees), each with a red kumkum mark'),
    'RISHIS': ('a group of venerable forest rishis in ochre and white robes with white beards and kamandalus, most with '
               'white Vishnu namam and some with three ash-white Shiva lines'),
    'RAKSHASAS': ('an army of varied rakshasa soldiers in which no two faces are alike and none resembles Ravana (different ages, skin tones, builds, hair and beards, all single-headed and uncrowned), in traditional dark dhotis and ornate armour, fierce but not '
                  'horror, different builds, some with moustaches, three horizontal ash-white Shiva lines with a red '
                  'dot on the forehead'),
    'VANARAS': ('a vast army of varied vanara warriors in traditional dhotis and sashes, different fur tones and builds, '
                'white Vishnu namam with a red centre line on the forehead'),
}


def known(keys):
    return all(k in LIB or k in GROUP_TEXT for k in keys)


def order(keys):
    """The cast in the order the scene lists it, the place last (as the page lists them)."""
    is_place = lambda k: k in LIB and LIB[k]['kind'] == 'place'
    return [k for k in keys if not is_place(k)] + [k for k in keys if is_place(k)]


def ref_keys(keys):
    return [k for k in order(keys) if k in LIB]


def use_sentence(keys):
    keys = [k for k in keys if k in LIB]
    if not keys:
        return ''
    lst = '; '.join(f"{k}.png = {LIB[k]['label']}" for k in keys)
    if len(keys) == 1:
        if LIB[keys[0]]['kind'] == 'place':
            return (f"Use the attached reference image as the exact look of the place ({lst}): match its "
                    "architecture, landscape, colours and layout exactly, keep the same art style, and do not "
                    "redesign it. ")
        return f"Use the attached reference image as the exact look of the character ({lst}): {MATCH_CHAR} it. "
    who = 'each character, object and place' if any(LIB[k]['kind'] == 'place' for k in keys) else 'each character'
    return f"Use the attached reference images as the exact look of {who} ({lst}): {MATCH_CHAR} them. "


def cast(keys, video):
    """'Characters: …. Location (…): …. ' for the given (ordered) keys."""
    looks = [GROUP_TEXT[k] if k in GROUP_TEXT else LIB[k]['look'] for k in keys
             if k in GROUP_TEXT or LIB[k]['kind'] != 'place']
    places = [k for k in keys if k in LIB and LIB[k]['kind'] == 'place']
    out = ''
    if looks:
        out += ('Characters (keep exactly this look for the whole shot): ' if video else 'Characters: ') \
               + '; '.join(looks) + '. '
    for p in places:
        out += f"Location (match the attached place reference {p}.png): {LIB[p]['look']}. "
    return out


def hands_note(keys, *texts):
    return f' {HANDS_FREE}' if 'VALMIKI' in keys and not re.search(r'manuscript|palm-leaf|stylus|writ',
                                                                    ' '.join(texts), re.I) else ''


# Framing per clip role, and the scroll-stopping first frame of the hook (first made on the live pages, brought
# into the builder on 2026-11-08 so a rebuild keeps them).
HOOK_FRAME = ("This is the very first frame of a YouTube Short and must stop the scroll: show the most emotional moment "
              "of this scene as a bold close-up or medium close-up, faces and expressions large and clearly readable, "
              "strong dramatic devotional lighting with rich contrast, one clear focal point and an uncluttered "
              "background; reverent and dignified, never frightening. ")
CINE = {
    'హుక్': "a striking, cinematic opening composition like the key art of a high-end Indian mythological film, the "
            "emotion of the moment (wonder, devotion, sorrow, courage or resolve) instantly clear in the eyes and "
            "posture, warm rim light separating the characters from the background, shallow depth of field.",
    'తాత్పర్యం – 1': "a cinematic storytelling shot like a high-end Indian mythological film: medium or medium-close "
                     "framing at eye level, the characters' emotion (devotion, sorrow, resolve or joy) clearly readable "
                     "in their eyes, faces and posture, motivated lighting with a soft rim light separating them from "
                     "the background, shallow depth of field, rich foreground and background depth.",
    'తాత్పర్యం – 2': "a cinematic storytelling shot like a high-end Indian mythological film: a different angle from "
                     "the previous shot (over-the-shoulder, profile or reaction close-up), the characters' emotion "
                     "clearly readable in their eyes, faces and posture, motivated lighting with a soft rim light, "
                     "shallow depth of field, rich foreground and background depth.",
    'శ్లోక పఠనం – 1': "a sacred, majestic shot for the sloka recital: the scene's central image framed with "
                      "near-symmetry from a gentle low angle that gives dignity, golden god rays and soft floating "
                      "light particles, the main subject in the middle third with calm, uncluttered space in the upper "
                      "and lower thirds for the on-screen sloka text.",
    'శ్లోక పఠనం – 2': "a sacred, majestic shot for the sloka recital, slightly closer than the previous one: "
                      "near-symmetrical framing, soft golden divine light and floating light particles, the main "
                      "subject in the middle third with calm, uncluttered space in the upper and lower thirds for the "
                      "on-screen sloka text.",
    'జీవిత పాఠం': "a calm, reflective, symbolic shot: medium-wide framing in a peaceful natural setting, soft warm "
                  "light, a sense of stillness that lets the lesson sink in.",
    'ముగింపు & CTA': "a warm, hopeful closing shot in soft golden light, composed so that it flows naturally back "
                     "into the opening shot when the Short loops.",
}


@soft
def still(keys, frame, light, role=None):
    keys = order(keys)
    cine = f"Cinematography: {CINE[role]} " if role in CINE else ''
    return ("Vertical 9:16 cinematic still image, 1080x1920, main subject in the centre safe area. "
            f"{HOOK_FRAME if role == 'హుక్' else ''}"
            f"{QUALITY_STILL} {use_sentence(keys)}Style: {STYLE}. {cast(keys, False)}"
            f"Scene: {frame}{hands_note(keys, frame)} Lighting and atmosphere: {light} {cine}"
            f"{ANATOMY}. {RESPECT} No text, letters, logos or watermarks.")


STABLE = ("Keep it stable: every character keeps exactly the same face, hair, clothes, ornaments, colours and size "
          "as in the start frame for the whole shot; nobody new appears and nobody disappears; no sudden or jerky "
          "movements, no running, jumping or turning unless the action says so; hands and weapons stay natural; "
          "the background and props stay fixed; one continuous shot with no cuts and no scene change.")
STABLE_HOOK = ("Keep every character exactly the same face, hair, clothes, ornaments, colours and size as in the start "
               "frame for the whole shot; nobody new appears and nobody disappears; hands and weapons stay natural; "
               "one continuous shot with no cuts and no scene change.")
GENTLE = ("Only small, natural, gentle movement: soft breathing, a slow blink, a slight turn of the head or eyes, "
          "clothes, hair and leaves stirring in a light breeze, lamp flames and water shimmering softly; "
          "the characters stay in their places and keep their poses.")


VIDEO_START = "Animate the attached start frame as one continuous 8 second vertical 9:16 shot. "
# The user's own image for the clip comes first: the video follows it, not a style of its own (2026-11-06).
FOLLOW_IMAGE = ("The start frame is the image made for this clip and is the exact look of the whole video: keep its "
                "art style, rendering, colours, lighting and framing, and keep every character, animal, vehicle and "
                "place exactly as it is there (the same faces, bodies, feathers, clothes, crowns and ornaments; the "
                "same number of heads, arms, legs and wings); do not restyle, redraw or redesign anything and do not "
                "add or remove anyone; only bring the image to life with motion. ")
VIDEO_STYLE = ("exactly the style of the start frame: premium, highly detailed cinematic 3D like a big-budget Indian "
               "mythological feature film, lifelike skin, hair, fabric, feather, gold and stone textures, real depth "
               "and film lighting, characters with divine, graceful, dignified features faithful to traditional Hindu "
               "iconography and each with a clearly individual face; rich jewel-tone colours with temple-gold "
               "accents, volumetric god rays, high detail, smooth fluid motion, reverent devotional mood; never a "
               "cartoon, anime, flat 2D, clay, toy-like or plastic look")
RESPECT_VIDEO = RESPECT.replace('Everyone is fully', 'Every person is fully') \
    + " Birds and animals stay exactly as in the start frame, with no clothes."


@soft
def start_video(keys, frame, motion, cam, light, action, hook=False):
    """Flow Frames to Video: the image made with still() is the first frame and the look to follow. Action clips
    play their motion over 0–2 s settle / 2–6 s action / 6–8 s rest; the other clips only breathe. The hook
    (first clip) moves boldly from the first second, to stop the scroll (user, 2026-11-08)."""
    keys = order(keys)
    if hook:
        motion, cam = motion.rstrip(' .'), re.sub(r'(?i)(very )?slow(ly)?\s*', '', cam.rstrip(' .'), count=1).strip() or 'push-in'
        move = (f"Action, bold and dramatic from the very first second (this is the opening hook of a YouTube Short "
                f"and must stop the scroll): 0–1 s the motion starts at once, no still hold; 1–6 s {motion}, with "
                "strong, clearly visible movement all through the frame: wind in the hair and cloth, swirling dust, "
                "leaves, petals or sparks, light flaring and shifting; 6–8 s end on a striking, emotional close-up "
                "and hold.")
        cam = (f"{cam}; a bold, sweeping cinematic move (a fast push-in, a rising crane or an orbit around the "
               "subject), smooth and stable, no shake")
    else:
        cam = cam.rstrip(' .')
        move = (f"Action, slow and smooth: 0–2 s hold the start frame and settle; 2–6 s {motion}; 6–8 s come to "
                "rest and hold the final pose." if action else GENTLE)
        cam = (cam if action else 'a very slow, steady push-in') + '; slow, steady and smooth, no shake, no sudden zoom'
    return (f"{VIDEO_START}{FOLLOW_IMAGE}"
            f"{QUALITY_VIDEO} {use_sentence(keys)}Style: {VIDEO_STYLE}. {cast(keys, True)}"
            f"The frame shows: {frame}{hands_note(keys, frame, motion)} {move} Camera: {cam}. "
            f"Lighting and effects: {light} {STABLE_HOOK if hook else STABLE} {ANATOMY}; physically "
            f"consistent motion with no morphing or flicker. {RESPECT_VIDEO} No text, letters, subtitles, logos or "
            "watermarks anywhere in the frame. Audio: soft ambient atmosphere only, no speech, no singing, no music.")


@soft
def video(keys, frame, motion, cam, light):
    keys = order(keys)
    return ("Vertical 9:16 cinematic shot, 8 seconds, main subject in the centre safe area. "
            f"{QUALITY_VIDEO} {use_sentence(keys)}Style: {STYLE}. {cast(keys, True)}"
            f"Opening frame: {frame} Then: {motion}{hands_note(keys, frame, motion)} Camera: {cam} "
            f"Lighting and effects: {light} {ANATOMY}; smooth, physically consistent motion with no morphing or "
            f"flicker. {RESPECT} No text, letters, subtitles, logos or watermarks anywhere in the frame. "
            "Audio: soft ambient atmosphere only, no speech, no singing, no music.")


@soft
def thumb(keys, frame, light):
    keys = [k for k in order(keys) if k in GROUP_TEXT or LIB[k]['kind'] != 'place']   # a close-up: no place image
    return ("Vertical 9:16 YouTube Shorts thumbnail key art, single still image, 1080x1920. "
            f"{QUALITY_STILL} {use_sentence(keys)}Style: {STYLE}. {cast(keys, False)}"
            f"Scene: {frame}{hands_note(keys, frame)} Make it a bold, emotional close-up of the main character or "
            f"symbol in the lower-middle of the frame, strong expression, high contrast, glowing rim light. {light} "
            "Keep the top 35% of the frame a clean dark gradient or soft sky with no important detail (space for a "
            "headline) and the bottom 12% calm and plain (space for a small line). "
            f"{RESPECT} No text, letters, numbers, logos or watermarks in the image."), ref_keys(keys)


@soft
def library(keys=None):
    """The reference list a helper page shows: only the images its clips use (all of them when keys is None)."""
    return [{'key': k, 'prompt': v['refprompt'], 'face': v.get('face') or '', 'label': v['te'], 'group': v['group'],
             **({'look': v['look']} if v['kind'] == 'place' else {})}   # the page shows a look only for places
            for k, v in LIB.items() if keys is None or k in keys]
