import React from 'react';
import {CalculateMetadataFunction, Composition, Folder} from 'remotion';
import {SARGAS} from './data';
import {Short, ShortProps} from './Short';
import {FPS, makeTimeline} from './timeline';

// The Video Maker page (maker/server.mjs) keeps the clips, voice and music and tells us their lengths.
export const MAKER = 'http://localhost:3333';

export const compId = (kandaEn: string, sarga: number, n: number) =>
  `${kandaEn}-S${String(sarga).padStart(3, '0')}-Sloka-${String(n).padStart(3, '0')}`;

type Props = ShortProps & {kanda: string};

const metadata: CalculateMetadataFunction<Props> = async ({props, abortSignal}) => {
  let media = {};
  let server = false;
  try {
    const q = `k=${props.kanda}&s=${props.sarga}&n=${props.sloka.n}`;
    const r = await fetch(`${MAKER}/api/media?${q}`, {signal: abortSignal});
    media = (await r.json()).media;
    server = true;
  } catch (e) {
    // page not running: show the layout with empty clip slots
  }
  const timeline = makeTimeline(media);
  return {durationInFrames: Math.ceil(timeline.total * FPS), props: {...props, media, timeline, server}};
};

export const Root: React.FC = () => (
  <>
    {SARGAS.map((d) => (
      <Folder key={d.kanda + d.sarga} name={`${d.kandaEn}-Sarga-${String(d.sarga).padStart(3, '0')}`}>
        {d.slokas.map((s) => (
          <Composition
            key={s.n}
            id={compId(d.kandaEn, d.sarga, s.n)}
            component={Short as unknown as React.FC<Props>}
            width={1080}
            height={1920}
            fps={FPS}
            durationInFrames={45 * FPS}
            defaultProps={{kanda: d.kanda, kandaTe: d.kandaTe, sarga: d.sarga, sloka: s, media: {}, timeline: null, server: false} as Props}
            calculateMetadata={metadata}
          />
        ))}
      </Folder>
    ))}
  </>
);
