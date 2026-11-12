import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {Audio, Video} from '@remotion/media';
import {CTA_GAP, END, FPS, HOOK, MEANING, Media, MediaMap, SLOKA, Span, Timeline, VOICE_OF, WORDS, cues} from './timeline';
import {DEV, LAT, TE, TITLE} from './fonts';
import {ambienceAt, momentIn} from './sound';

export type Line = {orig: string; te: string; dev: string; iast: string};
export type Word = {key: string; te: string; dev: string; iast: string; mte: string; mhi: string; men: string};
export type Sloka = {
  n: number;
  hook: {voice: string; screen: string};
  meaning: {voice: string; screen: string};
  end: {voice: string};
  clips: {label: string; video: boolean; shows: string; says?: string; mood?: string}[];
  lines: Line[];
  words: Word[];
};
export type ShortProps = {
  kandaTe: string;
  sarga: number;
  sloka: Sloka;
  media: MediaMap;
  timeline: Timeline | null;
  server: boolean;
};

const GOLD = '#f6cf6a';
const CREAM = '#fbeed2';
const CARD_BG = 'rgba(28,12,4,0.78)';
const KEY_WORDS = ['శ్రీరాము', 'రాము', 'రామ', 'సీతమ్మ', 'సీత', 'లక్ష్మణ', 'హనుమ', 'రావణ', 'నారద', 'వాల్మీకి', 'జటాయు', 'ధర్మ', 'దశరథ', 'భరత', 'విశ్వామిత్ర', 'సుగ్రీవ', 'కౌసల్య', 'కైకేయి'];

