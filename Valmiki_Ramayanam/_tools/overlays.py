"""On-screen śloka cards for the Shorts: transparent 1080x1920 PNGs to lay over the clips in the editor.

  python overlays.py 1_Bala_Kanda 1          (all ślokas of the sarga)
  python overlays.py 1_Bala_Kanda 1 53       (one śloka)

For every śloka that has data/…/multilang_*.txt:
  • one card per half of the śloka, shown while it is recited: Telugu (easy-reading form), Devanagari, IAST;
  • word cards for the తాత్పర్యం part: each word in the three scripts with its Telugu, Hindi and English meaning.
Writes <kanda>/Sarga_NNN/overlays/Sloka_NNN/NN_<what>_<start>-<end>.png and overlays/Sloka_NNN.txt (the timings).
Drawn by Edge/Chrome in headless mode, which joins Telugu and Devanagari letters correctly (Pillow here cannot).
"""
import glob
import html
import json
import os
import re
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import build as B  # noqa: E402

W, H = 1080, 1920
BROWSERS = [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Google\Chrome\Application\chrome.exe']
SLOKA_SLOTS = [(4, 10), (10, 15)]   # build.SLOTS 1–2: the recitation
WORDS_SPAN = (15, 31)               # build.SLOTS 3–4: the తాత్పర్యం clips
MAX_CARDS = 5                       # at least ~3 s on screen for each word card

CSS = """
*{box-sizing:border-box;margin:0}
html,body{background:transparent;width:%dpx}
.page{position:relative;width:%dpx;height:%dpx;overflow:hidden}
.card{position:absolute;left:44px;right:150px;bottom:360px;padding:30px 36px 34px;border-radius:30px;
 background:rgba(24,12,4,.74);border:3px solid #d9a93c;box-shadow:0 8px 40px rgba(0,0,0,.45)}
.chip{display:inline-block;font:600 26px 'Nirmala UI','Segoe UI';color:#2a1500;background:#e9b949;
 padding:4px 18px;border-radius:40px;margin-bottom:18px}
.te{font:700 50px/1.32 'Nirmala UI';color:#ffe39a}
.dev{font:600 42px/1.36 'Nirmala UI';color:#fff;margin-top:12px}
.ia{font:italic 400 35px/1.35 'Segoe UI';color:#f1e3c8;margin-top:10px}
.w{margin-top:6px}
.w + .w{border-top:2px solid rgba(233,185,73,.45);margin-top:18px;padding-top:16px}
.wte{font:700 46px/1.3 'Nirmala UI';color:#ffe39a}
.wsub{font:500 32px/1.35 'Nirmala UI','Segoe UI';color:#f1e3c8;margin-top:4px}
.wsub i{font-family:'Segoe UI'}
.m{display:flex;gap:16px;align-items:baseline;margin-top:10px;font:500 34px/1.36 'Nirmala UI','Segoe UI';color:#fff}
.m b{flex:0 0 auto;font:700 22px 'Segoe UI','Nirmala UI';color:#2a1500;background:#f4d27a;border-radius:10px;
 padding:3px 10px;position:relative;top:-4px}
""" % (W, W, H)


def mmss(s):
    return f'{int(s) // 60}m{s % 60:04.1f}s'.replace('.', '_')


def data_for(kanda_dir, sarga):
    """Each śloka with the parts the cards show (only ślokas that already have Hindi and English meanings)."""
    data = os.path.join(TOOLS, 'data', kanda_dir, f'Sarga_{sarga:03d}')
    verses = json.load(open(os.path.join(data, 'verses.json'), encoding='utf-8'))
    pps = {n: body.split('తాత్పర్యం\n', 1)[0].replace('ప్రతిపదార్థం\n', '', 1).strip()
           for n, body in B.blocks(os.path.join(data, 'meanings_*.txt'))}
    multi = {n: dict(l.split(': ', 1) for l in body.split('\n') if ': ' in l)
             for n, body in B.blocks(os.path.join(data, 'multilang_*.txt'))}
    B.honor.DISCIPLE_BHARADWAJA = kanda_dir.startswith('1_')
    hon = lambda t: B.honor.Honorer(quotes=False)(t)
    out = []
    for n, lines in verses:
        if n not in multi:
            continue
        text = re.sub(r'  +', ' ', '\n'.join(lines))
        for a, b in B.FIX.get((kanda_dir, sarga, n), []):
            text = text.replace(a, b)
        ls = text.split('\n')
        ls[-1] = ls[-1].rstrip(' ।॥') + f' ॥ {n} ॥'
        rows = [l[2:] if l.startswith(('- ', '• ')) else l for l in pps[n].split('\n') if l.startswith(('- ', '• '))]
        keys = [r.split(': ', 1)[0] for r in rows]
        te_mean = [r.split(': ', 1)[1] for r in hon('\n'.join(rows)).split('\n')]
        m = multi[n]
        hiw = [x.strip() for x in m['HIW'].split(' | ')]
        enw = [x.strip() for x in m['ENW'].split(' | ')]
        assert len(keys) == len(te_mean) == len(hiw) == len(enw), f'śloka {n}: word counts differ'
        out.append({'n': n, 'lines': ls, 'words': list(zip(keys, te_mean, hiw, enw))})
    return out


def groups(words):
    """Words per card: one each, two when there are more words than cards."""
    k = min(len(words), MAX_CARDS)
    size, extra = divmod(len(words), k)
    out, i = [], 0
    for c in range(k):
        j = i + size + (1 if c < extra else 0)
        out.append(words[i:j])
        i = j
    return out


def cards(s, kanda_te, sarga):
    e = html.escape
    half = (len(s['lines']) + 1) // 2
    parts = [s['lines'][:half], s['lines'][half:]]
    out = []
    for i, (part, (a, b)) in enumerate(zip(parts, SLOKA_SLOTS), 1):
        body = (f"<div class=chip>శ్లోకం {s['n']} · श्लोक · Shloka</div>"
                + ''.join(f"<div class=te>{e(B.reading(l))}</div>" for l in part)
                + ''.join(f"<div class=dev>{e(B.te2dev(l))}</div>" for l in part)
                + ''.join(f"<div class=ia>{e(B.te2iast(l))}</div>" for l in part))
        out.append((f'{len(out) + 1:02d}_sloka{i}_{mmss(a)}-{mmss(b)}', a, b, body))
    gs = groups(s['words'])
    a0, b0 = WORDS_SPAN
    step = (b0 - a0) / len(gs)
    for i, g in enumerate(gs):
        a, b = a0 + i * step, a0 + (i + 1) * step
        body = f"<div class=chip>పదార్థం · शब्दार्थ · Word meaning  {i + 1}/{len(gs)}</div>" + ''.join(
            f"<div class=w><div class=wte>{e(B.reading(k))}</div>"
            f"<div class=wsub>{e(B.te2dev(k))} · <i>{e(B.te2iast(k))}</i></div>"
            f"<div class=m><b>తె</b><span>{e(te)}</span></div>"
            f"<div class=m><b>हि</b><span>{e(hi)}</span></div>"
            f"<div class=m><b>EN</b><span>{e(en)}</span></div></div>"
            for k, te, hi, en in g)
        out.append((f'{len(out) + 1:02d}_words{i + 1}_{mmss(a)}-{mmss(b)}', a, b, body))
    return out


def render(items, out_dir):
    """All cards of one śloka in one browser run (stacked pages), then cut into separate PNGs."""
    from PIL import Image
    browser = next(p for p in BROWSERS if os.path.exists(p))
    doc = ('<!doctype html><html><head><meta charset=utf-8><style>' + CSS + '</style></head><body>'
           + ''.join(f'<div class=page><div class=card>{body}</div></div>' for _, _, _, body in items)
           + '</body></html>')
    tmp = tempfile.mkdtemp()
    page, shot = os.path.join(tmp, 'cards.html'), os.path.join(tmp, 'cards.png')
    open(page, 'w', encoding='utf-8').write(doc)
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--default-background-color=00000000', f'--window-size={W},{H * len(items)}',
                    f'--screenshot={shot}', f'--user-data-dir={os.path.join(tmp, "profile")}', 'file:///' + page.replace('\\', '/')],
                   check=True, capture_output=True, timeout=120)
    img = Image.open(shot).convert('RGBA')
    assert img.size == (W, H * len(items)), img.size
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, '*.png')):
        os.remove(old)
    for i, (name, _, _, _) in enumerate(items):
        img.crop((0, i * H, W, (i + 1) * H)).save(os.path.join(out_dir, name + '.png'))


def secs(s):
    return f'{int(s) // 60}:{s % 60:04.1f}'


def main(kanda_dir, sarga, only=None):
    kanda_te = B.KANDAS[kanda_dir]
    base = os.path.join(B.ROOT, kanda_dir, f'Sarga_{sarga:03d}', 'overlays')
    done = 0
    for s in data_for(kanda_dir, sarga):
        if only and s['n'] != only:
            continue
        items = cards(s, kanda_te, sarga)
        name = f"Sloka_{s['n']:03d}"
        render(items, os.path.join(base, name))
        open(os.path.join(base, name + '.txt'), 'w', encoding='utf-8', newline='\n').write(
            f"{kanda_te} · సర్గ {sarga} · శ్లోకం {s['n']} – తెరపై కార్డులు (overlays/{name}/)\n\n"
            + '\n'.join(f"{secs(a)} – {secs(b)}  {nm}.png" for nm, a, b, _ in items) + '\n')
        done += 1
        print(name, len(items), 'cards', flush=True)
    print(f'{kanda_te} sarga {sarga}: overlays for {done} ślokas')


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else None)
