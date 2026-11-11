// Presenter mode: the user on camera with the pictures (16:9), edited with energy (user, 2026-11-11):
// quick hook scenes with punch-in zooms, flashes, popping questions and whooshes; the channel intro; the user's welcome
// on camera; then the story, where each topic title slams in with a boom, the films' version has a cool "cinema" look
// with letterbox bars and Valmiki's version a warm golden look, joined by a golden light sweep. The camera box (when
// the user gives a clip) glides between a circle, a 9:16 side panel, a floating card, a split and full screen.
import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, useCurrentFrame, Easing, spring} from 'remotion';
import {Audio, Video} from '@remotion/media';
import {useAudioData, visualizeAudio} from '@remotion/media-utils';
import {FPS, Media} from './timeline';
import {FilmLook, Visual, moveFor} from './Short';
import {TE, TITLE} from './fonts';
import {MOVE, PresenterData, PresenterMedia, PresenterTimeline, Rect, Segment, W, H, camRect, mix, picRect} from './presenterTimeline';

export type PresenterProps = {data: PresenterData; media: PresenterMedia; timeline: PresenterTimeline | null; server: boolean};

const GOLD = '#f6cf6a';
const SHADOW = '0 0 24px rgba(0,0,0,.95), 0 3px 0 rgba(40,15,0,.9)';
const XF = 1.2; // music cross-fade
const BADGE: Record<string, [string, string]> = {film: ['🎬 సినిమాల్లో', '#b3261e'], valmiki: ['📜 వాల్మీకి రామాయణంలో', '#c2520f'],
  sloka: ['🕉️ శ్లోకం', '#7a4fb3']};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Box: React.FC<{r: Rect; children: React.ReactNode; ring?: boolean; style?: React.CSSProperties}> = ({r, children, ring, style}) => (
  <div style={{position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: r.r, overflow: 'hidden', opacity: r.o,
    boxShadow: ring && r.w < W ? `0 0 0 6px ${GOLD}, 0 18px 50px rgba(0,0,0,.6)` : undefined, ...style}}>
    {children}
  </div>
);

const Placeholder: React.FC<{s: Segment; what: string}> = ({s, what}) => (
  <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #5b2a10 0%, #24100a 60%, #0d0604 100%)', alignItems: 'center',
    justifyContent: 'center', textAlign: 'center', padding: 40}}>
    <div style={{fontFamily: TE, color: 'rgba(246,207,106,.6)', fontSize: 44, fontWeight: 800}}>{what} {s.no}</div>
    <div style={{fontFamily: TE, color: 'rgba(251,238,210,.45)', fontSize: 26, marginTop: 12}}>{s.label}</div>
  </AbsoluteFill>
);

