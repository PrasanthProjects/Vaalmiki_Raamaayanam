// Which sounds a Short gets, from what its pictures show (the kit's "The frame shows" line of each clip).
// The files themselves are made once by the user (src/data/sfx_prompts.json) and kept in Video_Maker/SFX.
//
// Checked clip by clip against every Bala 1 Short's picture and words (2026-11-12). Rules that came out of it:
// - whole words only ("toward" had matched "war" and put a battle under Rama and Sugriva's quiet talk in 1.60);
// - a memory, flashback or symbolic picture names no place of its own;
// - the big backgrounds (battle, fire, ocean, flight) only where the picture itself shows them happening: active
//   fighting (an empty battlefield, fallen weapons or vanaras rising in light is not a battle), a real blaze (a lamp,
//   yagna or sacred fire is not), the sea, flying; a vanara army marching or searching is not a battle;
// - otherwise the picture's own setting (palace, forest, river, night), else the Short's main setting, else none:
//   silence under the music is better than a wrong place.

const BIG: [string, RegExp][] = [
  ['amb_battle', /\b(?:battle|fighting|fights?|duel|charging|charges|attack(?:s|ing)?|war|soldiers|commanders roaring|arm(?:y|ies)|battling|wrestl\w*|battlefield)\b/i],
  ['amb_fire', /\b(?:flames?|pyre|blaze|blazing fire|burning|on fire|forest fire|wildfire|fire pit|aflame|burns)\b/i],
  ['amb_ocean', /\b(?:ocean|sea|seashore|sea shore|waves)\b|bridge (?:across|stretching)/i],
  ['amb_sky', /\b(?:flying|flies|fly|leaping|leaps|soaring|pushpaka|descends from|descending)\b/i],   // "aerial view" is the camera
];
const SETTING: [string, RegExp][] = [
  ['amb_palace', /\b(?:palace|court|throne|hall|chamber|ayodhya|nandigrama|market|streets?)\b/i],
  ['amb_river', /\b(?:river|riverbank|bank of|stream|lake|pond|ganga|godavari|tamasa|pampa|sarayu)\b/i],
  ['amb_night', /\b(?:night|moon|moonlight|dark room|lamps?|dim chamber)\b/i],
  ['amb_forest', /\b(?:forest|trees?|hermitage|ashram|jungle|garden|grove|hill|hilltop|rishyamuka|mountains?|slope|rocky|cave|chitrakuta|panchavati|leaf hut|hut|valmiki|sages?)\b/i],
];
const MEMORY = /flashback|memory|inset|golden haze|golden-haze|symbolic|recall|remember|dream|vision of|as valmiki imagines|seen as a (?:glowing )?vision|glowing vision|storybook panel|faint images?/i;

// the picture's own scene: its parts (split at ';') without the memory or flashback ones, and phrases that only look
// like a place or an action
const ownScene = (shows: string) =>
  shows.split(';').filter((x) => !MEMORY.test(x)).join(';')
    .replace(/\([^)]*\)/g, ' ')                                        // notes like "(outdoors, no throne, no palace)"
    .replace(/\blamps?\b[^;,.]*/gi, ' lamp ')                          // a burning lamp is a quiet night, not a blaze
    .replace(/\b(?:yagna|sacred|homa) fires?\b[^;,.]*/gi, ' ashram ')   // a sacred fire is the hermitage's calm
    .replace(/\bafter (?:his|her|the|their) fight\b[^;,.]*/gi, ' ')    // a fight already over is not a battle now
    .replace(/\bready for battle\b/gi, ' ')                            // a vow, not the fight
    .replace(/\bvanara arm(?:y|ies)\b/gi, ' vanaras ')                  // marching or searching, not fighting
    .replace(/\bas if\b[^;,.]*/gi, ' ')                                // "as if describing…" is not a place
    .replace(/\bstreams? of\b/gi, ' ')                                 // a stream of arrows is not a river
    .replace(/\b(?:empty|quiet)\s+battlefield\b/gi, ' ')               // an empty battlefield is quiet, not a fight
    .replace(/\bbattlefield sky\b/gi, ' sky ')                        // gods watching from the clouds, not the fight
    .replace(/\bbattlefield\b(?=[^;]*\b(?:fallen|revived|rise again|rising|calmly|peace\w*)\b)/gi, ' ')
    .replace(/\b(?:fallen|revived)\b[^;]*\bbattlefield\b/gi, ' ');