const fade = (t: number, a: number, b: number, inS = 0.25, outS = 0.25) =>
  interpolate(t, [a, a + inS, b - outS, b], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const inSpan = (t: number, s: Span) => t >= s.start && t < s.end;

// ---------- pictures and videos ----------
// How a picture comes in. Chosen by where it is in the story and the Short's mood, like a human editor would:
// a warm flash into the śloka, a zoom-through into the story, slides (or soft fades for sorrow, fast whips for action)
// between story pictures, a dip to dark before the ending, and quick fades between extra pictures in one box.
export type Enter = 'none' | 'fade' | 'flash' | 'zoom' | 'slide' | 'whip' | 'dip';
const ENTER_LEN: Record<Enter, number> = {none: 0, fade: 0.35, flash: 0.25, zoom: 0.45, slide: 0.4, whip: 0.3, dip: 0.5};

// The camera move on a still picture, as an editor would pick it: push in on faces, rise toward the sky and gods,
// drift across wide places, and otherwise alternate a slow push-in and a slow pull-back.
export type Move = 'in' | 'out' | 'pan' | 'up' | 'down' | 'panL' | 'panR' | 'punch' | 'still';
// one clip's own edit (వైభవం page): speed ('auto' fits the video to its slot, never slower than 0.5×), seconds trimmed
// from the start, the clip's own sound volume (0 = muted), and the picture's camera move ('auto' = from the scene)
export type ClipEdit = {speed?: number | 'auto'; trim?: number; own?: number; move?: Move | 'auto'};
export function moveFor(shows: string, k: number): Move {
  if (/close-up|close on|face|eyes|tears|smil|weep/i.test(shows)) return 'in';
  if (/sky|celestial|divine|god|heaven|clouds|rising|ascend|glow/i.test(shows)) return 'up';
  if (/wide|forest|landscape|city|army|ocean|river|path|valley|kingdom|crowd|land|hills/i.test(shows)) return k % 2 ? 'out' : 'pan';
  return k % 2 ? 'out' : 'in';
}
// z: the eased progress through the picture's time (0 → 1); t: seconds since it appeared (for the quick punch-in)
function moveStyle(move: Move, z: number, t = 0): string {
  if (move === 'out') return `scale(${1.14 - 0.14 * z})`;
  if (move === 'pan' || move === 'panL') return `scale(1.14) translateX(${50 - 100 * z}px)`;
  if (move === 'panR') return `scale(1.14) translateX(${-50 + 100 * z}px)`;
  if (move === 'up') return `scale(1.12) translateY(${50 - 100 * z}px)`;
  if (move === 'down') return `scale(1.12) translateY(${-50 + 100 * z}px)`;
  if (move === 'still') return 'scale(1.02)';
  if (move === 'punch') {
    // a quick, smooth punch-in over the first 0.45 s, then a slow drift closer (the climax moment)
    const p = Easing.out(Easing.cubic)(Math.min(1, t / 0.45));
    return `scale(${1 + 0.12 * p + 0.05 * z})`;
  }
  return `scale(${1 + 0.14 * z})`;
}

export const Visual: React.FC<{m: Media | undefined; len: number; enter: Enter; fadeLen?: number; move: Move; placeholder: React.ReactNode; edit?: ClipEdit}> = ({m, len, enter, fadeLen, move, placeholder, edit}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const d = (enter === 'fade' && fadeLen) || ENTER_LEN[enter] || 0.01;
  const p = interpolate(t, [0, d], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  let style: React.CSSProperties = {};
  if (enter === 'fade' || enter === 'flash' || enter === 'dip') style = {opacity: p};
  if (enter === 'zoom') style = {opacity: Math.min(1, p * 2), transform: `scale(${1.3 - 0.3 * p})`, filter: `blur(${12 * (1 - p)}px)`};
  if (enter === 'slide') style = {transform: `translateX(${(1 - p) * 100}%)`};
  if (enter === 'whip') style = {transform: `translateX(${(1 - p) * 100}%)`, filter: `blur(${20 * (1 - p)}px)`};
  let body = placeholder;
  if (m?.video) {
    // speed: a chosen speed, else fit the video to its slot (slowed, never below 0.5× so motion stays smooth);
    // if it is still too short at that speed it loops; trim cuts seconds off the start; own = the clip's own sound
    // (the śloka Shorts pass no edit and keep their approved behaviour: slowed to fit, no floor, no loop)
    const trim = Math.max(0, edit?.trim || 0);
    const left = m.dur ? Math.max(0.5, m.dur - trim) : null;
    const floor = edit ? 0.5 : 0;
    const rate = typeof edit?.speed === 'number' ? edit.speed : left ? Math.min(1, Math.max(floor, left / len)) : 1;
    const loop = !!edit && !!left && left / rate < len - 0.05;
    const own = Math.max(0, Math.min(1, edit?.own || 0));
    body = <Video src={m.url} muted={!own} volume={own || undefined} playbackRate={rate} loop={loop}
      trimBefore={trim ? Math.round(trim * FPS) : undefined} objectFit="cover" style={{width: '100%', height: '100%'}} />;
  } else if (m) {
    const z = interpolate(t, [0, len + 0.9], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
    body = <Img src={m.url} style={{width: '100%', height: '100%', objectFit: 'cover', transform: moveStyle(move, z, t)}} />;
  }
  return <AbsoluteFill style={{overflow: 'hidden', ...style}}>{body}</AbsoluteFill>;
};

const Placeholder: React.FC<{i: number; sloka: Sloka}> = ({i, sloka}) => {
  const c = sloka.clips[i];
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 35%, #5b2a10 0%, #24100a 55%, #0d0604 100%)',
      alignItems: 'center', justifyContent: 'center', padding: 90, textAlign: 'center'}}>
      <div style={{fontFamily: TE, color: 'rgba(246,207,106,.55)', fontSize: 64, fontWeight: 800}}>క్లిప్ {i + 1}</div>
      <div style={{fontFamily: TE, color: 'rgba(251,238,210,.5)', fontSize: 44, marginTop: 14}}>{c.label} · {c.video ? '🎥 వీడియో' : '🖼️ ఇమేజ్'}</div>
      <div style={{fontFamily: LAT, color: 'rgba(251,238,210,.35)', fontSize: 34, marginTop: 30, lineHeight: 1.35}}>{c.shows}</div>
    </AbsoluteFill>
  );
};

// ---------- text on screen ----------
const Pop: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, children, style}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - at * fps, fps, config: {damping: 12, stiffness: 140}});
  return <div style={{transform: `scale(${0.6 + 0.4 * s})`, opacity: Math.min(1, s * 1.5), ...style}}>{children}</div>;
};

