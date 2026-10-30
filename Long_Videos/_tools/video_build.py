"""Re-cut the long episodes into YouTube videos of a set length (10–12 minutes, or the data file's LENGTH line),
narrated without the slokas.

usage:  python video_build.py data/0_1_Parichayam_Baala.txt

Reads the same scene tables and data files as long_build.py (episode files are only read, never written) and writes
Long_Videos/Videos/:
  - <kaanda>/V01_E0.01-E1.02.md …   one complete kit per video: recording script, clips, thumbnail, upload text
  - <kaanda>/00_INDEX.md            which episodes went into which video, and the lengths
  - captions/<kaanda>/V01.srt
  - <kaanda>_VIDEOS_HELPER.html     the phone/computer helper page (and its claude.ai copy in _tools/publish/)

What changes from the episode kits:
  - every sloka scene is dropped; the few lines that pointed at a sloka are reworded (data/*_videos.txt)
  - consecutive episodes are joined until a video runs 10–12 minutes ('LENGTH | 8 10' in data/*_videos.txt: 8–10)
  - inside a video, only the first episode keeps its "గత భాగంలో…" recap and only the last keeps its teaser;
    each later episode opens with its own hook as a re-hook, so the join feels like a new peak, not a restart
  - one life lesson (the last episode's) and one subscribe line, at the end
"""
import glob
import json
import math
import os
import re
import sys

import long_build as L
import long_style as S
from long_style import PLACES, place_for, STYLE
import tts
import honor

QUOTE_WRAPPED = False
from long_build import BUMPER, OUTRO, KAANDAS, HASHTAGS, mmss

VIDEOS = os.path.join(L.LONG, 'Videos')
L.CUES['R'] = '[ఇంతవరకు · సహజంగా, కొంచెం వేగంగా – కొత్త వీక్షకుడికి కథ గుర్తుచేస్తున్నట్లు]'
L.CUES['T'] = '[తరువాతి వీడియో టీజర్ · నెమ్మదిగా, ఉత్కంఠగా, ప్రశ్న మీద ఆగండి]'
TARGET, LOW, HIGH = 11 * 60, 10 * 60, 12 * 60
MINUTES = '10–12'   # the length range in page titles (data LENGTH line)
SIMPLE = []   # [exact words, plain Telugu, times used] (data/*_videos.txt SIMPLE lines)
PLACES_USED = set()
CLIPS_NOTE = ('ప్రతి క్లిప్‌కు రెండు ప్రాంప్ట్‌లు: ముందు 🖼️ ఇమేజ్ చేయండి (రిఫరెన్స్ ఇమేజ్‌లు జత చేసి). వీడియో కావాలంటే '
              'ఆ ఇమేజ్‌ను Flow → Frames to Video లో మొదటి ఫ్రేమ్‌గా పెట్టి 🎥 వీడియో ప్రాంప్ట్ వాడండి. "యాక్షన్" క్లిప్‌లు కథలో '
              'కదలిక ఉన్నవి; "మెల్లని కదలిక" క్లిప్‌లకు ఇమేజ్ + ఎడిటర్ కదలిక చాలు, కావాలంటే వీడియో కూడా చేయవచ్చు. '
              'వీడియోలో పాత్రలు అకస్మాత్తుగా కదిలితే: మళ్ళీ Generate చేయండి, లేదా ఇమేజ్ + ఎడిటర్ కదలిక వాడండి.')
CARDS = {}   # (episode, scene) -> on-screen meaning under a kept sloka (data/*_videos.txt CARD lines)
CUTS = []        # (episode, chapter scene or None): where each video starts (data/*_videos.txt CUTS line)
PLACE_MAP = {}   # episode -> [(first scene, last scene, PLACES key)] for scripts without a location column
CAST = {}        # (episode, scene) -> character keys on screen, where the prompt only mentions someone (data CAST lines)
VIS = {}         # (episode, scene) -> a corrected picture description (data VIS lines)
LOCS = {}        # (episode, scene) -> a corrected location register (data LOC lines)
LESSON_PIC = {}  # episode -> the scene whose picture goes with its life lesson (data LESSON lines)


def cast(keys, visual, ep, loc=''):
    """Looks and reference images for an explicit cast; 'RAMA:S1' forces an age stage (flashbacks)."""
    looks, refs = [], []
    for key in keys:
        k, _, stage = key.partition(':')
        assert k in S.BIBLE, f'{ep}: CAST names unknown character {k}'
        line = S.STAGES.get(k, [])
        at = next((e for e, st in line if st == stage), None) if stage else ep
        assert at, f'{ep}: {k} has no stage {stage}'
        looks.append(S.character(k, at))
        st = S.stage_of(k, at) if line else None
        refs.append(f'{k}_{st}' if st else k)
    g_looks, g_refs = L.group_looks(visual, loc, ep)
    return looks + g_looks, refs + g_refs


def read_fixes(path):
    """Line fixes per scene, and the opening hook / closing teaser for videos that cut an episode at a chapter."""
    fixes, splits = {}, {}
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            if line.startswith('KEEP '):
                _, ep, no = line.split()
                fixes.setdefault((ep, int(no)), []).append('KEEP')
                continue
            if line.startswith('DROP '):
                _, ep, no = line.split()
                fixes.setdefault((ep, int(no)), []).append(None)
                continue
            head, rest = line.split(' | ', 1)
            if head.startswith(('REHOOK ', 'HOOK ')):   # 'REHOOK E1.11 8 | …': the picture comes from scene 8
                w = head.split()
                splits[(w[1], w[0].lower())] = rest
                if len(w) > 2:
                    splits[(w[1], w[0].lower() + '_from')] = int(w[2])
                continue
            if head == 'CUTS':     # "E0.01, E1.02 22, E1.06, …": the first unit of every video, in order
                for x in rest.split(','):
                    w = x.split()
                    CUTS.append((w[0], int(w[1]) if len(w) > 1 else None))
                continue
            if head == 'LENGTH':     # "8 10": videos of 8–10 minutes, aimed near the short end
                global TARGET, LOW, HIGH, MINUTES
                lo, hi = map(int, rest.split())
                LOW, HIGH, TARGET, MINUTES = lo * 60, hi * 60, lo * 60 + 20, f'{lo}–{hi}'
                continue
            if head == 'SIMPLE':
                old, new = rest.split(' => ', 1)
                SIMPLE.append([old, new, 0])
                continue
            if head.startswith('PLACE '):
                w = head.split()
                assert rest in PLACES, f'unknown place {rest!r}'
                for rng in (w[2] if len(w) > 2 else '0-999').split(','):    # "2-5,7,10-14": insets left out
                    lo, _, hi = rng.partition('-')
                    PLACE_MAP.setdefault(w[1], []).append((int(lo), int(hi or lo), rest))
                continue
            if head.startswith('CARD '):
                _, ep, no = head.split()
                CARDS[(ep, int(no))] = rest
                continue
            if head.startswith('VIS '):    # the script's picture line is a production note or wrong: say what is seen
                _, ep, no = head.split()
                VIS[(ep, int(no))] = rest
                continue
            if head.startswith('SAY '):    # the whole line retold to match Valmiki's verses (the book strays there)
                _, ep, no = head.split()
                fixes.setdefault((ep, int(no)), []).append((None, rest))
                continue
            if head.startswith('LOC '):
                _, ep, no = head.split()
                LOCS[(ep, int(no))] = rest
                continue
            if head.startswith('LESSON '):
                LESSON_PIC[head.split()[1]] = int(rest)
                continue
            if head.startswith('CAST '):   # who is really on screen: "RAMA:S1, MARICHA_YOUNG", or "-" for nobody
                w = head.split()
                for rng in w[2].split(','):
                    lo, _, hi = rng.partition('-')
                    for no in range(int(lo), int(hi or lo) + 1):
                        CAST[(w[1], no)] = [k.strip() for k in rest.split(',') if k.strip() not in ('', '-')]
                continue
            if head.startswith('WELCOME '):
                w = head.split()
                splits[(w[1], int(w[2]) if len(w) > 2 else None, 'welcome')] = rest
                continue
            if head.startswith('TONE '):
                w = head.split()
                assert rest in tts.TONES, f'unknown tone {rest!r}; use one of {", ".join(tts.TONES)}'
                splits[(w[1], int(w[2]), 'tone') if len(w) > 2 else (w[1], 'tone')] = rest
                continue
            if head.startswith('SPLIT '):
                _, ep, n = head.split()
                splits[(ep, int(n))] = dict(x.split(': ', 1) for x in rest.split(' | '))
                continue
            ep, no = head.split()
            old, new = (rest + ' ').split(' => ', 1)    # "old =>" with nothing after it deletes the words
            new = new[:-1]
            fixes.setdefault((ep, int(no)), []).append((old, new))
    return fixes, splits


