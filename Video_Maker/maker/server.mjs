// Video Maker page: http://localhost:3333
// Keeps each Short's clips, voice and music in media/<kanda>/Sarga_NNN/Sloka_NNN/ under fixed names
// (clip1 … clip7, voice or voice1 … voice4, music), tells the Remotion template their lengths,
// and renders the finished MP4 into out/ when asked.
import http from 'node:http';
import os from 'node:os';
import fs from 'node:fs';
import path from 'node:path';
import {spawn, execFile} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {makeTimeline, cues, HOOK, SLOKA, WORDS, MEANING, END} from '../src/timeline.ts';
import {makeMovieTimeline, movieCues} from '../src/movieTimeline.ts';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const MEDIA = path.join(ROOT, 'media');
const BRAND = path.join(ROOT, 'Branding'); // end_banner.png: the channel banner shown at the end of every Short
const MUSIC = path.join(ROOT, 'Music');
const SFX = path.join(ROOT, 'SFX');       // sound effects and scene backgrounds (src/data/sfx_prompts.json), used by every Short
const SFX_NAMES = () => {
  try { return Object.keys(JSON.parse(fs.readFileSync(path.join(DATA, 'sfx_prompts.json'), 'utf8')).sounds); } catch (e) { return []; }
};
// a sound's file is named plainly in SFX/ (whoosh.mp3), its slot is sfx_whoosh
const fileName = (slot) => (isSfx(slot) ? slot.slice(4) : slot);
const isSfx = (slot) => slot.startsWith('sfx_') && SFX_NAMES().includes(slot.slice(4));   // the shared background tracks: one per mood + a default, used by every Short
const OUT = path.join(ROOT, 'out');
const DATA = path.join(ROOT, 'src', 'data');
const PORT = +process.env.PORT || 3333;
const SLOTS = ['clip1', 'clip2', 'clip3', 'clip4', 'clip5', 'clip6', 'clip7',
  ...[1, 2, 3, 4, 5, 6, 7].flatMap((c) => [`clip${c}_2`, `clip${c}_3`]),   // up to 3 pictures or videos in one box
  'voice', 'voice1', 'voice2', 'voice3', 'voice4', 'music'];
const VIDEO = ['.mp4', '.mov', '.webm', '.m4v'];
const IMAGE = ['.png', '.jpg', '.jpeg', '.webp'];
const AUDIO = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'];
const TYPES = {'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm', '.m4v': 'video/mp4', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4',
  '.aac': 'audio/aac', '.ogg': 'audio/ogg', '.flac': 'audio/flac', '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.srt': 'application/x-subrip; charset=utf-8'};

const pad = (n) => String(n).padStart(3, '0');
// Shared music (media/ root): one default plus one track per mood; each śloka's mood is in src/data/music_moods.json.
const MOODS = ['calm', 'sad', 'heroic', 'mystery', 'joyful'];
const SHARED = ['music_default', ...MOODS.map((m) => 'music_' + m)];
const moodOf = (k, s, n) => {
  try { return JSON.parse(fs.readFileSync(path.join(DATA, 'music_moods.json'), 'utf8'))[`${k}_S${pad(s)}`][n] || 'calm'; }
  catch (e) { return 'calm'; }
};
// the four closing lines in the user's own voice (Branding/cta_1 … cta_4), one per Short (src/data … end.cta)
const CTAS = ['cta_1', 'cta_2', 'cta_3', 'cta_4'];
const ctaOf = (k, s, n) => {
  try { return (JSON.parse(fs.readFileSync(path.join(DATA, `${k}_S${pad(s)}.json`), 'utf8')).slokas.find((x) => x.n === +n) || {end: {}}).end.cta || 0; }
  catch (e) { return 0; }
};
const slotDir = (slot, k, s, n) => (slot === 'end_banner' || CTAS.includes(slot) ? BRAND : isSfx(slot) ? SFX : SHARED.includes(slot) ? MUSIC : slokaDir(k, s, n));
const slokaDir = (k, s, n) => path.join(MEDIA, k, `Sarga_${pad(s)}`, `Sloka_${pad(n)}`);
const safe = (k) => /^[0-9]_[A-Za-z]+_Kanda$/.test(k);

function findSlot(dir, slot) {
  if (!fs.existsSync(dir)) return null;
  const f = fs.readdirSync(dir).find((x) => path.parse(x).name === slot);
  return f ? path.join(dir, f) : null;
}

