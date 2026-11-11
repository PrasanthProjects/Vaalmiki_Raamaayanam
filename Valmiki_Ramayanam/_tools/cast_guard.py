# -*- coding: utf-8 -*-
"""Keep Sita out of pictures she is not in (user, 2026-11-11).

Image models add Sita on their own when Rama and Lakshmana appear together (the familiar exile trio), and when a
character's look mentions her ("Sita's father", "his wedding with Sita"). In Bala V06 the scene "Rama, Lakshmana and
Vishwamitra walking along the forest path" came back as Rama, Sita and Lakshmana. Every builder (Shorts live_style.cast,
long_build.scene_cast, video_build.cast, cinema_build.cast) adds this line when Sita is not in the cast.
"""
import re

WOMEN = {'SITA', 'KAUSALYA', 'KAIKEYI', 'SUMITRA', 'MANTHARA', 'URMILA', 'MANDAVI', 'SHRUTAKIRTI', 'SHABARI', 'TARA',
         'MANDODARI', 'AHALYA', 'TRIJATA', 'SHURPANAKHA', 'TATAKA', 'AYOMUKHI', 'SURASA', 'SIMHIKA', 'HARIJATA', 'RUMA',
         'ANJANA', 'DHANYAMALINI', 'ANASUYA', 'SATYAVATI', 'SOMADA', 'GANGA', 'UMA', 'PARVATI', 'MENAKA', 'RAMBHA',
         'SWAYAMPRABHA', 'LANKINI', 'DITI', 'KESHINI', 'SUMATI', 'VEDAVATI', 'SARASWATI', 'LAKSHMI'}

STRONG = ("Sita is NOT in this scene: do not show Sita or any young woman beside Rama and Lakshmana; only the "
          "characters described here appear.")
MILD = "Sita is NOT in this scene: do not show her; only the characters described here appear."


def _base(k):
    return k.split(':')[0].split('_')[0].upper()


def sita_guard(keys, looks='', scene=''):
    """keys: the cast's reference or character keys (RAMA_VISHWAMITRA, SITA_ARANYA, ...); looks: their descriptions;
    scene: the scene's own words. '' when Sita is cast, when the scene itself speaks of her (her birth, a memory), or
    when nothing would bring her in."""
    bases = {_base(k) for k in keys}
    if 'SITA' in bases or re.search(r'\b(Sita|Seeta|Janaki|Vaidehi|Maithili)\b', scene, re.I):
        return ''
    pair = {'RAMA', 'LAKSHMANA'} <= bases
    if not (pair or re.search(r'\bSita\b', looks)):
        return ''
    other_women = bases & (WOMEN - {'SITA'})
    # before the wedding (baby, boy, with Vishwamitra) Sita is never with them: "the three", "her" mean someone else
    young = any(re.fullmatch(r'(RAMA|LAKSHMANA)_(BABY|BOY|VISHWAMITRA|S1)', k.split(':')[0]) for k in keys)
    if not young and not other_women and re.search(r'\b(she|her|hers|herself|wife|bride|princess|the three|trio|couple|group|infant|baby|daughter|wedding|kanyadan\w*)\b', scene, re.I):
        return ''   # "the deer in front of her", "Janaka placing her hand in Rama's": Sita is there, only unnamed
    return MILD if other_women or not pair else STRONG


# ---- how people talk and cry on screen (user, 2026-11-11, Bala 1.60: "Rama sits in front of Sugriva and tells him") ----
TALK = re.compile(r'\b(speak|speaks|speaking|tell|tells|telling|narrat\w*|explain\w*|listen\w*|talk\w*|asks?|asking|answer\w*|'
                  r'describ\w*|confid\w*|pleading|advis\w*|instruct\w*)\b', re.I)
STAGING = ("Natural conversation staging, as in a real film scene: the characters sit or stand facing each other, seen from "
           "the side or over the listener's shoulder; the one speaking is turned toward the listener and the listener "
           "is turned toward the speaker, attentive; they do not both face the camera, and nobody stands behind another.")
TEARS = re.compile(r'\b(tear|tears|tearful|crying|cries|weep\w*|sob\w*|eyes wet|wet eyes)\b', re.I)
GENTLE_TEARS = ("Gentle, real tears as people cry while speaking: eyes glistening, one or two tears rolling slowly down "
                "the cheek, the face calm and dignified; no sobbing, no open-mouthed wailing, no distorted face.")


