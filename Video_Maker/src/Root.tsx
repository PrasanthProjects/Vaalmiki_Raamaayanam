import React from 'react';
import {CalculateMetadataFunction, Composition, Folder} from 'remotion';
import {MOVIES, PRESENTERS, SARGAS, VAIBHAVAM} from './data';
import {Vaibhavam, VaibhavamProps} from './Vaibhavam';
import {VSeries, VShort, makeVaibhavamTimeline} from './vaibhavamTimeline';
import {Short, ShortProps} from './Short';
import {FPS, makeTimeline} from './timeline';
import {Movie, MovieProps} from './Movie';
import {MovieData, makeMovieTimeline} from './movieTimeline';
import {Presenter, PresenterProps} from './Presenter';
import {PresenterData, makePresenterTimeline} from './presenterTimeline';

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

// movie mode: one composition per Valmiki Cinema script (ids allow only letters, digits and '-')
export const movieId = (d: {id: string; mode?: string; kandaEn: string; file: string}) =>
  d.mode === 'long' ? d.id : `Cinema-${d.kandaEn}-${d.file.replace(/_/g, '-')}`;
const movieMetadata: CalculateMetadataFunction<MovieProps> = async ({props, abortSignal}) => {
  let media = {shots: {}, scenes: {}, shared: {}};
  let server = false;
  try {
    const r = await fetch(`${MAKER}/api/movie-media?id=${encodeURIComponent(props.data.id)}`, {signal: abortSignal});
    media = (await r.json()).media;
    server = true;
  } catch (e) {
    // page not running: the layout with empty shots
  }
  const timeline = makeMovieTimeline(props.data, media);
  return {durationInFrames: Math.ceil(timeline.total * FPS), props: {...props, media, timeline, server}};
};

// presenter mode: the user on camera with the pictures (maker/presenter.html)
const presenterMetadata: CalculateMetadataFunction<PresenterProps> = async ({props, abortSignal}) => {
  let media = {segs: {}, layouts: {}, shared: {}};
  let server = false;
  try {
    const r = await fetch(`${MAKER}/api/presenter-media?pid=${encodeURIComponent(props.data.id)}`, {signal: abortSignal});
    media = (await r.json()).media;
    server = true;
  } catch (e) {
    // page not running: the layout with empty boxes
  }
  const timeline = makePresenterTimeline(props.data, media);
  return {durationInFrames: Math.ceil(timeline.total * FPS), props: {...props, media, timeline, server}};
};

// వైభవం mode: the Rama and Krishna elevation Shorts (maker/vaibhavam.html)
export const vaibhavamId = (id: string) => `Vaibhavam-${id}`;
const vaibhavamMetadata: CalculateMetadataFunction<VaibhavamProps> = async ({props, abortSignal}) => {
  let media = {};
  let edit = {};
  let server = false;
  try {
    const r = await fetch(`${MAKER}/api/vaibhavam-media?vid=${encodeURIComponent(props.short.id)}`, {signal: abortSignal});
    const j = await r.json();
    media = j.media;
    edit = j.edit || {};
    server = true;
  } catch (e) {
    // page not running: the layout with empty clips
  }
  const timeline = makeVaibhavamTimeline(props.short, media);
  return {durationInFrames: Math.ceil(timeline.total * FPS), props: {...props, media, edit, timeline, server}};
};

export const Root: React.FC = () => (
  <>
    {(VAIBHAVAM as unknown as VSeries[]).map((d) => (
      <Folder key={d.series} name={`Vaibhavam-${d.series}`}>
        {d.shorts.map((s: VShort) => (
          <Composition
            key={s.id}
            id={vaibhavamId(s.id)}
            component={Vaibhavam as unknown as React.FC<VaibhavamProps>}
            width={1080}
            height={1920}
            fps={FPS}
            durationInFrames={Math.ceil((s.planLength + 2) * FPS)}
            defaultProps={{series: d.series, seriesTe: d.seriesTe, short: s, media: {}, timeline: null, server: false}}
            calculateMetadata={vaibhavamMetadata}
          />
        ))}
      </Folder>
    ))}
    <Folder name="Presenter">
      {PRESENTERS.map((d) => (
        <Composition
          key={d.id}
          id={d.id}
          component={Presenter as unknown as React.FC<PresenterProps>}
          width={1920}
          height={1080}
          fps={FPS}
          durationInFrames={60 * FPS}
          defaultProps={{data: d as unknown as PresenterData, media: {segs: {}, layouts: {}, shared: {}}, timeline: null, server: false}}
          calculateMetadata={presenterMetadata}
        />
      ))}
    </Folder>
    <Folder name="Valmiki-Cinema">
      {MOVIES.map((d) => (
        <Composition
          key={d.id}
          id={movieId(d)}
          component={Movie as unknown as React.FC<MovieProps>}
          width={1920}
          height={1080}
          fps={FPS}
          durationInFrames={Math.ceil(d.planLength * FPS)}
          defaultProps={{data: d as unknown as MovieData, media: {shots: {}, scenes: {}, shared: {}}, timeline: null, server: false}}
          calculateMetadata={movieMetadata}
        />
      ))}
    </Folder>
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
