"""Respectful Telugu for the main characters and the sages, in the narration and (by who is speaking) in dialogue.

    రాముడు అన్నాడు      → శ్రీరాములవారు అన్నారు
    సీతమ్మ ఏడ్చింది      → సీతమ్మవారు ఏడ్చారు
    విశ్వామిత్రుడితో    → విశ్వామిత్ర మహర్షితో

The storyteller always speaks with respect. Inside a character's words ("…") the respect follows Telugu custom:
a follower or a younger person speaks of Rama as శ్రీరాములవారు, but his father, mothers and gurus say రాముడు,
Rama says లక్ష్మణుడు of his brother, nobody honours himself, and villains keep their own words. When the speaker
cannot be told, dialogue stays as written. Calls such as రామా! are never changed.

Used by video_build.py (long videos) and Valmiki_Ramayanam/_tools/build.py (Shorts). Source files stay unchanged.
"""
import re

TE = 'ఀ-౿'
W = rf'(?<![{TE}])'            # start of a Telugu word

# key: (nominative, oblique, gender)   oblique + కి/ని/తో/లో… gives the other cases
HONOR = {
    'RAMA': ('శ్రీరాములవారు', 'శ్రీరాములవారి', 'm'),
    'LAKSHMANA': ('లక్ష్మణులవారు', 'లక్ష్మణులవారి', 'm'),
    'BHARATA': ('భరతులవారు', 'భరతులవారి', 'm'),
    'SHATRUGHNA': ('శత్రుఘ్నులవారు', 'శత్రుఘ్నులవారి', 'm'),
    'HANUMAN': ('హనుమంతులవారు', 'హనుమంతులవారి', 'm'),
    'DASHARATHA': ('దశరథ మహారాజుగారు', 'దశరథ మహారాజుగారి', 'm'),
    'JANAKA': ('జనక మహారాజుగారు', 'జనక మహారాజుగారి', 'm'),
    'SITA': ('సీతమ్మవారు', 'సీతమ్మవారి', 'f'),
    'KAUSALYA': ('కౌసల్యాదేవిగారు', 'కౌసల్యాదేవిగారి', 'f'),
    'SUMITRA': ('సుమిత్రాదేవిగారు', 'సుమిత్రాదేవిగారి', 'f'),
}
SAGES = {'VALMIKI': 'వాల్మీకి', 'VISHWAMITRA': 'విశ్వామిత్ర', 'VASISHTHA': 'వశిష్ఠ', 'NARADA': 'నారద',
         'AGASTYA': 'అగస్త్య', 'BHARADWAJA': 'భరద్వాజ', 'GAUTAMA': 'గౌతమ', 'SHARABHANGA': 'శరభంగ',
         'SUTIKSHNA': 'సుతీక్ష్ణ', 'RISHYASHRINGA': 'ఋష్యశృంగ', 'SHATANANDA': 'శతానంద'}
for k, stem in SAGES.items():
    HONOR[k] = (f'{stem} మహర్షి', f'{stem} మహర్షి', 'm')

# -ుడు nouns: the word start before డు/డి/ని (రాము|డు, లక్ష్మణు|డి …)
UDU = {'శ్రీరాము': 'RAMA', 'రాము': 'RAMA', 'శ్రీరామచంద్రు': 'RAMA', 'రామచంద్రు': 'RAMA',
       'లక్ష్మణు': 'LAKSHMANA', 'భరతు': 'BHARATA', 'శత్రుఘ్ను': 'SHATRUGHNA', 'హనుమంతు': 'HANUMAN',
       'ఆంజనేయు': 'HANUMAN', 'దశరథు': 'DASHARATHA', 'జనకు': 'JANAKA', 'విశ్వామిత్రు': 'VISHWAMITRA',
       'వశిష్ఠు': 'VASISHTHA', 'వసిష్ఠు': 'VASISHTHA', 'వశిష్టు': 'VASISHTHA', 'నారదు': 'NARADA',
       'అగస్త్యు': 'AGASTYA', 'భరద్వాజు': 'BHARADWAJA', 'భారద్వాజు': 'BHARADWAJA', 'గౌతము': 'GAUTAMA',
       'శరభంగు': 'SHARABHANGA', 'సుతీక్ష్ణు': 'SUTIKSHNA', 'ఋష్యశృంగు': 'RISHYASHRINGA', 'శతానందు': 'SHATANANDA'}
