"""Narration text for AI voice (ElevenLabs): only words and the punctuation a voice should act on.

- no delivery cues, ⏸ marks or episode markers (a voice model would read them aloud)
- one paragraph per spoken part; a sentence that runs across scenes stays in one paragraph,
  so the voice never stops at a comma as if the sentence had ended
- digits become Telugu words ("24,000 శ్లోకాలు" -> "ఇరవై నాలుగు వేల శ్లోకాలు"); a comma inside a number is a pause
- quotes, brackets, '=', ';' and joining hyphens go; '(gloss)' becomes ', gloss,'
- every paragraph ends on . ? or !, and the text is cut into pieces under LIMIT characters at paragraph ends
"""
import re

LIMIT = 2400

# Delivery per tone: (Eleven v3 audio tag at the start of the paragraph, cue for reading it yourself).
# No "excited" anywhere: on hooks it makes the voice jump in pitch and laugh, which sounds wrong in a sacred story.
TONES = {
    'serious': ('[serious]', 'గంభీరంగా, నెమ్మదిగా – ఉత్సాహం, నవ్వు వద్దు'),
    'sad': ('[sad]', 'బాధగా, మృదువుగా, నెమ్మదిగా'),
    'awe': ('[in awe]', 'భక్తితో, ఆశ్చర్యంగా, మృదువైన స్వరంతో'),
    'tense': ('[tense]', 'ఉత్కంఠగా, తక్కువ స్వరంలో – అరవకుండా'),
    'curious': ('[curious]', 'ఆసక్తిగా, ప్రశ్న మీద స్వరం కొంచెం పైకి'),
    'warm': ('[warm]', 'ఆత్మీయంగా, చిరునవ్వుతో, సహజంగా'),
    'calm': ('[calm]', 'ప్రశాంతంగా, కథ చెబుతున్నట్లు'),
}
STORY = 'calm'    # the book's narration between the new parts

ONES = ['', 'ఒకటి', 'రెండు', 'మూడు', 'నాలుగు', 'ఐదు', 'ఆరు', 'ఏడు', 'ఎనిమిది', 'తొమ్మిది']
TEENS = ['పది', 'పదకొండు', 'పన్నెండు', 'పదమూడు', 'పద్నాలుగు', 'పదిహేను', 'పదహారు', 'పదిహేడు', 'పద్దెనిమిది', 'పందొమ్మిది']
TENS = ['', '', 'ఇరవై', 'ముప్పై', 'నలభై', 'యాభై', 'అరవై', 'డెబ్బై', 'ఎనభై', 'తొంభై']
ORD = {1: 'మొదటి', 2: 'రెండవ', 3: 'మూడవ', 4: 'నాలుగవ', 5: 'ఐదవ', 6: 'ఆరవ', 7: 'ఏడవ', 8: 'ఎనిమిదవ', 9: 'తొమ్మిదవ', 10: 'పదవ'}


def _small(n, attr):
    if n < 10:
        return 'ఒక' if attr and n == 1 else ONES[n]
    if n < 20:
        return TEENS[n - 10]
    t, u = divmod(n, 10)
    return TENS[t] + ('' if not u else ' ' + ('ఒక్క' if attr and u == 1 else ONES[u]))


def words(n, attr=False):
    """Telugu number words; attr=True is the form before a noun (మూడు వందల ఏళ్ళు, ఒక్క)."""
    assert 0 < n < 100000, n
    out = []
    th, rest = divmod(n, 1000)
    if th:
        out.append('వెయ్యి' if th == 1 else _small(th, False) + (' వేల' if rest or attr else ' వేలు'))
    h, rest = divmod(rest, 100)
    if h:
        if h == 1:
            out.append('నూట' if rest else 'వంద')
        else:
            out.append(ONES[h] + (' వందల' if rest or attr else ' వందలు'))
    if rest:
        out.append(_small(rest, attr))
    return ' '.join(out)


def _number(m):
    n = int(m.group(1).replace(',', ''))
    if m.group(2):                                     # 6వ రోజున -> ఆరవ రోజున
        return ORD[n]
    attr = bool(re.match(r' ?[\u0c00-\u0c7f]', m.string[m.end():]))
    return words(n, attr)


