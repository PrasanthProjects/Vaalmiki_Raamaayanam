"""Build publish/sundarakanda_parayanam.html: the Sundarakanda Parayanam section page.

Reads the Suno song file(s) in Sundarakanda_Parayanam/songs/ and shows, for each song,
copy-ready lyrics + style (exactly the SUNO_*.txt text), the chanted Valmiki slokas with
their sources, which slokas each charanam follows, and the parayanam credit plan.
Run:  python sundara_page.py
"""
import json, re
from pathlib import Path

import live_style as LS
from soften import soften

HERE = Path(__file__).resolve().parent
# the long videos' 9:16 -> 16:9 swap (Long_Videos/_tools/long_build.py WIDE)
WIDE = [('Vertical 9:16 cinematic still image, 1080x1920, main subject in the centre safe area.',
         'Cinematic 16:9 still image, 1920x1080, main subject well framed.'),
        ('Vertical 9:16 YouTube Shorts thumbnail key art, single still image, 1080x1920.',
         '16:9 YouTube video thumbnail key art, single still image, 1920x1080.'),
        ('Keep the top 35% of the frame a clean dark gradient or soft sky with no important detail (space for a '
         'headline) and the bottom 12% calm and plain (space for a small line).',
         'Keep the left 40% of the frame a clean dark gradient or soft sky with no important detail (space for a '
         'headline); the main subject on the right.'),
        ('vertical 9:16', '16:9'), ('Vertical 9:16', '16:9'), ('9:16', '16:9'), ('1080x1920', '1920x1080'),
        ('centre safe area', 'frame')]
SONG_CAM = 'very slow, steady push-in'


def wide(text):
    for a, b in WIDE:
        text = text.replace(a, b)
    return text


def keys_of(s):
    return [k.strip() for k in s.split(',') if k.strip()]


def pictures(scenes, thumbpic):
    """Each song section's picture in the Shorts' own prompt style: a 16:9 still for the full song video, a 9:16
    still for song Shorts, and a gentle video prompt that animates that picture (the video follows the image)."""
    out, used = [], set()
    for sec, keys, frame, light in scenes:
        ks = keys_of(keys)
        used.update(LS.ref_keys(ks))
        frame, light = frame.rstrip('. ') + '.', light.rstrip('. ') + '.'
        tall = soften(LS.still(ks, frame, light, motion='', cam=SONG_CAM))
        vid = soften(LS.start_video(ks, frame, 'gentle natural movement', SONG_CAM, light, False))
        out.append({'sec': sec, 'refs': LS.ref_keys(ks), 'frame': frame,
                    'wide': wide(tall), 'tall': tall, 'video': wide(vid), 'videoTall': vid})
    thumb = None
    if thumbpic:
        tk, tf, tl = thumbpic
        t, trefs = LS.thumb(keys_of(tk), tf.rstrip('. ') + '.', tl.rstrip('. ') + '.')
        thumb = {'wide': soften(wide(t)), 'tall': soften(t), 'refs': trefs}
        used.update(trefs)
    return {'scenes': out, 'thumb': thumb, 'refs': LS.library(used)}
SONGS = HERE.parent / 'Sundarakanda_Parayanam' / 'songs'
OUT = HERE / 'publish' / 'sundarakanda_parayanam.html'