# names without -ుడు: the bare word is nominative or genitive; suffixes give the cases
BARE = {'సీతమ్మ': 'SITA', 'సీతాదేవి': 'SITA', 'సీత': 'SITA', 'కౌసల్యాదేవి': 'KAUSALYA', 'కౌసల్య': 'KAUSALYA',
        'సుమిత్రాదేవి': 'SUMITRA', 'సుమిత్ర': 'SUMITRA', 'హనుమ': 'HANUMAN', 'వాల్మీకి': 'VALMIKI'}
# already respectful words: only their verbs need to agree
RESPECTFUL_NOM = {'రామచంద్రమూర్తి': 'RAMA', 'మహర్షి': 'SAGE', 'దశరథ మహారాజు': 'DASHARATHA',
                  'జనక మహారాజు': 'JANAKA', 'సీతమ్మ తల్లి': 'SITA'}
BARE_SUFFIX = {'': 'base', 'ే': 'base_e', 'ని': 'acc', 'ను': 'acc', 'నే': 'acc_e', 'కి': 'dat', 'కు': 'dat',
               'కే': 'dat_e', 'తో': 'tho', 'తోనే': 'thone', 'లో': 'lo', 'ది': 'di', 'యొక్క': 'gen'}

VILLAINS = {'రావణ', 'శూర్పణఖ', 'మారీచ', 'ఖర', 'దూషణ', 'త్రిశిర', 'విరాధ', 'కబంధ', 'కుంభకర్ణ', 'ఇంద్రజిత్',
            'మేఘనాద', 'మంథర', 'తాటక', 'సుబాహు', 'అకంపన', 'వాలి', 'ప్రహస్త', 'లంకిణి', 'సింహిక', 'అతికాయ'}
FAMILY_ELDERS = {'DASHARATHA', 'KAUSALYA', 'SUMITRA', 'KAIKEYI', 'JANAKA', 'PARASHURAMA', 'BRAHMA', 'GODS'}
ALL_SAGES = set(SAGES) | {'SAGE'}
# who speaks of a person without honorifics (elders of that person)
ELDERS = {
    'RAMA': FAMILY_ELDERS | ALL_SAGES,
    'SITA': FAMILY_ELDERS | ALL_SAGES | {'RAMA'},
    'BHARATA': FAMILY_ELDERS | ALL_SAGES | {'RAMA', 'SITA'},
    'LAKSHMANA': FAMILY_ELDERS | ALL_SAGES | {'RAMA', 'SITA', 'BHARATA'},
    'SHATRUGHNA': FAMILY_ELDERS | ALL_SAGES | {'RAMA', 'SITA', 'BHARATA', 'LAKSHMANA'},
    'HANUMAN': FAMILY_ELDERS | ALL_SAGES | {'RAMA', 'SITA', 'LAKSHMANA', 'BHARATA', 'SUGRIVA', 'JAMBAVAN'},
    'DASHARATHA': ALL_SAGES | {'BRAHMA', 'GODS', 'KAUSALYA', 'SUMITRA', 'KAIKEYI'},
    'KAUSALYA': ALL_SAGES | {'BRAHMA', 'GODS', 'DASHARATHA'},
    'SUMITRA': ALL_SAGES | {'BRAHMA', 'GODS', 'DASHARATHA'},
    'JANAKA': ALL_SAGES | {'BRAHMA', 'GODS'},
}
for k in SAGES:
    ELDERS[k] = {'BRAHMA', 'GODS'}
