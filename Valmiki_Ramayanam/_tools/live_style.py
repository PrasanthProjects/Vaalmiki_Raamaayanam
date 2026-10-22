"""Clip prompts in the format of the published Flow helper page (claude.ai), with its reference library.

data/shorts_refs.json holds every character, crowd, object and place of that page: its English label (as the
prompts name it), its look (the text a prompt repeats), its Telugu label, group, and its reference-image prompt.
A sarga whose flow rows name only keys from this library is built in this format (see build.py).
"""
import json
import os
import re

TOOLS = os.path.dirname(os.path.abspath(__file__))
LIB = json.load(open(os.path.join(TOOLS, 'data', 'shorts_refs.json'), encoding='utf-8'))

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
    'RAKSHASAS': ('an army of varied rakshasa soldiers in traditional dark dhotis and ornate armour, fierce but not '
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


def still(keys, frame, light):
    keys = order(keys)
    return ("Vertical 9:16 cinematic still image, 1080x1920, main subject in the centre safe area. "
            f"{QUALITY_STILL} {use_sentence(keys)}Style: {STYLE}. {cast(keys, False)}"
            f"Scene: {frame}{hands_note(keys, frame)} Lighting and atmosphere: {light} "
            f"{ANATOMY}. {RESPECT} No text, letters, logos or watermarks.")


def video(keys, frame, motion, cam, light):
    keys = order(keys)
    return ("Vertical 9:16 cinematic shot, 8 seconds, main subject in the centre safe area. "
            f"{QUALITY_VIDEO} {use_sentence(keys)}Style: {STYLE}. {cast(keys, True)}"
            f"Opening frame: {frame} Then: {motion}{hands_note(keys, frame, motion)} Camera: {cam} "
            f"Lighting and effects: {light} {ANATOMY}; smooth, physically consistent motion with no morphing or "
            f"flicker. {RESPECT} No text, letters, subtitles, logos or watermarks anywhere in the frame. "
            "Audio: soft ambient atmosphere only, no speech, no singing, no music.")


def thumb(keys, frame, light):
    keys = [k for k in order(keys) if k in GROUP_TEXT or LIB[k]['kind'] != 'place']   # a close-up: no place image
    return ("Vertical 9:16 YouTube Shorts thumbnail key art, single still image, 1080x1920. "
            f"{QUALITY_STILL} {use_sentence(keys)}Style: {STYLE}. {cast(keys, False)}"
            f"Scene: {frame}{hands_note(keys, frame)} Make it a bold, emotional close-up of the main character or "
            f"symbol in the lower-middle of the frame, strong expression, high contrast, glowing rim light. {light} "
            "Keep the top 35% of the frame a clean dark gradient or soft sky with no important detail (space for a "
            "headline) and the bottom 12% calm and plain (space for a small line). "
            f"{RESPECT} No text, letters, numbers, logos or watermarks in the image."), ref_keys(keys)


def library(keys=None):
    """The reference list a helper page shows: only the images its clips use (all of them when keys is None)."""
    return [{'key': k, 'prompt': v['refprompt'], 'face': v.get('face') or '', 'label': v['te'], 'group': v['group'],
             **({'look': v['look']} if v['kind'] == 'place' else {})}   # the page shows a look only for places
            for k, v in LIB.items() if keys is None or k in keys]