// ---- every audio file is levelled when it is dropped in, so all Shorts and films sound the same ----
// voices: YouTube loudness (-16 LUFS) with the low rumble cut; music: -15 LUFS (the Suno level the mix was tuned on);
// sound effects: -16 LUFS. The template's volumes then keep the same balance in every video.
function levelOf(slot) {
  if (/^(voice\d?|line\d|cta_\d)$/.test(slot)) return {lufs: -16, filter: 'highpass=f=70,'};
  if (/^(music|music_\w+|bgm)$/.test(slot)) return {lufs: -15, filter: ''};
  if (slot === 'fx' || slot.startsWith('sfx_')) return {lufs: -16, filter: ''};
  return null;
}
function levelAudio(file, slot) {
  const lv = levelOf(slot);
  if (!lv || !AUDIO.includes(path.extname(file).toLowerCase())) return Promise.resolve();
  const tmp = file + '.levelling' + path.extname(file);
  return new Promise((res) => {
    execFile('ffmpeg', ['-v', 'error', '-y', '-i', file, '-af', `${lv.filter}loudnorm=I=${lv.lufs}:TP=-1.5:LRA=11`, '-ar', '48000',
      ...(file.toLowerCase().endsWith('.wav') ? [] : ['-b:a', '192k']), tmp], (err) => {
      if (!err) { try { fs.renameSync(tmp, file); } catch (e) { try { fs.unlinkSync(tmp); } catch (e2) {} } }
      else { try { fs.unlinkSync(tmp); } catch (e) {} }
      res();
    });
  });
}

const durCache = new Map();
function duration(file) {
  const st = fs.statSync(file);
  const key = file + st.mtimeMs;
  if (durCache.has(key)) return Promise.resolve(durCache.get(key));
  return new Promise((res) => {
    execFile('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file], (err, out) => {
      const d = err ? null : parseFloat(out) || null;
      durCache.set(key, d);
      res(d);
    });
  });
}

async function entry(f) {
  const ext = path.extname(f).toLowerCase();
  const dirOf = path.dirname(f);
  const rel = dirOf === MUSIC ? 'music/' + path.basename(f) : dirOf === SFX ? 'sfx/' + path.basename(f)
    : dirOf === BRAND ? 'brand/' + encodeURIComponent(path.basename(f))
    : 'media/' + path.relative(MEDIA, f).split(path.sep).join('/');
  const st = fs.statSync(f);
  return {name: path.basename(f), url: `http://localhost:${PORT}/${rel}?v=${Math.round(st.mtimeMs)}`,
    video: VIDEO.includes(ext), dur: IMAGE.includes(ext) ? null : await duration(f), size: st.size};
}

// ---- movie mode (Valmiki Cinema): media/movie/<id>/shot_NNN/{clip,clip_2,clip_3,line1…line6,fx}, scene_NN/music ----
const MOVIE_SHOT_SLOTS = ['clip', 'clip_2', 'clip_3', 'clip_4', 'clip_5', 'clip_6', 'clip_7', 'clip_8',
  'line1', 'line2', 'line3', 'line4', 'line5', 'line6', 'fx', 'bgm'];