SPEAKERS = {   # word starts that name a speaker (nominative) besides the honoured ones
    'కైకేయి': 'KAIKEYI', 'కైకేయ': 'KAIKEYI', 'కైక': 'KAIKEYI', 'సుగ్రీవు': 'SUGRIVA', 'జాంబవంతు': 'JAMBAVAN', 'పరశురాము': 'PARASHURAMA',
    'బ్రహ్మ': 'BRAHMA', 'ఇంద్రు': 'GODS', 'దేవతలు': 'GODS', 'ఋషులు': 'SAGE', 'మహర్షి': 'SAGE', 'మునులు': 'SAGE',
}
OTHER_NAMES = {'జటాయువు', 'వాలి', 'సంపాతి', 'ముని', 'ఋషి', 'బ్రహ్మ', 'విష్ణువు', 'అగ్ని', 'వాయువు', 'కైకేయి', 'కైక',
               'కైకేయ', 'శూర్పణఖ', 'తాటక', 'మంథర', 'శబరి', 'అనసూయ', 'ఊర్మిళ', 'తార', 'స్వయంప్రభ', 'అహల్య', 'త్రిజట', 'మండోదరి'}
STOP_NOM = {'నేను', 'నువ్వు', 'మీరు', 'మేము', 'మనం', 'వాళ్ళు', 'వారు', 'అతను', 'అతడు', 'ఆమె', 'ఆయన', 'వాడు',
            'వీడు', 'ఎవడు', 'రాజు', 'మహారాజు', 'కొడుకు', 'మంత్రి', 'సేనాపతి', 'బ్రహ్మగారు', 'అందరూ', 'ఇద్దరూ'}
NOT_VERB = {'వాడు', 'వీడు', 'ఎవడు', 'అప్పుడు', 'ఇప్పుడు', 'ఎప్పుడు', 'పిల్లవాడు', 'కుర్రవాడు', 'పాడు', 'మగాడు', 'మొగుడు', 'నాడు', 'ఆనాడు', 'ఈనాడు', 'ఏనాడు', 'మంది'}
GEN_CUE = {'మనసు', 'మనస్సు', 'ముఖం', 'ముఖము', 'కళ్ళు', 'కళ్ళ', 'కన్నులు', 'మాట', 'మాటలు', 'జాడ', 'చేయి', 'చెయ్యి',
           'పాదాలు', 'పాదములు', 'ఒడి', 'ఆభరణాలు', 'చీర', 'జడ', 'దుఃఖం', 'కోపం', 'ఆనందం', 'బాధ', 'అందం', 'రూపం',
           'గొంతు', 'హృదయం', 'ప్రాణం', 'ఆలోచన', 'వంక', 'దగ్గర', 'దగ్గరికి', 'దగ్గరకు', 'పక్కన', 'కోసం', 'మీద', 'వైపు',
           'ముందు', 'వెనుక', 'గురించి', 'చుట్టూ', 'ఎదుట', 'లాగా', 'జాడని', 'క్షేమం', 'సౌందర్యం', 'తండ్రి', 'తల్లి',
           'కొడుకు', 'భర్త', 'భార్య', 'అన్న', 'తమ్ముడు', 'వీపు', 'భుజం', 'శరీరం', 'ఉంగరం', 'చూడామణి', 'ఆశ్రమం', 'పర్ణశాల',
           'ఒళ్ళు', 'గుండె', 'కన్నీళ్ళు', 'మెడ', 'తల', 'నుదురు', 'పెదవులు', 'వెంట', 'సన్నిధి', 'ఆజ్ఞ', 'కాళ్ళు', 'పాదాల',
           'చేతి', 'ఆశ్రమము', 'సభ', 'మందిరం', 'ఇల్లు', 'ఇంటి', 'రాజ్యం', 'వంశం', 'కుమారుడు', 'కుమార్తె', 'కోడలు', 'పెద్ద',
           'పేరు', 'నామం', 'ధనుస్సు', 'బాణం', 'బాణాలు', 'కోదండం', 'పాదుకలు', 'రథం', 'సేవ', 'దర్శనం', 'కథ', 'రూపు', 'శిష్యులు'}
GEN_CUE |= {'కంట', 'కంటికి', 'కంటి', 'కంటిముందు', 'దృష్టి', 'చెవిన', 'చెవికి'}
GEN_END = ('లో', 'లోని', 'లోకి', 'లోనే', 'లోంచి')
# Bala Kanda's Bharadwaja is Valmiki's young disciple, not the sage of Prayaga (set by the builders per kaanda)
DISCIPLE_BHARADWAJA = False