def open_ended(text):
    """A line that does not finish its sentence: '… ప్రార్థించగా,'  '… ఇలా చెప్పాడు —'  '… ఇలా అన్నాడు.'"""
    t = text.rstrip(' "\'')
    if t.endswith(')') and not t.rstrip(')').endswith((',', '—', '-')):
        return False     # a narrator's aside in brackets closes its sentence: "(… తన జీవితాన్ని వ్యర్థం చేసుకున్నాడు)"
    return not t.endswith(('.', '?', '!')) or bool(re.search(
        r'ఇలా\s*(అని\s*)?(అన్నాడు|అన్నారు|అంది|అన్నది|పలికాడు|పలికారు|పలికింది|చెప్పాడు|చెప్పారు|చెప్పింది)\.$', t))


CLOSE = r'"\s*(అని|అన్నా[డరు]|అంది|అంటూ|అనుకు|—|$)'   # a quote mark that ends someone's words


def opens_speech(text):
    """The line leaves a quote open: '… ఇలా అన్నాడు — "అయ్యా! నాకు సంతానం లేదు.'"""
    return text.count('"') % 2 == 1 and not re.search(CLOSE + r'[^"]*$', text)


def ends_speech(text):
    """The line finishes words someone began on an earlier line: '… చేయించాలి" అని పాదములు పట్టి ప్రార్థించాడు.'"""
    return not text.lstrip().startswith('"') and bool(re.match(r'[^"]*' + CLOSE, text))


def inside_speech(prev, cur, before=(), after=()):
    """True when a break between prev and cur would cut someone's words in half. One line with no quote mark
    on either side (before = lines leading up to prev, after = lines following cur) still counts as the same
    short speech; a long monologue has to carry its bridges inside it, so the search stops there."""
    back = next((t for t in [prev, *before[:1]] if '"' in t), '')
    ahead = next((t for t in [cur, *after[:1]] if '"' in t), '')
    return opens_speech(back) and ends_speech(ahead)


def chapter_starts(d, sc):
    """Chapter -> first kept scene at or after its old start (a chapter that lost its scenes merges into the next).
    A chapter never starts right after a lead-in ("… ఇలా అన్నాడు —") or in the middle of someone's words:
    the bridge would cut the speaker off, so the chapter (and its bridge) moves back to where the words begin."""
    nos = [s['no'] for s in sc]
    text = {s['no']: s['narration'] for s in sc}
    lead_in = {s['no'] for s in sc if open_ended(s['narration'])}
    out = []
    for n, title in d['chapters']:
        at = next((x for x in nos if x >= n), None)
        while at is not None and nos.index(at) > 0 and nos[nos.index(at) - 1] not in [a for a, _, _ in out]:
            i = nos.index(at)
            prev = nos[i - 1]
            if prev not in lead_in and not inside_speech(text[prev], text[at], [text[x] for x in reversed(nos[:i - 1])],
                                                         [text[x] for x in nos[i + 1:]]):
                break
            at = prev
        if at is not None and at not in [a for a, _, _ in out]:
            out.append((at, title, n))
    return out


def story(ep, d, fixes):
    """The episode's scenes without slokas (except the few chosen to KEEP), fixes applied, and chapter starts."""
    text, tel, src, scenes = L.parse_episode(L.episode_file(ep))
    out = []
    for s in scenes:
        mine = fixes.pop((ep, s['no']), [])
        verse = L.is_verse(s['narration'])
        if (verse and 'KEEP' not in mine) or None in mine:
            continue
        s = dict(s, verse=verse, ep=ep)
        if (ep, s['no']) in VIS:
            s['visual'] = VIS.pop((ep, s['no']))
        if (ep, s['no']) in LOCS:
            s['loc'] = LOCS.pop((ep, s['no']))
        if not s['loc']:   # PLACE lines name the setting where the script does not
            key = next((k for lo, hi, k in PLACE_MAP.get(ep, []) if lo <= s['no'] <= hi), None)
            s['loc'] = PLACES[key][0][0] if key else ''
        if not verse:     # plain Telugu for the listener (never inside a sloka)
            for rule in SIMPLE:
                if rule[0] in s['narration']:
                    s['narration'] = s['narration'].replace(rule[0], rule[1])
                    rule[2] += 1
        for old, new in (m for m in mine if m != 'KEEP'):
            if old is None:
                s['narration'] = new
            else:
                assert old in s['narration'], f'{ep} scene {s["no"]}: fix text not found: {old}'
                s['narration'] = s['narration'].replace(old, new)
            s['secs'] = max(s['secs'], L.speak_secs(s['narration']))   # a longer line needs a longer clip
        out.append(s)
    kinds = dict(zip([s['no'] for s in out], L.kinds_for(out)))
    for s in out:
        s['kind'] = kinds[s['no']]
    return {'ep': ep, 'tel': tel, 'src': src, 'scenes': out, 'd': d, 'k': int(ep[1:].split('.')[0]),
            'starts': chapter_starts(d, out)}


def part_scenes(e, c0, c1):
    st = e['starts']
    lo = st[c0][0] if c0 else -1
    hi = st[c1][0] if c1 < len(st) else 10 ** 6
    return [s for s in e['scenes'] if lo <= s['no'] < hi]


def trim(sc, drop_recap, drop_teaser):
    """Inner joins lose the recap and the teaser (a teaser's story sentence before 'చూద్దాం' stays)."""
    sc = list(sc)
    if drop_recap:
        sc = [s for i, s in enumerate(sc) if not (i < 2 and s['narration'].startswith('గత భాగ'))]
    if drop_teaser and 'చూద్దాం' in sc[-1]['narration']:
        keep = [x for x in re.split(r'(?<=[.!?])\s+', sc[-1]['narration']) if x and 'చూద్దాం' not in x]
        sc = sc[:-1] + ([dict(sc[-1], narration=' '.join(keep))] if keep else [])
    return sc