const HookTitle: React.FC<{text: string; span: Span; t: number}> = ({text, span, t}) => {
  if (!text || !inSpan(t, span)) return null;
  const o = interpolate(t, [span.end - 0.3, span.end], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', paddingTop: 250, opacity: o}}>
      <Pop at={span.start + 0.15} style={{maxWidth: 900, textAlign: 'center'}}>
        <div style={{fontFamily: TITLE, fontSize: 92, lineHeight: 1.25, color: GOLD,
          textShadow: '0 0 30px rgba(0,0,0,.9), 0 6px 0 #3a1500, 0 0 60px rgba(255,170,40,.45)',
          WebkitTextStroke: '3px #2a1000', paintOrder: 'stroke fill'}}>{text}</div>
      </Pop>
    </AbsoluteFill>
  );
};

const Tag: React.FC<{text: string; t: number; from: number}> = ({text, t, from}) => {
  const o = interpolate(t, [from, from + 0.4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 150, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: o}}>
      <div style={{fontFamily: TE, fontWeight: 700, fontSize: 30, color: '#2a1500', background: GOLD, padding: '6px 26px',
        borderRadius: 40, boxShadow: '0 4px 20px rgba(0,0,0,.4)'}}>{text}</div>
    </div>
  );
};

const card: React.CSSProperties = {position: 'absolute', left: 48, right: 140, background: CARD_BG, border: `3px solid ${GOLD}`,
  borderRadius: 32, padding: '28px 34px 32px', boxShadow: '0 10px 50px rgba(0,0,0,.5)'};
const chip: React.CSSProperties = {display: 'inline-block', fontFamily: TE, fontWeight: 700, fontSize: 26, color: '#2a1500',
  background: GOLD, padding: '4px 18px', borderRadius: 40, marginBottom: 16};

// One card on the śloka picture: the heading, then the śloka while it is chanted (gold glow along the line
// being chanted), then the word meanings for a moment with no voice. Telugu only, as the user shows it.
const Heading: React.FC<{text: string}> = ({text}) => (
  <div style={{fontFamily: TE, fontWeight: 700, fontSize: 34, color: GOLD, letterSpacing: 0.5, marginBottom: 22,
    paddingBottom: 14, borderBottom: '2px solid rgba(246,207,106,.45)'}}>{text}</div>
);