def staging(n_chars, text):
    """The staging sentence when two or more characters talk; '' otherwise."""
    return STAGING if n_chars >= 2 and TALK.search(text or '') else ''


def tears(text):
    return GENTLE_TEARS if TEARS.search(text or '') else ''


# ---- cinematic camera moves chosen from the scene (user, 2026-11-11: drones over kingdoms, top and side views, the
# arrow followed from Rama to the rakshasa). Each move gives where the camera starts (the start image), how it moves
# (the video) and where it ends (the end image), so the three always agree. ----
MOVES = {
    'drone': ("a high, wide aerial drone view of the whole place from above and in front",
              "a smooth aerial drone glide: the camera flies forward over the place and gently descends toward the main subject",
              "a lower, closer view of the main subject with the place still visible around it"),
    'top_down': ("a top-down view from directly above the scene",
                 "the camera descends from the top-down view and tilts smoothly into a side view at eye level",
                 "an eye-level side view of the scene"),
    'arrow': ("a view from just behind the archer's shoulder as the arrow (or weapon) leaves the bow, the target far ahead",
              "the camera travels alongside the arrow in one smooth tracking move, following its glowing path through the "
              "air from the archer to the target",
              "the target at the moment the arrow reaches it, seen from the side; clean and dignified, shown through light "
              "and a burst of glow"),
    'side_front': ("a side view of the characters in profile as they talk",
                   "a slow arc around the one speaking, from the side to the front",
                   "a front view of the face of the one speaking, the listener soft in the foreground"),
    'side_top': ("a side view at eye level",
                 "a slow crane move rising from the side view to a high view looking down",
                 "a high view looking down on the whole scene"),
    'low_up': ("a low angle from below the main figure",
               "a slow tilt up from below toward the figure and the sky",
               "the figure framed against the glowing sky from a low angle"),
    'zoom_in': ("a medium shot of the main character",
                "a slow, steady zoom in toward the face",
                "a close view of the face"),
}
_ARROW = re.compile(r'\b(arrows?|astras?|shoots?|shooting|loos\w+|weapon flies|hurls?|throws?|flicks?|missiles?)\b', re.I)
_PLACE = re.compile(r'\b(city|cities|kingdom|capital|ayodhya|lanka|kishkindha|mithila|ocean|sea|setu|bridge|mountains?|hills?|'
                    r'valley|landscape|panorama|aerial|island|ramparts|palaces? of|golden city)\b', re.I)
_CROWD = re.compile(r'\b(army|armies|battlefield|troops|crowds?|citizens|procession|vanaras? (?:army|host))\b', re.I)
_SKY = re.compile(r'\b(sky|heavens?|clouds|descend\w*|rising|ascend\w*|divine light|celestial|gods? (?:appear|watch))\b', re.I)
_FACE = re.compile(r'\b(close on|close-up|face|eyes|tears?|smil\w+)\b', re.I)
_GIVEN = re.compile(r'\b(drone|aerial|crane|tracking|orbit|arc|top[- ]down|overhead|two-shot|from (?:a|the) \w+ (?:view|shot) to)\b', re.I)


def camera_move(n_chars, frame, motion='', cam=''):
    """The camera move for a clip, or None when the author's own camera is specific enough (or nothing fits)."""
    text = f'{frame} {motion}'
    if _ARROW.search(text) and n_chars >= 1:   # the arrow is always followed from the archer to the target
        return MOVES['arrow']
    if _GIVEN.search(cam or ''):
        return None
    seed = sum(map(ord, frame)) % 2   # vary between two fitting moves, the same each build
    if _CROWD.search(text):
        return MOVES['top_down'] if seed else MOVES['drone']
    if _PLACE.search(text):
        return MOVES['drone'] if seed or n_chars == 0 else MOVES['side_top']
    if _SKY.search(text):
        return MOVES['low_up'] if seed else MOVES['side_top']
    if n_chars >= 2 and TALK.search(text):
        return MOVES['side_front']
    if _FACE.search(text):
        return MOVES['zoom_in']
    return None


def given_cam(cam):
    """True when the author wrote a specific camera path (drone, crane, tracking, two-shot to …): always keep it."""
    return bool(_GIVEN.search(cam or ''))