NAMES = {'వాల్మీకి', 'మహర్షి', 'రాముడు', 'రాముడి', 'విశ్వామిత్రుడు', 'విశ్వామిత్రుడి', 'దశరథ', 'మహారాజు', 'సీతమ్మ'}


def repeats(line, nxt):
    """Words a teaser line shares with the line right after it (names do not count)."""
    return (L._words(line) & L._words(nxt[:120])) - NAMES


def lesson(extras, lesson_ep, ep):
    """The life-lesson clip, pictured from the scene a LESSON line names (else the first scene with a character)."""
    pick = [s for s in lesson_ep['scenes'] if s['no'] == LESSON_PIC.get(lesson_ep['ep'])]
    item = dict(L.lesson_item(extras[lesson_ep['ep']], pick or lesson_ep['scenes']), ep=ep)
    if pick:
        item.update(from_no=pick[0]['no'], cast_ep=lesson_ep['ep'])
    return item


def assemble(parts, extras, splits, vid_index):
    """The spoken order of one video and its chapters. parts = [(episode, first chapter, end chapter)]."""
    seq, chapters, warn = [], [], []
    lesson_ep = next((e for e, c0, c1 in reversed(parts) if c1 == len(e['starts'])), None)
    for j, (e, c0, c1) in enumerate(parts):
        first, last = j == 0, j == len(parts) - 1
        st, x = e['starts'], extras[e['ep']]
        ep_start, ep_end = c0 == 0, c1 == len(st)
        sc = trim(part_scenes(e, c0, c1), ep_start and not first, ep_end and not last)
        bridges = dict(zip([n for n, _ in e['d']['chapters'][1:]], x['bridges']))
        if ep_start:
            hook_text = splits.get((e['ep'], 'hook')) or (x['hook'] if first else splits.get((e['ep'], 'rehook'), x['hook']))
            own = 'hook' if (first or (e['ep'], 'rehook') not in splits) else 'rehook'
            hook_from = splits.get((e['ep'], own + '_from'), x['hook_from'])
            tone = splits.get((e['ep'], 'tone'), 'curious')
        else:
            tone = splits.get((e['ep'], st[c0][2], 'tone'), 'curious')
            sp = splits.get((e['ep'], st[c0][2]))
            if not sp:
                warn.append(f"{e['ep']}: video starts at chapter {st[c0][2]} – add 'SPLIT {e['ep']} {st[c0][2]} | HOOK: … | TEASE: …'")
                sp = {'HOOK': bridges.get(st[c0][2], x['hook'])}
            hook_text, hook_from = sp['HOOK'], int(sp.get('FROM', sc[0]['no']))
        src = next((s for s in e['scenes'] if s['no'] == hook_from), sc[0])
        hook = {'id': 'H', 'ep': e['ep'], 'label': 'హుక్' if first else f'రీ-హుక్ → {st[c0][1]}', 'kind': 'video',
                'secs': L.speak_secs(hook_text), 'narration': hook_text, 'new': True, 'loc': src['loc'],
                'onscreen': '' if first else st[c0][1], 'tone': tone, 'from_no': src['no'],
                'visual': f"Fast, dramatic flash-forward teaser of this story's biggest moment: {src['visual']}"}
        seq.append(hook)
        chapters.append((hook, st[c0][1]))
        # hook first (it holds the viewer), then the channel intro and a welcome that sets the scene;
        # E0.01 opens with its own "నమస్తే. ఇది పురాణ కథా శ్రవణం ఛానల్", so the intro clip would only repeat it
        if first and e['ep'] != 'E0.01':
            seq.append({'id': 'I', 'ep': e['ep'], 'label': 'ఇంట్రో (ఛానల్ బంపర్)', 'kind': 'video', 'secs': BUMPER,
                        'narration': '', 'new': True, 'loc': '', 'onscreen': 'పురాణ కథా శ్రవణం', 'tone': 'calm',
                        'visual': INTRO_VISUAL})
            welcome = splits.get((e['ep'], st[c0][2] if c0 else None, 'welcome'))
            if welcome:
                seq.append({'id': 'W', 'ep': e['ep'], 'label': 'స్వాగతం', 'kind': 'image', 'secs': L.speak_secs(welcome),
                            'narration': welcome, 'new': True, 'loc': sc[0]['loc'], 'onscreen': '', 'tone': 'welcome',
                            'from_no': sc[0]['no'],
                            'visual': f"A calm, wide establishing view of the setting: {sc[0]['visual']}"})
            elif e['ep'] != 'E0.01':
                warn.append(f"{e['ep']}: video opening has no 'WELCOME {e['ep']}{' ' + str(st[c0][2]) if c0 else ''} | …' line")
        if not ep_start and sp.get('RECAP'):
            seq.append({'id': 'R', 'ep': e['ep'], 'label': 'ఇంతవరకు', 'kind': 'image', 'secs': L.speak_secs(sp['RECAP']),
                        'narration': sp['RECAP'], 'new': True, 'loc': sc[0]['loc'], 'onscreen': '',
                        'from_no': e['scenes'][max(0, e['scenes'].index(sc[0]) - 1)]['no'],
                        'visual': f"Soft, slightly faded memory-like frame: {e['scenes'][max(0, e['scenes'].index(sc[0]) - 1)]['visual']}"})
        if not (first and ep_start) and len(repeats(hook_text, sc[0]['narration'])) >= 2:
            warn.append(f"{e['ep']}: hook repeats its next line ({', '.join(sorted(repeats(hook_text, sc[0]['narration'])))})")
        bridge_at = {at: (title, bridges[n]) for at, title, n in st[c0 + 1:c1] if n in bridges}
        teaser_last = last and ep_end and sc[-1]['narration'].startswith(L.TEASER_STARTS + ('ఇంతటితో',))   # also a kaanda's closing line
        for s in sc:
            if s['no'] in bridge_at:
                title, line = bridge_at[s['no']]
                if len(repeats(line, s['narration'])) >= 2:
                    warn.append(f"{e['ep']}: bridge before scene {s['no']} repeats it ({', '.join(sorted(repeats(line, s['narration'])))})")
                b = {'id': f"B{s['no']}", 'ep': e['ep'], 'label': f'బ్రిడ్జ్ → {title}', 'kind': 'image',
                     'secs': L.speak_secs(line), 'narration': line, 'new': True, 'loc': s['loc'], 'onscreen': title,
                     'from_no': s['no'],
                     'visual': f"{s['visual']}. Composed with calm open space on one side for an on-screen chapter title"}
                seq.append(b)
                chapters.append((b, title))
            if teaser_last and s is sc[-1]:
                seq.append(lesson(extras, lesson_ep, e['ep']))
            seq.append({'id': str(s['no']), 'ep': e['ep'], 'label': f"{e['ep']} · సీన్ {s['no']}", 'kind': s['kind'],
                        'secs': s['secs'], 'narration': s['narration'], 'new': False, 'visual': s['visual'],
                        'loc': s['loc'], 'onscreen': verse_card(s, sc), 'scene': s})
        if last and ep_end and not teaser_last and lesson_ep:
            seq.append(lesson(extras, lesson_ep, e['ep']))
        if last and not ep_end:   # the story goes on in the next video: end on its question, then the lesson
            at, title, n = st[c1]
            line = splits.get((e['ep'], n), {}).get('TEASE') or bridges.get(n, '')
            nxt = next(s for s in e['scenes'] if s['no'] == at)
            seq.append({'id': 'T', 'ep': e['ep'], 'label': 'తరువాతి వీడియో టీజర్', 'kind': 'image',
                        'secs': L.speak_secs(line), 'narration': line, 'new': True, 'loc': nxt['loc'], 'onscreen': '',
                        'from_no': nxt['no'],
                        'visual': f"A suspenseful glimpse, half in shadow: {nxt['visual']}"})
            if lesson_ep:
                seq.append(lesson(extras, lesson_ep, e['ep']))
    cta = L.CTAS[vid_index % len(L.CTAS)]
    seq.append({'id': 'C', 'ep': parts[-1][0]['ep'], 'label': 'ముగింపు', 'kind': 'image', 'secs': L.speak_secs(cta),
                'narration': cta, 'new': True, 'visual': L.CTA_VISUAL, 'loc': '', 'onscreen': L.cta_screen(cta)})
    # At an episode join, a story line left open ("…అడుగుపెట్టగానే —") moves to just after the re-hook,
    # so the re-hook never cuts a sentence in half and the line runs straight into its answer.
    # If that would still put the re-hook inside someone's words ("…చెయ్యాలి." ‖ "…అందుకని రామా నిద్రలే" —),
    # the re-hook moves forward instead, to the next bridge, once the speaker has finished.
    for k in range(1, len(seq)):
        if seq[k]['id'] == 'H' and k > 1:
            j = k
            while j > 0 and 'scene' in seq[j - 1] and open_ended(seq[j - 1]['narration']):
                j -= 1
            after = seq[j] if j < k else seq[k + 1]
            m = next((m for m in range(k + 1, len(seq)) if 'scene' not in seq[m]), len(seq))
            if ('scene' in seq[j - 1] and 'scene' in after
                    and inside_speech(seq[j - 1]['narration'], after['narration'])
                    and sum(x['secs'] for x in seq[k + 1:m]) <= 60):
                hook = seq[k]
                chapters[:] = [(seq[k + 1] if it is hook else it, t) for it, t in chapters]
                hook.update(label='రీ-హుక్', onscreen='')   # its chapter's story has been told by now
                seq[k:m] = seq[k + 1:m] + [hook]
            elif j < k:
                seq[j:k + 1] = [seq[k]] + seq[j:k]
    # Respect for the main characters and the sages, in the order the lines are spoken (a speech can run on over
    # several scene lines, and a dropped subject carries from line to line); slokas stay as Valmiki wrote them.
    hon = honor.Honorer()
    todo = [it for it in seq if it.get('narration') and not it.get('scene', {}).get('verse')]

    def view(t):
        """The line as the honorific pass should read it, and how to put its own quote marks back.
        Baala's scene tables wrap whole passages of the book in "…" and put speech in '…'; elsewhere "…" is speech
        (a whole line in "…" with no నేను/నువ్వు words is quoted narration, and a speech opened with " is sometimes
        closed with ')."""
        pre = suf = ''
        if QUOTE_WRAPPED:
            if t.lstrip().startswith('"'):
                a = t.index('"') + 1
                pre, t = t[:a], t[a:]
            if t.rstrip().endswith('"'):
                z = t.rindex('"')
                t, suf = t[:z], t[z:]
        elif honor.quoted_narration(t):
            a, z = t.index('"') + 1, t.rindex('"')
            pre, t, suf = t[:a], t[a:z], t[z:]
        swap = "'" in t and '"' not in t and (QUOTE_WRAPPED or (t.count("'") == 1 and re.search(r"'\s*(అని|అంటూ)\s", t)))
        core = t.replace("'", '"') if swap else t
        return core, (lambda n: pre + (n.replace('"', "'") if swap else n) + suf)

    views = [view(it['narration']) for it in todo]
    closes = [honor.first_quote_closes(c) for c, _ in views]
    last_speaker = None
    for j, item in enumerate(todo):
        core, restore = views[j]
        if 'scene' not in item:     # hooks, bridges, recaps: always the storyteller
            hon.reset()
            hon.in_quote = False
        if hon.in_quote:
            # an open speech runs on only into a line that closes it ("…" అని …), possibly after a few lines
            # with no quote mark; otherwise its closing quote is missing and it ended with the line before
            nxt = next((c for c in closes[j:j + 20] if c is not None), None)
            if not nxt:
                hon.in_quote, last_speaker = False, hon.speaker
        elif closes[j]:     # the line closes a speech whose opening we lost: what comes before the quote is speech
            hon.in_quote, hon.qtopic = True, None
            hon.speaker = honor.speaker_after_close(core) or last_speaker or 'UNKNOWN'
        if core.count('"') % 2 and not hon.in_quote:     # a speech opens and closes on a later line
            k = next((k for k in range(j + 1, min(j + 21, len(todo))) if closes[k] is not None), None)
            hon.hint = honor.speaker_after_close(views[k][0]) if k is not None and closes[k] else None
        new = restore(hon(core))
        if new != item['narration']:
            item['narration'] = new
            item['secs'] = max(item['secs'], L.speak_secs(new))
        if item.get('onscreen') and 'scene' not in item:
            item['onscreen'] = honor.Honorer(quotes=False)(item['onscreen'])
    chapters[:] = [(it, honor.Honorer(quotes=False)(t)) for it, t in chapters]
    for item in seq:   # every new part carries its delivery tone (hooks were set above)
        if item['new'] and 'tone' not in item:
            item['tone'] = {'B': 'curious' if item['narration'].rstrip().endswith('?') else 'calm',
                            'R': 'calm', 'T': 'curious', 'L': 'warm', 'C': 'warm', 'W': 'warm', 'I': 'calm'}[item['id'][0]]
    total = sum(i['secs'] for i in seq) + OUTRO       # the intro clip is an item now, after the hook
    return seq, chapters, total, warn


