// Video Maker page: http://localhost:3333
// Keeps each Short's clips, voice and music in media/<kanda>/Sarga_NNN/Sloka_NNN/ under fixed names
// (clip1 … clip7, voice or voice1 … voice4, music), tells the Remotion template their lengths,
// and renders the finished MP4 into out/ when asked.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {spawn, execFile} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {makeTimeline, cues, HOOK, SLOKA, WORDS, MEANING, END} from '../src/timeline.ts';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const MEDIA = path.join(ROOT, 'media');
const OUT = path.join(ROOT, 'out');
const DATA = path.join(ROOT, 'src', 'data');
const PORT = 3333;
const SLOTS = ['clip1', 'clip2', 'clip3', 'clip4', 'clip5', 'clip6', 'clip7', 'voice', 'voice1', 'voice2', 'voice3', 'voice4', 'music'];
const VIDEO = ['.mp4', '.mov', '.webm', '.m4v'];
const IMAGE = ['.png', '.jpg', '.jpeg', '.webp'];
const AUDIO = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'];
const TYPES = {'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm', '.m4v': 'video/mp4', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4',
  '.aac': 'audio/aac', '.ogg': 'audio/ogg', '.flac': 'audio/flac', '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.srt': 'application/x-subrip; charset=utf-8'};

const pad = (n) => String(n).padStart(3, '0');
const slokaDir = (k, s, n) => path.join(MEDIA, k, `Sarga_${pad(s)}`, `Sloka_${pad(n)}`);
const safe = (k) => /^[0-9]_[A-Za-z]+_Kanda$/.test(k);

function findSlot(dir, slot) {
  if (!fs.existsSync(dir)) return null;
  const f = fs.readdirSync(dir).find((x) => path.parse(x).name === slot);
  return f ? path.join(dir, f) : null;
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

async function mediaFor(k, s, n) {
  const dir = slokaDir(k, s, n);
  const media = {};
  const slots = [...SLOTS.map((x) => [x, dir]), ['music_default', MEDIA]];
  for (const [slot, d] of slots) {
    const f = findSlot(d, slot);
    if (!f) continue;
    const ext = path.extname(f).toLowerCase();
    const rel = path.relative(MEDIA, f).split(path.sep).join('/');
    const st = fs.statSync(f);
    media[slot] = {name: path.basename(f), url: `http://localhost:${PORT}/media/${rel}?v=${Math.round(st.mtimeMs)}`,
      video: VIDEO.includes(ext), dur: IMAGE.includes(ext) ? null : await duration(f), size: st.size};
  }
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
async function writeSrt(k, s, n) {
  const {id, text} = await srtFor(k, s, n);
  fs.mkdirSync(OUT, {recursive: true});
  fs.writeFileSync(path.join(OUT, `${id}.srt`), '﻿' + text, 'utf8');
  return id;
}

// ---- rendering: one at a time ----
let job = {state: 'idle'};
function render(k, kandaEn, s, n) {
  const id = `${kandaEn}-S${pad(s)}-Sloka-${pad(n)}`;
  fs.mkdirSync(OUT, {recursive: true});
  const out = path.join(OUT, `${id}.mp4`);
  const cli = path.join(ROOT, 'node_modules', '@remotion', 'cli', 'remotion-cli.js');
  job = {state: 'running', id, progress: 0, log: '', file: path.basename(out), started: Date.now()};
  const p = spawn(process.execPath, [cli, 'render', 'src/index.ts', id, out], {cwd: ROOT, env: {...process.env, FORCE_COLOR: '0'}});
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
    if (code === 0) await writeSrt(k, s, n).catch(() => {});
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
      const ok = slot.startsWith('clip') ? [...VIDEO, ...IMAGE] : AUDIO;
      if (!(SLOTS.includes(slot) || slot === 'music_default') || !ok.includes(ext)) return send(res, 400, {error: `${ext || 'ఈ ఫైల్'} ఇక్కడ పనికిరాదు`});
      const dir = slot === 'music_default' ? MEDIA : slokaDir(k, s, n);
      fs.mkdirSync(dir, {recursive: true});
      const old = findSlot(dir, slot);
      const tmp = path.join(dir, `.${slot}.uploading`);
      await new Promise((ok2, bad) => req.pipe(fs.createWriteStream(tmp)).on('finish', ok2).on('error', bad));
      if (old) fs.unlinkSync(old);
      fs.renameSync(tmp, path.join(dir, slot + ext));
      return send(res, 200, {media: await mediaFor(k, s, n)});
    }
    if (u.pathname === '/api/remove' && req.method === 'POST' && safe(k)) {
      const f = findSlot(q.slot === 'music_default' ? MEDIA : slokaDir(k, s, n), q.slot);
      if (f && (SLOTS.includes(q.slot) || q.slot === 'music_default')) fs.unlinkSync(f);
      return send(res, 200, {media: await mediaFor(k, s, n)});
    }
    if (u.pathname === '/api/render' && req.method === 'POST' && safe(k)) {
      if (job.state === 'running') return send(res, 409, {error: 'ఇంకో వీడియో తయారవుతోంది'});
      render(k, q.ke, s, n);
      return send(res, 200, job);
    }
    if (u.pathname === '/api/status') return send(res, 200, job);
    if (u.pathname === '/api/open' && req.method === 'POST') {
      const target = q.what === 'out' ? OUT : (safe(k) ? slokaDir(k, s, n) : MEDIA);
      fs.mkdirSync(target, {recursive: true});
      spawn('explorer.exe', [target], {detached: true});
      return send(res, 200, {ok: true});
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
