// Which sounds a Short gets, from what its pictures show (the kit's "The frame shows" line of each clip).
// The files themselves are made once by the user (src/data/sfx_prompts.json) and kept in Video_Maker/SFX.

// one quiet background for the whole Short: the place most of its pictures show
const AMBIENCE: [string, RegExp][] = [
  ['amb_battle', /battle|army|war|soldiers|fight|duel|chariot/i],
  ['amb_fire', /fire|flame|pyre|blaze|burn/i],
  ['amb_ocean', /ocean|sea\b|shore|waves|bridge/i],
  ['amb_sky', /sky|clouds|flying|leap|pushpaka|aerial/i],
  ['amb_night', /night|moon|dark room|lamp/i],
  ['amb_palace', /palace|court|throne|hall|chamber|ayodhya/i],
  ['amb_river', /river|stream|lake|pond|ganga|godavari|tamasa|pampa/i],
  ['amb_forest', /forest|tree|hermitage|ashram|jungle|garden|grove/i],
];
export function ambienceFor(shows: string[]): string {
  const text = shows.join(' ');
  let best = 'amb_forest';
  let n = 0;
  for (const [name, re] of AMBIENCE) {
    const c = (text.match(new RegExp(re.source, 'gi')) || []).length;
    if (c > n) [best, n] = [name, c];
  }
  return best;
}

// one sound at the start of a picture, when it shows that moment
const MOMENTS: [string, RegExp][] = [
  ['roar', /rakshasa|demon|kabandha|viradha|tataka|monster|ravana|khara/i],
  ['arrow', /arrow|bow drawn|draws? (his )?bow|looses/i],
  ['thunder', /storm|lightning|thunder/i],
  ['conch', /conch|coronation|crowned|victory/i],
  ['crowd', /crowd|citizens|celebrat|cheer|festival/i],
  ['drums', /army|march|war drums/i],
  ['veena', /veena|narada/i],
];
export function momentFor(shows: string): string | null {
  for (const [name, re] of MOMENTS) if (re.test(shows)) return name;
  return null;
}

// Big sounds only where the scene is action (user, 2026-11-11): a roar under a calm talk or a flashback felt wrong
// (Bala 1.60, Ravana in a memory of the abduction). Gentle ones (veena, conch, crowd) fit any mood.
const QUIET = /flashback|memory|inset|golden haze|symbolic|recall|remember|dream/i;
const BIG = new Set(['roar', 'arrow', 'thunder', 'drums']);
export function momentIn(shows: string, mood: string): string | null {
  const m = momentFor(shows);
  if (!m || QUIET.test(shows)) return null;
  return BIG.has(m) && mood !== 'heroic' && mood !== 'mystery' ? null : m;
}