def verse_card(s, sc):
    """On-screen card for a kept sloka: the sloka itself, and under it the first line of its meaning."""
    if not s.get('verse'):
        return ''
    i = sc.index(s)
    n = next((x for x in sc[i + 1:] if not x.get('verse')), None)
    meaning = CARDS.get((s['ep'], s['no'])) or (L.first_sentence(tts.clean(n['narration'])) if n else '')
    return 'శ్లోకం తెలుగు లిపిలో, అక్షరం అక్షరం కనిపిస్తూ' + (f' · కింద అర్థం: {meaning}' if meaning else '')


def expand(seq):
    """Retention pass: recap-length tip, and two stills (wide, then closer) for long still scenes."""
    out = []
    for item in seq:
        item = dict(item)
        if 'scene' in item and item['narration'].startswith('గత భాగ') and item['secs'] > 8:
            item['tip'] = 'రీక్యాప్‌ను ఎడిట్‌లో 8 సెకన్లలోపు కుదించండి – హుక్ తరువాత వీక్షకులు వెంటనే కొత్త కథ కోరుకుంటారు.'
        if item['kind'] == 'image' and item['secs'] >= 11 and not item['new']:
            a = math.ceil(item['secs'] / 2)
            out.append(dict(item, id=item['id'] + 'a', label=item['label'] + ' (1/2)', secs=a,
                            visual='Wide establishing view: ' + item['visual']))
            out.append(dict(item, id=item['id'] + 'b', label=item['label'] + ' (2/2)', secs=item['secs'] - a,
                            visual='Closer, emotional framing of the same moment: ' + item['visual'],
                            narration='(పై నెరేషన్ కొనసాగుతుంది – చిత్రం మాత్రమే మారుతుంది)', cont=True, tip=''))
        else:
            out.append(item)
    return out