def _pref_re(prefixes):
    return '|'.join(sorted(map(re.escape, prefixes), key=len, reverse=True))


UDU_RE = re.compile(W + rf'({_pref_re(UDU)})(డు|డి|ని|ణ్ణి|డ)([{TE}]*)')
BARE_RE = re.compile(W + rf'({_pref_re(BARE)})((?:{"|".join(sorted((s for s in BARE_SUFFIX if s), key=len, reverse=True))})?)(?![{TE}])')
RESP_RE = re.compile(W + rf'({_pref_re(RESPECTFUL_NOM)})(?![{TE}])')
WORD = re.compile(rf'[{TE}]+')
MASC_V = re.compile(rf'(ాడ|ేడ|లడ)(ు|ని|నీ|ంటే|ట|ో|ేమో)$')
# feminine verbs (ది = ద + ి, so "…దని", "…దట", "…దో" end in ద + another vowel sign)
_SUF = {'ి': '', 'ని': 'ని', 'ట': 'ట', 'ో': 'ో'}


def _fem(stem_new):
    return lambda m: stem_new + ('ు' if not _SUF[m.group(1)] else _SUF[m.group(1)])


FEM_V = [(re.compile(r'అంద(ి|ని|ట|ో)$'), _fem('అన్నార')),
         (re.compile(r'(?<=[ఏఎ])మంద(ి|ని|ట|ో)$'), _fem('మన్నార')),
         (re.compile(r'ఉంద(ి|ని|ట|ో)$'), _fem('ఉన్నార')),
         (re.compile(r'కూర్చుంద(ి|ని|ట|ో)$'), _fem('కూర్చున్నార')),
         (re.compile(r'కుంద(ి|ని|ట|ో)$'), _fem('కున్నార')),
         (re.compile(r'([తట])ుంద(ి|ని|ట|ో)$'), lambda m: m.group(1) + 'ార' + ('ు' if not _SUF[m.group(2)] else _SUF[m.group(2)])),
         (re.compile(r'ంటిద(ి|ో)$'), lambda m: 'ంటివారు' if m.group(1) == 'ి' else 'ంటివారో'),
         (re.compile(r'ింద(ి|ని|ట|ో)$'), _fem('ార'))]


def _udu_form(key, case, rest):
    """The respectful word for an -ుడు form; returns (text, is_nominative)."""
    nom, obl, _ = HONOR[key]
    if case == 'డు':
        if rest in ('', 'ే', 'ూ'):
            return nom + rest, True
        return None, False
    if case == 'డ':   # రాముడంటే, రాముడని, రాముడైన, రాముడన్నాడు
        if rest == 'న్నాడు':
            return nom + ' అన్నారు', False
        if rest.startswith(('ంటే', 'ని', 'ైన', 'ైతే', 'ే')):
            base = nom[:-1] if nom.endswith('ు') else nom
            return base + {'ంటే': 'ంటే', 'ని': 'ని', 'ైన': 'ైన', 'ైతే': 'ైతే', 'ే': 'ే'}[next(
                p for p in ('ంటే', 'ని', 'ైన', 'ైతే', 'ే') if rest.startswith(p))] + rest[len(next(
                    p for p in ('ంటే', 'ని', 'ైన', 'ైతే', 'ే') if rest.startswith(p))):], False
        return None, False
    if case == 'ణ్ణి':
        return obl + 'ని' + rest, False
    return obl + rest, False      # డి/ని + కి, ని, తో, లో, ది, నే … (or the genitive alone)


def _bare_form(key, word, suf):
    nom, obl, _ = HONOR[key]
    kind = BARE_SUFFIX[suf]
    if kind in ('base', 'base_e'):
        return None                 # decided by context (nominative or genitive)
    return {'acc': obl + 'ని', 'acc_e': obl + 'నే', 'dat': obl + 'కి', 'dat_e': obl + 'కే', 'tho': obl + 'తో',
            'thone': obl + 'తోనే', 'lo': obl + 'లో', 'di': obl + 'ది', 'gen': obl + ' యొక్క'}[kind]


