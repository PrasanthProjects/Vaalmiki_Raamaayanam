// Presenter mode (user, 2026-11-11): the user on camera explaining, the pictures beside, around or behind them.
// Each segment has the user's camera clip (cam, with its own sound), and/or an ElevenLabs voice, and up to three
// pictures or clips. The camera box moves between layouts like an editor would cut a well-made explainer.
import type {Media} from './timeline';

export type Layout = 'full' | 'pic' | 'circle-br' | 'circle-bl' | 'circle-tr' | 'circle-tl' | 'side-left' | 'side-right'
  | 'split' | 'card-right' | 'card-left';
export const LAYOUTS: Layout[] = ['full', 'pic', 'circle-br', 'circle-bl', 'circle-tr', 'circle-tl', 'side-left', 'side-right',
  'split', 'card-right', 'card-left'];

export type Segment = {no: number; role: string; label: string; text: string; onscreen: string; layout: Layout; mood: string;
  est: number; refs?: string[]};
export type PresenterData = {id: string; kind: 'presenter'; title: string; headline: string; badge: string; segments: Segment[]};
// media: per segment (cam, voice, pic, pic_2, pic_3), the user's layout choices, and shared files (music, banner, intro)
export type PresenterMedia = {segs: Record<string, Record<string, Media>>; layouts: Record<string, Layout>;
  shared: Record<string, Media>};

export type SegTime = {no: number; start: number; end: number; layout: Layout; hasCam: boolean};
export type PresenterTimeline = {segs: SegTime[]; intro: {start: number; end: number}; endCard: {start: number; end: number}; total: number};

export const W = 1920, H = 1080;
export const GAP = 0.35; // a breath after each segment
export const END_CARD = 5; // the channel banner at the end
export const MOVE = 0.7; // seconds the camera box takes to glide to its new place

export function makePresenterTimeline(d: PresenterData, media: PresenterMedia): PresenterTimeline {
  // the hooks first, then the channel intro clip, then the rest (user, 2026-11-11)
  const introLen = media.shared.intro?.dur || 0;
  let intro = {start: 0, end: 0};
  let t = 0;
  const segs: SegTime[] = d.segments.map((s) => {
    if (s.role !== 'hook' && intro.end === 0 && introLen) {
      intro = {start: t, end: t + introLen};
      t += introLen;
    }
    const m = media.segs[String(s.no)] || {};
    const len = m.voice?.dur || m.cam?.dur || s.est;   // a voice sets the length; else the camera clip; else the plan
    const hasCam = !!m.cam;
    const chosen = media.layouts[String(s.no)] || s.layout;
    // a photo instead of a video: not a still full screen – beside the pictures (unless the user chose 'full')
    const photoFull = hasCam && !m.cam!.video && !media.layouts[String(s.no)] && chosen === 'full';
    const layout: Layout = !hasCam ? 'pic' : photoFull ? 'side-left' : chosen;   // no camera clip: pictures only
    const seg = {no: s.no, start: t, end: t + len + GAP, layout, hasCam};
    t = seg.end;
    return seg;
  });
  const endCard = {start: t, end: t + END_CARD};
  return {segs, intro, endCard, total: endCard.end};
}

// where the camera box and the picture area sit for each layout (1920x1080)
export type Rect = {x: number; y: number; w: number; h: number; r: number; o: number};
const M = 56; // margin from the frame edge
const C = 400; // circle size
const PW = Math.round((H * 9) / 16); // a 9:16 panel the full height: 608
const CW = 420, CH = Math.round((CW * 16) / 9); // a floating 9:16 card
export function camRect(l: Layout): Rect {
  switch (l) {
    case 'full': return {x: 0, y: 0, w: W, h: H, r: 0, o: 1};
    case 'circle-br': return {x: W - C - M, y: H - C - M, w: C, h: C, r: C / 2, o: 1};
    case 'circle-bl': return {x: M, y: H - C - M, w: C, h: C, r: C / 2, o: 1};
    case 'circle-tr': return {x: W - C - M, y: M, w: C, h: C, r: C / 2, o: 1};
    case 'circle-tl': return {x: M, y: M, w: C, h: C, r: C / 2, o: 1};
    case 'side-left': return {x: 0, y: 0, w: PW, h: H, r: 0, o: 1};
    case 'side-right': return {x: W - PW, y: 0, w: PW, h: H, r: 0, o: 1};
    case 'split': return {x: W / 2, y: 0, w: W / 2, h: H, r: 0, o: 1};
    case 'card-right': return {x: W - CW - M, y: (H - CH) / 2, w: CW, h: CH, r: 28, o: 1};
    case 'card-left': return {x: M, y: (H - CH) / 2, w: CW, h: CH, r: 28, o: 1};
    default: return {x: W - C / 2 - M, y: H - C / 2 - M, w: C / 2, h: C / 2, r: C / 4, o: 0};   // 'pic': shrinks away
  }
}
export function picRect(l: Layout): Rect {
  switch (l) {
    case 'side-left': return {x: PW, y: 0, w: W - PW, h: H, r: 0, o: 1};
    case 'side-right': return {x: 0, y: 0, w: W - PW, h: H, r: 0, o: 1};
    case 'split': return {x: 0, y: 0, w: W / 2, h: H, r: 0, o: 1};
    default: return {x: 0, y: 0, w: W, h: H, r: 0, o: 1};
  }
}
export const mix = (a: Rect, b: Rect, k: number): Rect => ({x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, w: a.w + (b.w - a.w) * k,
  h: a.h + (b.h - a.h) * k, r: a.r + (b.r - a.r) * k, o: a.o + (b.o - a.o) * k});