const movieSafe = (id) => /^[A-Za-z0-9_-]+$/.test(id || '');
// films: Valmiki Cinema (movie_*.json) and long videos (long_*.json, the full copies with prompts)
const filmFiles = () => fs.readdirSync(DATA).filter((x) => /^(movie|long)_.*\.json$/.test(x));
function movieData(id) {
  for (const f of filmFiles()) {
    const d = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
    if (d.id === id) return d;
  }
  return null;
}
const movieDir = (id) => path.join(MEDIA, 'movie', id);
const shotDir = (id, no) => path.join(movieDir(id), `shot_${pad(no)}`);
const sceneDir = (id, si) => path.join(movieDir(id), `scene_${String(si).padStart(2, '0')}`);
const movieCompId = (d) => (d.mode === 'long' ? d.id : `Cinema-${d.kandaEn}-${d.file.replace(/_/g, '-')}`);
async function movieMediaFor(id) {
  const d = movieData(id);
  const media = {shots: {}, scenes: {}, shared: {}};
  for (const sc of d.scenes) {
    const m = findSlot(sceneDir(id, sc.si), 'music');
    const vp = findSlot(sceneDir(id, sc.si), 'voice');   // a long video's recorded part
    if (m || vp) media.scenes[sc.si] = {...(m ? {music: await entry(m)} : {}), ...(vp ? {voice: await entry(vp)} : {})};
    for (const sh of sc.shots) {
      const dir = shotDir(id, sh.no);
      if (!fs.existsSync(dir)) continue;
      const o = {};
      for (const slot of MOVIE_SHOT_SLOTS) {
        const f = findSlot(dir, slot);
        if (f) o[slot] = await entry(f);
      }
      media.shots[sh.no] = o;
    }
  }
  for (const x of SFX_NAMES()) {
    const f = findSlot(SFX, x);
    if (f) media.shared['sfx_' + x] = await entry(f);
  }
  // a long video's part with no music of its own plays its mood's track from Music/ (else the default)
  if (d.mode === 'long') {
    for (const sc of d.scenes) {
      if (media.scenes[sc.si]?.music || sc.shots.every((x) => x.bumper)) continue;
      const f = findSlot(MUSIC, 'music_' + (sc.mood || 'calm')) || findSlot(MUSIC, 'music_default');
      if (f) media.scenes[sc.si] = {...(media.scenes[sc.si] || {}), music: {...(await entry(f)), auto: true}};
    }
  }
  // the long-video banner (16:9) if there is one, else the Shorts banner
  const intro = findSlot(BRAND, 'channel_intro');   // the long videos' channel intro clip, with its own sound
  if (intro) media.shared.intro = await entry(intro);
  const wide = findSlot(BRAND, 'end_banner_wide');
  const banner = wide || findSlot(BRAND, 'end_banner');
  if (banner) media.shared.banner = {...(await entry(banner)), wide: !!wide};
  return media;
}
// ---- presenter mode (user on camera + pictures): media/presenter/<id>/seg_NNN/{cam,voice,pic,pic_2,pic_3}, layouts.json ----
const PRES_SLOTS = ['cam', 'voice', 'pic', 'pic_2', 'pic_3'];
const presFiles = () => fs.readdirSync(DATA).filter((x) => /^presenter_.*\.json$/.test(x));
function presenterData(id) {
  for (const f of presFiles()) {
    const d = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
    if (d.id === id) return d;
  }
  return null;
}
const presDir = (id) => path.join(MEDIA, 'presenter', id);
const segDir = (id, no) => path.join(presDir(id), `seg_${pad(no)}`);
const presLayouts = (id) => { try { return JSON.parse(fs.readFileSync(path.join(presDir(id), 'layouts.json'), 'utf8')); } catch (e) { return {}; } };
async function presenterMediaFor(id) {
  const d = presenterData(id);
  const media = {segs: {}, layouts: presLayouts(id), shared: {}};
  for (const sg of d.segments) {
    const dir = segDir(id, sg.no);
    if (!fs.existsSync(dir)) continue;
    const o = {};
    for (const slot of PRES_SLOTS) {
      const f = findSlot(dir, slot);
      if (f) o[slot] = await entry(f);
    }
    media.segs[sg.no] = o;
  }
  for (const m of [...MOODS.map((x) => 'music_' + x), 'music_default']) {
    const f = findSlot(MUSIC, m);
    if (f) media.shared[m] = await entry(f);
  }
  for (const x of SFX_NAMES()) {   // whoosh, boom, shimmer for the cuts; the rest when needed
    const f = findSlot(SFX, x);
    if (f) media.shared['sfx_' + x] = await entry(f);
  }
  const intro = findSlot(BRAND, 'channel_intro');
  if (intro) media.shared.intro = await entry(intro);
  const banner = findSlot(BRAND, 'end_banner_wide') || findSlot(BRAND, 'end_banner');
  if (banner) media.shared.banner = await entry(banner);
  return media;
}

async function movieSrt(id, base) {
  const d = movieData(id);
  const tl = makeMovieTimeline(d, await movieMediaFor(id));
  const text = movieCues(d, tl).map((c, i) => `${i + 1}\n${stamp(c.start)} --> ${stamp(c.end)}\n${c.text}\n`).join('\n');
  fs.mkdirSync(OUT, {recursive: true});
  fs.writeFileSync(path.join(OUT, `${base}.srt`), '\ufeff' + text, 'utf8');
}

