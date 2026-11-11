// Movie mode: one Valmiki Cinema sarga as a 16:9 film, in the same style as the approved Shorts
// (soft cross-fades, a camera move chosen per picture, warm film look) with titles, voices, scene music and sounds.
import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, useCurrentFrame, Easing} from 'remotion';
import {Audio, Video} from '@remotion/media';
import {FPS, Media} from './timeline';
import {FilmLook, Visual, moveFor} from './Short';
import {TE, TITLE, LAT} from './fonts';
import {ambienceFor, momentFor} from './sound';
import {MovieData, MovieMedia, MovieTimeline} from './movieTimeline';

export type MovieProps = {data: MovieData; media: MovieMedia; timeline: MovieTimeline | null; server: boolean};

const GOLD = '#f6cf6a';
const SCENE_FADE = 1.0; // a slow dissolve from one scene to the next
const SHOT_FADE = 0.5; // a soft dissolve between shots of one scene
const smooth = (fn: (t: number) => number, t: number) => [-0.5, -0.25, 0, 0.25, 0.5].reduce((a, d) => a + fn(t + d), 0) / 5;

const Placeholder: React.FC<{no: number; pic: string}> = ({no, pic}) => (
  <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #5b2a10 0%, #24100a 60%, #0d0604 100%)',
    alignItems: 'center', justifyContent: 'center', padding: '0 220px', textAlign: 'center'}}>
    <div style={{fontFamily: TE, color: 'rgba(246,207,106,.55)', fontSize: 60, fontWeight: 800}}>షాట్ {no}</div>
    <div style={{fontFamily: LAT, color: 'rgba(251,238,210,.4)', fontSize: 30, marginTop: 20, lineHeight: 1.4}}>{pic}</div>
  </AbsoluteFill>
);