def _agree(words, gender):
    """Index and new form of the verb that agrees with a respectful subject, scanning words that follow it."""
    for i, w in enumerate(words):
        if w in STOP_NOM or w in OTHER_NAMES or (w.endswith('ుడు') and w not in NOT_VERB) or w.endswith(('వారు', 'గారు')):
            return None
        if w.endswith('వాడు'):
            continue
        if w.endswith(('ారు', 'ారని', 'ారట', 'ారో')):
            return i, w             # already respectful
        if gender in ('m', 's') and w not in NOT_VERB:
            m = MASC_V.search(w)
            if m:
                return i, w[:m.start()] + {'ాడ': 'ార', 'ేడ': 'ేర', 'లడ': 'లర'}[m.group(1)] + m.group(2)
        if gender in ('f', 's'):
            for rx, fn in FEM_V:
                m = rx.search(w)
                if m:
                    return i, w[:m.start()] + fn(m)
    return None


def _is_nom(after, gender, before_quote=False):
    """A bare name is the subject when its own verb follows in the clause; a following body word, place word or
    a word in -లో makes it the owner (సీతమ్మ చేతిలో, మతంగ మహర్షి ఆశ్రమం)."""
    words = WORD.findall(re.split(r'[.?!,]', after, 1)[0])
    if not words:
        return True                 # the name ends the clause ("…భార్య సీత.") or a speech follows ("సీతమ్మ "…")
    if words[0] in ('నా', 'నేను', 'నీ', 'నువ్వు', 'మా', 'మేము', 'మీరు', 'మీ', 'నాయన', 'నాయనా', 'అయ్యా', 'అమ్మా',
                    'తల్లీ', 'రామా', 'లక్ష్మణా', 'సీతా', 'హనుమా', 'ఓ'):
        return True                 # a speech starts: "సీతమ్మ నా పేరు సీత …" – she is the one speaking
    hit = _agree(words, gender)
    if not hit:
        # verb forms that need no change ("ఏదీ అడగలేదు", "నాకు కనపడకపోతే") still make the name the subject,
        # unless an owned thing comes first ("సీతమ్మ జాడ దొరకలేదు")
        if words[0] in GEN_CUE or words[0].endswith(GEN_END):
            return False
        if words[0] in ('నాకు', 'నీకు', 'మాకు', 'మనకు', 'మీకు', 'తనకు', 'అతనికి', 'ఆయనకు', 'వాళ్ళకి', 'వారికి',
                        'ఏదీ', 'ఏమీ', 'ఎవరినీ', 'ఎప్పుడూ', 'కూడా', 'మాత్రం', 'ఇలా', 'అలా', 'అప్పుడు', 'వెంటనే', 'మళ్ళీ'):
            return True
        return any(w.endswith(('లేదు', 'లేదని', 'లేదట', 'కపోతే', 'కుండా')) for w in words[:6])
    if words[0] in GEN_CUE or words[0].endswith(GEN_END):
        # "కన్నీళ్ళు పెట్టుకున్నాడు", "మనసులో అనుకుంది": a reflexive verb (…కు…) keeps the name as the subject
        return bool(re.search(r'కు(న్న|ంది|ంటు|ని)', hit[1]))
    return True


def _speaker_of(text):
    """The first nominative name in a clause: who is about to speak."""
    for w in WORD.findall(text):
        for pre, key in list(UDU.items()):
            if w == pre + 'డు':
                return key
        for pre, key in SPEAKERS.items():
            if w.startswith(pre) and (w == pre or w.startswith(pre + 'డు') or w.startswith(pre + 'ుడు')):
                return key
        if w in BARE and BARE[w] != 'VALMIKI':
            return BARE[w]
        if w == 'వాల్మీకి':
            return 'VALMIKI'
        for v in VILLAINS:
            if w.startswith(v):
                return 'VILLAIN'
    return None