async function mediaFor(k, s, n) {
  const dir = slokaDir(k, s, n);
  const media = {};
  const slots = [...SLOTS.map((x) => [x, dir]), ...SHARED.map((x) => [x, MUSIC]), ...SFX_NAMES().map((x) => ['sfx_' + x, SFX]), ...CTAS.map((x) => [x, BRAND])];
  for (const [slot, d] of slots) {
    const f = findSlot(d, fileName(slot));
    if (!f) continue;
    const ext = path.extname(f).toLowerCase();
    const dirOf = path.dirname(f);
    const rel = dirOf === MUSIC ? 'music/' + path.basename(f) : dirOf === SFX ? 'sfx/' + path.basename(f)
      : dirOf === BRAND ? 'brand/' + encodeURIComponent(path.basename(f)) : 'media/' + path.relative(MEDIA, f).split(path.sep).join('/');
    const st = fs.statSync(f);
    media[slot] = {name: path.basename(f), url: `http://localhost:${PORT}/${rel}?v=${Math.round(st.mtimeMs)}`,
      video: VIDEO.includes(ext), dur: IMAGE.includes(ext) ? null : await duration(f), size: st.size};
  }
  const banner = findSlot(BRAND, 'end_banner');
  if (banner) media.banner = {name: path.basename(banner), video: false, dur: null,
    url: `http://localhost:${PORT}/brand/${encodeURIComponent(path.basename(banner))}?v=${Math.round(fs.statSync(banner).mtimeMs)}`};
  // the music this Short uses: its own track, else its mood's track, else the default
  const mood = moodOf(k, s, n);
  media.mood = mood;
  media.bgm = media.music || media['music_' + mood] || media.music_default || null;
  const c = ctaOf(k, s, n);
  media.ctaNo = c;
  media.cta = c ? media['cta_' + c] || null : null;
  return media;
}

