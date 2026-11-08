// When each part and clip plays.
// Parts: హుక్ · శ్లోక పఠనం · పదార్థం (2 s, no voice, same picture) · తాత్పర్యం & జీవిత పాఠం · ముగింపు.
export type Media = {url: string; video: boolean; dur: number | null; name: string};
export type MediaMap = Record<string, Media | undefined>;
export type Span = {start: number; end: number};
export type Timeline = {
  mode: 'parts' | 'full' | 'none';
  parts: Span[]; // HOOK, SLOKA, WORDS, MEANING, END
  speech: Span[]; // where the words of each part are spoken (subtitle timing)
  clips: (Span | null)[]; // clip1 … clip7 (clip3 only when given)
  total: number;
};
export const HOOK = 0, SLOKA = 1, WORDS = 2, MEANING = 3, END = 4;

export const FPS = 30;
export const WORDS_HOLD = 2; // the word meanings stay this long after the chanting, with no voice
const PLAN = [4, 11, WORDS_HOLD, 23, 7]; // seconds; the voice parts follow the kit's 45 s plan
const AFTER_VOICE = [0.35, 0.3, 0, 0.35, 0.3]; // a breath after each voice part
export const END_HOLD = 1.2; // the closing card stays a little after the last word
// voice files for HOOK, SLOKA, MEANING, END (no voice during WORDS)
export const VOICE_OF: Record<number, string> = {[HOOK]: 'voice1', [SLOKA]: 'voice2', [MEANING]: 'voice3', [END]: 'voice4'};

export function makeTimeline(media: MediaMap): Timeline {
  const voiced = [HOOK, SLOKA, MEANING, END];
  let durs: number[];
  let speechLen: number[];
  let mode: Timeline['mode'];
  if (voiced.some((p) => media[VOICE_OF[p]]?.dur)) {
    mode = 'parts';
    speechLen = PLAN.map((p, i) => (i === WORDS ? 0 : media[VOICE_OF[i]]?.dur ?? p - AFTER_VOICE[i]));
    durs = speechLen.map((d, i) => (i === WORDS ? WORDS_HOLD : d + AFTER_VOICE[i]));
  } else if (media.voice?.dur) {
    // One recording for everything: it cannot pause, so the word list shows over the start of the meaning.
    mode = 'full';
    const k = (media.voice.dur + 0.3) / 45;
    durs = PLAN.map((p, i) => (i === WORDS ? 0 : p * k));
    speechLen = durs.map((d) => Math.max(0, d - 0.15));
  } else {
    mode = 'none';
    durs = [...PLAN];
    speechLen = durs.map((d, i) => (i === WORDS ? 0 : d - 0.3));
  }
  durs[END] += END_HOLD;
  const parts: Span[] = [];
  const speech: Span[] = [];
  let t = 0;
  durs.forEach((d, i) => {
    parts.push({start: t, end: t + d});
    speech.push({start: t + 0.05, end: t + speechLen[i]});
    t += d;
  });
  if (mode === 'full') parts[WORDS] = {start: parts[MEANING].start, end: parts[MEANING].start + WORDS_HOLD};

  const clips: (Span | null)[] = Array(7).fill(null);
  clips[0] = parts[HOOK];
  clips[1] = {start: parts[SLOKA].start, end: Math.max(parts[SLOKA].end, parts[WORDS].end)}; // one picture for śloka + words
  // the meaning narration: clips 4, 5, 6 (and clip 3 first, if one was made)
  const m = {start: clips[1].end, end: parts[MEANING].end};
  const order = media.clip3 ? [2, 3, 4, 5] : [3, 4, 5];
  const w = media.clip3 ? [5, 8, 8, 7] : [8, 8, 7];
  const sum = w.reduce((a, b) => a + b, 0);
  let c = m.start;
  order.forEach((ci, k) => {
    const d = ((m.end - m.start) * w[k]) / sum;
    clips[ci] = {start: c, end: c + d};
    c += d;
  });
  clips[6] = parts[END];
  return {mode, parts, speech, clips, total: t};
}

// Cut words into k pieces of even length, liking breaks after a comma (small search: a sentence has few words).
function balance(words: string[], k: number): string[] {
  if (k <= 1 || words.length <= 1) return [words.join(' ')];
  const n = words.length;
  const len = (a: number, b: number) => words.slice(a, b).join(' ').length;
  const target = words.join(' ').length / k;
  const memo = new Map<string, {cost: number; cuts: number[]}>();
  const best = (a: number, left: number): {cost: number; cuts: number[]} => {
    const key = a + ',' + left;
    if (memo.has(key)) return memo.get(key)!;
    let r = {cost: Infinity, cuts: [] as number[]};
    if (left === 1) r = {cost: (len(a, n) - target) ** 2, cuts: []};
    else
      for (let b = a + 1; b <= n - left + 1; b++) {
        const comma = /[,;:]$/.test(words[b - 1]) ? -40 : 0;
        const rest = best(b, left - 1);
        const c = (len(a, b) - target) ** 2 + comma + rest.cost;
        if (c < r.cost) r = {cost: c, cuts: [b, ...rest.cuts]};
      }
    memo.set(key, r);
    return r;
  };
  const cuts = [0, ...best(0, k).cuts, n];
  return cuts.slice(0, -1).map((a, i) => words.slice(a, cuts[i + 1]).join(' '));
}

// Subtitle lines: short phrases, broken at punctuation, timed by their length inside the spoken span.
export type Cue = {start: number; end: number; text: string};
export function cues(text: string, span: Span, maxChars = 24): Cue[] {
  // whole sentences; a short one joins the next; a long one is cut into even pieces at word breaks
  const sentences = text.replace(/\s+/g, ' ').trim().split(/(?<=[.!?…])\s+/).filter(Boolean);
  const joined: string[] = [];
  for (const s of sentences) {
    const last = joined[joined.length - 1];
    if (last && (last.length < 14 || s.length < 14) && (last + ' ' + s).length <= maxChars) joined[joined.length - 1] = last + ' ' + s;
    else joined.push(s);
  }
  const lines: string[] = [];
  for (const s of joined) {
    lines.push(...balance(s.split(' '), Math.ceil(s.length / maxChars)));
  }
  const weight = (s: string) => s.replace(/\s/g, '').length + 4;
  const total = lines.reduce((a, l) => a + weight(l), 0);
  const len = span.end - span.start;
  let t = span.start;
  return lines.map((l) => {
    const d = (len * weight(l)) / total;
    const c = {start: t, end: t + d, text: l};
    t += d;
    return c;
  });
}