// Titles: the film's opening titles big in the middle, a part's title in the centre, a place name small at the lower left.
type CapKind = 'opening' | 'part' | 'place';
const Caption: React.FC<{text: string; kind: CapKind; start: number; end: number; t: number}> = ({text, kind, start, end, t}) => {
  if (t < start || t >= end) return null;
  const fd = Math.min(0.7, (end - start) / 3);   // the fade fits even a short title
  const o = interpolate(t, [start, start + fd, end - fd, end], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rise = interpolate(t, [start, start + 0.9], [18, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const shadow = '0 0 24px rgba(0,0,0,.95), 0 3px 0 rgba(40,15,0,.9)';
  if (kind === 'place')
    return (
      <div style={{position: 'absolute', left: 110, bottom: 120, opacity: o, transform: `translateY(${rise}px)`}}>
        <div style={{width: 70, height: 3, background: GOLD, marginBottom: 12, opacity: 0.85}} />
        <div style={{fontFamily: TE, fontWeight: 700, fontSize: 44, color: '#fff', textShadow: shadow}}>{text}</div>
      </div>
    );
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: kind === 'opening' ? 'center' : 'flex-end', paddingBottom: kind === 'part' ? 150 : 0,
      opacity: o}}>
      <div style={{transform: `translateY(${rise}px)`, textAlign: 'center', maxWidth: 1500}}>
        <div style={{fontFamily: TITLE, fontSize: kind === 'opening' ? 96 : 70, color: GOLD, textShadow: shadow, lineHeight: 1.3}}>{text}</div>
        <div style={{margin: '18px auto 0', width: kind === 'opening' ? 360 : 220, height: 3,
          background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`}} />
      </div>
    </AbsoluteFill>
  );
};

export const Movie: React.FC<MovieProps> = ({data, media, timeline, server}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!timeline) return null;
  const f = (s: number) => Math.round(s * FPS);
  const total = f(timeline.total);
  const sfx = (name: string | null) => (name ? media.shared['sfx_' + name] : undefined);
  const byNo = new Map(timeline.shots.map((s) => [s.no, s]));
  const allShots = data.scenes.flatMap((sc) => sc.shots.map((sh, k) => ({sc, sh, firstOfScene: k === 0, time: byNo.get(sh.no)!})));

  // pictures: up to 3 per shot share its time; a slow dissolve where a scene starts, a softer one between shots
  const visuals: {no: number; pic: string; m: Media | undefined; start: number; end: number; fade: number; k: number}[] = [];
  allShots.forEach(({sh, firstOfScene, time}) => {
    const m = media.shots[String(sh.no)] || {};
    const files = ['clip', 'clip_2', 'clip_3', 'clip_4', 'clip_5', 'clip_6', 'clip_7', 'clip_8'].map((x) => m[x]).filter(Boolean) as Media[];
    const list: (Media | undefined)[] = files.length ? files : [undefined];
    const step = (time.end - time.start) / list.length;
    list.forEach((x, k) => visuals.push({no: sh.no, pic: sh.pic, m: x, start: time.start + k * step, end: time.start + (k + 1) * step,
      fade: k ? 0.4 : firstOfScene ? SCENE_FADE : SHOT_FADE, k: visuals.length}));
  });

  // titles
  const caps: {text: string; kind: CapKind; start: number; end: number}[] = [];
  allShots.forEach(({sh, firstOfScene, time}, idx) => {
    const n = sh.cap.length;
    if (!n || (sh.bumper && media.shared.intro)) return;
    const span = Math.max(1.5 * n, Math.min(time.end - time.start - 0.4, Math.max(4, 3.5 * n)));
    const each = span / n;
    sh.cap.forEach((c, j) => {
      const kind: CapKind = idx === 0 ? 'opening' : firstOfScene && j === 0 ? 'part' : /^తరువాత/.test(c) ? 'part' : 'place';
      caps.push({text: c, kind, start: time.start + 0.4 + j * each, end: time.start + 0.4 + (j + 1) * each});
    });
  });

  // voice: is anyone speaking at time u? (the music steps down under voices and rises when only music plays)
  const spans = timeline.shots.flatMap((s) => s.lines);
  const speaking = (u: number) => spans.some((l) => u >= l.start - 0.2 && u < l.end + 0.2);

  // sounds: the script's own sound note for a shot (fx), the moment a picture shows, a quiet background per scene
  const hits: {at: number; m: Media; vol: number}[] = [];
  allShots.forEach(({sh, time}) => {
    const own = media.shots[String(sh.no)]?.fx;
    if (own) hits.push({at: Math.max(0, time.start - 0.2), m: own, vol: 0.55});
    else {
      const mo = sfx(momentFor(sh.pic));
      if (mo) hits.push({at: Math.max(0, time.start - 0.3), m: mo, vol: 0.4});
    }
  });

  // a shot with its own music (an action or fight beat): it plays over the shot and the scene's music steps aside
  const own = allShots.filter(({sh}) => media.shots[String(sh.no)]?.bgm).map(({sh, time}) => ({m: media.shots[String(sh.no)].bgm, ...time}));
  const inOwn = (u: number) => own.some((o) => u >= o.start && u < o.end);

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{filter: 'contrast(1.04) saturate(1.06) sepia(0.06)'}}>
        {visuals.map((v, k) => {
          const from = f(v.start);
          const nextFade = visuals[k + 1]?.fade ?? SHOT_FADE;
          const last = k === visuals.length - 1;
          return (
            <Sequence key={k} from={from} durationInFrames={Math.max(1, (last ? f(timeline.endCard.start) + f(1) : f(v.end) + f(nextFade + 0.15)) - from)} premountFor={30}>
              <Visual m={v.m} len={v.end - v.start} enter={k ? 'fade' : 'none'} fadeLen={v.fade} move={moveFor(v.pic, v.k)}
                placeholder={<Placeholder no={v.no} pic={v.pic} />} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
      <FilmLook frame={frame} w={1920} h={1080} />
      {caps.map((c, k) => <Caption key={k} {...c} t={t} />)}

      {(timeline.parts || []).map((p) => (
        <Sequence key={'p' + p.si} from={f(p.start)} durationInFrames={Math.max(1, f(p.end - p.start) + f(0.5))}>
          {p.intro ? <Video src={p.url} objectFit="cover" style={{width: '100%', height: '100%'}} /> : <Audio src={p.url} />}
        </Sequence>
      ))}
      {timeline.shots.map((s) => s.lines.map((l, i) => l.url && (
        <Sequence key={`${s.no}-${i}`} from={f(l.start)} durationInFrames={Math.max(1, f(l.end - l.start) + f(0.5))}>
          <Audio src={l.url} />
        </Sequence>
      )))}
      {timeline.scenes.map((sc) => {
        const m = media.scenes[String(sc.si)]?.music;
        const amb = sfx(ambienceFor([data.scenes[sc.si - 1].loc, ...data.scenes[sc.si - 1].shots.map((x) => x.pic)]));
        const from = Math.max(0, sc.start - SCENE_FADE);
        const until = sc.si === timeline.scenes.length ? timeline.total : sc.end + SCENE_FADE;
        const env = (u: number) => interpolate(u, [from, from + 1.5, until - 1.5, until], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <React.Fragment key={sc.si}>
            {m && (
              <Sequence from={f(from)} durationInFrames={Math.max(1, f(until - from))}>
                <Audio src={m.url} loop volume={(fr) => { const u = from + fr / FPS; return smooth((x) => (inOwn(x) ? 0 : speaking(x) ? 0.13 : 0.32), u) * env(u); }} />
              </Sequence>
            )}
            {amb && (
              <Sequence from={f(from)} durationInFrames={Math.max(1, f(until - from))}>
                <Audio src={amb.url} loop volume={(fr) => 0.07 * env(from + fr / FPS)} />
              </Sequence>
            )}
          </React.Fragment>
        );
      })}
      {own.map((o, k) => (
        <Sequence key={'b' + k} from={f(Math.max(0, o.start - 0.3))} durationInFrames={Math.max(1, f(o.end - o.start + 0.9))}>
          <Audio src={o.m.url} volume={(fr) => interpolate(fr, [0, f(0.4), f(o.end - o.start + 0.3), f(o.end - o.start + 0.9)], [0, 0.38, 0.38, 0],
            {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
        </Sequence>
      ))}
      {hits.map((h, k) => (
        <Sequence key={'s' + k} from={f(h.at)} durationInFrames={Math.max(1, total - f(h.at))}>
          <Audio src={h.m.url} volume={h.vol} />
        </Sequence>
      ))}

      {/* the channel banner closes the film */}
      {media.shared.banner && t >= timeline.endCard.start - 0.8 && (
        <AbsoluteFill style={{backgroundColor: '#000', alignItems: 'center', justifyContent: 'center',
          opacity: interpolate(t, [timeline.endCard.start - 0.8, timeline.endCard.start + 0.2], [0, 1], {extrapolateRight: 'clamp'})}}>
          {(media.shared.banner as unknown as {wide?: boolean}).wide ? (
            // the long-video banner (16:9) fills the frame
            <Img src={media.shared.banner.url} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          ) : (
            <>
              {/* only the 9:16 Shorts banner: a soft, dark, blurred copy fills the wide frame behind it */}
              <Img src={media.shared.banner.url} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover',
                filter: 'blur(40px) brightness(.45)', transform: 'scale(1.15)'}} />
              <Img src={media.shared.banner.url} style={{position: 'relative', height: '100%', objectFit: 'contain'}} />
            </>
          )}
        </AbsoluteFill>
      )}
      {!server && (
        <div style={{position: 'absolute', top: 30, left: 30, right: 30, fontFamily: TE, fontSize: 30, color: '#fff', background: 'rgba(160,30,30,.85)',
          padding: '10px 18px', borderRadius: 14, textAlign: 'center'}}>వీడియో మేకర్ (START_VIDEO_MAKER.bat) తెరవలేదు</div>
      )}
    </AbsoluteFill>
  );
};