function sendFile(req, res, file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return send(res, 404, 'not found');
  const size = fs.statSync(file).size;
  const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
  const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
  const head = {'Content-Type': type, 'Accept-Ranges': 'bytes', 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-cache'};
  if (range) {
    const a = range[1] ? +range[1] : 0;
    const b = range[2] ? +range[2] : size - 1;
    res.writeHead(206, {...head, 'Content-Range': `bytes ${a}-${b}/${size}`, 'Content-Length': b - a + 1});
    fs.createReadStream(file, {start: a, end: b}).pipe(res);
  } else {
    res.writeHead(200, {...head, 'Content-Length': size});
    fs.createReadStream(file).pipe(res);
  }
}

function send(res, code, body) {
  const json = typeof body !== 'string';
  res.writeHead(code, {'Content-Type': json ? 'application/json' : 'text/plain; charset=utf-8', 'Access-Control-Allow-Origin': '*'});
  res.end(json ? JSON.stringify(body) : body);
}

// ---- YouTube captions: the same timing the video uses ----
const stamp = (x) => {
  const ms = Math.max(0, Math.round(x * 1000));
  const p2 = (v, n = 2) => String(v).padStart(n, '0');
  return `${p2(Math.floor(ms / 3600000))}:${p2(Math.floor(ms / 60000) % 60)}:${p2(Math.floor(ms / 1000) % 60)},${p2(ms % 1000, 3)}`;
};
async function srtFor(k, s, n) {
  const d = JSON.parse(fs.readFileSync(path.join(DATA, `${k}_S${pad(s)}.json`), 'utf8'));
  const sl = d.slokas.find((x) => x.n === n);
  const tl = makeTimeline(await mediaFor(k, s, n));
  const sp = tl.speech;
  const out = [...cues(sl.hook.voice, sp[HOOK], 40)];
  const lines = sl.lines.map((l) => l.orig);
  const per = (sp[SLOKA].end - sp[SLOKA].start) / Math.max(1, lines.length);
  lines.forEach((l, i) => out.push({start: sp[SLOKA].start + i * per, end: sp[SLOKA].start + (i + 1) * per, text: l}));
  const meaning = tl.mode === 'full' ? {start: tl.parts[WORDS].end, end: sp[MEANING].end} : sp[MEANING];
  out.push(...cues(sl.meaning.voice, meaning, 40), ...cues(sl.end.voice, sp[END], 40));
  const text = out.map((c, i) => `${i + 1}\n${stamp(c.start)} --> ${stamp(c.end)}\n${c.text}\n`).join('\n');
  return {id: `${d.kandaEn}-S${pad(s)}-Sloka-${pad(n)}`, text};
}
async function writeSrt(k, s, n, base) {
  const {id, text} = await srtFor(k, s, n);
  fs.mkdirSync(OUT, {recursive: true});
  fs.writeFileSync(path.join(OUT, `${base || id}.srt`), '﻿' + text, 'utf8');
  return id;
}

// Put the finished video in out/. The old file may be locked (open in a player or the page, or OneDrive uploading it):
// then try a few times, and if it is still locked keep the new video under a time-stamped name instead of failing.
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function place(tmp, id) {
  const dest = path.join(OUT, `${id}.mp4`);
  for (let i = 0; i < 6; i++) {
    try {
      if (fs.existsSync(dest)) fs.unlinkSync(dest);
      try { fs.renameSync(tmp, dest); } catch (e) { fs.copyFileSync(tmp, dest); fs.unlinkSync(tmp); }
      return path.basename(dest);
    } catch (e) { await sleep(1000); }
  }
  const t = new Date();
  const alt = path.join(OUT, `${id}_${String(t.getHours()).padStart(2, '0')}${String(t.getMinutes()).padStart(2, '0')}.mp4`);
  try { fs.renameSync(tmp, alt); } catch (e) { fs.copyFileSync(tmp, alt); fs.unlinkSync(tmp); }
  return path.basename(alt);
}

// ---- rendering: one at a time ----
let job = {state: 'idle'};
function render(k, kandaEn, s, n) {
  const id = `${kandaEn}-S${pad(s)}-Sloka-${pad(n)}`;
  run(id, id, null, (base) => writeSrt(k, s, n, base));
}
function run(comp, id, frames, afterSrt) {
  fs.mkdirSync(OUT, {recursive: true});
  // render outside OneDrive (it locks files while uploading), then move the result into out/
  const tmpDir = path.join(os.tmpdir(), 'raamaayanam-video-maker');
  fs.mkdirSync(tmpDir, {recursive: true});
  const out = path.join(tmpDir, `${id}.mp4`);
  const cli = path.join(ROOT, 'node_modules', '@remotion', 'cli', 'remotion-cli.js');
  job = {state: 'running', id, progress: 0, log: '', file: path.basename(out), started: Date.now()};
  const args = [cli, 'render', 'src/index.ts', comp, out, ...(frames ? [`--frames=${frames}`] : [])];
  const p = spawn(process.execPath, args, {cwd: ROOT, env: {...process.env, FORCE_COLOR: '0'}});
  const onData = (b) => {
    const text = b.toString();
    job.log = (job.log + text).slice(-4000);
    const m = [...text.matchAll(/Rendered (\d+)\/(\d+)/g)].pop();
    if (m) job.progress = Math.round((100 * +m[1]) / +m[2]);
    if (/Encoded|Stitching/.test(text)) job.progress = Math.max(job.progress, 99);
  };
  p.stdout.on('data', onData);
  p.stderr.on('data', onData);
  p.on('close', async (code) => {
    if (code === 0) {
      try {
        job.file = await place(out, id);
        await afterSrt(job.file.replace(/\.mp4$/, '')).catch(() => {});
        // master the sound to YouTube's level and check the video before upload (tools/master_check.py)
        job.log += '\nసౌండ్ సరిచేసి, అప్‌లోడ్ చెక్ చేస్తున్నాం…';
        job.check = await new Promise((ok) => execFile('python', [path.join(ROOT, 'tools', 'master_check.py'), path.join(OUT, job.file)],
          {env: {...process.env, PYTHONIOENCODING: 'utf-8'}, maxBuffer: 4 << 20},
          (err, stdout) => { try { ok(JSON.parse(String(stdout).trim().split('\n').pop())); } catch (e) { ok({ok: false, lines: ['చెక్ చేయలేకపోయాం: ' + String(err || e).slice(0, 200)]}); } }));
        if (job.file !== `${id}.mp4`) job.note = 'పాత వీడియో తెరిచి ఉంది (ప్లేయర్ / OneDrive), అందుకే కొత్తది ఈ పేరుతో సేవ్ అయింది';
      } catch (e) {
        job.log += '\n' + String(e.message || e);
        code = 1;
      }
    }
    job.state = code === 0 ? 'done' : 'error';
    job.progress = code === 0 ? 100 : job.progress;
    job.seconds = Math.round((Date.now() - job.started) / 1000);
  });
}

const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, `http://localhost:${PORT}`);
    const q = Object.fromEntries(u.searchParams);
    const n = +q.n, s = +q.s, k = q.k;
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST', 'Access-Control-Allow-Headers': '*'});
      return res.end();
    }
    if (u.pathname === '/') return sendFile(req, res, path.join(ROOT, 'maker', 'index.html'));
    if (u.pathname === '/api/sargas') {
      const list = fs.readdirSync(DATA).filter((f) => /_S\d+\.json$/.test(f)).map((f) => {
        const d = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
        return {file: f, kanda: d.kanda, kandaEn: d.kandaEn, kandaTe: d.kandaTe, sarga: d.sarga};
      });
      return send(res, 200, list);
    }
    if (u.pathname === '/api/sarga' && safe(k)) {
      const d = JSON.parse(fs.readFileSync(path.join(DATA, `${k}_S${pad(s)}.json`), 'utf8'));
      const base = path.join(MEDIA, k, `Sarga_${pad(s)}`);
      d.have = {};
      for (const sl of d.slokas) {
        const dir = path.join(base, `Sloka_${pad(sl.n)}`);
        d.have[sl.n] = fs.existsSync(dir) ? fs.readdirSync(dir).map((x) => path.parse(x).name) : [];
        const mp4 = path.join(OUT, `${d.kandaEn}-S${pad(s)}-Sloka-${pad(sl.n)}.mp4`);
        if (fs.existsSync(mp4)) d.have[sl.n].push('_rendered');
      }
      return send(res, 200, d);
    }
    if (u.pathname === '/api/media' && safe(k)) return send(res, 200, {media: await mediaFor(k, s, n)});
    if (u.pathname === '/api/upload' && req.method === 'POST' && safe(k)) {
      const slot = q.slot;
      const ext = path.extname(q.name || '').toLowerCase();
      const ok = slot.startsWith('clip') ? [...VIDEO, ...IMAGE] : slot === 'end_banner' ? IMAGE : AUDIO;
      if (!(SLOTS.includes(slot) || SHARED.includes(slot) || CTAS.includes(slot) || isSfx(slot) || slot === 'end_banner') || !ok.includes(ext)) return send(res, 400, {error: `${ext || 'ఈ ఫైల్'} ఇక్కడ పనికిరాదు`});
      const dir = slotDir(slot, k, s, n);
      fs.mkdirSync(dir, {recursive: true});
      const old = findSlot(dir, fileName(slot));
      const tmp = path.join(dir, `.${slot}.uploading`);
      await new Promise((ok2, bad) => req.pipe(fs.createWriteStream(tmp)).on('finish', ok2).on('error', bad));
      if (old) fs.unlinkSync(old);
      fs.renameSync(tmp, path.join(dir, fileName(slot) + ext));
      await levelAudio(path.join(dir, fileName(slot) + ext), slot);
      return send(res, 200, {media: await mediaFor(k, s, n)});
    }
    if (u.pathname === '/api/remove' && req.method === 'POST' && safe(k)) {
      const f = findSlot(slotDir(q.slot, k, s, n), fileName(q.slot));
      if (f && (SLOTS.includes(q.slot) || SHARED.includes(q.slot) || CTAS.includes(q.slot) || isSfx(q.slot) || q.slot === 'end_banner')) fs.unlinkSync(f);
      return send(res, 200, {media: await mediaFor(k, s, n)});
    }
    if (u.pathname === '/api/render' && req.method === 'POST' && safe(k)) {
      if (job.state === 'running') return send(res, 409, {error: 'ఇంకో వీడియో తయారవుతోంది'});
      render(k, q.ke, s, n);
      return send(res, 200, job);
    }
    if (u.pathname === '/api/status') return send(res, 200, job);
    if (u.pathname === '/movie') return sendFile(req, res, path.join(ROOT, 'maker', 'movie.html'));
    if (u.pathname === '/api/movies') {
      const list = filmFiles().map((f) => {
        const d = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
        return {id: d.id, title: d.title, kandaEn: d.kandaEn, sarga: d.sarga, mode: d.mode || 'movie', file: d.file};
      });
      return send(res, 200, list);
    }
    if (u.pathname === '/presenter') return sendFile(req, res, path.join(ROOT, 'maker', 'presenter.html'));
    if (u.pathname === '/api/presenters') {
      return send(res, 200, presFiles().map((f) => { const d = JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8'));
        return {id: d.id, title: d.title, badge: d.badge, segments: d.segments.length}; }));
    }
    if (q.pid !== undefined) {
      const id = q.pid;
      if (!movieSafe(id) || !presenterData(id)) return send(res, 404, {error: 'not found'});
      const d = presenterData(id);
      if (u.pathname === '/api/presenter') {
        d.outputs = fs.existsSync(OUT) ? fs.readdirSync(OUT).filter((x) => x.startsWith(id) && x.endsWith('.mp4')) : [];
        return send(res, 200, d);
      }
      if (u.pathname === '/api/presenter-media') return send(res, 200, {media: await presenterMediaFor(id)});
      if (u.pathname === '/api/layout' && req.method === 'POST') {
        const l = presLayouts(id);
        if (q.layout && q.layout !== 'auto') l[q.seg] = q.layout; else delete l[q.seg];
        fs.mkdirSync(presDir(id), {recursive: true});
        fs.writeFileSync(path.join(presDir(id), 'layouts.json'), JSON.stringify(l, null, 1));
        return send(res, 200, {media: await presenterMediaFor(id)});
      }
      const ok = q.slot === 'voice' ? AUDIO : [...VIDEO, ...IMAGE];   // cam: your video, or just your photo
      if (u.pathname === '/api/upload' && req.method === 'POST') {
        const ext = path.extname(q.name || '').toLowerCase();
        if (!q.seg || !PRES_SLOTS.includes(q.slot) || !ok.includes(ext)) return send(res, 400, {error: `${ext || 'ఈ ఫైల్'} ఇక్కడ పనికిరాదు`});
        const dir = segDir(id, +q.seg);
        fs.mkdirSync(dir, {recursive: true});
        const old = findSlot(dir, q.slot);
        const tmp = path.join(dir, `.${q.slot}.uploading`);
        await new Promise((ok2, bad) => req.pipe(fs.createWriteStream(tmp)).on('finish', ok2).on('error', bad));
        if (old) fs.unlinkSync(old);
        fs.renameSync(tmp, path.join(dir, q.slot + ext));
        if (q.slot === 'voice') await levelAudio(path.join(dir, q.slot + ext), 'voice');
        return send(res, 200, {media: await presenterMediaFor(id)});
      }
      if (u.pathname === '/api/remove' && req.method === 'POST') {
        const f = q.seg && PRES_SLOTS.includes(q.slot) && findSlot(segDir(id, +q.seg), q.slot);
        if (f) fs.unlinkSync(f);
        return send(res, 200, {media: await presenterMediaFor(id)});
      }
      if (u.pathname === '/api/render' && req.method === 'POST') {
        if (job.state === 'running') return send(res, 409, {error: 'ఇంకో వీడియో తయారవుతోంది'});
        run(id, id, null, async () => {});
        return send(res, 200, job);
      }
      if (u.pathname === '/api/open' && req.method === 'POST') {
        const dir = q.seg ? segDir(id, +q.seg) : presDir(id);
        fs.mkdirSync(dir, {recursive: true});
        spawn('explorer.exe', [dir], {detached: true});
        return send(res, 200, {ok: true});
      }
    }
    if (q.movie !== undefined || q.id !== undefined) {
      const id = q.movie || q.id;
      if (!movieSafe(id) || !movieData(id)) return send(res, 404, {error: 'movie not found'});
      const d = movieData(id);
      if (u.pathname === '/api/movie') {
        d.outputs = fs.existsSync(OUT) ? fs.readdirSync(OUT).filter((x) => x.startsWith(movieCompId(d)) && x.endsWith('.mp4')) : [];
        return send(res, 200, d);
      }
      if (u.pathname === '/api/movie-media') return send(res, 200, {media: await movieMediaFor(id)});
      // where a movie slot lives: a shot's pictures, voice lines and sound, or a scene's music
      const target = () => {
        if (q.scene && q.slot === 'music') return {dir: sceneDir(id, +q.scene), name: 'music', ok: AUDIO};
        if (q.slot === 'end_banner_wide') return {dir: BRAND, name: 'end_banner_wide', ok: IMAGE};
        if (q.slot === 'channel_intro') return {dir: BRAND, name: 'channel_intro', ok: VIDEO};
        if (q.scene && q.slot === 'voice') return {dir: sceneDir(id, +q.scene), name: 'voice', ok: AUDIO};
        if (q.shot && MOVIE_SHOT_SLOTS.includes(q.slot))
          return {dir: shotDir(id, +q.shot), name: q.slot, ok: q.slot.startsWith('clip') ? [...VIDEO, ...IMAGE] : AUDIO};
        return null;
      };
      if (u.pathname === '/api/upload' && req.method === 'POST') {
        const tg = target();
        const ext = path.extname(q.name || '').toLowerCase();
        if (!tg || !tg.ok.includes(ext)) return send(res, 400, {error: `${ext || 'ఈ ఫైల్'} ఇక్కడ పనికిరాదు`});
        fs.mkdirSync(tg.dir, {recursive: true});
        const old = findSlot(tg.dir, tg.name);
        const tmp = path.join(tg.dir, `.${tg.name}.uploading`);
        await new Promise((ok2, bad) => req.pipe(fs.createWriteStream(tmp)).on('finish', ok2).on('error', bad));
        if (old) fs.unlinkSync(old);
        fs.renameSync(tmp, path.join(tg.dir, tg.name + ext));
        await levelAudio(path.join(tg.dir, tg.name + ext), tg.name);
        return send(res, 200, {media: await movieMediaFor(id)});
      }
      if (u.pathname === '/api/remove' && req.method === 'POST') {
        const tg = target();
        const f = tg && findSlot(tg.dir, tg.name);
        if (f) fs.unlinkSync(f);
        return send(res, 200, {media: await movieMediaFor(id)});
      }
      if (u.pathname === '/api/render' && req.method === 'POST') {
        if (job.state === 'running') return send(res, 409, {error: 'ఇంకో వీడియో తయారవుతోంది'});
        const comp = movieCompId(d);
        if (q.scene) {   // one scene only: its frames of the whole film
          const tl = makeMovieTimeline(d, await movieMediaFor(id));
          const sc = tl.scenes.find((x) => x.si === +q.scene);
          const a = Math.max(0, Math.round(sc.start * 30)), b = Math.round(sc.end * 30) - 1;
          const name = `${comp}-scene-${String(sc.si).padStart(2, '0')}`;
          run(comp, name, `${a}-${b}`, async () => {});
        } else run(comp, comp, null, (base) => movieSrt(id, base));
        return send(res, 200, job);
      }
      if (u.pathname === '/api/open' && req.method === 'POST') {
        const dir = q.shot ? shotDir(id, +q.shot) : movieDir(id);
        fs.mkdirSync(dir, {recursive: true});
        spawn('explorer.exe', [dir], {detached: true});
        return send(res, 200, {ok: true});
      }
    }
    if (u.pathname === '/api/music-prompts') return sendFile(req, res, path.join(DATA, 'music_prompts.json'));
    if (u.pathname === '/api/open' && req.method === 'POST') {
      const target = q.what === 'out' ? OUT : (safe(k) ? slokaDir(k, s, n) : MEDIA);
      fs.mkdirSync(target, {recursive: true});
      spawn('explorer.exe', [target], {detached: true});
      return send(res, 200, {ok: true});
    }
    if (u.pathname.startsWith('/sfx/')) {
      return sendFile(req, res, path.join(SFX, path.basename(decodeURIComponent(u.pathname.slice(5)))));
    }
    if (u.pathname === '/api/sfx-prompts') return sendFile(req, res, path.join(DATA, 'sfx_prompts.json'));
    if (u.pathname.startsWith('/brand/')) {
      return sendFile(req, res, path.join(BRAND, path.basename(decodeURIComponent(u.pathname.slice(7)))));
    }
    if (u.pathname.startsWith('/music/')) {
      return sendFile(req, res, path.join(MUSIC, path.basename(decodeURIComponent(u.pathname.slice(7)))));
    }
    if (u.pathname.startsWith('/media/')) {
      const f = path.join(MEDIA, decodeURIComponent(u.pathname.slice(7)));
      if (!f.startsWith(MEDIA)) return send(res, 403, 'no');
      return sendFile(req, res, f);
    }
    if (u.pathname.startsWith('/out/')) {
      const f = path.join(OUT, path.basename(decodeURIComponent(u.pathname.slice(5))));
      return sendFile(req, res, f);
    }
    send(res, 404, 'not found');
  } catch (e) {
    send(res, 500, {error: String(e.message || e)});
  }
});

server.listen(PORT, () => {
  console.log(`Video Maker: http://localhost:${PORT}`);
  if (process.argv.includes('--open')) spawn('cmd', ['/c', 'start', '', `http://localhost:${PORT}`], {detached: true});
});