const SlokaCard: React.FC<{heading: string; sloka: Sloka; span: Span; t: number}> = ({heading, sloka, span, t}) => {
  const ls = sloka.lines;
  if (!ls.length || !inSpan(t, span)) return null;
  const o = fade(t, span.start, span.end, 0.3, 0.2);
  const lift = interpolate(t, [span.start, span.start + 0.45], [40, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const per = (span.end - span.start - 0.4) / ls.length;
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 120px 260px 48px'}}>
      <div style={{...card, position: 'relative', left: 0, right: 0, opacity: o, transform: `translateY(${lift}px)`, padding: '30px 38px 36px'}}>
        <Heading text={heading} />
        {ls.map((l, k) => {
          const a = span.start + 0.2 + k * per;
          const sweep = interpolate(t, [a, a + per], [0, 112], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <div key={k} style={{fontFamily: TE, fontWeight: 800, fontSize: 58, lineHeight: 1.45,
              backgroundImage: `linear-gradient(90deg, #ffe08a ${sweep - 12}%, #fff ${sweep}%, #fff 100%)`,
              WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
              filter: t >= a && t < a + per ? 'drop-shadow(0 0 14px rgba(255,200,80,.55))' : 'none'}}>{l.orig}</div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const WordList: React.FC<{heading: string; words: Word[]; span: Span; t: number}> = ({heading, words, span, t}) => {
  if (!words.length || !inSpan(t, span)) return null;
  const o = interpolate(t, [span.end - 0.25, span.end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const step = Math.min(0.12, 1 / words.length);
  const size = words.length > 8 ? 38 : 44;
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 120px 260px 48px'}}>
      <div style={{...card, position: 'relative', left: 0, right: 0, opacity: o, padding: '30px 38px 34px'}}>
        <Heading text={heading} />
        {words.map((w, k) => {
          const a = span.start + k * step;
          const p = interpolate(t, [a, a + 0.25], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <div key={k} style={{fontFamily: TE, fontSize: size, lineHeight: 1.4, marginTop: k ? 8 : 0, opacity: p,
              transform: `translateX(${(1 - p) * 30}px)`}}>
              <span style={{fontWeight: 800, color: GOLD}}>{w.key}:</span>{' '}
              <span style={{fontWeight: 600, color: '#fff'}}>{w.mte}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const LessonChips: React.FC<{text: string; span: Span; t: number}> = ({text, span, t}) => {
  const items = text.split('|').map((s) => s.trim()).filter(Boolean);
  if (!items.length || !inSpan(t, span)) return null;
  const o = interpolate(t, [span.end - 0.25, span.end], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 240, left: 60, right: 140, display: 'flex', flexWrap: 'wrap', gap: 18,
      justifyContent: 'center', opacity: o}}>
      {items.map((s, k) => (
        <Pop key={k} at={span.start + 0.15 + k * 0.45}>
          <div style={{fontFamily: TITLE, fontSize: 54, color: '#2a1500', background: `linear-gradient(180deg, #ffe8a3, ${GOLD})`,
            padding: '10px 30px', borderRadius: 24, boxShadow: '0 8px 30px rgba(0,0,0,.5)'}}>{s}</div>
        </Pop>
      ))}
    </div>
  );
};

const Subtitle: React.FC<{text: string; span: Span; t: number}> = ({text, span, t}) => {
  if (!text || !inSpan(t, span)) return null;
  const c = cues(text, span).find((q) => t >= q.start && t < q.end);
  if (!c) return null;
  const s = interpolate(t, [c.start, c.start + 0.12], [0.92, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', bottom: 430, left: 60, right: 140, textAlign: 'center', transform: `scale(${s})`}}>
      <span style={{fontFamily: TE, fontWeight: 800, fontSize: 60, lineHeight: 1.3, color: '#fff', WebkitTextStroke: '10px #120700',
        paintOrder: 'stroke fill', textShadow: '0 4px 18px rgba(0,0,0,.8)'}}>
        {c.text.split(' ').map((w, k) => (
          <span key={k} style={{color: KEY_WORDS.some((x) => w.startsWith(x)) ? '#ffd84a' : '#fff'}}>{w} </span>
        ))}
      </span>
    </div>
  );
};

// The closing card follows what the closing voice asks for (the CTA changes from Short to Short).
const EndCard: React.FC<{voice: string; part: Span; t: number}> = ({voice, part, t}) => {
  const from = Math.max(part.start + 0.5, part.end - 3.4);
  if (t < from) return null;
  const asks: [string, string][] = [];
  if (/జై శ్రీ ?రామ్|కామెంట్/.test(voice)) asks.push(['💬', 'జై శ్రీరామ్']);
  if (/లైక్/.test(voice)) asks.push(['👍', 'లైక్']);
  if (/షేర్/.test(voice)) asks.push(['↗️', 'షేర్']);
  if (/సబ్‌?స్క్రైబ్|సబ్స్క్రైబ్/.test(voice)) asks.push(['🔔', 'సబ్‌స్క్రైబ్']);
  if (!asks.length) asks.push(['🙏', 'జై శ్రీరామ్']);
  return (
    <div style={{position: 'absolute', bottom: 640, left: 50, right: 140, display: 'flex', gap: 18, justifyContent: 'center', flexWrap: 'wrap'}}>
      {asks.map(([icon, label], k) => (
        <Pop key={k} at={from + k * 0.3}>
          <div style={{fontFamily: TE, fontWeight: 800, fontSize: 44, color: '#fff', background: k === asks.length - 1 && label === 'సబ్‌స్క్రైబ్' ? '#d62828' : 'rgba(20,8,2,.82)',
            border: `3px solid ${GOLD}`, padding: '10px 28px', borderRadius: 60, boxShadow: '0 8px 30px rgba(0,0,0,.5)'}}>{icon} {label}</div>
        </Pop>
      ))}
    </div>
  );
};

// The channel banner (Branding/end_banner.png) over the closing request (like / share / subscribe / comment),
// and always at least the last 2.5 s of the Short.
const CTA_RE = /లైక్|షేర్|సబ్‌?స్క్రైబ్|సబ్స్క్రైబ్|కామెంట్|బెల్|జై శ్రీ ?రామ్/;
function bannerFrom(voice: string, speech: Span, total: number): number {
  const parts = voice.split(/(?<=[.!?…])\s+/);
  const i = parts.findIndex((p) => CTA_RE.test(p));
  let at = total - 2.5;
  if (i >= 0) {
    const before = parts.slice(0, i).join(' ').length;
    at = Math.min(at, speech.start + (speech.end - speech.start) * (before / Math.max(1, voice.length)));
  }
  return Math.max(speech.start, at);
}
const Banner: React.FC<{url: string; from: number; t: number}> = ({url, from, t}) => {
  if (t < from) return null;
  const p = interpolate(t, [from, from + 0.45], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{opacity: p, backgroundColor: '#000'}}>
      <Img src={url} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.06 - 0.06 * p})`}} />
    </AbsoluteFill>
  );
};

const Warning: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', top: 40, left: 40, right: 40, fontFamily: TE, fontSize: 28, color: '#fff', background: 'rgba(160,30,30,.85)',
    padding: '10px 18px', borderRadius: 14, textAlign: 'center'}}>{text}</div>
);

const STYLED = false; // styled transitions off: soft cross-fades only, and no transition sounds
// The quieter "edited by a person" touches (tried 2026-11-08): cuts on sentence ends, camera moves chosen per picture,
// slow dissolves into the śloka and the ending, sounds a moment before their picture, and one warm film look.
const HUMAN = true;

// a soft vignette and a fine moving grain over every picture, so pictures from different prompts feel like one film
export const FilmLook: React.FC<{frame: number; w?: number; h?: number}> = ({frame, w = 1080, h = 1920}) => (
  <>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.32) 100%)'}} />
    <AbsoluteFill style={{opacity: 0.07, mixBlendMode: 'overlay'}}>
      <svg width={w} height={h}>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 7} stitchTiles="stitch" /></filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  </>
);

// smooth a stepped level over ±0.4 s so the music rises and dips like a hand on the fader
const smooth = (fn: (t: number) => number, t: number) => [-0.4, -0.2, 0, 0.2, 0.4].reduce((a, d) => a + fn(t + d), 0) / 5;

export const Short: React.FC<ShortProps> = ({kandaTe, sarga, sloka, media, timeline, server}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!timeline) return null;
  const {parts, speech, clips, mode, lead} = timeline;
  const f = (s: number) => Math.round(s * FPS);
  const total = f(timeline.total);
  const music = (media.bgm as unknown as Media | null) ?? media.music ?? media.music_default;
  const heading = `${kandaTe} · సర్గ ${sarga} · శ్లోకం ${sloka.n}`;
  const mood = (media.mood as unknown as string) || 'calm';
  const sfx = (name: string | null) => (name ? media['sfx_' + name] : undefined);

  // every picture of every box (up to 3 per box), with how it comes in
  const firstStory = clips[2] ? 2 : 3;
  const between: Enter = mood === 'sad' ? 'fade' : mood === 'heroic' || mood === 'mystery' ? 'whip' : 'slide';
  const shots: {box: number; m: Media | undefined; start: number; end: number; enter: Enter; fadeLen: number}[] = [];
  // Change story pictures where a sentence of the meaning voice ends (as an editor cuts), not at even shares:
  // each boundary moves to the nearest sentence end within 2.5 s, keeping every picture at least 2.5 s.
  const box = clips.map((c) => (c ? {...c} : null));
  if (HUMAN && mode === 'parts') {
    const text = sloka.meaning.voice;
    const sp = speech[MEANING];
    const sents = text.split(/(?<=[.!?…])\s+/);
    const ends: number[] = [];
    let n = 0;
    sents.forEach((x) => { n += x.length + 1; ends.push(sp.start + ((sp.end - sp.start) * Math.min(n, text.length)) / text.length + 0.15); });
    const story = [2, 3, 4, 5].filter((i) => box[i]);
    for (let j = 1; j < story.length; j++) {
      const a = box[story[j - 1]]!, b = box[story[j]]!;
      const next = box[story[j + 1]] || {end: box[6]!.start};
      const ok = ends.filter((e) => Math.abs(e - b.start) <= 2.5 && e - a.start >= 2.5 && next.end - e >= 2.5);
      if (ok.length) {
        const e = ok.reduce((x, y) => (Math.abs(y - b.start) < Math.abs(x - b.start) ? y : x));
        a.end = e;
        b.start = e;
      }
    }
  }
  box.forEach((c, i) => {
    if (!c) return;
    const files = ['', '_2', '_3'].map((x) => media[`clip${i + 1}${x}`]).filter(Boolean) as Media[];
    const list: (Media | undefined)[] = files.length ? files : [undefined];
    // The user prefers the plain soft cross-fade everywhere (flash / zoom / whip / dip tried 2026-11-08, not liked).
    // The other kinds stay in Enter for a later try; set STYLED = true to bring them back.
    const boxEnter: Enter = i === 0 ? 'none' : !STYLED ? 'fade' : i === 1 ? 'flash' : i === firstStory ? 'zoom' : i === 6 ? 'dip' : between;
    const step = (c.end - c.start) / list.length;
    // a slow, soft dissolve into the śloka and into the ending; a quicker one between story pictures
    const pace = !HUMAN ? 0.35 : i === 1 || i === 6 ? 0.8 : 0.3;
    list.forEach((m, k) => shots.push({box: i, m, start: c.start + k * step, end: c.start + (k + 1) * step, enter: k ? 'fade' : boxEnter, fadeLen: k ? 0.35 : pace}));
  });
  const boundary = (e: Enter) => shots.filter((x) => x.enter === e).map((x) => x.start);
  const flashO = Math.max(0, ...boundary('flash').map((b) => interpolate(t, [b - 0.12, b, b + 0.35], [0, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})));
  const dipO = Math.max(0, ...boundary('dip').map((b) => interpolate(t, [b - 0.4, b, b + 0.45], [0, 0.92, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})));

  // sounds: one per transition, one per moment a picture shows, and a quiet background for the place
  const transSfx: Record<Enter, string | null> = {none: null, fade: null, flash: 'shimmer', zoom: 'whoosh', slide: 'swish', whip: 'whoosh',
    dip: mood === 'sad' ? null : mood === 'heroic' || mood === 'mystery' ? 'boom' : 'bell'};
  const hits: {at: number; m: Media; vol: number}[] = [];
  shots.forEach((x, k) => {
    const tr = STYLED ? sfx(transSfx[x.enter]) : undefined;
    if (tr && x.start > 0) hits.push({at: Math.max(0, x.start - 0.15), m: tr, vol: 0.35});
    const mo = x.box === 1 ? undefined : sfx(momentIn(sloka.clips[x.box]?.shows || '', sloka.clips[x.box]?.mood || mood));
    if (mo && (k === 0 || shots[k - 1].box !== x.box)) hits.push({at: Math.max(0, x.start + (HUMAN ? -0.3 : 0.25)), m: mo, vol: 0.4});
  });
  // music and background change with the story (user, 2026-11-11): each picture box has its own mood and place;
  // neighbours with the same track join into one stretch, and stretches cross-fade over XF seconds.
  const XF = 1.2;
  const own = media.music as Media | undefined;   // the user's own track for this śloka: kept for the whole Short
  type Stretch = {key: string; m: Media; start: number; end: number};
  const stretches = (pick: (i: number) => Media | undefined) => {
    const out: Stretch[] = [];
    box.forEach((c, i) => {
      if (!c) return;
      const m = pick(i);
      if (!m) return;
      const last = out[out.length - 1];
      if (last && last.key === m.url) last.end = Math.max(last.end, c.end);
      else out.push({key: m.url, m, start: c.start, end: c.end});
    });
    if (out.length) { out[0].start = 0; out[out.length - 1].end = timeline.total; }
    return out;
  };
  const moodAt = (i: number) => sloka.clips[i]?.mood || mood;
  const musicParts = own ? [{key: own.url, m: own, start: 0, end: timeline.total}]
    : stretches((i) => (media['music_' + moodAt(i)] as Media | undefined) ?? (media.music_default as Media | undefined) ?? music ?? undefined);
  const ambParts = stretches((i) => sfx(ambienceAt(sloka.clips.map((c) => c?.shows || ''), i)));
  const xfade = (g: Stretch, k: number, n: number, u: number) =>
    (k ? interpolate(u, [g.start - XF / 2, g.start + XF / 2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1)
    * (k < n - 1 ? interpolate(u, [g.end - XF / 2, g.end + XF / 2], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1);
  const noVoice = (u: number) => inSpan(u, parts[WORDS]) || (lead[MEANING] > 0 && u >= parts[MEANING].start && u < parts[MEANING].start + lead[MEANING]);
  const ends = (fr: number) => interpolate(fr, [0, f(0.6), total - f(1.5), total], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // music: low under the voice, lower under the chanting, up when only pictures and music play
  const musicLevel = (u: number) => (inSpan(u, parts[SLOKA]) ? 0.07 : noVoice(u) ? 0.26 : 0.12);

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{filter: HUMAN ? 'contrast(1.04) saturate(1.06) sepia(0.06)' : undefined}}>
        {shots.map((x, k) => {
          const from = f(x.start);
          const last = k === shots.length - 1;
          const nextFade = shots[k + 1]?.fadeLen ?? 0.35;
          return (
            <Sequence key={k} from={from} durationInFrames={Math.max(1, (last ? total : f(x.end) + f(nextFade + 0.15)) - from)} premountFor={30}>
              <Visual m={x.m} len={x.end - x.start} enter={x.enter} fadeLen={x.fadeLen}
                move={HUMAN ? moveFor(sloka.clips[x.box]?.shows || '', k) : 'in'} placeholder={<Placeholder i={x.box} sloka={sloka} />} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
      {HUMAN && <FilmLook frame={frame} />}
      {/* darker top and bottom so the words always read clearly */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%)'}} />
      {flashO > 0 && <AbsoluteFill style={{backgroundColor: '#fff3d6', opacity: flashO}} />}
      {dipO > 0 && <AbsoluteFill style={{backgroundColor: '#000', opacity: dipO}} />}

      {/* On the pictures: only the śloka and the word meanings, with the heading (the user's choice).
          Captions go to YouTube as an SRT file (maker/server.mjs), so viewers can turn them on or off. */}
      <SlokaCard heading={heading} sloka={sloka} span={parts[SLOKA]} t={t} />
      <WordList heading={heading} words={sloka.words} span={parts[WORDS]} t={t} />

      {mode === 'parts' &&
        [HOOK, SLOKA, MEANING, END].map((i) => media[VOICE_OF[i]] && (
          <Sequence key={i} from={f(parts[i].start + lead[i])} durationInFrames={f(parts[i].end - parts[i].start) + 1}>
            <Audio src={media[VOICE_OF[i]]!.url} />
          </Sequence>
        ))}
      {mode === 'full' && media.voice && <Audio src={media.voice.url} />}
      {mode === 'parts' && media.cta && media[VOICE_OF[END]]?.dur && (
        <Sequence from={f(parts[END].start + lead[END] + media[VOICE_OF[END]]!.dur! + CTA_GAP)}>
          <Audio src={media.cta.url} />
        </Sequence>
      )}
      {musicParts.map((g, k) => {
        const from = f(Math.max(0, g.start - XF / 2));
        return (
          <Sequence key={'m' + k} from={from} durationInFrames={Math.max(1, Math.min(total, f(g.end + XF / 2)) - from)}>
            <Audio src={g.m.url} loop volume={(fr) => { const u = (from + fr) / FPS; return smooth(musicLevel, u) * ends(from + fr) * xfade(g, k, musicParts.length, u); }} />
          </Sequence>
        );
      })}
      {ambParts.map((g, k) => {
        const from = f(Math.max(0, g.start - XF / 2));
        return (
          <Sequence key={'a' + k} from={from} durationInFrames={Math.max(1, Math.min(total, f(g.end + XF / 2)) - from)}>
            <Audio src={g.m.url} loop volume={(fr) => { const u = (from + fr) / FPS; return smooth((v) => (inSpan(v, parts[SLOKA]) ? 0.04 : 0.08), u) * ends(from + fr) * xfade(g, k, ambParts.length, u); }} />
          </Sequence>
        );
      })}
      {hits.map((h, k) => (
        <Sequence key={'s' + k} from={f(h.at)} durationInFrames={Math.max(1, total - f(h.at))}>
          <Audio src={h.m.url} volume={h.vol} />
        </Sequence>
      ))}
      {media.banner && <Banner url={media.banner.url} from={bannerFrom(sloka.end.voice, speech[END], timeline.total)} t={t} />}
      {!server && <Warning text="వీడియో మేకర్ (START_VIDEO_MAKER.bat) తెరవలేదు – క్లిప్‌లు, వాయిస్ కనిపించవు" />}
    </AbsoluteFill>
  );
};
