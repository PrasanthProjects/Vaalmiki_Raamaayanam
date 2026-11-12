// వైభవం mode: the Rama and Krishna elevation Shorts (9:16). One voice-and-music file (the _MIX.mp3 made by
// elevation_voice.py: music from the first second, the voice 0.4 s in, the music ringing 1.6 s after the last word),
// or for a LOOP Short only its music; each clip's time follows its own line, so the pictures move with the voice.
import {cues} from './timeline.ts';   // with the extension: the page server (node) imports this file too
import type {Cue, Media} from './timeline';
import type {ClipEdit} from './Short';

export type VClip = {no: number; start: number; end: number; label: string; say: string; shows: string; climax: boolean;
  refs: string[]; move: string; img: string; end2: string; vid: string; sfx?: [string, number, number][]};
export type VShort = {id: string; n: number; label: string; headline: string; hl: string; sub: string; src: string; loop: boolean;
  caption: string; planLength: number; clips: VClip[]; title: string; desc: string; pinned: string; thumb: string;
  thumbRefs: string[]; musicPrompt: string; kit: string; voiceScript: string; auto: string; autoMusic?: string};
export type VSeries = {series: string; seriesTe: string; folder: string; shorts: VShort[]};
// dropped files: clip1 … clip8 (+ clipN_2, clipN_3), mix (voice + music), voice (a voice alone), music (loops, or under a voice);
// auto: the series' ready _MIX.mp3 when no audio was dropped
export type VMedia = Record<string, Media | undefined>;
// the page's per-file edits (media/vaibhavam/<id>/edit.json): speed, trim, own sound, camera move
export type VEdit = Record<string, ClipEdit>;

export const VOICE_IN = 0.4;   // the voice starts 0.4 s into the MIX (elevation_voice.mix)
export const RING = 1.6;       // the music rings this long after the last word
export const HEADLINE = 2.6;   // the hook headline stays this long

export type VTimeline = {clips: {no: number; start: number; end: number}[]; voice: {start: number; end: number}; total: number;
  audio: Media | null; music: Media | null; subs: Cue[]};

export function makeVaibhavamTimeline(s: VShort, media: VMedia): VTimeline {
  // mix: the ready voice + music (dropped, else the series' auto _MIX.mp3); voice: a voice alone (music goes under it)
  const voiceOnly = !media.mix && media.voice ? media.voice : null;
  const audio = (media.mix || voiceOnly || media.auto || null) as Media | null;
  const music = (media.music || media.automusic || null) as Media | null;   // a dropped track, else the loop's ready music
  const n = s.clips.length;
  if (s.loop) {
    // a loop: exactly its planned length (or its music's), clips share it evenly; no voice
    const total = music?.dur && Math.abs(music.dur - s.planLength) < 3 ? music.dur : s.planLength;
    const clips = s.clips.map((c, i) => ({no: c.no, start: (total * i) / n, end: (total * (i + 1)) / n}));
    return {clips, voice: {start: 0, end: 0}, total, audio: null, music, subs: []};
  }
  // the voice length: the MIX minus its lead-in and ring-out; a dropped voice alone is all voice
  const mixLike = !!audio && !voiceOnly;
  const voiceLen = audio?.dur ? (mixLike ? Math.max(1, audio.dur - VOICE_IN - RING) : audio.dur) : s.planLength;
  const v0 = VOICE_IN;
  const scale = voiceLen / s.planLength;
  const total = v0 + voiceLen + RING;
  const clips = s.clips.map((c, i) => ({no: c.no, start: i === 0 ? 0 : v0 + c.start * scale, end: i === n - 1 ? total : v0 + c.end * scale}));
  const subs: Cue[] = [];
  s.clips.forEach((c) => subs.push(...cues(c.say, {start: v0 + c.start * scale, end: v0 + c.end * scale}, 26)));
  return {clips, voice: {start: v0, end: v0 + voiceLen}, total, audio, music: mixLike ? null : music, subs};
}
