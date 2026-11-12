// వైభవం mode: a Rama or Krishna elevation Short (1080x1920). The clips in order with soft, quick cross-fades and a
// camera move on still pictures, the hook's bold headline, Telugu subtitles of the voice, and for a LOOP Short its
// caption on top the whole time (the last frame flows back into the first). Sound: the ready voice-and-music file
// (or a loop's music). No lightning or flash effects (the user's choice, 2026-11-12).
import React from 'react';
import {AbsoluteFill, Easing, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import {FPS, Media} from './timeline';
import {FilmLook, Move, Visual, moveFor} from './Short';
import {TE, TITLE, LAT} from './fonts';
import {HEADLINE, VClip, VEdit, VMedia, VShort, VTimeline} from './vaibhavamTimeline';

export type VaibhavamProps = {series: string; seriesTe: string; short: VShort; media: VMedia; timeline: VTimeline | null; server: boolean; edit?: VEdit};

// a picture's camera move follows its clip's planned camera (push-in → zoom in, pull-back → zoom out, crane up / tilt up
// → up, drone sweeping down / top-down → down, follow / fly-through / tracking / orbit → a pan); a climax line gets a
// quick punch-in unless its camera reveals (pull-back, sweep down, crane up); otherwise the scene's own words decide
export function vMove(c: VClip, k: number): Move {
  const cam = (c.move || '').toLowerCase();
  const reveal = /pull-?back|pull out|zoom out|sweeping down|crane up/.test(cam);
  if (c.climax && !reveal) return 'punch';
  if (/pull-?back|pull out|zoom out/.test(cam)) return 'out';
  if (/push-?in|zoom in|dolly in/.test(cam)) return 'in';
  if (/crane up|rising|tilt up/.test(cam)) return 'up';
  if (/sweeping down|tilt down|crane down|top-down shot following the fall/.test(cam)) return 'down';
  if (/right to left/.test(cam)) return 'panL';
  if (/left to right/.test(cam)) return 'panR';
  if (/follow|fly-through|tracking|orbit|along|sweep|moving/.test(cam)) return k % 2 ? 'panR' : 'panL';
  return moveFor(c.shows, k);
}

const YELLOW = '#ffd400';
const FADE = 0.3;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Placeholder: React.FC<{no: number; shows: string}> = ({no, shows}) => (
  <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #5b2a10 0%, #24100a 60%, #0d0604 100%)',
    alignItems: 'center', justifyContent: 'center', padding: '0 90px', textAlign: 'center'}}>
    <div style={{fontFamily: TE, color: 'rgba(246,207,106,.6)', fontSize: 70, fontWeight: 800}}>క్లిప్ {no}</div>
    <div style={{fontFamily: LAT, color: 'rgba(251,238,210,.45)', fontSize: 34, marginTop: 24, lineHeight: 1.4}}>{shows}</div>
  </AbsoluteFill>
);

// the headline with its key word in yellow
const Marked: React.FC<{text: string; hl: string}> = ({text, hl}) => {
  const i = hl ? text.indexOf(hl) : -1;
  if (i < 0) return <>{text}</>;
  return <>{text.slice(0, i)}<span style={{color: YELLOW}}>{hl}</span>{text.slice(i + hl.length)}</>;
};

const stroke = {WebkitTextStroke: '12px #140800', paintOrder: 'stroke fill' as const, textShadow: '0 6px 24px rgba(0,0,0,.85)'};

