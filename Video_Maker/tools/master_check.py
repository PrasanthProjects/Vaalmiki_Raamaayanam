# -*- coding: utf-8 -*-
"""After every render (user, 2026-11-11): master the sound to YouTube's level and check the video before upload.

    python tools/master_check.py out/Bala-S001-Sloka-060.mp4 [--no-master]

1. Mastering: two-pass loudnorm to -14 LUFS integrated, true peak -1.5 dBTP (YouTube plays everything at about
   -14 LUFS; a master at that level keeps the voice clear and never clips). The picture is copied untouched.
2. Checks (ffmpeg only): format and size for a Short or a long video, length, loudness, long silences, black screens,
   frozen pictures, and "looks like an earlier video" (a small picture fingerprint of every 2 seconds, compared with
   earlier renders of the same kind: many identical frames is the "reused content" pattern YouTube does not pay for).
Prints one JSON line: {"ok": bool, "lines": [Telugu report lines]}. Fingerprints are kept in out/.fingerprints.json.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'out')
FP = os.path.join(OUT, '.fingerprints.json')


def run(args, text=True):
    return subprocess.run(args, capture_output=True, text=text, encoding='utf-8' if text else None, errors='replace' if text else None)


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate:format=duration',
             '-of', 'json', path])
    d = json.loads(r.stdout)
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    a, b = v['r_frame_rate'].split('/')
    return {'w': v['width'], 'h': v['height'], 'fps': round(int(a) / int(b), 2), 'dur': float(d['format']['duration']),
            'audio': any(s['codec_type'] == 'audio' for s in d['streams'])}


def master(path):
    """Two-pass loudnorm to -14 LUFS / -1.5 dBTP; video stream copied as is."""
    r = run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
    m = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr)[-1])
    tmp = path[:-4] + '.master.mp4'
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    r = run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-c:v', 'copy', '-af', af, '-ar', '48000', '-c:a', 'aac', '-b:a', '320k',
             '-movflags', '+faststart', tmp])
    if r.returncode or not os.path.exists(tmp):
        raise RuntimeError(r.stderr[-500:])
    os.replace(tmp, path)


def loudness(path):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'])
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return (float(i[-1]) if i else None), (float(tp[-1]) if tp else None)


def spans(path, vf=None, af=None, key='silence'):
    args = ['ffmpeg', '-hide_banner', '-nostats', '-i', path]
    args += ['-vf', vf, '-an'] if vf else ['-af', af, '-vn']
    r = run(args + ['-f', 'null', '-'])
    if key == 'black':
        return [(float(a), float(b)) for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', r.stderr)]
    starts = [float(x) for x in re.findall(rf'{key}_start: ?([\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(rf'{key}_end: ?([\d.]+)', r.stderr)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def fingerprints(path, dur):
    """A 64-bit difference hash of one frame every 2 seconds."""
    r = run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'fps=0.5,scale=9:8,format=gray', '-f', 'rawvideo', '-'], text=False)
    px = np.frombuffer(r.stdout, dtype=np.uint8)
    n = len(px) // 72
    out = []
    for k in range(n):
        f = px[k * 72:(k + 1) * 72].reshape(8, 9).astype(int)
        bits = (f[:, 1:] > f[:, :-1]).flatten()
        out.append(int(''.join('1' if b else '0' for b in bits), 2))
    return out


def similar(a, b):
    """Share of frames of a that have a near-identical frame in b (Hamming distance <= 4)."""
    if not a or not b:
        return 0.0
    bb = np.array(b, dtype=np.uint64)
    hit = 0
    for x in a:
        d = np.unpackbits((bb ^ np.uint64(x)).view(np.uint8)).reshape(-1, 64).sum(1)
        hit += int(d.min() <= 4)
    return hit / len(a)


def main(path, do_master=True):
    lines, ok = [], True
    name = os.path.basename(path)
    p = probe(path)
    short = p['h'] > p['w']
    kind = 'short' if short else 'long'
    if do_master and p['audio']:
        master(path)
        lines.append('🔊 సౌండ్ YouTube స్థాయికి (-14 LUFS) సరిచేశాం – వాయిస్, సంగీతం సమంగా, ఎక్కడా పగలదు.')
    # format and length
    want = (1080, 1920) if short else (1920, 1080)
    if (p['w'], p['h']) != want:
        ok = False; lines.append(f"⚠ సైజ్ {p['w']}×{p['h']} – {'Short' if short else 'లాంగ్ వీడియో'} కి {want[0]}×{want[1]} ఉండాలి.")
    else:
        lines.append(f"✓ సైజ్ {p['w']}×{p['h']}, {p['fps']} fps.")
    if short and p['dur'] > 180:
        ok = False; lines.append(f"⚠ నిడివి {p['dur']:.0f} సె – Shorts గరిష్టం 3 నిమిషాలు.")
    elif not short and p['dur'] < 480:
        lines.append(f"• నిడివి {p['dur'] / 60:.1f} ని. – 8 నిమిషాలు దాటితే మధ్యలో ప్రకటనలు (mid-roll) పెట్టవచ్చు.")
    else:
        lines.append(f"✓ నిడివి {p['dur'] / 60:.1f} ని." if not short else f"✓ నిడివి {p['dur']:.0f} సె.")
    # sound
    if not p['audio']:
        ok = False; lines.append('⚠ సౌండ్ లేదు.')
    else:
        i, tp = loudness(path)
        if i is not None and abs(i + 14) > 2:
            lines.append(f'• సౌండ్ స్థాయి {i:.1f} LUFS (సరైనది -14 దగ్గర).')
        if tp is not None and tp > -1.0:
            ok = False; lines.append(f'⚠ సౌండ్ గరిష్టం {tp:.1f} dB – పగిలే ప్రమాదం.')
        sil = [(a, b) for a, b in spans(path, af='silencedetect=n=-45dB:d=2.5') if b is None or b - a >= 2.5]
        sil = [(a, b) for a, b in sil if a < p['dur'] - 6]   # the end card is meant to be quiet
        if sil:
            lines.append('⚠ పూర్తి నిశ్శబ్దం: ' + ', '.join(f'{a:.0f}–{(b or p["dur"]):.0f} సె' for a, b in sil[:5])
                         + ' – ఆ భాగానికి వాయిస్ / సంగీతం ఉందో చూడండి.')
    # picture
    black = [(a, b) for a, b in spans(path, vf='blackdetect=d=0.5:pix_th=0.08', key='black')]
    if black:
        lines.append('⚠ నల్ల తెర: ' + ', '.join(f'{a:.1f}–{b:.1f} సె' for a, b in black[:5]) + ' – ఆ క్లిప్ ఇమేజ్ / వీడియో పెట్టారా?')
    frozen = [(a, b) for a, b in spans(path, vf='freezedetect=n=0.002:d=6', key='lavfi.freezedetect.freeze') if b is None or b - a >= 6]
    if frozen:
        lines.append('• కదలని చిత్రం 6 సె పైగా: ' + ', '.join(f'{a:.0f}–{(b or p["dur"]):.0f} సె' for a, b in frozen[:5])
                     + ' – అక్కడ వీడియో లేదా జూమ్ కదలిక పెడితే బాగుంటుంది.')
    # looks like an earlier video of the same kind?
    fp = fingerprints(path, p['dur'])
    db = {}
    if os.path.exists(FP):
        try:
            db = json.load(open(FP, encoding='utf-8'))
        except ValueError:
            db = {}
    worst = max(((similar(fp, v['fp']), k) for k, v in db.items() if k != name and v.get('kind') == kind), default=(0.0, ''))
    if worst[0] >= 0.4:
        ok = False
        lines.append(f'⚠ ఈ వీడియోలో {worst[0] * 100:.0f}% చిత్రాలు ఇంతకు ముందు చేసిన {worst[1]} లో ఉన్నవే – YouTube దీన్ని '
                     '"మళ్ళీ వాడిన కంటెంట్" గా చూడవచ్చు. కొత్త చిత్రాలు లేదా వేరే క్రమం వాడండి.')
    else:
        lines.append('✓ చిత్రాలు మీ ఇతర వీడియోలకు భిన్నంగా ఉన్నాయి.')
    db[name] = {'kind': kind, 'fp': fp}
    os.makedirs(OUT, exist_ok=True)
    json.dump(db, open(FP, 'w', encoding='utf-8'))
    lines.append('📋 అప్‌లోడ్ ముందు: AI చిత్రాలు నిజంలా కనిపిస్తే "Altered or synthetic content" టిక్ చేయండి; '
                 + ('పిల్లల సిరీస్ అయితేనే "Made for kids".' if short else 'అధ్యాయాలు (chapters) వివరణలో ఉన్నాయి.'))
    print(json.dumps({'ok': ok, 'lines': lines}, ensure_ascii=False))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args[0], '--no-master' not in sys.argv)