def clean(text):
    t = text
    t = re.sub(r'(\d{1,3}(?:,\d{3})+) వేల', r'\1', t)          # "30,000 వేల" says thousand twice
    t = t.replace('300 కి పైగా', 'మూడు వందలకు పైగా')
    t = re.sub(r'(\d{1,3}(?:,\d{3})+|\d+)(వ(?![\u0c00-\u0c7f]))?', _number, t)
    t = re.sub(r'["\'“”‘’\[\]]', '', t)
    t = t.replace('=', ' ').replace(';', ',').replace('–', '—')
    t = re.sub(r'(?<=[\u0c00-\u0c7f])-(?=[\u0c00-\u0c7f])', ' ', t)
    t = re.sub(r'\s*\(\s*', ', ', t)
    t = re.sub(r'\s*\)\s*', ', ', t)
    t = re.sub(r'\s+([,.?!])', r'\1', t)
    for _ in range(3):
        t = re.sub(r',\s*([,.?!—])', r'\1', t)              # ", ." -> "."   ", —" -> "—"
        t = re.sub(r'([.?!])\s*,', r'\1', t)
        t = re.sub(r'—\s*,', '—', t)                        # "— (gloss" -> "— gloss"
        t = re.sub(r'—\s*([.?!])', r'\1', t)
    t = re.sub(r'\s*—\s*', ' — ', t)
    t = re.sub(r'([,.?!])(?=[^\s,.?!])', r'\1 ', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return re.sub(r'^[—,\s]+', '', t)


def _close(p):
    p = p.rstrip(' ,—')
    return p if p.endswith(('.', '?', '!')) else p + '.'


def chant(verse):
    """A kept sloka as its own piece: one half-line per line, each closed with '.' so the voice pauses there."""
    halves = [h.strip(' "\'') for h in re.split(r'[।॥]+', verse) if h.strip(' "\'')]
    return '\n'.join(re.sub(r'\s+', ' ', h) + '.' for h in halves)


# Audio tags only work on Eleven v3; Multilingual v2 / v1 read "[serious]" aloud. Off until v3 is available.
TAGS = False


def paragraphs(spoken, tags=None):
    """spoken: the video's items in order -> [(kind, text)]. New parts (hook, bridge, recap, lesson, teaser, subscribe)
    are their own paragraph; with tags on (Eleven v3) each opens with the audio tag of its tone and the story
    paragraph after one goes back to the calm storytelling tag. Scene lines join until a sentence ends;
    a kept sloka is kind 'verse'."""
    tags = TAGS if tags is None else tags
    res, last = [], None
    for kind, text, tone in _paragraphs(spoken):
        if kind == 'verse':
            res.append((kind, text))
            last = None
            continue
        if tone and tone not in ('warm', 'curious'):
            text = text.replace('!', '.')       # in a hook, an exclamation pushes the voice into excitement
        tone = tone or STORY
        res.append((kind, f'{TONES[tone][0]} {text}' if tags and tone != last else text))
        last = tone
    return res


def _paragraphs(spoken):
    out, cur = [], ''
    for x in spoken:
        if x.get('scene', {}).get('verse'):
            if cur:
                out.append(('text', _close(cur), None))
                cur = ''
            if out and out[-1][0] == 'verse':          # a sloka that runs over two scenes stays one piece
                out[-1] = ('verse', out[-1][1] + '\n' + chant(x['narration']), None)
            else:
                out.append(('verse', chant(x['narration']), None))
            continue
        t = clean(x['narration'])
        if not t:
            continue
        if x['new']:
            if cur:
                out.append(('text', _close(cur), None))
                cur = ''
            out.append(('text', _close(t), x.get('tone')))
            continue
        cur = f'{cur} {t}'.strip()
        if cur.endswith(('.', '?', '!')):
            out.append(('text', cur, None))
            cur = ''
    if cur:
        out.append(('text', _close(cur), None))
    return out


def pieces(paras, limit=LIMIT):
    """[(kind, text)] -> [(kind, piece)]: narration packed under `limit` characters; every sloka a piece of its own
    (generate it separately, or record it in your own voice, and place it where it stands)."""
    out, cur = [], []
    for kind, p in paras:
        if kind == 'verse' or (cur and len('\n\n'.join(cur + [p])) > limit):
            if cur:
                out.append(('text', '\n\n'.join(cur)))
            cur = []
        if kind == 'verse':
            out.append(('verse', p))
        else:
            cur.append(p)
    if cur:
        out.append(('text', '\n\n'.join(cur)))
    if not TAGS:
        return out
    tag = TONES[STORY][0]                          # each piece is generated alone: never start one untagged
    return [(k, p if k == 'verse' or p.startswith('[') else f'{tag} {p}') for k, p in out]