export const Vaibhavam: React.FC<VaibhavamProps> = ({short, media, timeline, server, edit = {}}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!timeline) return null;
  const f = (s: number) => Math.round(s * FPS);
  const total = f(timeline.total);
  const files = (no: number) => ['', '_2', '_3'].map((x) => `clip${no}${x}`).filter((k) => media[k]);

  // pictures: up to 3 per clip share its time; a quick soft dissolve between them. Each file keeps its own edit
  // (speed, trim, own sound, camera move) from the page; the camera move is otherwise chosen from the scene.
  const visuals: {no: number; shows: string; m: Media | undefined; slot: string; move: Move; start: number; end: number; k: number}[] = [];
  timeline.clips.forEach((c, i) => {
    const sc = short.clips[i];
    const list = files(c.no).length ? files(c.no) : [''];
    const step = (c.end - c.start) / list.length;
    list.forEach((slot, j) => {
      const k = visuals.length;
      const chosen = edit[slot]?.move;
      visuals.push({no: c.no, shows: sc.shows, m: slot ? media[slot] : undefined, slot, k,
        move: chosen && chosen !== 'auto' ? chosen : vMove(sc, i * 3 + j), start: c.start + j * step, end: c.start + (j + 1) * step});
    });
  });

  // scene sounds: each clip's own (bow, arrow, thunder, crash…) at its moment, over the voice and music
  const hits: {at: number; m: Media; vol: number}[] = [];
  timeline.clips.forEach((c, i) => (short.clips[i].sfx || []).forEach(([name, at, vol]) => {
    const m = media['sfx_' + name];
    if (m) hits.push({at: c.start + at * (c.end - c.start), m, vol});
  }));
  const sub = timeline.subs.find((c) => t >= c.start && t < c.end);
  const head = short.loop ? 1 : interpolate(t, [0, 0.25, HEADLINE - 0.35, HEADLINE], [0, 1, 1, 0], clamp);
  const pop = short.loop ? 1 : interpolate(t, [0, 0.3], [0.82, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{filter: 'contrast(1.05) saturate(1.1)'}}>
        {visuals.map((v, k) => {
          const from = f(v.start);
          const last = k === visuals.length - 1;
          return (
            <Sequence key={k} from={from} durationInFrames={Math.max(1, (last ? total : f(v.end) + f(FADE + 0.1)) - from)} premountFor={30}>
              <Visual m={v.m} len={v.end - v.start} enter={k ? 'fade' : 'none'} fadeLen={FADE} move={v.move}
                edit={edit[v.slot] || {}} placeholder={<Placeholder no={v.no} shows={v.shows} />} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
      <FilmLook frame={frame} />

      {/* the hook's headline (a loop keeps its caption on top the whole time) */}
      {head > 0 && (
        <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: short.loop ? 170 : 300, opacity: head}}>
          <div style={{transform: `scale(${pop})`, textAlign: 'center', maxWidth: 960, fontFamily: TITLE, color: '#fff',
            fontSize: short.loop ? 76 : 104, lineHeight: 1.25, ...stroke}}>
            <Marked text={short.loop ? short.caption : short.headline} hl={short.hl} />
          </div>
        </AbsoluteFill>
      )}

      {/* subtitles of the voice */}
      {sub && (
        <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 430}}>
          <div style={{maxWidth: 940, textAlign: 'center', fontFamily: TE, fontWeight: 800, fontSize: 64, lineHeight: 1.3, color: '#fff', ...stroke,
            WebkitTextStroke: '10px #120700'}}>{sub.text}</div>
        </AbsoluteFill>
      )}

      {timeline.audio && <Audio src={timeline.audio.url} />}
      {hits.map((h, k) => (
        <Sequence key={'s' + k} from={f(h.at)} durationInFrames={Math.max(1, Math.min(total - f(h.at), f((h.m.dur || 3) + 0.2)))}>
          <Audio src={h.m.url} volume={h.vol} />
        </Sequence>
      ))}
      {/* with the scene's own sounds (a laugh, cows, birds) the music steps back a little so they come through */}
      {timeline.music && <Audio src={timeline.music.url} loop={short.loop} volume={timeline.audio ? 0.35 : media.sounds ? 0.55 : 1} />}
      {media.sounds && <Audio src={media.sounds.url} volume={1} />}

      {!server && (
        <div style={{position: 'absolute', top: 40, left: 40, right: 40, fontFamily: TE, fontSize: 34, color: '#fff', background: 'rgba(160,30,30,.85)',
          padding: '12px 20px', borderRadius: 16, textAlign: 'center'}}>వీడియో మేకర్ (START_VIDEO_MAKER.bat) తెరవలేదు</div>
      )}
    </AbsoluteFill>
  );
};
