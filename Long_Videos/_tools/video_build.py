"""Re-cut the long episodes into 10–12 minute YouTube videos, narrated without the slokas.

usage:  python video_build.py data/0_1_Parichayam_Baala.txt

Reads the same scene tables and data files as long_build.py (episode files are only read, never written) and writes
Long_Videos/Videos/:
  - <kaanda>/V01_E0.01-E1.02.md …   one complete kit per video: recording script, clips, thumbnail, upload text
  - <kaanda>/00_INDEX.md            which episodes went into which video, and the lengths
  - captions/<kaanda>/V01.srt
  - <kaanda>_VIDEOS_HELPER.html     the phone/computer helper page (and its claude.ai copy in _tools/publish/)

What changes from the episode kits:
  - every sloka scene is dropped; the few lines that pointed at a sloka are reworded (data/*_videos.txt)
  - consecutive episodes are joined until a video runs 10–12 minutes
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
import tts
from long_build import BUMPER, OUTRO, KAANDAS, HASHTAGS, mmss

VIDEOS = os.path.join(L.LONG, 'Videos')
L.CUES['R'] = '[ఇంతవరకు · సహజంగా, కొంచెం వేగంగా – కొత్త వీక్షకుడికి కథ గుర్తుచేస్తున్నట్లు]'
L.CUES['T'] = '[తరువాతి వీడియో టీజర్ · నెమ్మదిగా, ఉత్కంఠగా, ప్రశ్న మీద ఆగండి]'
TARGET, LOW, HIGH = 11 * 60, 10 * 60, 12 * 60


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
            if head.startswith(('REHOOK ', 'HOOK ')):
                splits[(head.split()[1], head.split()[0].lower())] = rest
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
            old, new = rest.split(' => ', 1)
            fixes.setdefault((ep, int(no)), []).append((old, new))
    return fixes, splits


def chapter_starts(d, sc):
    """Chapter -> first kept scene at or after its old start (a chapter that lost its scenes merges into the next).
    A chapter never starts right after a lead-in ("… ఇలా అన్నాడు —"): the bridge would cut the speaker off,
    so the chapter (and its bridge) moves back to the lead-in line."""
    nos = [s['no'] for s in sc]
    lead_in = {s['no'] for s in sc if s['narration'].rstrip(' "\'').endswith(('—', 'ఇలా అన్నాడు.', 'ఇలా పలికారు.'))}
    out = []
    for n, title in d['chapters']:
        at = next((x for x in nos if x >= n), None)
        while at is not None and nos.index(at) > 0 and nos[nos.index(at) - 1] in lead_in                 and nos[nos.index(at) - 1] not in [a for a, _, _ in out]:
            at = nos[nos.index(at) - 1]
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
        s = dict(s, verse=verse)
        for old, new in (m for m in mine if m != 'KEEP'):
            assert old in s['narration'], f'{ep} scene {s["no"]}: fix text not found: {old}'
            s['narration'] = s['narration'].replace(old, new)
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
            hook_from, tone = x['hook_from'], splits.get((e['ep'], 'tone'), 'curious')
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
                'onscreen': '' if first else st[c0][1], 'tone': tone,
                'visual': f"Fast, dramatic flash-forward teaser of this story's biggest moment: {src['visual']}"}
        seq.append(hook)
        chapters.append((hook, st[c0][1]))
        if not ep_start and sp.get('RECAP'):
            seq.append({'id': 'R', 'ep': e['ep'], 'label': 'ఇంతవరకు', 'kind': 'image', 'secs': L.speak_secs(sp['RECAP']),
                        'narration': sp['RECAP'], 'new': True, 'loc': sc[0]['loc'], 'onscreen': '',
                        'visual': f"Soft, slightly faded memory-like frame: {e['scenes'][max(0, e['scenes'].index(sc[0]) - 1)]['visual']}"})
        if not (first and ep_start) and len(repeats(hook_text, sc[0]['narration'])) >= 2:
            warn.append(f"{e['ep']}: hook repeats its next line ({', '.join(sorted(repeats(hook_text, sc[0]['narration'])))})")
        bridge_at = {at: (title, bridges[n]) for at, title, n in st[c0 + 1:c1] if n in bridges}
        teaser_last = last and ep_end and sc[-1]['narration'].startswith(L.TEASER_STARTS)
        for s in sc:
            if s['no'] in bridge_at:
                title, line = bridge_at[s['no']]
                if len(repeats(line, s['narration'])) >= 2:
                    warn.append(f"{e['ep']}: bridge before scene {s['no']} repeats it ({', '.join(sorted(repeats(line, s['narration'])))})")
                b = {'id': f"B{s['no']}", 'ep': e['ep'], 'label': f'బ్రిడ్జ్ → {title}', 'kind': 'image',
                     'secs': L.speak_secs(line), 'narration': line, 'new': True, 'loc': s['loc'], 'onscreen': title,
                     'visual': f"{s['visual']}. Composed with calm open space on one side for an on-screen chapter title"}
                seq.append(b)
                chapters.append((b, title))
            if teaser_last and s is sc[-1]:
                seq.append(dict(L.lesson_item(extras[lesson_ep['ep']], lesson_ep['scenes']), ep=e['ep']))
            seq.append({'id': str(s['no']), 'ep': e['ep'], 'label': f"{e['ep']} · సీన్ {s['no']}", 'kind': s['kind'],
                        'secs': s['secs'], 'narration': s['narration'], 'new': False, 'visual': s['visual'],
                        'loc': s['loc'], 'onscreen': verse_card(s, sc), 'scene': s})
        if last and ep_end and not teaser_last and lesson_ep:
            seq.append(dict(L.lesson_item(extras[lesson_ep['ep']], lesson_ep['scenes']), ep=e['ep']))
        if last and not ep_end:   # the story goes on in the next video: end on its question, then the lesson
            at, title, n = st[c1]
            line = splits.get((e['ep'], n), {}).get('TEASE') or bridges.get(n, '')
            nxt = next(s for s in e['scenes'] if s['no'] == at)
            seq.append({'id': 'T', 'ep': e['ep'], 'label': 'తరువాతి వీడియో టీజర్', 'kind': 'image',
                        'secs': L.speak_secs(line), 'narration': line, 'new': True, 'loc': nxt['loc'], 'onscreen': '',
                        'visual': f"A suspenseful glimpse, half in shadow: {nxt['visual']}"})
            if lesson_ep:
                seq.append(dict(L.lesson_item(extras[lesson_ep['ep']], lesson_ep['scenes']), ep=e['ep']))
    cta = L.CTAS[vid_index % len(L.CTAS)]
    seq.append({'id': 'C', 'ep': parts[-1][0]['ep'], 'label': 'సబ్‌స్క్రైబ్', 'kind': 'image', 'secs': L.speak_secs(cta),
                'narration': cta, 'new': True, 'visual': L.CTA_VISUAL, 'loc': '', 'onscreen': 'SUBSCRIBE 🔔'})
    for item in seq:   # every new part carries its delivery tone (hooks were set above)
        if item['new'] and 'tone' not in item:
            item['tone'] = {'B': 'curious' if item['narration'].rstrip().endswith('?') else 'calm',
                            'R': 'calm', 'T': 'curious', 'L': 'warm', 'C': 'warm'}[item['id'][0]]
    total = BUMPER + sum(i['secs'] for i in seq) + OUTRO
    return seq, chapters, total, warn


def verse_card(s, sc):
    """On-screen card for a kept sloka: the sloka itself, and under it the first line of its meaning."""
    if not s.get('verse'):
        return ''
    i = sc.index(s)
    n = next((x for x in sc[i + 1:] if not x.get('verse')), None)
    meaning = L.first_sentence(tts.clean(n['narration'])) if n else ''
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
    """Cut the kaanda's chapters into videos as close to 11 minutes as possible (DP over cut points).
    Whole episodes are preferred; an episode is cut at a chapter only when that keeps videos in 10–12 minutes,
    and preferably where data/*_videos.txt already has a SPLIT opening for that chapter."""
    units = [(e, c) for e in eps for c in range(len(e['starts']))]
    n = len(units)
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


def recording(spoken):
    out, ep = [], None
    for x in spoken:
        if x['ep'] != ep and x['id'] not in ('L', 'C'):
            if ep:
                out.append(f'\n[── ఇక్కడి నుండి {x["ep"]} కథ ──]')
            ep = x['ep']
        if x['new']:      # the part's own tone, not one fixed "ఉత్సాహంగా" for every hook
            part = {'H': 'హుక్', 'B': 'బ్రిడ్జ్', 'R': 'ఇంతవరకు', 'T': 'టీజర్', 'L': 'జీవిత పాఠం', 'C': 'సబ్‌స్క్రైబ్'}[x['id'][0]]
            out += [f"[{part} · {tts.TONES[x['tone']][1]}]", *L.breath(x['narration']), '⏸']
        else:
            out.append(L.performance_script([x]))
    return '\n'.join(out)


def build_video(i, parts, extras, splits, refs_used, kaanda_te, folder_name):
    group = [p[0] for p in parts]
    seq, chap_items, total, warn = assemble(parts, extras, splits, i - 1)
    spoken = list(seq)
    seq = expand(seq)
    t = BUMPER
    for item in seq:
        item['start'] = t
        t += item['secs']
    body_end = next(x['start'] for x in seq if x['id'] == 'C')
    start_of = {id(x): x['start'] for x in seq}
    chap = [(0 if j == 0 else start_of[id(next(s for s in seq if s['id'] == it['id'] and s['ep'] == it['ep']))], title)
            for j, (it, title) in enumerate(chap_items)]
    ends = [c[0] for c in chap[1:]] + [total]
    for (a, title), b in zip(chap, ends):
        assert b - a >= 10, f'V{i}: chapter "{title}" is {b - a}s (YouTube minimum is 10s)'

    cards, md_items = [], []
    for n, item in enumerate(seq, 1):
        s = {'visual': item['visual'], 'loc': item['loc']}
        looks, refs = L.scene_cast(s, item['ep'])
        refs_used.update(refs)
        kind, secs = item['kind'], item['secs']
        note = ''
        if kind == 'video' and secs > 8:
            note = (f"Flow 8 సెకన్లు ఇస్తుంది; మిగిలిన {secs - 8} సె కోసం చివరి ఫ్రేమ్‌ను నెమ్మదిగా జూమ్‌తో "
                    "పట్టుకోండి లేదా క్లిప్‌ను కొద్దిగా స్లో చేయండి.")
        if item['onscreen']:
            note = (note + ' ' if note else '') + f"తెరపై టెక్స్ట్: «{item['onscreen']}»"
        if item.get('tip'):
            note = (note + ' ' if note else '') + item['tip']
        move = '' if kind == 'video' else L.editor_move(item['visual'], n)
        a = item['start']
        card = {'no': str(n), 'time': f"{mmss(a)} – {mmss(a + secs)}", 'label': f"{item['label']} · {secs} సె",
                'kind': kind, 'narration': item['narration'], 'refs': refs, 'move': move, 'note': note,
                'prompt': L.scene_prompt(s, kind, looks)}
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

    script = recording(spoken)
    voice = tts.pieces(tts.paragraphs(spoken))
    labels = [f'భాగం {n} / {len(voice)}' + (' · 🕉️ శ్లోకం' if kind == 'verse' else '')
              for n, (kind, _) in enumerate(voice, 1)]
    voice_md = '\n'.join(f'**{lab}** · {len(v)} అక్షరాలు\n\n```text\n{v}\n```\n' for lab, (_, v) in zip(labels, voice))
    verses = [x['narration'] for x in spoken if x.get('scene', {}).get('verse')]
    lead = group[0]
    main, hl, sub = lead['d']['head']
    tprompt, trefs = L.thumb_prompt(lead['scenes'], lead['ep'])
    refs_used.update(trefs)
    tels = [e['tel'] for e in group]
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
    desc = (f"{title}\n\n" + '\n'.join(e['d']['sum'] for e in group)
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
    hooks = [f"- **{x['label']}:** {x['narration']}" for x in spoken if x['id'] in ('H', 'T')]
    md = '\n'.join([
        f'# V{i:02d} · {names} ({eps_txt})\n',
        '*`Long_Videos/_tools/video_build.py` తయారుచేసిన ఫైల్. చేత్తో మార్చవద్దు – మార్పులు సీన్ పట్టికలో లేదా '
        '`_tools/data/` లో చేసి మళ్ళీ బిల్డ్ చేయండి.*\n',
        '| | |\n|---|---|',
        f'| వీడియో నిడివి | **{mmss(total)}** (బంపర్ {BUMPER} సె + {len(seq)} క్లిప్‌లు + ఔట్రో {OUTRO} సె) |',
        f"| ఎపిసోడ్‌లు | {eps_long} – శ్లోకాలు లేకుండా, ఒకే కథగా కలిపి |",
        f'| క్లిప్‌లు | 🎥 వీడియో {n_video} · 🖼️ ఇమేజ్ + కదలిక {len(seq) - n_video} |',
        f'| క్యాప్షన్లు | `{srt_rel}` |',
        f'| ఎండ్ స్క్రీన్ | చివరి {OUTRO} సె: తరువాతి వీడియో, కాండ ప్లేలిస్ట్, సబ్‌స్క్రైబ్ |\n',
        '### 1. 🔊 ElevenLabs టెక్స్ట్ (AI వాయిస్)\n',
        f'ప్రతి భాగాన్ని వరుసగా ఒక్కొక్కటిగా పేస్ట్ చేయండి ({tts.LIMIT} అక్షరాల లోపు). సూచనలు, ⏸ గుర్తులు లేవు; '
        'అంకెలు తెలుగు పదాలుగా; ప్రతి పేరా . ? ! తో ముగుస్తుంది; కామా దగ్గర చిన్న విరామం, పేరా మధ్య పెద్ద విరామం. '
        '**స్వరం:** ప్రతి పేరా ముందు ఉన్న `[serious]` `[sad]` `[in awe]` `[tense]` `[curious]` `[warm]` `[calm]` – Eleven v3 '
        'ఆడియో ట్యాగ్‌లు, ఆ సన్నివేశానికి తగిన స్వరం కోసం (అవి చదవబడవు). v3 లో **Stability: Natural** (లేదా Robust) పెట్టండి – '
        '"Creative" లో హుక్‌లు అతిగా నవ్వుతూ, పిచ్ పెంచి వస్తాయి. వేరే మోడల్ ట్యాగ్‌లను చదివేస్తే వాటిని తొలగించి పేస్ట్ చేయండి. '
        '**🕉️ శ్లోకం** భాగాలు విడిగా: AI వాయిస్ సంస్కృతాన్ని సరిగ్గా పలకకపోవచ్చు – ఒకసారి విని, బాగోలేకపోతే మీ గొంతుతో '
        'నెమ్మదిగా, శ్రావ్యంగా రికార్డ్ చేసి, కింద తంబుర/వీణ సంగీతంతో అదే స్థానంలో పెట్టండి. '
        f'అదే టెక్స్ట్ `{tts_rel}` లో కూడా ఉంది. ముందు వచ్చే ఇంట్రో (బంపర్) ఒక్కసారే చేయాలి: '
        '`Long_Videos/Videos/tts/00_INTRO.txt` – «పురాణ కథా శ్రవణం! మన పురాణాలు, మన ఇతిహాసాలు, మన జీవన విధానాలు!»\n',
        voice_md,
        '### 1బి. 🎙️ సొంత గొంతుతో చదవాలంటే – రికార్డింగ్ స్క్రిప్ట్\n',
        *hooks,
        *[f"- **జీవిత పాఠం:** {x['narration']}" for x in spoken if x['id'] == 'L'],
        f"- **సబ్‌స్క్రైబ్:** {L.CTAS[(i - 1) % len(L.CTAS)]}\n",
        'ఈ వరుసలోనే చదవండి. [ ] లో ఎలా చెప్పాలో సూచన; ప్రతి లైను ఒక శ్వాసలో; ⏸ దగ్గర ఒక సెకను ఆగండి. '
        '[── … ──] గుర్తు దగ్గర తరువాతి ఎపిసోడ్ కథ మొదలవుతుంది – అక్కడ రెండు సెకన్లు ఆగండి.\n',
        f'```text\n{script}\n```\n',
        '### 2. క్లిప్‌లు (16:9 · ఫోటోరియలిస్టిక్)\n',
        '- **🎥 వీడియో:** Flow (Veo) లో. ముందు ఇదే ప్రాంప్ట్‌తో ఇమేజ్ చేసి, నచ్చితే *Frames to Video* లో మొదటి ఫ్రేమ్‌గా వాడండి.',
        '- **🖼️ ఇమేజ్ + కదలిక:** ఇమేజ్ మాత్రమే చేసి, ఎడిటర్‌లో ఇచ్చిన జూమ్/ప్యాన్‌తో క్లిప్ నిడివి అంతా చూపించండి.',
        f'- ప్రతి క్లిప్‌కు **రిఫరెన్స్** ఇమేజ్‌లను Flow లో *Ingredients* గా జత చేయండి. సమయాలు బంపర్ ({BUMPER} సె) తో కలిపి.\n',
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
        f"**పిన్ కామెంట్:**\n\n```text\n{lead['d']['pin']}\n```\n",
        f'**ట్యాగ్‌లు:**\n\n```text\n{tags}\n```\n',
        f'**క్యాప్షన్ ఫైల్:** `{srt_rel}` – YouTube Studio → Subtitles → Upload file.\n'])
    fname = f"V{i:02d}_{eps_txt.replace('–', '-')}.md"
    page = {'n': f'V{i:02d}', 'headline': main, 'hl': hl, 'sub': sub, 'badge': f'{kaanda_te} · {i} · {mmss(total)}',
            'title': title, 'sloka': [], 'tts': [v for _, v in voice], 'ttsLabels': labels, 'reading': None, 'clips': cards, 'thumbPrompt': tprompt,
            'thumbRefs': trefs, 'desc': desc, 'pinned': lead['d']['pin'], 'srt': srt_rel}
    return fname, md, L.srt(spoken), page, total, warn, eps_long, list(zip(labels, [v for _, v in voice]))


def main(data_path):
    data = L.read_data(data_path)
    extras = L.read_narration(data_path.replace('.txt', '_narration.txt'))
    fixes, splits = read_fixes(data_path.replace('.txt', '_videos.txt'))
    eps = [story(ep, d, fixes) for ep, d in data.items()]
    assert not fixes, f'fixes for scenes that were not found: {sorted(fixes)}'
    by_kaanda = {}
    for e in eps:
        by_kaanda.setdefault(max(e['k'], 1), []).append(e)    # Parichayam opens the Baala series
    tpl = open(os.path.join(L.ROOT, 'Valmiki_Ramayanam', '_tools', 'flow_helper_template.html'), encoding='utf-8').read()
    refs_used, warns = set(), []
    for k, kaanda_eps in by_kaanda.items():
        folder, kaanda_te = KAANDAS[k]
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
                         f"{' · '.join(e['tel'] for e in group)} |")
            print(f"V{i:02d} {mmss(total):>6}  {eps_long}")
        label = ('పరిచయం + ' if any(e['k'] == 0 for e in kaanda_eps) else '') + kaanda_te
        open(os.path.join(out_dir, '00_INDEX.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join([
            f'# {label} – 10–12 నిమిషాల వీడియోలు (శ్లోకాలు లేకుండా)\n',
            f'{len(kaanda_eps)} ఎపిసోడ్‌లు → **{len(pages)} వీడియోలు**. ప్రతి వీడియో ఫైల్‌లో పూర్తి కిట్ ఉంది: రికార్డింగ్ స్క్రిప్ట్, '
            'క్లిప్ ప్రాంప్ట్‌లు, థంబ్‌నెయిల్, టైటిల్, అధ్యాయాలతో వివరణ, పిన్ కామెంట్, క్యాప్షన్లు.\n',
            '| వీడియో | ఎపిసోడ్‌లు | నిడివి | కథ |', '|---|---|---|---|', *index, '']))
        payload = {'key': f'videos_{k}', 'name': f'{label} – 10–12 నిమిషాల వీడియోలు', 'slokas': pages,
                   'refs': L.reference_file(refs_used)[1], 'unit': 'వీడియోలు', 'clipWord': '',
                   'subtitle': 'శ్లోకాలు లేకుండా · ప్రతి క్లిప్‌కు Flow ప్రాంప్ట్, థంబ్‌నెయిల్, అప్‌లోడ్',
                   'scriptTitle': '', 'ttsTitle': '🔊 ElevenLabs టెక్స్ట్ – ప్రతి భాగం వరుసగా కాపీ చేసి పేస్ట్ చేయండి'}
        blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
        frag = tpl.replace('__TITLE__', f'{kaanda_te} వీడియోలు').replace('__DATA__', blob)
        os.makedirs(os.path.join(L.TOOLS, 'publish'), exist_ok=True)
        open(os.path.join(L.TOOLS, 'publish', f'{name}_videos.html'), 'w', encoding='utf-8', newline='\n').write(frag)
        full = ('<!doctype html><html lang="te"><head><meta charset="utf-8"><meta name="viewport" '
                'content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + frag + '</body></html>')
        open(os.path.join(VIDEOS, f'{name}_VIDEOS_HELPER.html'), 'w', encoding='utf-8', newline='\n').write(full)
    for w in warns:
        print('WARN', w)


if __name__ == '__main__':
    main(sys.argv[1])