def read_song(path):
    src = path.read_text(encoding='utf-8')
    head, lyr = src.split('\n---\n', 1)
    meta, sources, scenes, thumbpic = {}, [], [], None
    for l in head.splitlines():
        k, _, v = l.partition(': ')
        if k == 'SOURCE':
            sources.append([x.strip() for x in v.split('|', 2)])
        elif k == 'SCENE':
            scenes.append([x.strip() for x in v.split('|', 3)])
        elif k == 'THUMBPIC':
            thumbpic = [x.strip() for x in v.split('|', 2)]
        elif k:
            meta[k] = v
    chants = []
    for m in re.finditer(r'\[శ్లోక గానం \|[^|]*\| (\d+) \|[^\]]*\]\n(.+?)\n(.+?)\n', lyr):
        ref = f"సుందరకాండ {meta['SARGA']}.{m.group(1)}"
        mean = next((s[2] for s in sources if s[0].startswith('శ్లోక గానం') and s[1] == ref), '')
        chants.append({'ref': ref, 'l1': m.group(2), 'l2': m.group(3), 'mean': mean})
    # the copy-ready SUNO_*.txt files belong to song 1 only; later songs use their own text
    first = path.name == 'sundara_sarga_001_song.txt'
    lyrics_file = SONGS / ('SUNO_lyrics.txt' if first else '_none_')
    style_file = SONGS / ('SUNO_style.txt' if first else '_none_')
    lyrics = lyrics_file.read_text(encoding='utf-8').strip() if lyrics_file.exists() else lyr.strip()
    style = style_file.read_text(encoding='utf-8').strip() if style_file.exists() else meta['STYLE']
    return {'title': meta['TITLE'], 'sarga': meta['SARGA'], 'gist': meta['GIST'], 'raga': meta['RAGA'],
            'tala': meta['TALA'], 'bpm': meta['BPM'], 'length': meta['LENGTH'], 'style': style,
            'exclude': meta['EXCLUDE'], 'lyrics': lyrics, 'chants': chants, 'pics': pictures(scenes, thumbpic),
            'sources': [s for s in sources if not s[0].startswith('శ్లోక గానం')]}