def to_parts(units):
    parts = []
    for e, c in units:
        if parts and parts[-1][0] is e:
            parts[-1][2] = c + 1
        else:
            parts.append([e, c, c + 1])
    return [tuple(p) for p in parts]


SPLIT_COST = 100 ** 2   # cutting an episode costs as much as missing 11 minutes by 100 seconds


def group_videos(eps, extras, splits):
    """Cut the kaanda's chapters into videos as close to TARGET as possible (DP over cut points).
    Whole episodes are preferred; an episode is cut at a chapter only when that keeps videos in LOW–HIGH,
    and preferably where data/*_videos.txt already has a SPLIT opening for that chapter."""
    units = [(e, c) for e in eps for c in range(len(e['starts']))]
    n = len(units)
    if CUTS:    # data/*_videos.txt pins where each video starts, so a narration fix never re-cuts the kaanda
        at = {(e['ep'], e['starts'][c][2] if c else None): i for i, (e, c) in enumerate(units)}
        missing = [x for x in CUTS if x not in at]
        assert not missing, f'CUTS not at a chapter start: {missing}'
        idx = [at[x] for x in CUTS] + [n]
        assert idx == sorted(idx) and idx[0] == 0, 'CUTS must be in order and start with the first episode'
        return [to_parts(units[a:b]) for a, b in zip(idx, idx[1:])]
    best = [(0, None)] + [(float('inf'), None)] * n
    for b in range(1, n + 1):
        for a in range(b - 1, -1, -1):
            t = assemble(to_parts(units[a:b]), extras, splits, 0)[2]
            miss = max(0, LOW - t, t - HIGH)
            e, c = units[a]
            cut = 0 if not c else SPLIT_COST if (e['ep'], e['starts'][c][2]) in splits else 20 * SPLIT_COST
            cost = best[a][0] + (t - TARGET) ** 2 + 50 * miss ** 2 + cut
            if cost < best[b][0]:
                best[b] = (cost, a)
            if t > HIGH + 180:
                break
    cuts, b = [], n
    while b:
        a = best[b][1]
        cuts.append(to_parts(units[a:b]))
        b = a
    return cuts[::-1]


INTRO_VISUAL = ('Channel title bumper: the Purana Katha Shravanam wordmark forming from a softly glowing palm-leaf '
                'manuscript page, a kalasha with a single falling drop of nectar beside it, warm gold light')


def srt(items):
    """Captions from 0:00 (the hook comes first); the intro clip has no words."""
    cues, t = [], 0
    for s in items:
        lines = L.chunks(s['narration'])
        total = sum(len(x) for x in lines) or 1
        a = t
        for line in lines:
            b = a + s['secs'] * len(line) / total
            cues.append((a, b, line))
            a = b
        t += s['secs']
    return '\n'.join(f'{i}\n{L.srt_time(a)} --> {L.srt_time(b)}\n{x}\n' for i, (a, b, x) in enumerate(cues, 1))


def place_refs():
    """Reference prompts for every place the videos use: an empty establishing view, no people."""
    out = []
    for key in sorted(PLACES_USED):
        desc = PLACES[key][2]
        out.append({'key': key, 'prompt': (
            "Location reference image for film continuity: one wide establishing view of the place only, with no "
            f"people and no animals in the foreground, 16:9 frame, clear daylight unless described otherwise. "
            f"Style: {STYLE}. Place: {desc}. Keep the architecture, landscape, colours and layout exactly as "
            "described; this image will be reused for every scene set here. "
            "No text, letters, logos or watermarks.")})
    return out


def reference_md(refs_used):
    """Long_Videos/Videos/<kaanda>/00_REFERENCES.md: every character and place reference the videos use."""
    chars = L.reference_file(refs_used)[1]
    lines = [f'# రిఫరెన్స్ ఇమేజ్‌లు – {MINUTES} నిమిషాల వీడియోలు (పాత్రలు + ప్రదేశాలు)\n',
             'ప్రతి పాత్రకు, ప్రతి ప్రదేశానికి ఒక్కసారే ఇమేజ్ చేయండి. ఉత్తమమైనది ఇచ్చిన పేరుతో `Long_Videos/_reference_images/` లో '
             'సేవ్ చేసి, క్లిప్‌లో "రిఫరెన్స్" లో ఉన్న ఇమేజ్‌లన్నీ Flow లో *Ingredients* గా జత చేయండి. '
             'ప్రదేశం ఇమేజ్‌లో మనుషులు ఉండరు – పాత్రలు వేరుగా జత అవుతాయి.\n',
             f'## పాత్రలు ({len(chars)})\n']
    block = '### `{0}.png`\n\n```text\n{1}\n```\n'
    lines += [block.format(r['key'], r['prompt']) for r in chars]
    places = place_refs()
    lines.append(f'## ప్రదేశాలు ({len(places)})\n')
    lines += [block.format(r['key'], r['prompt']) for r in places]
    return '\n'.join(lines)


def recording(seq):
    """Own-voice script in the same numbered steps as the clips: one step per spoken part, in video order,
    so nothing is read from another place (a split still's second clip joins its first)."""
    steps = []
    for n, x in enumerate(seq, 1):
        if x.get('cont'):
            steps[-1][1] = n
            continue
        steps.append([n, n, x])
    out = []
    for a, b, x in steps:
        end = seq[b - 1]['start'] + seq[b - 1]['secs']
        nums = f'{a}–{b}' if b > a else str(a)
        label = re.sub(r' \(1/2\)$', '', x['label'])
        out.append(f"#### 🎙️ {nums}. {label} · {mmss(x['start'])} – {mmss(end)} · {end - x['start']} సె\n")
        if x['id'] == 'I':
            out.append('ఏమీ చదవనక్కర్లేదు – ఒక్కసారే చేసిన ఇంట్రో ఆడియో (`Long_Videos/Videos/tts/00_INTRO.txt`) ఇక్కడ పెట్టండి.\n')
            continue
        verse = x.get('scene', {}).get('verse')
        if x['new']:      # the part's own tone, not one fixed "ఉత్సాహంగా" for every hook
            lines = [f"[{tts.TONES[x['tone']][1]}]", *L.breath(x['narration']), '⏸']
        elif verse:
            lines = [L.CUES['V'], *L.breath(x['narration'], True), '⏸']
        else:
            lines = L.breath(x['narration'])
        out.append('```text\n' + '\n'.join(lines) + '\n```\n')
    return '\n'.join(out)


