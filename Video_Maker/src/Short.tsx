import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {Audio, Video} from '@remotion/media';
import {END, FPS, HOOK, MEANING, MediaMap, SLOKA, Span, Timeline, VOICE_OF, WORDS, cues} from './timeline';
import {DEV, LAT, TE, TITLE} from './fonts';

export type Line = {orig: string; te: string; dev: string; iast: string};
export type Word = {key: string; te: string; dev: string; iast: string; mte: string; mhi: string; men: string};
export type Sloka = {
  n: number;
  hook: {voice: string; screen: string};
  meaning: {voice: string; screen: string};
  end: {voice: string};
  clips: {label: string; video: boolean; shows: string}[];
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
const Clip: React.FC<{i: number; span: Span; media: MediaMap; sloka: Sloka; first: boolean}> = ({i, span, media, sloka, first}) => {
  const frame = useCurrentFrame();
  const len = span.end - span.start;
  const t = frame / FPS;
  const m = media[`clip${i + 1}`];
  const opacity = first ? 1 : interpolate(t, [0, 0.35], [0, 1], {extrapolateRight: 'clamp'});
  if (m?.video) {
    const rate = m.dur ? Math.min(1, m.dur / len) : 1;
    return (
      <AbsoluteFill style={{opacity}}>
        <Video src={m.url} muted playbackRate={rate} objectFit="cover" style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
    );
  }
  if (m) {
    // The kit's "slow zoom-in (100% → 112%)"; every other picture also drifts up a little.
    const p = interpolate(t, [0, len + 0.35], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
    const scale = 1 + 0.12 * p;
    const y = i % 2 ? -30 * p : 0;
    return (
      <AbsoluteFill style={{opacity, overflow: 'hidden'}}>
        <Img src={m.url} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translateY(${y}px) scale(${scale})`}} />
      </AbsoluteFill>
    );
  }
  const c = sloka.clips[i];
  return (
    <AbsoluteFill style={{opacity, background: 'radial-gradient(circle at 50% 35%, #5b2a10 0%, #24100a 55%, #0d0604 100%)',
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

const Warning: React.FC<{text: string}> = ({text}) => (
  <div style={{position: 'absolute', top: 40, left: 40, right: 40, fontFamily: TE, fontSize: 28, color: '#fff', background: 'rgba(160,30,30,.85)',
    padding: '10px 18px', borderRadius: 14, textAlign: 'center'}}>{text}</div>
);

export const Short: React.FC<ShortProps> = ({kandaTe, sarga, sloka, media, timeline, server}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!timeline) return null;
  const {parts, speech, clips, mode} = timeline;
  const f = (s: number) => Math.round(s * FPS);
  const fadeIn = f(0.35);
  const total = f(timeline.total);
  const music = media.music ?? media.music_default;
  const heading = `${kandaTe} · సర్గ ${sarga} · శ్లోకం ${sloka.n}`;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {clips.map((c, i) => {
        if (!c) return null;
        const from = f(c.start);
        const last = i === clips.length - 1;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, (last ? total : f(c.end) + fadeIn) - from)} premountFor={30}>
            <Clip i={i} span={c} media={media} sloka={sloka} first={i === 0} />
          </Sequence>
        );
      })}
      {/* darker top and bottom so the words always read clearly */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%)'}} />

      {/* On the pictures: only the śloka and the word meanings, with the heading (the user's choice).
          Captions go to YouTube as an SRT file (maker/server.mjs), so viewers can turn them on or off. */}
      <SlokaCard heading={heading} sloka={sloka} span={parts[SLOKA]} t={t} />
      <WordList heading={heading} words={sloka.words} span={parts[WORDS]} t={t} />

      {mode === 'parts' &&
        [HOOK, SLOKA, MEANING, END].map((i) => media[VOICE_OF[i]] && (
          <Sequence key={i} from={f(parts[i].start)} durationInFrames={f(parts[i].end - parts[i].start) + 1}>
            <Audio src={media[VOICE_OF[i]]!.url} />
          </Sequence>
        ))}
      {mode === 'full' && media.voice && <Audio src={media.voice.url} />}
      {music && (
        <Audio src={music.url} loop
          volume={(fr) => (inSpan(fr / FPS, parts[SLOKA]) ? 0.07 : 0.12) *
            interpolate(fr, [0, f(1), total - f(1.5), total], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      )}
      {!server && <Warning text="వీడియో మేకర్ (START_VIDEO_MAKER.bat) తెరవలేదు – క్లిప్‌లు, వాయిస్ కనిపించవు" />}
    </AbsoluteFill>
  );
};