def _allowed(target, speaker):
    if speaker is None:            # the storyteller
        return True
    if speaker in ('UNKNOWN', 'VILLAIN') or speaker == target:
        return False
    if target in ('SAGE',) or target in SAGES:
        return speaker not in ELDERS.get(target, set())
    return speaker not in ELDERS.get(target, set())


def honor_clause(text, speaker=None, before_quote=False):
    """One stretch of text spoken by one voice (None = storyteller)."""
    out = []
    pos = 0
    pending = []      # (index in out, gender) of respectful subjects whose verb must agree
    # collect replacements in order of position
    spans = []
    for m in UDU_RE.finditer(text):
        key = UDU[m.group(1)]
        if not _allowed(key, speaker):
            continue
        if re.match(r'\s+(అనే|అని పేరు)', text[m.end():]):
            continue            # the name as a name: "రాముడు అనే పేరుతో"
        if key == 'BHARADWAJA' and (DISCIPLE_BHARADWAJA or 'శిష్య' in text[max(0, m.start() - 30):m.end() + 30]):
            continue            # the disciple, not the sage
        new, nom = _udu_form(key, m.group(2), m.group(3))
        if new:
            spans.append((m.start(), m.end(), new, HONOR[key][2] if nom else None))
    for m in BARE_RE.finditer(text):
        key, word, suf = BARE[m.group(1)], m.group(1), m.group(2)
        if not _allowed(key, speaker) or any(a <= m.start() < b for a, b, _, _ in spans):
            continue
        nxt = text[m.end():m.end() + 12]
        if re.match(r'\s+(అనే|అని పేరు)', nxt):
            continue
        if not suf and (nxt.lstrip().startswith('!') or re.search(r'(నాయన|నాయనా|అయ్యా|ఓ|ఓయీ)\s*$', text[:m.start()])):
            continue                # a call: "నాయన హనుమ!"
        if key == 'VALMIKI':
            if suf or nxt.startswith((' మహర్షి', ' రామాయణ', ' మహాముని')):
                continue
            new = 'వాల్మీకి మహర్షి'
            spans.append((m.start(), m.end(), new, 'm' if _is_nom(text[m.end():], 'm', before_quote) else None))
            continue
        if key == 'SITA' and nxt.startswith(' తల్లి'):
            continue
        form = _bare_form(key, word, suf)
        if form:
            spans.append((m.start(), m.end(), form, None))
            continue
        # nominative or genitive: nominative when her/his own verb follows in this clause
        if re.search(r'పేరు\s*$', text[:m.start()]):
            continue                # "నా పేరు సీత"
        nom, obl, g = HONOR[key]
        is_nom = _is_nom(text[m.end():], g, before_quote)
        spans.append((m.start(), m.end(), (nom if is_nom else obl) + ('ే' if suf == 'ే' else ''), g if is_nom else None))
    if speaker is None or _allowed('SAGE', speaker):
        for m in RESP_RE.finditer(text):
            if any(a <= m.start() < b for a, b, _, _ in spans):
                continue
            key = RESPECTFUL_NOM[m.group(1)]
            g = 'm' if key == 'SAGE' else HONOR[key][2]
            phrase = m.group(1)
            nom = _is_nom(text[m.end():], g, before_quote)
            if key in ('DASHARATHA', 'JANAKA'):
                if text[m.end():m.end() + 3].startswith((' గా', 'గా')):
                    continue
                spans.append((m.start(), m.end(), HONOR[key][0] if nom else HONOR[key][1], g if nom else None))
            elif nom:
                spans.append((m.start(), m.end(), phrase, g))
    spans.sort()
    res, last, marks = [], 0, []
    for a, b, new, g in spans:
        if a < last:
            continue
        res.append(text[last:a])
        start = sum(len(x) for x in res)
        res.append(new)
        key_g = g or next((v[2] for v in HONOR.values() if new.startswith(v[1]) or new.startswith(v[0])), None)
        marks.append((start, start + len(new), g, key_g))
        last = b
    res.append(text[last:])
    return ''.join(res), marks


def _other_nom(w):
    return (w in STOP_NOM or w in OTHER_NAMES or (w.endswith('ుడు') and w not in NOT_VERB)
            or w.endswith(('వారు', 'గారు')) or w.startswith('ఎవడ'))