def build_video(i, parts, extras, splits, refs_used, kaanda_te, folder_name):
    group = [p[0] for p in parts]
    seq, chap_items, total, warn = assemble(parts, extras, splits, i - 1)
    spoken = list(seq)
    seq = expand(seq)
    t = 0
    for item in seq:
        item['start'] = t
        t += item['secs']
    body_end = next(x['start'] for x in seq if x['id'] == 'C')
    start_of = {id(x): x['start'] for x in seq}
    chap = [(0 if j == 0 else start_of[id(next(s for s in seq if s['id'] in (it['id'], it['id'] + 'a')
                                                and s['ep'] == it['ep']))], title)
            for j, (it, title) in enumerate(chap_items)]
    ends = [c[0] for c in chap[1:]] + [total]
    for (a, title), b in zip(chap, ends):
        assert b - a >= 10, f'V{i}: chapter "{title}" is {b - a}s (YouTube minimum is 10s)'

    cards, md_items = [], []
    for n, item in enumerate(seq, 1):
        s = {'visual': item['visual'], 'loc': item['loc']}
        no = item['scene']['no'] if 'scene' in item else item.get('from_no')
        if (item.get('cast_ep', item['ep']), no) in CAST:
            looks, refs = cast(CAST[(item.get('cast_ep', item['ep']), no)], item['visual'], item['ep'], item['loc'])
        else:
            looks, refs = L.scene_cast(s, item['ep'])
        refs_used.update(refs)
        place = place_for(item['loc'], item['ep'])
        if place:   # the location gets its own reference image, like a character
            refs = refs + [place]
            PLACES_USED.add(place)
            s['loc'] = f"{item['loc']} (match the attached place reference {place}.png): {PLACES[place][2]}"
        kind, secs = item['kind'], item['secs']
        note = ''
        if kind == 'video' and secs > 8:
            note = (f"Flow 8 సెకన్లు ఇస్తుంది; మిగిలిన {secs - 8} సె కోసం చివరి ఫ్రేమ్‌ను నెమ్మదిగా జూమ్‌తో "
                    "పట్టుకోండి లేదా క్లిప్‌ను కొద్దిగా స్లో చేయండి.")
        if item['onscreen']:
            note = (note + ' ' if note else '') + f"తెరపై టెక్స్ట్: «{item['onscreen']}»"
        if item.get('tip'):
            note = (note + ' ' if note else '') + item['tip']
        move = '' if kind == 'video' else L.editor_move(item['visual'], n) + ' (వీడియో చేయకపోతే)'
        a = item['start']
        card = {'no': str(n), 'time': f"{mmss(a)} – {mmss(a + secs)}", 'label': f"{item['label']} · {secs} సె",
                'kind': kind, 'narration': item['narration'], 'refs': refs, 'move': move, 'note': note,
                'prompt': L.scene_prompt(s, kind, looks), 'imagePrompt': L.scene_prompt(s, 'image', looks),
                'videoPrompt': L.video_prompt(s, kind, looks, n)}
        cards.append(card)
        head = '🎥 వీడియో' if kind == 'video' else '🖼️ ఇమేజ్ + కదలిక'
        star = ' · ✨ కొత్తది' if item['new'] else (' · 🔁 అదే నెరేషన్, కొత్త చిత్రం' if item.get('cont') else '')
        nar = item['narration']
        short = nar if item['new'] or len(nar) <= 110 else nar[:110].rsplit(' ', 1)[0] + '…'
        lines = [f"#### {n}. {item['label']} · {card['time']} · {secs} సె · {head}{star}\n",
                 f"- **నెరేషన్:** {short}",
                 f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in refs) if refs else 'అవసరం లేదు'}"]
        if move:
            lines.append(f'- **ఎడిటర్‌లో కదలిక:** {move}')
        if note:
            lines.append(f'- **గమనిక:** {note}')
        lines.append(f"\n```text\n{card['prompt']}\n```\n")
        md_items.append('\n'.join(lines))

    script = recording(seq)
    voice = tts.pieces(tts.paragraphs(spoken))
    labels = [f'భాగం {n} / {len(voice)}' + {'verse': ' · 🕉️ శ్లోకం', 'intro': ' · 🎬 ఇంట్రో క్లిప్ – ఒక్కసారే చేసినది ఇక్కడ పెట్టండి',
                                              'text': ''}[kind]
              for n, (kind, _) in enumerate(voice, 1)]
    voice_md = '\n'.join(f'**{lab}** · {len(v)} అక్షరాలు\n\n```text\n{v}\n```\n' for lab, (_, v) in zip(labels, voice))
    verses = [x['narration'] for x in spoken if x.get('scene', {}).get('verse')]
    lead = group[0]
    plain = lambda t: honor.Honorer(quotes=False)(t)
    main, hl, sub = (plain(x) for x in lead['d']['head'])
    pin = plain(lead['d']['pin'])
    tprompt, trefs = L.thumb_prompt(lead['scenes'], lead['ep'])
    refs_used.update(trefs)
    tels = [plain(e['tel']) for e in group]
    names = ' · '.join(tels)
    if len(names) > 66:
        names = f'{tels[0]} … {tels[-1]}'
    title = f'{names} | రామాయణం {kaanda_te} {i}'
    if len(title) > 100:
        title = f'{main} | రామాయణం {kaanda_te} {i}'
    assert len(title) <= 100, f'V{i}: title is {len(title)} characters'
    def tag(p, end):
        e, c0, c1 = p
        cut = (c0 > 0) if not end else (c1 < len(e['starts']))
        return e['ep'] + (f"({'భాగం 2' if not end else 'భాగం 1'})" if cut else '')
    eps_txt = f"{group[0]['ep']}–{group[-1]['ep']}" if len(group) > 1 else group[0]['ep']
    eps_long = ' + '.join(tag(p, False) if j == 0 and p[1] else tag(p, True) for j, p in enumerate(parts))
    srcs = ', '.join(e['src'] for e in group if e['src'])
    desc = (f"{title}\n\n" + '\n'.join(plain(e['d']['sum']) for e in group)
            + ''.join(f"\n\n🕉️ {v}" for v in verses) + "\n\n⏱️ అధ్యాయాలు\n"
            + '\n'.join(f'{mmss(a)} {c}' for a, c in chap)
            + "\n\n📖 మూలం: చిత్రరూపంలో సంపూర్ణ వాల్మీకి రామాయణము" + (f", {srcs}" if srcs else '') + "\n"
            "🔔 పురాణ కథా శ్రవణం – రామాయణం మొదటి నుండి చివరి వరకు, భాగం భాగంగా.\n\n"
            f"{HASHTAGS} #{kaanda_te.replace(' ', '')}")
    assert len(desc) <= 5000, f'V{i}: description is {len(desc)} characters'
    tags = ', '.join(['రామాయణం', 'శ్రీరాముడు', 'వాల్మీకి రామాయణం', kaanda_te, *tels[:4], 'Ramayanam in Telugu',
                      'Valmiki Ramayanam', 'Telugu devotional', 'Purana Katha Shravanam'])
    srt_rel = f'Long_Videos/Videos/captions/{folder_name}/V{i:02d}.srt'
    tts_rel = f'Long_Videos/Videos/tts/{folder_name}/V{i:02d}.txt'
    n_video = sum(c['kind'] == 'video' for c in cards)
    md = '\n'.join([
        f'# V{i:02d} · {names} ({eps_txt})\n',
        '*`Long_Videos/_tools/video_build.py` తయారుచేసిన ఫైల్. చేత్తో మార్చవద్దు – మార్పులు సీన్ పట్టికలో లేదా '
        '`_tools/data/` లో చేసి మళ్ళీ బిల్డ్ చేయండి.*\n',
        '| | |\n|---|---|',
        f'| వీడియో నిడివి | **{mmss(total)}** (హుక్ → ఇంట్రో {BUMPER} సె → స్వాగతం → కథ … → ఔట్రో {OUTRO} సె; {len(seq)} క్లిప్‌లు) |',
        f"| ఎపిసోడ్‌లు | {eps_long} – శ్లోకాలు లేకుండా, ఒకే కథగా కలిపి |",
        f'| క్లిప్‌లు | 🎥 వీడియో {n_video} · 🖼️ ఇమేజ్ + కదలిక {len(seq) - n_video} |',
        f'| క్యాప్షన్లు | `{srt_rel}` |',
        f'| ఎండ్ స్క్రీన్ | చివరి {OUTRO} సె: తరువాతి వీడియో, కాండ ప్లేలిస్ట్, సబ్‌స్క్రైబ్ |\n',
        '### 1. 🔊 ElevenLabs టెక్స్ట్ (AI వాయిస్)\n',
        f'ప్రతి భాగాన్ని వరుసగా ఒక్కొక్కటిగా పేస్ట్ చేయండి ({tts.LIMIT} అక్షరాల లోపు). సూచనలు, ⏸ గుర్తులు లేవు; '
        'అంకెలు తెలుగు పదాలుగా; ప్రతి పేరా . ? ! తో ముగుస్తుంది; కామా దగ్గర చిన్న విరామం, పేరా మధ్య పెద్ద విరామం. '
        + ('**స్వరం (Eleven v3):** ప్రతి పేరా ముందు `[serious]` `[sad]` `[in awe]` `[tense]` `[curious]` `[warm]` `[calm]` '
           'ఆడియో ట్యాగ్‌లు – అవి చదవబడవు. **Stability: Natural** పెట్టండి; "Creative" లో హుక్‌లు అతిగా నవ్వుతూ వస్తాయి. '
           if tts.TAGS else
           '**స్వరం (Multilingual v2):** టెక్స్ట్‌లో ట్యాగ్‌లు లేవు (v2 వాటిని పైకి చదివేస్తుంది). సెట్టింగ్‌లు: **Stability 60–70%**, '
           '**Similarity 75%**, **Style exaggeration 0%**, Speaker boost ఆన్. Stability తక్కువైతే, Style పెరిగితే హుక్‌లు '
           'పిచ్ పెంచి నవ్వుతున్నట్లు వస్తాయి. ఏదైనా హుక్ ఇంకా అలా వస్తే Regenerate చేయండి లేదా Stability 75% చేయండి. ')
        +
        '**🕉️ శ్లోకం** భాగాలు విడిగా: AI వాయిస్ సంస్కృతాన్ని సరిగ్గా పలకకపోవచ్చు – ఒకసారి విని, బాగోలేకపోతే మీ గొంతుతో '
        'నెమ్మదిగా, శ్రావ్యంగా రికార్డ్ చేసి, కింద తంబుర/వీణ సంగీతంతో అదే స్థానంలో పెట్టండి. '
        f'అదే టెక్స్ట్ `{tts_rel}` లో కూడా ఉంది. ముందు వచ్చే ఇంట్రో (బంపర్) ఒక్కసారే చేయాలి: '
        '`Long_Videos/Videos/tts/00_INTRO.txt` – «పురాణ కథా శ్రవణం! మన పురాణాలు, మన ఇతిహాసాలు, మన జీవన విధానాలు!»\n',
        voice_md,
        '### 1బి. 🎙️ సొంత గొంతుతో చదవాలంటే – రికార్డింగ్ స్క్రిప్ట్\n',
        'కింద 2వ విభాగంలోని క్లిప్‌ల నంబర్లతోనే దశలు – పై నుండి కిందకి ఒక్కొక్కటిగా చదివితే చాలు, వేరే చోటికి వెళ్ళనక్కర్లేదు. '
        'ఒక్కో దశను ఒక్కో ఆడియో ఫైల్‌గా సేవ్ చేయండి (ఉదా. `04-05.wav`) – ఎడిటర్‌లో అదే నంబర్ క్లిప్‌ల కింద పెట్టవచ్చు. '
        '«4–5» అంటే ఒకే నెరేషన్ రెండు చిత్రాల మీద. [ ] లో ఎలా చెప్పాలో సూచన (సూచన లేని దశలు ప్రశాంతంగా, కథ చెబుతున్నట్లు); '
        'ప్రతి లైను ఒక శ్వాసలో; ⏸ దగ్గర ఒక సెకను ఆగండి.\n',
        script,
        '### 2. క్లిప్‌లు (16:9 · ఫోటోరియలిస్టిక్)\n',
        '- **🎥 వీడియో:** Flow (Veo) లో. ముందు ఇదే ప్రాంప్ట్‌తో ఇమేజ్ చేసి, నచ్చితే *Frames to Video* లో మొదటి ఫ్రేమ్‌గా వాడండి.',
        '- **🖼️ ఇమేజ్ + కదలిక:** ఇమేజ్ మాత్రమే చేసి, ఎడిటర్‌లో ఇచ్చిన జూమ్/ప్యాన్‌తో క్లిప్ నిడివి అంతా చూపించండి.',
        f'- ప్రతి క్లిప్‌కు **రిఫరెన్స్** ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేయండి. సమయాలు వీడియో మొదటి నుండి (హుక్ 0:00 నుండి).\n',
        '\n'.join(md_items),
        '### 3. థంబ్‌నెయిల్ (1280×720 · 16:9)\n',
        '| భాగం | టెక్స్ట్ | రూపం |\n|---|---|---|',
        f'| హెడ్‌లైన్ (ఎడమ 45%) | **{main}** | తెలుపు, **{hl}** పసుపు (#FFD700), నల్ల అవుట్‌లైన్ + షాడో |',
        f'| కింది లైన్ | {sub} | తెలుపు, సెమీ-బోల్డ్ |',
        f'| బ్యాడ్జ్ (పై ఎడమ) | {kaanda_te} · {i} | కాషాయ పట్టీ |\n',
        f"- **రిఫరెన్స్:** {' · '.join(f'`{r}.png`' for r in trefs) if trefs else 'అవసరం లేదు'}",
        '- బ్యాక్‌గ్రౌండ్ ఈ ప్రాంప్ట్‌తో చేసి, టెక్స్ట్ Canva లో వేయండి.\n',
        f'```text\n{tprompt}\n```\n',
        '### 4. YouTube అప్‌లోడ్\n',
        f'**టైటిల్:**\n\n```text\n{title}\n```\n',
        f'**వివరణ (అధ్యాయాలతో):**\n\n```text\n{desc}\n```\n',
        f"**పిన్ కామెంట్:**\n\n```text\n{pin}\n```\n",
        f'**ట్యాగ్‌లు:**\n\n```text\n{tags}\n```\n',
        f'**క్యాప్షన్ ఫైల్:** `{srt_rel}` – YouTube Studio → Subtitles → Upload file.\n'])
    fname = f"V{i:02d}_{eps_txt.replace('–', '-')}.md"
    page = {'n': f'V{i:02d}', 'headline': main, 'hl': hl, 'sub': sub, 'badge': f'{kaanda_te} · {i} · {mmss(total)}',
            'title': title, 'sloka': [], 'tts': [v for _, v in voice], 'ttsLabels': labels,
            'ttsAll': '\n\n'.join(v for k, v in voice if k != 'intro'),
            'ttsAllNote': 'ఇంట్రో క్లిప్ లేకుండా, శ్లోకాలతో సహా మొత్తం వరుసగా. ElevenLabs ఒకేసారి ఇంత పెద్ద టెక్స్ట్ తీసుకోకపోతే కింద ఉన్న భాగాలు ఒక్కొక్కటిగా వాడండి.', 'reading': None, 'clips': cards, 'thumbPrompt': tprompt,
            'thumbRefs': trefs, 'desc': desc, 'pinned': pin, 'srt': srt_rel}
    return fname, md, srt(spoken), page, total, warn, eps_long, list(zip(labels, [v for _, v in voice]))