const first = (list: [string, RegExp][], text: string) => {
  let best: string | null = null;
  let n = 0;
  for (const [name, re] of list) {
    const c = (text.match(new RegExp(re.source, 'gi')) || []).length;
    if (c > n) [best, n] = [name, c];
  }
  return best;
};
const bigOf = (shows: string) => first(BIG, ownScene(shows));
const settingOf = (shows: string) => first(SETTING, ownScene(shows));

// one background for a whole scene list (films: a scene's place and its shots)
export function ambienceFor(shows: string[]): string {
  const text = shows.join(' ; ');
  return bigOf(text) || settingOf(text) || 'amb_forest';
}

// one background per picture of a Short: what it shows happening, else its own place, else the Short's main place
export function ambienceAt(all: string[], i: number): string {
  const own = bigOf(all[i] || '') || settingOf(all[i] || '');
  if (own) return own;
  const count: Record<string, number> = {};
  // the Short's main place: the settings, and the sea when two or more pictures are at sea (one seashore teaser does
  // not put a whole Short at sea)
  all.forEach((x) => { const s = settingOf(x || ''); if (s) count[s] = (count[s] || 0) + 1; });
  const sea = all.filter((x) => bigOf(x || '') === 'amb_ocean').length;
  if (sea >= 2) count.amb_ocean = sea;
  const main = Object.entries(count).sort((a, b) => b[1] - a[1])[0];
  return main ? main[0] : '';   // no place anywhere: no background, only the music
}

// one sound at the start of a picture, when it shows that moment (arrow first: a bow drawn at an army is the arrow)
const MOMENTS: [string, RegExp][] = [
  ['arrow', /\barrows?\b|bow drawn|draws? (?:his )?bow|drawing his bow|looses|shooting/i],
  // a living rakshasa or monster in action; Ravana is a king, never a monster's roar; bones, the fallen or a memory are quiet
  ['roar', /\b(?:rakshasas?|demons?|kabandha|viradha|tataka|monster|khara)\b/i],
  ['thunder', /\b(?:storms?|stormy|lightning|thunder)\b/i],
  ['conch', /\b(?:blowing (?:a |the )?conch|conch (?:blast|sound)|coronation|crowned|victory)\b(?![^;]*\b(?:empty|stopped|halted)\b)/i],
  ['crowd', /\b(?:crowds?|citizens|celebrat\w*|cheer\w*|festival|dancing)\b/i],
  ['drums', /\b(?:arm(?:y|ies)|marching|war drums)\b/i],
  ['veena', /\b(?:veena|narada)\b/i],
];
const STILL = /\b(?:fallen|falling|bones|skeleton|dried|lying|defeated|bound|shown gently|weapons? lying)\b/i;
export function momentFor(shows: string): string | null {
  const text = ownScene(shows);
  for (const [name, re] of MOMENTS) {
    if (!re.test(text)) continue;
    if (name === 'roar' && STILL.test(text)) continue;
    return name;
  }
  return null;
}

// Big sounds only where the scene is action (user, 2026-11-11): a roar under a calm talk or a flashback felt wrong
// (Bala 1.60, Ravana in a memory of the abduction). Gentle ones (veena, conch, crowd) fit any mood.
const LOUD = new Set(['roar', 'arrow', 'thunder', 'drums']);
export function momentIn(shows: string, mood: string): string | null {
  const m = momentFor(shows);
  if (!m || (MEMORY.test(shows) && !ownScene(shows).trim())) return null;
  return LOUD.has(m) && mood !== 'heroic' && mood !== 'mystery' ? null : m;
}