def _fix_verbs(s, marks, topic):
    """Make every finite verb of a respectful subject respectful, following the subject from sentence to sentence
    (Telugu drops the subject after the first sentence) until someone else becomes the subject."""
    out, pos = [], 0
    cur = topic
    ref = topic                     # the last respectful person mentioned in any case (for ఆయన)
    for m in WORD.finditer(s):
        w = m.group(0)
        hit = next((mk for mk in marks if mk[0] <= m.start() < mk[1]), None)
        if hit:
            if hit[2]:
                cur = hit[2]
            ref = hit[3] or ref
            continue
        if w == 'ఆయన' and (cur or ref):
            cur = cur or ref        # "ఆయన" after a respectful person is that person
            continue
        if _other_nom(w):
            cur = None
            ref = None
            continue
        if not cur or w in NOT_VERB:
            continue
        if w.endswith('వాడు'):     # "కన్నులున్నవాడు" said of him becomes వారు; "ఎవడు విసిరినవాడు" stays
            last = max((mk[1] for mk in marks if mk[0] <= m.start() and mk[2]), default=None)
            if last is not None and not re.search(r'[.?!]', s[last:m.start()]) and 'ఎవడ' not in s[:m.start()]:
                out.append(s[pos:m.start()] + w[:-4] + 'వారు')
                pos = m.end()
            continue
        new = None
        if cur in ('m', 's'):
            mm = MASC_V.search(w)
            if mm:
                new = w[:mm.start()] + {'ాడ': 'ార', 'ేడ': 'ేర', 'లడ': 'లర'}[mm.group(1)] + mm.group(2)
        if not new and cur in ('f', 's'):
            for rx, fn in FEM_V:
                mm = rx.search(w)
                if mm:
                    new = w[:mm.start()] + fn(mm)
                    break
        if new:
            out.append(s[pos:m.start()] + new)
            pos = m.end()
    out.append(s[pos:])
    return ''.join(out), cur


def honor_text(text, speaker=None, topic=None, before_quote=False):
    """Respectful names and verbs for one voice; returns the new text and the subject carried to the next line."""
    s, marks = honor_clause(text, speaker, before_quote)
    return _fix_verbs(s, marks, topic)


class Honorer:
    """Carries who is speaking across lines (a speech can open in one scene line and close several lines later)."""

    def __init__(self, quotes=True):
        self.quotes = quotes
        self.in_quote = False
        self.speaker = None
        self.tail = ''
        self.topic = None      # whose verbs follow when the storyteller drops the subject
        self.qtopic = None

    def reset(self):
        """A new hook, bridge or recap line: the dropped subject does not carry over."""
        self.topic = None

    def __call__(self, text):
        if not self.quotes:
            new, self.topic = honor_text(text, None, self.topic)
            return new
        parts = re.split(r'(")', text)
        out, before = [], self.tail
        for k, p in enumerate(parts):
            if p == '"':
                if not self.in_quote:     # a speech opens: its speaker is the first name in the clause before it
                    clause = re.split(r'[.?!]', before)[-1]
                    self.speaker = _speaker_of(clause) or 'UNKNOWN'
                else:
                    self.speaker = None
                self.qtopic = None
                self.in_quote = not self.in_quote
                out.append(p)
                continue
            if self.in_quote and self.speaker == 'UNKNOWN':
                # the speaker may be named right after the speech closes ("…" అని రాముడు అన్నాడు)
                after = text.split('"', text.count('"'))[-1] if text.count('"') % 2 == 0 else ''
                m = re.match(r'\s*(?:అని|అంటూ)\s+(.{0,40})', after)
                if m:
                    self.speaker = _speaker_of(m.group(1)) or 'UNKNOWN'
            if self.in_quote:
                new, self.qtopic = honor_text(p, self.speaker, self.qtopic)
            else:
                opens = k + 1 < len(parts) and parts[k + 1] == '"'
                new, self.topic = honor_text(p, None, self.topic, opens)
            out.append(new)
            before += p
        self.tail = (self.tail + text)[-300:]
        return ''.join(out)
