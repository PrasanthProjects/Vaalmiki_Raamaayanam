"""Visual rules for the long-form episodes: photorealistic, per 00_STYLE_GUIDE.md,
with every character's look taken from 00_CHARACTER_BIBLE.md (its Visual Lock and
age stages). The bible is read at build time, so editing it updates every prompt.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STYLE = ("photorealistic live-action historical film, as in a big-budget Indian epic: cinematic lighting, "
         "natural skin texture and cloth movement, real woven fabric and real built sets, shot on a real camera "
         "lens (35mm/50mm equivalent) with naturalistic depth of field. Treta Yuga in a South Indian visual "
         "register: early Dravidian temple-era architecture and dress (veshti and angavastram for men, single-wrap "
         "drape for women, early Dravidian jewellery), never Mughal or North-Indian motifs. Forest and ashram "
         "settings are lush, green and serene with flowering trees, clear rivers, deer, peacocks and birds unless "
         "the scene says otherwise. Not flat illustration, anime, cartoon, painted storybook or glossy plastic 3D")

RESPECT = ("This is a sacred Hindu devotional scene from the Ramayana: depict every deity and character with deep "
           "reverence and faithful traditional Indian iconography. Everyone is fully and modestly dressed in "
           "traditional attire (women's drapes covering the shoulders and body); no revealing, Western, "
           "fantasy-armour or modern clothing; no sexualised or suggestive poses; no blood, wounds, gore or graphic "
           "violence (show impact through light, dust and reaction); no horror look; no comedy or caricature; no "
           "distorted or disrespectful depiction of gods; no modern objects, buildings, vehicles or technology.")

TAIL = ("No text, letters, subtitles, logos or watermarks anywhere in the frame. "
        "Audio: soft ambient atmosphere only, no speech, no singing, no music.")

VN = "white Vishnu namam (U-shaped white mark with a red centre line) on the forehead"
SN = "three horizontal ash-white Shiva lines with a red dot on the forehead (mark of allegiance to Ravana)"
KUM = "red kumkum bindi on the forehead and sindoor in the hair parting"
BOTTU = "small red kumkum dot between the eyebrows"

VANARA = ("heroic, muscular, human-proportioned warrior with an expressive monkey face, fur on the face, head, "
          "lower forearms and lower legs, bare golden-tan to reddish skin on the chest and limbs, a visible tail, "
          "standing upright like a person, never a literal ape; warrior dhoti and gold ornaments")

# Spellings used in the scene prompts -> bible key
ALIASES = {
    'Jambavan': 'JAMBAVANTHA', 'Jambavantha': 'JAMBAVANTHA', 'Sugreeva': 'SUGRIVA', 'Vasishtha': 'VASHISHTHA',
    'Viswamitra': 'VISHWAMITRA', 'Seeta': 'SITA', 'Lakshman': 'LAKSHMANA', 'Meghanada': 'INDRAJIT',
    'Shurpanakha': 'SHURPANAKHA', 'Dushana': 'KHARA', 'Trishira': 'KHARA', 'Nila': 'NALA', 'Anjana': None,
}

WOMEN = {'SITA', 'KAUSALYA', 'KAIKEYI', 'SUMITRA', 'MANTHARA', 'URMILA', 'SHABARI', 'TARA', 'MANDODARI',
         'AHALYA', 'TRIJATA', 'SHURPANAKHA', 'TATAKA', 'AYOMUKHI', 'SURASA', 'SIMHIKA', 'HARIJATA'}
RAVANA_SIDE = {'RAVANA', 'KUMBHAKARNA', 'INDRAJIT', 'KHARA', 'MARICHA', 'AKSHAKUMARA', 'JAMBUMALI', 'KUMBHA',
               'SUKA', 'VIRADHA'}
NO_MARK = {'BRAHMA', 'VISHNU', 'INDRA', 'JATAYU', 'KABANDHA', 'SURASA', 'SIMHIKA', 'SHURPANAKHA', 'TATAKA',
           'AYOMUKHI'}

# Age stages by episode (first episode of each stage). Episodes before the first entry use the first stage.
STAGES = {
    'RAMA': [('E0.00', 'S2'), ('E1.05', 'S1'), ('E1.23', 'S2'), ('E2.18', 'S3'), ('E3.15', 'S4'), ('E6.39', 'S5')],
    'SITA': [('E0.00', 'S1'), ('E2.01', 'S2'), ('E2.18', 'S3'), ('E3.15', 'S4'), ('E6.35', 'S5')],
    'LAKSHMANA': [('E0.00', 'S2'), ('E1.05', 'S1'), ('E1.23', 'S2'), ('E2.18', 'S3'), ('E3.15', 'S4'), ('E6.39', 'S5')],
}


def ep_key(ep):
    k, n = ep[1:].split('.')
    return (int(k), int(n))


def parse_bible():
    """Return {KEY: {'lock': text, 'stages': {S1: look}}} from 00_CHARACTER_BIBLE.md."""
    text = open(os.path.join(ROOT, '00_CHARACTER_BIBLE.md'), encoding='utf-8').read()
    out = {}
    for block in re.split(r'^### ', text, flags=re.M)[1:]:
        head, body = block.split('\n', 1)
        if '—' not in head:
            continue
        eng = head.split('—', 1)[1].strip()
        m = re.search(r'\*\*Visual Lock[^*]*:\*\*\s*(.+)', body)
        if not m:
            continue
        lock = m.group(1).strip()
        stages = {s: look.strip() for s, look in
                  re.findall(r'^\|\s*(S\d)[^|]*\|[^|]*\|[^|]*\|([^|]+)\|', body, flags=re.M)}
        change = re.search(r'\*\*Change point — ([^(*]+)[^*]*\*\*\s*(.+)', body)
        for name in re.split(r',\s*', re.sub(r'\(.*?\)', '', eng)):
            words = [w for w in name.split() if w.isalpha() and w.isupper() and w not in ('SAGE', 'KING', 'QUEEN')]
            if words:
                out[words[0]] = {'lock': lock, 'stages': stages}
        if change and 'Agnisharma' in change.group(1):
            out['AGNISHARMA'] = {'lock': change.group(2).strip(), 'stages': {}}
    return out


BIBLE = parse_bible()


META = ('pick ONE', 'never mix', 'can simplify', 'stay consistent', 'Switch permanently', 'scheme as Rama',
        'from S1 onward', 'Production Bible', 'first appearance', 'note which', 'deliberate distinguishing',
        'Single continuous appearance', 'Progressive visual aging', 'No aging across', 'identical lock',
        'change point', 'following the source')


def clean_lock(lock):
    lock = re.sub(r'\*\*Convention locked[^*]*:\*\*', '', lock)
    lock = re.sub(r'\([^)]*(?:deliberate|see |Reference|Stage|E\d\.\d)[^)]*\)', '', lock)
    lock = ' '.join(x for x in re.split(r'(?<=[.;])\s+', lock) if not any(m in x for m in META))
    lock = lock.replace('Per the VANARA DESIGN BASELINE above — ', '').replace('Per the VANARA DESIGN BASELINE above', '')
    lock = re.sub(r'\s*\(Reference spec only[^)]*\)', '', lock)
    lock = re.sub(r'\*\*Convention locked[^*]*\*\*', '', lock)
    return re.sub(r'\s+', ' ', lock.replace('**', '')).strip()


def mark_for(key):
    if key in NO_MARK:
        return ''
    if key in WOMEN:
        return KUM
    if key in RAVANA_SIDE:
        return SN
    return VN


def stage_of(key, ep):
    for start, stage in reversed(STAGES.get(key, [])):
        if ep_key(ep) >= ep_key(start):
            return stage
    return STAGES[key][0][1] if key in STAGES else None


def character(key, ep):
    """Full look for one character in one episode, or None if the bible has no entry."""
    entry = BIBLE.get(key)
    if not entry:
        return None
    lock = clean_lock(entry['lock'])
    stage = stage_of('RAMA' if key == 'LAKSHMANA' else key, ep) if key in STAGES else None
    if stage:
        look = BIBLE.get('RAMA' if key == 'LAKSHMANA' else key, {}).get('stages', {}).get(stage)
        if look:
            lock = lock.rstrip(' .;') + f'. In this episode: {look.strip().rstrip(".")}.'
    if key in ('HANUMAN', 'SUGRIVA', 'VALI', 'TARA', 'ANGADA', 'NALA', 'NILA') and 'human-proportioned' not in lock:
        lock = f'{VANARA}; {lock}'
    mark = mark_for(key)
    name = key.title()
    return f"{name}: {lock.rstrip(' .;')}" + (f"; {mark}" if mark else '')


NAMES = None


def names_in(text):
    """Bible keys mentioned in a scene prompt, in order of first mention."""
    global NAMES
    if NAMES is None:
        NAMES = {k.title(): k for k in BIBLE}
        NAMES.update({a: k for a, k in ALIASES.items() if k})
    found = []
    for m in re.finditer(r"\b([A-Z][a-z]+)\b", text):
        k = NAMES.get(m.group(1))
        if k and k not in found:
            found.append(k)
    return found