// Your photo instead of a video: a slow push-in, a gentle sway and breath, and (with a voice) a small lift and a gold
// glow that follow how loud the voice is at each moment, so the photo feels like it is speaking.
const PhotoCam: React.FC<{photo: Media; len: number; level: number}> = ({photo, len, level}) => {
  const frame = useCurrentFrame();
  const u = frame / FPS;
  const zoom = 1.04 + 0.08 * Math.min(1, u / Math.max(1, len)) + 0.006 * Math.sin(u * 1.6) + 0.025 * level;
  const sway = 0.6 * Math.sin(u * 0.7);
  return (
    <AbsoluteFill>
      <Img src={photo.url} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom}) rotate(${sway}deg)`}} />
      <AbsoluteFill style={{boxShadow: `inset 0 0 ${24 + 70 * level}px rgba(246,207,106,${0.18 + 0.55 * level})`}} />
    </AbsoluteFill>
  );
};
const PhotoCamVoice: React.FC<{photo: Media; voice: Media; len: number}> = ({photo, voice, len}) => {
  const frame = useCurrentFrame();
  const audio = useAudioData(voice.url);
  let level = 0;
  if (audio) {   // the voice's loudness, smoothed over a few frames
    for (let d = 0; d < 3; d++) {
      const v = visualizeAudio({fps: FPS, frame: Math.max(0, frame - d), audioData: audio, numberOfSamples: 16});
      level += v.slice(0, 8).reduce((a, b) => a + b, 0) / 8 / 3;
    }
    level = Math.min(1, level * 6);
  }
  return <PhotoCam photo={photo} len={len} level={level} />;
};

const fade = (t: number, a: number, b: number, d = 0.4) => interpolate(t, [a, a + d, b - d, b], [0, 1, 1, 0], clamp);

export const Presenter: React.FC<PresenterProps> = ({data, media, timeline, server}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!timeline) return null;
  const f = (s: number) => Math.round(s * FPS);
  const total = f(timeline.total);
  const sfx = (n: string) => media.shared['sfx_' + n];
  const segs = data.segments.map((s, i) => ({s, time: timeline.segs[i], m: media.segs[String(s.no)] || {}}));
  const cur = Math.max(0, segs.findIndex((x) => t >= x.time.start && t < x.time.end));
  const now = segs[cur] || segs[segs.length - 1];
  const inIntro = t >= timeline.intro.start && t < timeline.intro.end;
  const inBody = !inIntro && t < timeline.endCard.start;

  // the camera box and the picture area glide from the last segment's layout to this one's
  const prev = segs[cur - 1]?.time.layout ?? now.time.layout;
  const k = interpolate(t, [now.time.start, now.time.start + MOVE], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const cam = mix(camRect(prev), camRect(now.time.layout), k);
  const pic = mix(picRect(prev), picRect(now.time.layout), k);

  // energy: a punch-in at every hook cut and topic title, a white flash on hook cuts, a gold sweep from film to Valmiki
  const since = t - now.time.start;
  const role = now.s.role;
  const punch = role === 'hook' || role === 'title' ? 1 + 0.12 * Math.exp(-since * 5) : 1;
  const flash = role === 'hook' ? interpolate(since, [0, 0.06, 0.32], [0.9, 0.7, 0], clamp) : 0;
  const fromFilm = segs[cur - 1]?.s.role === 'film' && role === 'valmiki';
  const sweep = fromFilm ? interpolate(since, [0, 0.55], [-0.3, 1.3], clamp) : -1;
  // the films' version: cooler, a little desaturated, with letterbox bars; Valmiki's: warm and golden
  const grade = role === 'film' ? 'saturate(.75) contrast(1.08) hue-rotate(-8deg) brightness(.95)'
    : role === 'valmiki' || role === 'sloka' ? 'saturate(1.12) sepia(.12) brightness(1.03)' : undefined;
  const bars = role === 'film' ? interpolate(since, [0, 0.5], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)}) : 0;

  // music: each segment's mood; neighbours with the same track join, stretches cross-fade; quiet under the intro clip
  type Stretch = {url: string; start: number; end: number};
  const music: Stretch[] = [];
  segs.forEach(({s, time}) => {
    const m = media.shared['music_' + s.mood] || media.shared.music_default;
    if (!m) return;
    const last = music[music.length - 1];
    if (last && last.url === m.url) last.end = time.end;
    else music.push({url: m.url, start: time.start, end: time.end});
  });
  if (music.length) music[music.length - 1].end = timeline.total;
  const speaking = (u: number) => segs.some(({time, m}) => (m.voice || m.cam) && u >= time.start && u < time.end - 0.3);
  const hookAt = (u: number) => segs.some(({s, time}) => s.role === 'hook' && u >= time.start && u < time.end);

  // one-shot sounds: a whoosh at each hook cut, a boom on each topic title, a shimmer on the film → Valmiki sweep
  const hits: {at: number; m: Media; vol: number}[] = [];
  segs.forEach(({s, time}, i) => {
    const n = s.role === 'hook' ? 'whoosh' : s.role === 'title' ? 'boom' : segs[i - 1]?.s.role === 'film' && s.role === 'valmiki' ? 'shimmer' : '';
    const m = n && sfx(n);
    if (m) hits.push({at: Math.max(0, time.start - (n === 'whoosh' ? 0.25 : 0.05)), m, vol: n === 'boom' ? 0.6 : 0.45});
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#0d0604'}}>
      {/* the channel intro clip, after the hooks, with its own sound */}
      {media.shared.intro && timeline.intro.end > 0 && (
        <Sequence from={f(timeline.intro.start)} durationInFrames={Math.max(1, f(timeline.intro.end - timeline.intro.start))}>
          <Video src={media.shared.intro.url} objectFit="cover" style={{width: W, height: H}} />
        </Sequence>
      )}

      {inBody && (
        <AbsoluteFill style={{transform: `scale(${punch})`, filter: grade}}>
          {/* behind everything: the segment's first picture, soft and dark, so a gliding box never leaves black gaps */}
          {(() => {
            const bg = ['pic', 'pic_2', 'pic_3'].map((x) => now.m[x]).find((p) => p && !p.video);
            return bg ? <Img src={bg.url} style={{position: 'absolute', inset: -60, width: W + 120, height: H + 120, objectFit: 'cover',
              filter: 'blur(36px) brightness(.45) saturate(1.2)'}} /> : null;
          })()}
          {/* pictures of each segment share its time, in the picture area */}
          <Box r={pic}>
            {segs.map(({s, time, m}, i) => {
              const files = ['pic', 'pic_2', 'pic_3'].map((x) => m[x]).filter(Boolean) as Media[];
              const list: (Media | undefined)[] = files.length ? files : [undefined];
              const step = (time.end - time.start) / list.length;
              return list.map((p, j) => (
                <Sequence key={`${i}-${j}`} from={f(time.start + j * step)} durationInFrames={Math.max(1, f(step + 0.5))} premountFor={30}>
                  <Visual m={p} len={step} enter={i === 0 && j === 0 ? 'none' : s.role === 'hook' ? 'none' : 'fade'} fadeLen={0.45}
                    move={moveFor(s.label, i + j)} placeholder={<Placeholder s={s} what="చిత్రం" />} />
                </Sequence>
              ));
            })}
            <FilmLook frame={frame} w={W} h={H} />
          </Box>
        </AbsoluteFill>
      )}

      {/* letterbox bars on the films' version */}
      {inBody && bars > 0 && (
        <>
          <div style={{position: 'absolute', left: pic.x, top: 0, width: pic.w, height: 96 * bars, background: '#000'}} />
          <div style={{position: 'absolute', left: pic.x, bottom: 0, width: pic.w, height: 96 * bars, background: '#000'}} />
        </>
      )}

      {/* the user's camera clip: its own sound unless an ElevenLabs voice is given for that segment */}
      {inBody && (now.time.hasCam || segs[cur - 1]?.time.hasCam) && (
        <Box r={cam} ring>
          {segs.map(({s, time, m}) => m.cam && (
            <Sequence key={s.no} from={f(time.start)} durationInFrames={Math.max(1, f(time.end - time.start))}>
              {m.cam.video ? <Video src={m.cam.url} muted={!!m.voice} objectFit="cover" style={{width: '100%', height: '100%'}} />
                : m.voice ? <PhotoCamVoice photo={m.cam} voice={m.voice} len={time.end - time.start} />
                : <PhotoCam photo={m.cam} len={time.end - time.start} level={0} />}
            </Sequence>
          ))}
        </Box>
      )}
      {segs.map(({s, time, m}) => m.cam && m.cam.video && !m.voice && time.layout === 'pic' && (
        <Sequence key={'a' + s.no} from={f(time.start)} durationInFrames={Math.max(1, f(time.end - time.start))}>
          <Audio src={m.cam.url} />
        </Sequence>
      ))}
      {segs.map(({s, time, m}) => m.voice && (
        <Sequence key={'v' + s.no} from={f(time.start)} durationInFrames={Math.max(1, f(time.end - time.start))}>
          <Audio src={m.voice.url} />
        </Sequence>
      ))}

      {/* flashes and the golden sweep */}
      {flash > 0 && <AbsoluteFill style={{backgroundColor: '#fff6df', opacity: flash}} />}
      {sweep > -0.3 && sweep < 1.3 && (
        <AbsoluteFill style={{background: `linear-gradient(100deg, transparent ${sweep * 100 - 18}%, rgba(255,214,120,.85) ${sweep * 100}%, transparent ${sweep * 100 + 18}%)`,
          mixBlendMode: 'screen'}} />
      )}

      {/* words on screen */}
      {inBody && segs.map(({s, time}) => {
        if (t < time.start || t >= time.end) return null;
        const o = fade(t, time.start, time.end, 0.3);
        const b = BADGE[s.role];
        const area = pic;
        const pop = spring({frame: frame - f(time.start + 0.15), fps: FPS, config: {damping: 11, stiffness: 160}});
        return (
          <React.Fragment key={'l' + s.no}>
            {b && (
              <div style={{position: 'absolute', left: area.x + 48, top: 44 + 96 * bars, opacity: o, transform: `scale(${0.7 + 0.3 * pop})`,
                transformOrigin: 'left center', background: b[1], color: '#fff', fontFamily: TE, fontWeight: 800, fontSize: 34,
                padding: '10px 26px', borderRadius: 999, boxShadow: '0 6px 20px rgba(0,0,0,.45)'}}>{b[0]}</div>
            )}
            {s.role === 'hook' && (
              <div style={{position: 'absolute', left: 0, right: 0, bottom: 110, display: 'flex', justifyContent: 'center', opacity: o}}>
                <div style={{transform: `scale(${0.5 + 0.5 * pop})`, fontFamily: TITLE, fontSize: 84, color: '#fff', textAlign: 'center',
                  maxWidth: 1600, lineHeight: 1.25, textShadow: `${SHADOW}, 0 0 40px rgba(246,207,106,.55)`}}>
                  {s.onscreen || s.text.split('?')[0] + '?'}
                </div>
              </div>
            )}
            {s.role === 'title' && (
              <div style={{position: 'absolute', left: area.x, top: 0, width: area.w, height: H, display: 'flex', alignItems: 'center',
                justifyContent: 'center', opacity: o, padding: 60, textAlign: 'center'}}>
                <div style={{transform: `scale(${1.5 - 0.5 * pop})`, opacity: Math.min(1, pop * 1.4), fontFamily: TITLE, fontSize: 80, color: GOLD,
                  textShadow: SHADOW, lineHeight: 1.3}}>{s.text}</div>
              </div>
            )}
            {s.role === 'sloka' && (
              <div style={{position: 'absolute', left: area.x + 80, top: 160, width: Math.min(area.w, cam.x) - 160, opacity: o,
                fontFamily: TE, fontWeight: 800, fontSize: 52, color: '#fff7e0', textShadow: SHADOW, lineHeight: 1.55}}>
                {s.text.split(/[।॥]/).filter((x) => x.trim()).map((x, j) => (
                  <div key={j} style={{opacity: interpolate(t, [time.start + 0.3 + j * 0.5, time.start + 0.8 + j * 0.5], [0, 1], clamp)}}>{x.trim()}</div>
                ))}
                <div style={{fontSize: 30, color: GOLD, marginTop: 16}}>{s.onscreen.split('—').pop()}</div>
              </div>
            )}
            {s.onscreen && !['title', 'sloka', 'hook', 'film'].includes(s.role) && (
              <div style={{position: 'absolute', left: area.x + 48, bottom: 56, maxWidth: area.w - 96, opacity: o, fontFamily: TE,
                transform: `translateX(${(1 - pop) * -60}px)`, fontWeight: 700, fontSize: 34, color: '#fff', background: 'rgba(0,0,0,.55)',
                padding: '12px 22px', borderRadius: 14, borderLeft: `6px solid ${GOLD}`}}>{s.onscreen}</div>
            )}
          </React.Fragment>
        );
      })}

      {music.map((g, i) => {
        const from = f(Math.max(0, g.start - XF / 2));
        const n = music.length;
        return (
          <Sequence key={'m' + i} from={from} durationInFrames={Math.max(1, Math.min(total, f(g.end + XF / 2)) - from)}>
            <Audio src={g.url} loop volume={(fr) => {
              const u = (from + fr) / FPS;
              const inn = i ? interpolate(u, [g.start - XF / 2, g.start + XF / 2], [0, 1], clamp) : 1;
              const out = i < n - 1 ? interpolate(u, [g.end - XF / 2, g.end + XF / 2], [1, 0], clamp) : 1;
              const ends = interpolate(u, [0, 0.3, timeline.total - 2, timeline.total], [0, 1, 1, 0], clamp);
              const underIntro = u >= timeline.intro.start && u < timeline.intro.end ? 0.15 : 1;
              const level = hookAt(u) ? 0.16 : speaking(u) ? 0.09 : 0.22;   // hooks ride higher for energy
              return level * inn * out * ends * underIntro;
            }} />
          </Sequence>
        );
      })}
      {hits.map((h, i) => (
        <Sequence key={'h' + i} from={f(h.at)} durationInFrames={Math.max(1, total - f(h.at))}>
          <Audio src={h.m.url} volume={h.vol} />
        </Sequence>
      ))}

      {/* the channel banner at the end */}
      {t >= timeline.endCard.start && (
        <AbsoluteFill style={{opacity: fade(t, timeline.endCard.start, timeline.total + 1, 0.6)}}>
          {media.shared.banner ? <Img src={media.shared.banner.url} style={{width: W, height: H, objectFit: 'cover'}} />
            : <AbsoluteFill style={{background: '#1a0c06', alignItems: 'center', justifyContent: 'center'}}>
                <div style={{fontFamily: TITLE, fontSize: 80, color: GOLD}}>{data.headline}</div></AbsoluteFill>}
        </AbsoluteFill>
      )}
      {!server && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, background: '#b3261e', color: '#fff', fontFamily: TE, fontSize: 28,
          padding: 10, textAlign: 'center'}}>వీడియో మేకర్ (START_VIDEO_MAKER.bat) తెరవలేదు – మీ వీడియో, చిత్రాలు కనిపించవు</div>
      )}
    </AbsoluteFill>
  );
};