TEMPLATE = r'''<title>సుందరకాండ పారాయణం</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Ramabhadra&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Serif+Telugu:wght@500;700&display=swap">
<style>
/* One reading column: each song (copy-ready for Suno), its chanted slokas, the charanam sources, then the parayanam plan. */
:root {
  --bg: #F6F1E8; --surface: #FFFDF8; --sunk: #EDE4D4; --ink: #24190F; --muted: #6E5D4B; --line: #E0D3BE;
  --accent: #B53A0B; --sea: #1E4E79; --sea-soft: #E1EBF5; --ok: #2F6B45; --on-accent: #FFFDF8;
  --display: "Ramabhadra", "Noto Sans Telugu", "Nirmala UI", sans-serif;
  --body: "Noto Sans Telugu", "Nirmala UI", "Gautami", system-ui, sans-serif;
  --verse: "Noto Serif Telugu", "Noto Sans Telugu", "Nirmala UI", serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #17120C; --surface: #211A12; --sunk: #2C2318; --ink: #F1E7D6; --muted: #B5A48C; --line: #3B3022;
  --accent: #F2864A; --sea: #8CB8E6; --sea-soft: #182A3C; --ok: #7CCB98; --on-accent: #17120C; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #17120C; --surface: #211A12; --sunk: #2C2318; --ink: #F1E7D6; --muted: #B5A48C; --line: #3B3022;
  --accent: #F2864A; --sea: #8CB8E6; --sea-soft: #182A3C; --ok: #7CCB98; --on-accent: #17120C; color-scheme: dark }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.7 var(--body); }
.wrap { max-width: 760px; margin: 0 auto; padding-block: 28px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 28px; }
header { display: grid; gap: 6px; }
.eyebrow { font-size: 13px; letter-spacing: .04em; color: var(--sea); font-weight: 600; }
h1 { font-family: var(--display); font-weight: 400; font-size: clamp(30px, 7vw, 44px); line-height: 1.2; margin: 0; text-wrap: balance; }
.lede { margin: 0; color: var(--muted); max-width: 62ch; }
h2 { font-family: var(--display); font-weight: 400; font-size: 23px; line-height: 1.35; margin: 0; text-wrap: balance; }
h3 { font-size: 16px; margin: 6px 0 0; }
section { display: grid; gap: 12px; }
.song { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px; display: grid; gap: 14px; }
.song .name { font-family: var(--display); font-weight: 400; font-size: 26px; margin: 0; color: var(--accent); line-height: 1.3; }
.facts { display: flex; flex-wrap: wrap; gap: 6px; }
.fact { font-size: 13px; padding: 2px 10px; border-radius: 999px; background: var(--sea-soft); color: var(--sea); }
.gist { margin: 0; }
.box { display: grid; gap: 8px; }
.lab { font-size: 13px; letter-spacing: .03em; color: var(--muted); font-weight: 600; }
pre { margin: 0; white-space: pre-wrap; word-break: break-word; background: var(--sunk); border-radius: 10px; padding: 12px 14px;
  font: 15px/1.75 var(--body); max-height: 20em; overflow: auto; }
pre.small { font-size: 13.5px; max-height: 12em; }
.copy { justify-self: start; border: 0; border-radius: 10px; padding: 10px 20px; min-height: 44px; font: inherit; font-weight: 700; cursor: pointer;
  background: var(--accent); color: var(--on-accent); }
.copy.ok { background: var(--ok); }
.copy:focus-visible { outline: 2px solid var(--sea); outline-offset: 2px; }
.steps { margin: 0; padding-left: 1.3em; display: grid; gap: 2px; }
.verse { border-left: 3px solid var(--accent); background: var(--sunk); border-radius: 0 10px 10px 0; padding: 12px 16px; display: grid; gap: 6px; }
.verse .ref { font-size: 13px; color: var(--sea); font-weight: 600; }
.verse .sk { font-family: var(--verse); font-size: 18.5px; line-height: 1.8; }
.verse .mean { color: var(--muted); font-size: 15px; margin: 0; }
.src { margin: 0; padding-left: 1.2em; display: grid; gap: 6px; color: var(--muted); font-size: 14.5px; }
.src b { color: var(--ink); font-weight: 600; }
.tablewrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 15px; }
th, td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-weight: 600; color: var(--muted); font-size: 13.5px; }
td.n { font-variant-numeric: tabular-nums; white-space: nowrap; }
tr:last-child td { border-bottom: 0; }
.note { color: var(--muted); font-size: 14.5px; margin: 0; max-width: 62ch; }
.pics { display: grid; gap: 10px; }
.fold { border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
.fold summary { cursor: pointer; padding: 10px 14px; display: grid; gap: 2px; min-height: 44px; }
.fold summary .t { font-weight: 600; }
.fold summary .sub { color: var(--muted); font-size: 13.5px; line-height: 1.5; }
.fold summary:focus-visible { outline: 2px solid var(--sea); outline-offset: 2px; }
.foldbody { padding: 4px 14px 14px; display: grid; gap: 12px; }
.reflab { font-size: 13.5px; color: var(--sea); font-weight: 600; word-break: break-word; }
</style>
<div class="wrap">
  <header>
    <span class="eyebrow">శ్రీమద్వాల్మీకి రామాయణం · సుందరకాండ</span>
    <h1>సుందరకాండ పారాయణం</h1>
    <p class="lede">వాల్మీకి సుందరకాండ శ్లోకాలు మాత్రమే – పారాయణం, శ్లోకాల పాటలు. 68 సర్గలు, 2,772 శ్లోకాలు (IIT కాన్పూర్ వాల్మీకి పాఠం; గీతా ప్రెస్ సంఖ్యలు కొద్దిగా మారవచ్చు).</p>
  </header>
  <div id="songs" style="display:grid;gap:28px"></div>
  <section aria-labelledby="planh">
    <h2 id="planh">పారాయణం గొంతు (ElevenLabs) – ఎంత అవుతుంది</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>ఎంత</th><th>క్రెడిట్‌లు</th><th>నిడివి (Vagmin)</th></tr></thead>
      <tbody>
        <tr><td>1 శ్లోకం</td><td class="n">~100</td><td class="n">~9 సె.</td></tr>
        <tr><td>100 శ్లోకాలు</td><td class="n">~10,600</td><td class="n">~15 ని.</td></tr>
        <tr><td>సర్గ 1 మొత్తం (201 శ్లోకాలు)</td><td class="n">~21,300</td><td class="n">~30 ని.</td></tr>
        <tr><td>సుందరకాండ మొత్తం (2,772)</td><td class="n">~3,06,500</td><td class="n">~7 గం.</td></tr>
      </tbody>
    </table></div>
    <p class="note">పారాయణం గొంతు ఇంకా తయారు చేయలేదు – మీరు చెప్పినట్లు క్రెడిట్‌లు వాడలేదు. ప్రయోగాలు (సర్గ 1 శ్లోకాలు 1–10 రెండు గొంతుల్లో; శ్లోకం 1.1 భజన సంగీతంతో) మీ కంప్యూటర్‌లో Valmiki_Ramayanam\Sundarakanda_Parayanam ఫోల్డర్‌లో ఉన్నాయి.</p>
  </section>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function () {
  const SONGS = JSON.parse(document.getElementById('data').textContent);
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  function copyBtn(label, text, pre) {
    const b = el('button', 'copy', label); b.type = 'button';
    b.addEventListener('click', () => {
      const done = () => { b.textContent = 'కాపీ అయింది ✓'; b.classList.add('ok'); setTimeout(() => { b.textContent = label; b.classList.remove('ok'); }, 1600); };
      const fallback = () => { const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'ఎంచుకున్నాం – కాపీ చేయండి'; };
      try { navigator.clipboard.writeText(text).then(done, fallback); } catch (e) { fallback(); }
    });
    return b;
  }
  function box(label, text, cls, btn) {
    const d = el('div', 'box'); const p = el('pre', cls || '', text);
    d.append(el('span', 'lab', label), p, copyBtn(btn, text, p)); return d;
  }
  function fold(title, sub, open) {
    const d = el('details', 'fold'); if (open) d.open = true;
    const sm = el('summary'); sm.append(el('span', 't', title)); if (sub) sm.append(el('span', 'sub', sub));
    d.append(sm); const body = el('div', 'foldbody'); d.append(body); return [d, body];
  }
  function picBlock(P) {
    const wrap = el('div', 'pics');
    wrap.append(el('h3', '', 'బొమ్మలు, వీడియోలు (Flow)'));
    wrap.append(el('p', 'note', 'ముందు కింది reference బొమ్మలు చేసి Flow లో ingredients గా పెట్టండి. ప్రతి భాగానికి: పూర్తి పాట వీడియోకు 16:9 బొమ్మ, పాట Shorts కు 9:16 బొమ్మ; ఆ బొమ్మను మెల్లగా కదిలించే వీడియో prompt.'));
    if (P.refs.length) {
      const [d, b] = fold('Reference బొమ్మలు', P.refs.length + ' బొమ్మలు', false);
      P.refs.forEach((r) => { b.append(el('div', 'reflab', r.label + ' · ' + r.key)); b.append(box('Reference prompt', r.prompt, 'small', '📋 కాపీ')); });
      wrap.append(d);
    }
    if (P.thumb) {
      const [d, b] = fold('Thumbnail', 'refs: ' + P.thumb.refs.join(', '), false);
      b.append(box('16:9 thumbnail (పూర్తి పాట)', P.thumb.wide, 'small', '📋 16:9 కాపీ'));
      b.append(box('9:16 thumbnail (Shorts)', P.thumb.tall, 'small', '📋 9:16 కాపీ'));
      wrap.append(d);
    }
    P.scenes.forEach((c, i) => {
      const [d, b] = fold((i + 1) + '. ' + c.sec, c.frame, false);
      b.append(el('div', 'reflab', 'Ingredients: ' + (c.refs.join(', ') || '—')));
      b.append(box('16:9 బొమ్మ (పూర్తి పాట)', c.wide, 'small', '📋 16:9 బొమ్మ కాపీ'));
      b.append(box('9:16 బొమ్మ (Shorts)', c.tall, 'small', '📋 9:16 బొమ్మ కాపీ'));
      b.append(box('16:9 వీడియో (బొమ్మను కదిలించడానికి)', c.video, 'small', '📋 16:9 వీడియో కాపీ'));
      b.append(box('9:16 వీడియో', c.videoTall, 'small', '📋 9:16 వీడియో కాపీ'));
      wrap.append(d);
    });
    return wrap;
  }
  const root = document.getElementById('songs');
  SONGS.forEach((s, i) => {
    const sec = el('section'); const hid = 'song' + (i + 1);
    const h = el('h2', '', 'పాట ' + (i + 1) + ' · సర్గ ' + s.sarga); h.id = hid; sec.setAttribute('aria-labelledby', hid);
    const card = el('div', 'song');
    card.append(el('p', 'name', s.title));
    const f = el('div', 'facts');
    [s.length + ' నిమిషాలు', 'రాగం ' + s.raga.split('(')[0].trim(), s.tala, s.bpm + ' bpm'].forEach((x) => f.append(el('span', 'fact', x)));
    card.append(f, el('p', 'gist', s.gist));
    const how = el('div', 'box'); how.append(el('span', 'lab', 'Suno లో ఎలా చేయాలి'));
    const ol = el('ol', 'steps');
    ['Create → Custom మోడ్ ఎంచుకోండి (Instrumental ఆఫ్).', 'Lyrics లో పాట సాహిత్యం పేస్ట్ చేయండి.', 'Style of Music లో Suno స్టైల్ పేస్ట్ చేయండి.', 'More Options → Exclude Styles లో చివరి పెట్టెలోని మాటలు.'].forEach((x) => ol.append(el('li', '', x)));
    how.append(ol); card.append(how);
    card.append(box('పాట సాహిత్యం (Lyrics)', s.lyrics, '', '📋 సాహిత్యం కాపీ'));
    card.append(box('Suno స్టైల్ (Style of Music)', s.style, 'small', '📋 స్టైల్ కాపీ'));
    card.append(box('Exclude Styles', s.exclude, 'small', '📋 కాపీ'));
    card.append(el('h3', '', 'పాటలో పారాయణంగా వచ్చే వాల్మీకి శ్లోకాలు'));
    s.chants.forEach((c) => {
      const v = el('div', 'verse'); const sk = el('div', 'sk'); sk.append(el('div', '', c.l1), el('div', '', c.l2));
      v.append(el('span', 'ref', c.ref), sk); if (c.mean) v.append(el('p', 'mean', c.mean)); card.append(v);
    });
    card.append(el('h3', '', 'ప్రతి భాగం ఏ శ్లోకాల నుండి'));
    const ul = el('ul', 'src');
    s.sources.forEach(([part, ref, text]) => { const li = el('li'); li.append(el('b', '', part + ' · ' + ref + ': '), document.createTextNode(text || '')); ul.append(li); });
    card.append(ul);
    if (s.pics && s.pics.scenes.length) card.append(picBlock(s.pics));
    sec.append(h, card); root.append(sec);
  });
})();
</script>
'''


def main():
    songs = [read_song(p) for p in sorted(SONGS.glob('sundara_sarga_*_song.txt'))]
    blob = json.dumps(songs, ensure_ascii=False).replace('</', '<\\/')
    OUT.write_text(TEMPLATE.replace('__DATA__', blob), encoding='utf-8', newline='\n')
    for s in songs:
        print(s['title'], '| chants', [c['ref'] for c in s['chants']], '| meanings', all(c['mean'] for c in s['chants']),
              '| sources', len(s['sources']), '| lyrics', len(s['lyrics']))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
