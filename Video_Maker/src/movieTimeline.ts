// Movie mode: when every shot, voice line and title plays (Valmiki Cinema scripts, 16:9).
import type {Media} from './timeline';

export type MovieLine = {who: string; label: string; voice: string; text: string; song: boolean; est: number};
export type MovieShot = {
  no: number; planStart: number; sec: number; fixedSec: number; kind: string; refs: string; pic: string;
  lines: MovieLine[]; music: string[]; fx: {te: string; prompt: string}[]; cap: string[]; img: string; vid: string; ref: string[];
  alts?: {pic: string; img: string; vid: string}[]; bgm?: string; bumper?: boolean; label?: string;
};
export type MovieScene = {si: number; title: string; refs: string; loc: string; suno: string; songstyle: string; shots: MovieShot[];
  voiceLabel?: string; voiceText?: string};
export type MovieData = {id: string; mode?: 'long'; kanda: string; kandaEn: string; file: string; sarga: number; title: string; covers: string;
  next: string; songnote: string; planLength: number; scenes: MovieScene[]};
// media of one movie: per shot (clip, clip_2, clip_3, line1 … line6, fx) and per scene (music)
export type MovieMedia = {shots: Record<string, Record<string, Media>>; scenes: Record<string, Record<string, Media>>;
  shared: Record<string, Media>};

export type Placed = {start: number; end: number};
export type ShotTime = Placed & {no: number; si: number; lines: (Placed & {url: string | null})[]; recorded: boolean};
// a long video's recorded part (or the channel intro clip) plays once from its start
export type PartVoice = Placed & {si: number; url: string; intro?: boolean};
export type MovieTimeline = {shots: ShotTime[]; scenes: (Placed & {si: number})[]; endCard: Placed; total: number; parts: PartVoice[]};

export const LEAD_IN = 0.3; // a breath before the first line of a shot
export const BETWEEN = 0.35; // between two lines of one shot
export const TAIL = 0.6; // after the last line, before the next shot
export const END_CARD = 4; // the channel banner after the last shot

export function makeMovieTimeline(d: MovieData, media: MovieMedia): MovieTimeline {
  const shots: ShotTime[] = [];
  const scenes: (Placed & {si: number})[] = [];
  const parts: PartVoice[] = [];
  let t = 0;
  for (const sc of d.scenes) {
    const sStart = t;
    // long videos: one recording per part; its pictures share the recording's length by how much each one says
    const part = d.mode === 'long' ? media.scenes[String(sc.si)]?.voice : undefined;
    const intro = d.mode === 'long' && sc.shots.every((x) => x.bumper) ? media.shared.intro : undefined;
    if (intro?.dur) {
      parts.push({si: sc.si, start: t, end: t + intro.dur, url: intro.url, intro: true});
      // the channel intro clip (with its own sound) fills the bumper part
      sc.shots.forEach((sh, i, a) => shots.push({no: sh.no, si: sc.si, start: t + (intro.dur! * i) / a.length,
        end: t + (intro.dur! * (i + 1)) / a.length, lines: [], recorded: true}));
      t += intro.dur;
      scenes.push({si: sc.si, start: sStart, end: t});
      continue;
    }
    if (part?.dur) {
      const chars = (x: MovieShot) => x.lines.reduce((a, l) => a + l.text.length, 0);
      const spoken = sc.shots.filter((x) => chars(x) > 0);
      const total = spoken.reduce((a, x) => a + chars(x), 0) || 1;
      const rate = total / part.dur; // characters per second of this recording
      const first = sc.shots.findIndex((x) => chars(x) > 0);
      const last = sc.shots.length - 1 - [...sc.shots].reverse().findIndex((x) => chars(x) > 0);
      // silent clips before the first word and after the last keep their own length; silent ones inside take a share
      let c = t;
      sc.shots.forEach((x, i) => {
        if (i < first) { shots.push({no: x.no, si: sc.si, start: c, end: c + (x.fixedSec || 3), lines: [], recorded: true}); c += x.fixedSec || 3; }
      });
      const vStart = c + LEAD_IN;
      const weights = sc.shots.map((x, i) => (i < first || i > last ? 0 : chars(x) || (x.fixedSec || 3) * rate));
      const wsum = weights.reduce((a, b) => a + b, 0) || 1;
      let v = vStart;
      sc.shots.forEach((x, i) => {
        if (i < first || i > last) return;
        const len = (part.dur! * weights[i]) / wsum;
        const lines = chars(x) ? [{start: v, end: v + len, url: null}] : [];
        shots.push({no: x.no, si: sc.si, start: i === first ? c : v, end: v + len + (i === last ? TAIL : 0), lines, recorded: true});
        v += len;
      });
      parts.push({si: sc.si, start: vStart, end: vStart + part.dur, url: part.url});
      c = v + TAIL;
      sc.shots.forEach((x, i) => {
        if (i > last) { shots.push({no: x.no, si: sc.si, start: c, end: c + (x.fixedSec || 3), lines: [], recorded: true}); c += x.fixedSec || 3; }
      });
      t = c;
      scenes.push({si: sc.si, start: sStart, end: t});
      continue;
    }
    for (const sh of sc.shots) {
      const m = media.shots[String(sh.no)] || {};
      const files = sh.lines.map((_, i) => m[`line${i + 1}`]);
      const recorded = sh.lines.length > 0 && files.every((f) => f?.dur);
      const lines: (Placed & {url: string | null})[] = [];
      let len: number;
      if (sh.lines.length) {
        // recorded lines use their real length; the rest the script's estimate, so the film can be previewed early
        let c = t + LEAD_IN;
        sh.lines.forEach((l, i) => {
          const dur = files[i]?.dur ?? l.est;
          lines.push({start: c, end: c + dur, url: files[i]?.url ?? null});
          c += dur + BETWEEN;
        });
        len = Math.max(c - BETWEEN + TAIL - t, sh.fixedSec || 0);
      } else len = sh.fixedSec || sh.sec || 6;
      shots.push({no: sh.no, si: sc.si, start: t, end: t + len, lines, recorded});
      t += len;
    }
    scenes.push({si: sc.si, start: sStart, end: t});
  }
  const endCard = {start: t, end: t + END_CARD};
  return {shots, scenes, endCard, total: t + END_CARD, parts};
}

// captions for YouTube: every spoken line at its real time
export function movieCues(d: MovieData, tl: MovieTimeline): {start: number; end: number; text: string}[] {
  const out: {start: number; end: number; text: string}[] = [];
  const byNo = new Map(tl.shots.map((s) => [s.no, s]));
  for (const sc of d.scenes) for (const sh of sc.shots) {
    const st = byNo.get(sh.no)!;
    sh.lines.forEach((l, i) => out.push({start: st.lines[i].start, end: st.lines[i].end, text: l.text}));
  }
  return out;
}