def main(data_path):
    data = L.read_data(data_path)
    extras = L.read_narration(data_path.replace('.txt', '_narration.txt'))
    fixes, splits = read_fixes(data_path.replace('.txt', '_videos.txt'))
    eps = [story(ep, d, fixes) for ep, d in data.items()]
    assert not fixes, f'fixes for scenes that were not found: {sorted(fixes)}'
    assert not VIS, f'VIS lines for scenes that were not found: {sorted(VIS)}'
    assert not LOCS, f'LOC lines for scenes that were not found: {sorted(LOCS)}'
    unused = [r[0] for r in SIMPLE if not r[2]]
    assert not unused, f'SIMPLE words not found anywhere: {unused}'
    by_kaanda = {}
    for e in eps:
        by_kaanda.setdefault(max(e['k'], 1), []).append(e)    # Parichayam opens the Baala series
    tpl = open(os.path.join(L.ROOT, 'Valmiki_Ramayanam', '_tools', 'flow_helper_template.html'), encoding='utf-8').read()
    refs_used, warns = set(), []
    for k, kaanda_eps in by_kaanda.items():
        folder, kaanda_te = KAANDAS[k]
        honor.DISCIPLE_BHARADWAJA = k == 1
        global QUOTE_WRAPPED
        QUOTE_WRAPPED = k == 1    # Baala's tables quote the book in "…" and speech in '…'
        name = folder.replace(' - ', '_').replace(' ', '_')
        out_dir, cap_dir = os.path.join(VIDEOS, name), os.path.join(VIDEOS, 'captions', name)
        tts_dir = os.path.join(VIDEOS, 'tts', name)
        for dr in (out_dir, cap_dir, tts_dir):
            os.makedirs(dr, exist_ok=True)
        for old in (glob.glob(os.path.join(out_dir, 'V*.md')) + glob.glob(os.path.join(cap_dir, 'V*.srt'))
                    + glob.glob(os.path.join(tts_dir, 'V*.txt'))):
            os.remove(old)    # a re-cut can rename videos; never leave a stale one behind
        pages, index = [], []
        for i, parts in enumerate(group_videos(kaanda_eps, extras, splits), 1):
            group = [p[0] for p in parts]
            fname, md, srt, page, total, warn, eps_long, voice = build_video(i, parts, extras, splits, refs_used,
                                                                             kaanda_te, name)
            warns += [f'V{i:02d} {w}' for w in warn]
            open(os.path.join(out_dir, fname), 'w', encoding='utf-8', newline='\n').write(md)
            open(os.path.join(cap_dir, f'V{i:02d}.srt'), 'w', encoding='utf-8', newline='\n').write(srt)
            open(os.path.join(tts_dir, f'V{i:02d}.txt'), 'w', encoding='utf-8', newline='\n').write(
                '\n\n'.join(f'===== {lab} =====\n\n{v}' for lab, v in voice) + '\n')
            pages.append(page)
            index.append(f"| [V{i:02d}]({fname}) | {eps_long} | {mmss(total)} | "
                         f"{' · '.join(honor.Honorer(quotes=False)(e['tel']) for e in group)} |")
            print(f"V{i:02d} {mmss(total):>6}  {eps_long}")
        label = ('పరిచయం + ' if any(e['k'] == 0 for e in kaanda_eps) else '') + kaanda_te
        open(os.path.join(out_dir, '00_INDEX.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join([
            f'# {label} – {MINUTES} నిమిషాల వీడియోలు (శ్లోకాలు లేకుండా)\n',
            f'{len(kaanda_eps)} ఎపిసోడ్‌లు → **{len(pages)} వీడియోలు**. ప్రతి వీడియో ఫైల్‌లో పూర్తి కిట్ ఉంది: రికార్డింగ్ స్క్రిప్ట్, '
            'క్లిప్ ప్రాంప్ట్‌లు, థంబ్‌నెయిల్, టైటిల్, అధ్యాయాలతో వివరణ, పిన్ కామెంట్, క్యాప్షన్లు.\n',
            '| వీడియో | ఎపిసోడ్‌లు | నిడివి | కథ |', '|---|---|---|---|', *index, '']))
        payload = {'key': f'videos_{k}', 'name': f'{label} – {MINUTES} నిమిషాల వీడియోలు', 'slokas': pages,
                   'refs': L.reference_file(refs_used)[1] + place_refs(), 'placeKeys': sorted(PLACES_USED), 'unit': 'వీడియోలు', 'clipWord': '', 'clipsNote': CLIPS_NOTE,
                   'subtitle': 'శ్లోకాలు లేకుండా · ప్రతి క్లిప్‌కు Flow ప్రాంప్ట్, థంబ్‌నెయిల్, అప్‌లోడ్',
                   'scriptTitle': '', 'ttsTitle': '🔊 ElevenLabs టెక్స్ట్ – ప్రతి భాగం వరుసగా కాపీ చేసి పేస్ట్ చేయండి'}
        blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
        frag = tpl.replace('__TITLE__', f'{kaanda_te} వీడియోలు').replace('__DATA__', blob)
        os.makedirs(os.path.join(L.TOOLS, 'publish'), exist_ok=True)
        open(os.path.join(L.TOOLS, 'publish', f'{name}_videos.html'), 'w', encoding='utf-8', newline='\n').write(frag)
        full = ('<!doctype html><html lang="te"><head><meta charset="utf-8"><meta name="viewport" '
                'content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + frag + '</body></html>')
        open(os.path.join(VIDEOS, f'{name}_VIDEOS_HELPER.html'), 'w', encoding='utf-8', newline='\n').write(full)
        open(os.path.join(out_dir, '00_REFERENCES.md'), 'w', encoding='utf-8', newline='\n').write(reference_md(refs_used))
    for w in warns:
        print('WARN', w)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')   # a Windows console would crash on the Telugu progress lines
    main(sys.argv[1])
