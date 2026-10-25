# శ్రీమద్రామాయణం — CHARACTER BIBLE
### Master visual + voice lock for every character, every episode, all 6 Khaandas

**Source:** "చిత్రరూపంలో సంపూర్ణ వాల్మీకి రామాయణము" (717 pages). Text is being extracted, corrected, and OCR-verified paragraph-by-paragraph before any episode script is finalized (see `00_INDEX.md` for pipeline status). This file governs visual/voice consistency; it does not itself need to wait on that verification and is safe to use now.

**Rule:** Copy the exact **Visual Lock** text into every AI video/image prompt for that character. Use the same **Voice Profile** for every line of that character's dialogue, in every episode, across every Khaanda — until an explicitly noted **Age/Appearance Change Point**. Never paraphrase from memory.

**Era & region baseline (applies to every character below unless noted):** Treta Yuga, South Indian visual register — Dravidian-temple-era architecture and dress, not Mughal/North-Indian. Pre-Nivi single-wrap drape for women, veshti/angavastram for men, early Dravidian jewelry (kadiyam, jhumka, ordanam waist-belts). See `00_STYLE_GUIDE.md` for the full style guide (palette, architecture-by-location, Kirata/tribal look, Vanara/Rakshasa design rules).

---

## TILAKAM (FOREHEAD MARK) — faction visual identifier

A deliberate, consistent visual device across the whole series: **every character's forehead mark (tilakam/namam) signals which side of the story they belong to**, at a glance, in every shot. Copy the correct mark into the Visual Lock of every character prompt — named or generic — per the rule below. This is in addition to, not a replacement for, that character's own established Visual Lock details.

**⚠️ No forehead is ever bare.** Every human/divine character in every shot wears at least a small red sindhuram/kumkum bottu (dot) between the eyebrows as the absolute minimum — a plain, unmarked forehead should never appear in this series. Characters with a story-side affiliation wear the fuller namam described below (which itself typically includes a kumkum accent as part of the mark); characters without a story-side affiliation still wear the plain kumkum bottu on its own, never nothing. Generic wildlife/animals are the only exception (not applicable).

- **Rama's side — విష్ణు నామం (Vishnu Namam / Urdhva Pundra):** a white sandalwood-paste U-shaped (or V-shaped) mark rising from the bridge of the nose into two vertical lines on the forehead, with a central vertical red or yellow line between them (kumkum or turmeric) — this central line satisfies the "never bare" rule on its own. Applies to every character below with a personal/political tie to Ayodhya or Rama's cause: Rama, Lakshmana, Bharata, Shatrughna, Dasharatha, Kausalya/Sumitra/Kaikeyi's households (Kaikeyi included — she is Ikshvaku-married, not Lanka-aligned), Janaka's family (Sita, Urmila, Mandavi, Shrutakirti), Sumantra, Guha, Bharadwaja, Vashishtha, and every vanara/Kishkindha character aligned with Rama (Hanuman, Sugriva, Angada, Jambavantha, Nala, Nila, Tara, generic vanara soldiers).
- **Ravana's side — శివ నామం (Shiva Namam / Tripundra), as a mark of allegiance:** three horizontal white/ash-grey lines (vibhuti) drawn straight across the forehead, with a small red bindu at the center (again satisfying the "never bare" rule). Applies to: Ravana, Kumbhakarna, Indrajit, Khara, Dushana, Trishira, and every generic రాక్షససైనికులు (rakshasa soldier) — reflecting Ravana's own famous, canon devotion to Shiva, worn by his whole army as a mark of political/military allegiance to him specifically.
- **మహర్షులు (sages) — mixed by personal devotion, not story-side:** sages are a special case — split the crowd between Vishnu Namam and Shiva Namam across different individuals, since real rishis in this tradition follow one or the other as personal worship, independent of the Rama/Ravana conflict. **Important distinction: a sage wearing the Shiva Namam is NOT thereby Lanka-aligned or antagonistic** — it signals only his own devotional lineage (a Shaiva sage), same as it would in any South Indian temple crowd today. Default a generic sages' crowd to roughly 2/3 Vishnu Namam, 1/3 Shiva Namam unless a specific episode's narration implies a particular assembly leans one way (e.g., a gathering explicitly described as devotees of one deity). Named sages (Vishwamitra, Vashishtha, Valmiki, Agastya, Bharadwaja, etc.) keep whichever mark is already set in their own individual Visual Lock entry below — do not change an established named sage's mark once locked.
- **Vibhishana — a tracked exception, not yet active:** he still wears the Shiva Namam (as Ravana's soldiers do, a mark of Lanka political allegiance, not personal devotion) through Aranya/Kishkindha/early Yuddha Khaanda material, since he's introduced as Ravana's brother within Lanka. The moment his own story has him defect to Rama's side (Yuddha Khaanda), his tilakam changes to the Vishnu Namam from that scene forward — a deliberate, visible signal of his changed allegiance, not an inconsistency. Flag this explicitly in that episode's Visual prompt column when the time comes, and add his own dedicated Character Bible entry with both Stages noted.
- **Unaligned/neutral figures:** దేవతలు (generic devatas) and any human character with no story-driven side (e.g. King Janaka's court before Sita's marriage, Kekaya-kingdom generic citizens) wear the plain red kumkum bottu described above — no namam, but never a bare forehead either.
- **Rakshasas — individual variation reminder:** per the "no clone armies" rule above, vary build, skin tone, and armor across rakshasa soldiers — and additionally, give some (not all) individual rakshasa soldiers mustaches (మీసలు) for natural crowd variety; others clean-shaven or with other facial-hair styles. Do not standardize every rakshasa to the same facial hair, same as no two should share the same face.

---

## NARRATOR

**Role:** Single male narrator voice for the entire series — no exceptions, no second narrator ever introduced.

**Voice Profile:**
- Male, ~28 years old vocal quality — young adult, not a "wise elder" register
- Warm, professional, unhurried storyteller tone (pravachanam/discourse style, not news-anchor)
- Clear literary Telugu, comfortable with correct Sanskrit shloka/padyam pronunciation
- Emotional register shifts with content (gentle for domestic scenes, grave for tragedy, rising energy for battle) — but the voice's pitch/timbre never changes
- Every stotram/shloka/padyam line is recited in full and correctly BEFORE being explained in narration — never paraphrased in place of the verse
- **Characters do not speak in these videos** — narrator describes what they do/say in third person (per production rule); the only exception is if a future phase adds per-character voice acting, in which case each character's Voice Profile below becomes the spec for that actor/TTS preset

**🔒 LOCKED TTS SPEC — fill in once, then never change for the rest of the series:**
- Engine/platform: _[e.g. ElevenLabs / Azure Neural TTS / Google Chirp 3 — TBD, pick after A/B listening to a same test clip on each]_
- Exact voice ID/name: _[e.g. "Abhi" / "te-IN-MohanNeural" — TBD]_
- Locked settings (write down every knob so nothing drifts): stability / similarity-boost / style-exaggeration (ElevenLabs) OR rate / pitch / SSML defaults (Azure/Google) — record the exact numbers used on episode 1 here, and reuse them unchanged for episode 255
- Test clip used to decide: the opening narration of `E1.01_valmiki_maharshi_katha.md`
- **Once this section is filled in, every future episode's audio must use this exact spec — never "closest available voice," never regenerated with default settings.**

---

## ⚠️ WHO SPEAKS ON SCREEN — the lip-sync / speaker-attribution rule

This is a hard production rule, not a suggestion, because getting it wrong is exactly the kind of mistake that undermines a whole video: **a character's mouth must never appear to be the source of dialogue audio that isn't actually theirs.**

**Current design (every episode written so far): this problem cannot occur, by construction.** Only the single Narrator's voice is ever recorded, and the Narrator is never shown on screen — every character in every scene is silent on-mic, always described in third person ("రాముడు ఇలా అన్నాడు — ..."). So:
- **No character in any AI video prompt should be generated with active, lip-synced, dialogue-matched mouth movement.** When a scene shows someone "speaking" per the narration (e.g. Janaka addressing Rama), the correct visual is a character with a natural, generic mouth posture — talking-adjacent body language (gesture, eye contact, head tilt) — NOT tight lip-sync animation timed to specific words, since there is no character-specific audio for lips to match. If your video tool defaults to auto-lip-syncing any face in frame to the loudest audio track, disable that feature or shoot the scene in a wider frame where lip detail isn't the focus.
- **Multi-character scenes are exactly where this risk is highest** — e.g. a scene with both Dasharatha and Vishwamitra on screen while the narration quotes Vishwamitra's line: make sure your video generation doesn't accidentally animate Dasharatha's mouth instead, or both mouths at once. The safest practice: only the character whose *action* is the current visual focus should be framed close/expressive; anyone else in the same shot should read as listening/reacting, not talking.
- Every episode script's Visual prompt column already names exactly which character is doing what in that scene (e.g. "[Vishwamitra Visual Lock] stating the request plainly; [Dasharatha Visual Lock] visibly collapsing") — use that framing as your guide for who should look active vs. who should look reactive in the shot.

**If you ever move to a future phase with per-character voice acting** (each character's own Voice Profile below becomes real recorded/TTS audio instead of just a reference spec): at that point, EVERY line of dialogue in every episode script must be explicitly tagged with who is speaking it, using this convention: `[DIALOGUE VOICE: CharacterName] "line of dialogue" [/DIALOGUE VOICE]` — matching the format already demonstrated in this project's own `sample_polish_1.1_and_1.4.md` reference. That tag does three things: (1) tells you which Voice Profile/TTS preset to render that line with, (2) tells your video tool which character's mouth — and only that character's mouth — should lip-sync to that specific audio clip, and (3) makes it trivial to audit a finished episode for any line where the visible speaker and the audio don't match. Retrofitting existing episodes with these tags would be required before turning on per-character voice acting — do not mix "narrator paraphrases everyone" and "some lines are directly voiced" within the same episode, since that's when speaker confusion actually happens.

---

## GENERIC CROWD TYPES

**⚠️ Realism applies to every entry below, no exceptions.** Devatas, rakshasas, vanaras, and wildlife are all real beings within this story's world, not stylized fantasy iconography — render every one of them as photorealistic, cinematic, physically plausible (real anatomy, real skin/fur/fabric texture, real lighting), exactly per `00_STYLE_GUIDE.md` → "Rendering style — realism." A "golden aura" is soft practical/rim lighting on a real body, not a cartoon glow effect; a vanara is a physically real monkey-human hybrid with actual fur texture and musculature, not a mascot-style illustration; a rakshasa is a real, physically imposing humanoid, not a stylized "demon" cartoon. If a generated image reads as illustration, anime, CGI-game, or mascot-costume, it fails the lock — regenerate.

**⚠️ No clone armies.** A "Visual Lock" for a crowd type is a shared *base* (build, attire, palette, silhouette) — not one face copy-pasted across every figure in the shot. Every individual within a crowd should read as a distinct real person sharing that base: different face shapes, ages-within-range, heights, skin-tone variation, minor asymmetries, individual posture/expression. If every figure in a crowd shot looks like the same person duplicated, that's a failed generation — regenerate with explicit "varied individuals, not duplicates" language in the prompt.

**⚠️ Gender composition and headcount are scene-driven, not fixed by the lock.** Each entry below states the traditional/default composition for that crowd type, but the actual mix in any given shot is set by what that episode's Visual prompt column and source narration actually describe — read the scene, not just this table. A sages' assembly is traditionally all elder men (rishis in this text are consistently male); a devatas crowd watching from the sky is traditionally a mixed assembly of gods and goddesses together, not one gender; a soldier formation (rakshasa or vanara) is traditionally all-male per the source's own battle scenes. Follow the specific episode's own description first — this table is the sensible default when a scene doesn't specify further, not an override.

### మహర్షులు — Generic sages/rishis (unnamed groups)
**Composition:** Male only, elderly — this text consistently depicts rishi/muni assemblies as male ascetics; do not add women into a generic sages' crowd unless a specific episode's narration names female sages present.
**Tilakam:** Mixed across the crowd — roughly 2/3 Vishnu Namam, 1/3 Shiva Namam per individual sage's own personal devotion (see "TILAKAM" section above for the full rule and the important note that a Shiva Namam here signals devotional lineage only, not Lanka allegiance — sages are never Ravana-aligned in this text).
**Visual Lock:** Elderly men, white/grey hair and beards, ochre or white cotton robes, wooden danda (staff) and kamandalu (water pot), calm contemplative expressions, seated in meditation or walking in small groups. Vary each individual within the group — different face shapes, exact ages (60s to 80s+), heights, builds, beard styles/lengths, skin tones — so the crowd reads as distinct real elders sharing a common ascetic dress code, not repeated copies of one face. Visually distinct from named sages (Vishwamitra, Vashishtha, Valmiki, Agastya, etc.), who are each more detailed/individualized per their own locks below. Photorealistic elderly human men — real skin texture, real weathered hands and faces, no stylization.

### దేవతలు — Generic devatas (background gods)
**Composition:** Mixed — devas (male) and devis (female) together, roughly balanced unless a specific scene's narration implies otherwise (e.g., an assembly the source describes as one gender). Do not default to an all-female crowd.
**Tilakam:** Unaligned/neutral by default (see "TILAKAM" section above) — devatas sit outside the Rama/Ravana conflict as a rule. Every figure still wears the plain red kumkum bottu between the eyebrows (never a bare forehead); do not apply either faction namam unless a specific scene explicitly ties a devata figure to one side of the story.
**Visual Lock:** Physically real, photorealistic humanoid figures — natural human anatomy and proportions, no exaggeration — with warm, soft practical-looking rim lighting (never a flat cartoon "glow" overlay). South Indian temple-deity register: richer, more layered ornamentation than an ordinary mortal character — multi-strand gold necklaces, armlets (vanki), earrings (jhumka/kamma), crowns or hair ornaments for the more senior figures — rendered as real, heavy, dimensional metal and gem work (not a single delicate chain, not flat/painted-on jewelry), alongside fine woven silk with real fabric texture and drape. Serene/awestruck expressions, usually shown as a crowd watching from the sky, sometimes showering flower petals (real petals with real physics, not a particle-effect look). Vary each figure's face, build, exact ornamentation, and drape color within the shared palette so the crowd doesn't read as one figure duplicated. Named gods (Brahma, Vishnu, Indra) are individually detailed and more distinct than this background treatment, but held to the same photorealism standard — never stylized/iconographic/painting-like.

### రాక్షససైనికులు — Generic rakshasa soldiers (Lanka army)
**Composition:** Male soldiers — this text's rakshasa armies are consistently depicted as male warrior ranks.
**Tilakam:** Shiva Namam (tripundra — three horizontal white/ash lines across the forehead, optional small red bindu at center) on every soldier — see "TILAKAM" section above. This is the army's visible mark of allegiance to Ravana, a devotee of Shiva.
**Visual Lock:** Muscular demon warriors with physically real, anatomically grounded builds — dark reddish-brown to grey skin (varying per individual within that range) rendered with real skin texture, fanged but not individually detailed faces, dark leather-and-metal armor with real material weight and wear, mace/sword/spear. Vary each soldier's exact build, height, skin-tone shade, armor wear/damage, and facial hair — give some (not all) individual soldiers mustaches, others clean-shaven or with other styles — so the ranks read as individual real fighters, not a repeated unit model. Kept simpler than named rakshasas (Ravana, Kumbhakarna, Indrajit, Vibhishana, Khara, Dushana, Trishira) so principals read clearly against the crowd — but never cartoonish or "movie-monster" stylized; they should read as real, physically threatening beings photographed in-scene, not illustrated or CGI-rendered creatures.

### వానరసైనికులు — Generic vanara soldiers (Kishkindha/Yuddha army)
**Composition:** Male soldiers — the vanara armies in this text are consistently depicted as male warrior ranks.
**Tilakam:** Vishnu Namam — see "TILAKAM" section above.
**Visual Lock:** Follow the **VANARA DESIGN BASELINE** (set out just above the Hanuman entry further down this file) exactly — heroic, muscular, human-proportioned warrior bodies with expressive simian faces, fur on face/head/lower limbs, bare muscular torsos and main limbs in a natural golden-tan-to-brown skin tone, visible tails; never a literal ape body, never cartoon/mascot styling. Natural fur-tone variety across individuals (browns/greys/tans/reddish), simple minimal warrior gear (sash, occasional small shield/club), energetic/agile posture, generally cheerful even in battle (devotional rather than mercenary motivation). Vary each individual's fur tone, build, height, and face structure so the group reads as distinct real individuals, not one model repeated. Kept simpler/less ornamented than named vanaras (Hanuman, Sugriva, Vali, Angada, Jambavantha, Nala, Nila, Tara) so principals read clearly against the crowd, but built on the exact same photorealistic design language as them, like real warriors captured on camera.

### అడవి జంతువులు — Generic forest wildlife
**Composition:** Natural mixed-sex animal groups as biologically appropriate for the species shown (herds of deer, flocks of birds, etc.) — no gender/composition rule needed beyond real-world animal behavior.
**Visual Lock:** Naturalistic deer, birds, small animals for atmosphere in forest scenes — fully photorealistic (real fur/feather texture, real animal proportions and movement), not semi-realistic or stylized. Vary individual animals within a group shot (size, coloring, posture) exactly as a real herd or flock would show natural variation. The krauncha bird pair in Episode 0.1 (Parichayam/Valmiki's origin) is a named narrative exception requiring individual emotional focus in that one scene only, still within the same photorealistic standard.

---

## NAMED DEITIES

### బ్రహ్మ — BRAHMA
**Role:** Creator god; blesses Valmiki (Ep 0.1); appears at other key divine turning points across Khaandas.
**Visual Lock:** Four-headed, four-armed, white/grey beard on all four faces, seated/standing on a lotus, white-and-gold silk, carries kamandalu, japamala (prayer beads), and the Vedas (small scroll), soft golden aura, all-knowing serene expression on all faces.
**Voice:** Male, ageless, deeply resonant, calm absolute authority, slow deliberate pace — every line a proclamation.

### శ్రీమహావిష్ణువు — VISHNU
**Role:** Supreme god whose avatar Rama is; appears only in brief divine-realm narration (devatas praying before Rama's birth, etc.), never during Rama's earthly scenes.
**Visual Lock:** Blue-tinted skin (the same symbolic tone Rama carries), four arms holding shankha (conch), chakra (discus), gada (mace), padma (lotus), yellow/gold pitambara silks, ornate crown, reclining on Adishesha or seated on a lotus, soft golden-blue glow.
**Voice:** Male, ageless, supreme, calm and benevolent, unhurried and final.

### ఇంద్రుడు — INDRA
**Role:** King of the gods; the Ahalya deception (Ep in Baala Khaanda), referenced in Vali's origin (Kishkindha) and Kaikeyi's Shambarasura-war backstory (Ayodhya).
**Visual Lock:** Regal warrior-king, fair/golden skin, heavily jeweled crown and armor (more martial/flashy than Vishnu), carries the vajra (thunderbolt), near his elephant Airavata in full regal scenes; in the Ahalya episode specifically, a subtly uneasy/roguish expression.
**Voice:** Male, regal but with an undertone of arrogance/impulsiveness; furtive and guilty in the Ahalya deception scene specifically.

---

## THE ROYAL FAMILY OF AYODHYA

### శ్రీరామచంద్రుడు — RAMA
**Role:** Protagonist, Vishnu's avatar, eldest son of Dasharatha.
**Visual Lock:** Deep blue-tinted dark skin (traditional divine-nature marker), calm serene expression, large expressive eyes, long dark hair, athletic-graceful build, always carries kodanda (bow) and quiver, minimal jewelry (simple earrings/armbands only — never ornate), expression consistently composed and dignified, never shown panicked.

**Age/Appearance Stages (see Production Bible §2 for the full locked scheme):**
| Stage | Tag | Coverage | Look |
|---|---|---|---|
| S1 — boy | RAMA-S1 | Baala Khaanda, birth → Vishwamitra's yagna → swayamvara | Slim boyish build, no facial hair, cream/kaavi silk dhoti, simple topknot |
| S2 — bridegroom | RAMA-S2 | End of Baala Khaanda → start of Ayodhya Khaanda | Same face, broader shoulders, gold-zari silk, princely jewelry |
| S3 — exile begins | RAMA-S3 | Ayodhya Khaanda exile onward → Aranya Khaanda | Jewelry removed, valkala (bark-cloth), coiled jataa begins, light beard |
| S4 — deep exile | RAMA-S4 | Rest of Aranya → Kishkindha → Sundara → Yuddha | Full jataa, visible beard, sun-weathered skin, valkala throughout — no jewelry/princely dress until coronation |
| S5 — coronation | RAMA-S5 | Final Yuddha Khaanda scene | Beard trimmed, royal hair + crown, full king's silk and jewelry return |

**Voice:** Male, young adult (~25-28 vocal quality), calm and steady, never raises pitch under stress, measured/deliberate pace — strength through steadiness, not volume. (Reference spec only, since characters do not speak aloud in this production — used if a future phase adds voice acting.)

### సీతాదేవి — SITA
**Role:** Rama's wife, Janaka's daughter, incarnation of Lakshmi.
**Visual Lock:** Warm golden-fair skin, long dark hair in a single braid (flowers in royal/pre-exile scenes), soft gentle features, graceful posture.

**Age/Appearance Stages:**
| Stage | Tag | Coverage | Look |
|---|---|---|---|
| S1 — princess/bride | SITA-S1 | Baala Khaanda | Delicate build, single flower-braid, simple princess silk |
| S2 — young queen | SITA-S2 | Ayodhya Khaanda pre-exile | Fuller bridal jewelry, longer plait styling |
| S3 — exile | SITA-S3 | Ayodhya exile onward → Aranya (pre-abduction) | Valkala, minimal jewelry, single plain braid |
| S4 — captivity | SITA-S4 | Aranya (post-abduction) → Sundara → Yuddha | Same valkala, visibly worn/thin, dishevelled hair, seated under Ashoka-tree motif — never in Lankan-style jewelry |
| S5 — reunion | SITA-S5 | End of Yuddha Khaanda | Cleaned but simple, until formally re-robed for the Ayodhya return |

**Voice:** Female, young adult (~22-26 vocal quality), soft, warm, dignified — gentle even when firm.

### లక్ష్మణుడు — LAKSHMANA
**Role:** Rama's younger brother, son of Sumitra, devoted, quick-tempered.
**Visual Lock:** Golden-fair skin, sharp alert eyes, lean strong build, shorter hair than Rama, one year younger, always at Rama's side. Stays clean-shaven even through the exile stages (deliberate distinguishing choice from Rama's beard, for at-a-glance recognition).

**Age/Appearance Stages (his own — the exile stages follow Valmiki: bark garments when leaving Ayodhya, 2.37; hair matted with banyan sap at Shringaverapura, 2.52):**
| Stage | Tag | Coverage | Look |
|---|---|---|---|
| S1 — boy | LAKSHMANA-S1 | Baala Khaanda, Vishwamitra's yagna → swayamvara | Slim boyish build, no facial hair, cream silk dhoti with a thin gold border, simple topknot, a small bow |
| S2 — prince | LAKSHMANA-S2 | End of Baala → Ayodhya until the bark garments (E2.18) | Same face, broad shoulders, gold-zari silk veshti and angavastram, princely jewelry (crown band, earrings, necklace, armlets) |
| S3 — exile begins | LAKSHMANA-S3 | E2.18–E2.22: bark garments in Dasharatha's court → Tamasa → Guha's riverbank | Same face, clean-shaven; plain brown bark-cloth (valkala) wrap and upper cloth over a simple ochre dhoti, hair tied in a plain knot, NO crown, NO jewelry, NO silk; bow in hand, two quivers on the back, a sword at the waist |
| S4 — forest | LAKSHMANA-S4 | From E2.23 (hair matted at Shringaverapura) → rest of Ayodhya, Aranya, Kishkindha, Sundara, Yuddha | Same face, always clean-shaven; long hair matted into a jata coiled high on the head; brown bark-cloth (valkala) wrap with a black deer-skin over one shoulder, only tulasi/rudraksha beads, sun-tanned skin, NO crown, NO jewelry, NO silk; bow in hand, two quivers on the back, a sword at the waist; alert, protective stance |
| S5 — coronation | LAKSHMANA-S5 | Final Yuddha Khaanda scene | Jata untied and hair dressed royally, gold-zari silk and princely jewelry return, still clean-shaven |
**Voice:** Male, early-to-mid-20s vocal quality, sharper/more energetic than Rama, quicker to show emotion, faster pace especially when angry/protective.

### భరతుడు — BHARATA
**Role:** Rama's half-brother, Kaikeyi's son, refuses the throne.
**Visual Lock:** Fair skin, gentle/refined features (softer than Lakshmana's), medium build, emotionally expressive face. Fine princely attire until he refuses the throne (Ayodhya Khaanda); from that point on — deliberately simple ascetic dress despite ruling as regent, minimal jewelry, never comfortable in royal splendor again; rules via Rama's paduka on the throne, never wears the crown himself.
**Voice:** Male, similar age-range to Lakshmana, earnest and emotionally open, prone to breaking with grief/pleading — softer/more vulnerable than either Rama or Lakshmana.

### శత్రుఘ్నుడు — SHATRUGHNA
**Role:** Sumitra's second son, bonded to Bharata.
**Visual Lock:** Similar build/coloring to Lakshmana, simple prince's attire, generally shown alongside Bharata. Minimal individual characterization — fewer standalone scenes in this text.
**Voice:** Male, similar register to Lakshmana, used sparingly.

### ఊర్మిళ, మాండవి, శ్రుతకీర్తి — URMILA, MANDAVI, SHRUTAKIRTI
**Role:** Janaka's niece (Urmila, m. Lakshmana) and Kushadhwaja's daughters (Mandavi m. Bharata, Shrutakirti m. Shatrughna) — married in the same joint ceremony as Rama-Sita.
**Visual Lock:** Bridal silks/jewelry matching Sita's quality (same royal status, same ceremony) but each with a distinct fixed saree color for group-shot recognition: Urmila green-gold, Mandavi blue-gold, Shrutakirti purple-gold — keep these three assignments constant everywhere they appear.
**Voice:** Female (all three), warm and gentle, minimal individual dialogue in this text.

### దశరథ మహారాజు — KING DASHARATHA
**Role:** King of Ayodhya, father of the four princes; dies of grief early in Ayodhya Khaanda.
**Visual Lock:** Elderly (60s+), white/grey hair and beard, regal but visibly aged bearing, rich red-and-gold royal robes and crown in court scenes. Single continuous appearance Baala→early Ayodhya Khaanda only (dies there — no appearance after). Progressive visual aging WITHIN Ayodhya Khaanda itself: robust king (early) → devastated/collapsing (the two-boons scene) → deathbed (final scene).
**Change point — young Dasharatha (Shravana Kumar flashback only):** Same facial bone structure minus age — black hair, no/short dark beard, no age lines, robust youthful build, simple prince's hunting attire. Use ONLY inside that one flashback inset; everywhere else (including the rest of that same episode's "present"), use his standard elderly lock.
**Voice:** Male, elderly (65+), authoritative and warm early on; breaks into genuine sobbing/pleading during the two-boons and death scenes — the single most emotionally extreme voice performance the story calls for.

### కౌసల్యాదేవి — KAUSALYA
**Role:** Rama's mother, Dasharatha's chief queen.
**Visual Lock:** Mature (40s-50s), dignified, rich but not overly ornate deep red/maroon silk sarees, simple elegant jewelry, hair neatly tied. Warm/motherly by default; capable of deep grief without losing composed dignity.
**Voice:** Female, 45-55 vocal quality, warm, maternal, dignified — retains a controlled noble quality even in grief (contrast with Kaikeyi's sharper tone).

### కైకేయి — KAIKEYI
**Role:** Dasharatha's favored younger queen, Bharata's mother; demands Rama's exile under Manthara's influence.
**Visual Lock:** Mature (35-45, younger-looking than Kausalya), striking features, bold jewelry, confident posture. Kopagriha (anger-chamber) scenes only: stripped of jewelry/fine clothes, plain garments on a bare floor, hair loose — a deliberate dramatic contrast; returns to normal royal appearance immediately after (through her last major scene).
**Voice:** Female, 40s vocal quality with a sharper/more commanding edge than Kausalya; warm/affectionate before Manthara's influence, shifting to cold, firm, unyielding once decided.

### సుమిత్రాదేవి — SUMITRA
**Role:** Dasharatha's third queen, mother of Lakshmana and Shatrughna.
**Visual Lock:** Similar age-range to Kausalya, gentle/quiet presence, modestly rich attire, understated jewelry — consistently a supporting/background figure in group scenes.
**Voice:** Female, gentle, soft-spoken, very few individual lines.

### మంథర — MANTHARA
**Role:** Kaikeyi's hunchbacked maidservant; triggers Rama's exile.
**Visual Lock:** Elderly, distinctive hunched back (kubja), sharp angular face, small calculating eyes, plain servant's attire. Human and cunning rather than cartoonishly monstrous — the text treats her as sympathetic in her devotion to Kaikeyi's interests.
**Voice:** Female, elderly, persuasive/insinuating, a "whisper in the ear" quality — never shouts, works through insistent repetition.

---

## SAGES ACROSS THE KHAANDAS

### వాల్మీకి మహర్షి — SAGE VALMIKI
**Role:** Narrator-sage of the frame story (Ep 0.1/0.2), author of the Ramayana.
**Visual Lock (default, post-transformation):** Elderly, long white beard, serene meditative expression, forest-hermit bark/ochre robes, often seated writing on palm leaves or in meditation.
**Change point — Agnisharma (pre-transformation, Ep 0.1 opening only):** Rough unkempt young/middle-aged man, coarse plain clothing (NOT sage robes), rugged weathered forest-bandit appearance, alert/wary expression — sharply different from the sage he becomes. Switch permanently to the elderly-sage lock once the anthill/meditation transformation happens in that same episode.
**Voice:** As Valmiki — soft, reflective, gentle. As Agnisharma — rougher, harsher, anxious/defensive, noticeably coarser.

### నారద మహర్షి — SAGE NARADA
**Role:** Wandering divine sage/messenger; narrates the condensed Ramayana to Valmiki (Ep 0.1); may recur briefly elsewhere as a messenger figure.
**Visual Lock:** Elderly-but-ageless, white beard, tall hair-knot, simple white/saffron robes, ALWAYS carries a veena — his single identifying prop, present in every scene. Usually shown mid-stride/mid-flight rather than seated — energetic and mobile, distinct from the stiller generic-sage look.
**Voice:** Male, ageless, light and quick, warm and lively — noticeably more animated/conversational than other elderly sages, brisker pace.

### విశ్వామిత్ర మహర్షి — SAGE VISHWAMITRA
**Role:** Takes young Rama-Lakshmana for yagna protection (Baala Khaanda); escorts them to Mithila.
**Visual Lock:** Elderly but powerfully built, long white/grey beard, piercing intense eyes, ochre/saffron robes, danda and kamandalu. Commanding presence — kings do not refuse him, unlike gentler sages.
**Voice:** Male, elderly but resonant/powerful (not frail), commanding, brooks no argument — the most powerful-sounding of the sage voices.

### వశిష్ఠ మహర్షి — SAGE VASHISHTHA
**Role:** Royal family guru/priest across Baala and Ayodhya Khaandas.
**Visual Lock:** Elderly, white beard, calm authoritative presence — gentler, more "family priest" register than Vishwamitra's warrior-sage energy.
**Voice:** Male, measured, wise, steady.

### జనక మహారాజు — KING JANAKA
**Role:** King of Mithila, Sita's father, philosopher-king.
**Visual Lock:** Mature-to-elderly, dignified/scholarly bearing, rich but tasteful robes, kind eyes, greying hair/beard — gentler and more approachable than Dasharatha's more martial-kingly presence.
**Voice:** Male, mature/elderly, warm, wise, fatherly.

### ఋష్యశృంగ మహర్షి — SAGE RISHYASHRINGA
**Role:** Raised in total isolation; his presence brings rain to Angadesha; conducts Dasharatha's Putrakameshti yagna.
**Visual Lock:** Young-to-middle-aged, small deer-horn-like protrusion on the forehead (his signature identifying feature, per his birth story), ochre robes, innocent/unworldly expression, slim build. Appears only in the Baala Khaanda yagna sequence.
**Voice:** Male, gentle, soft-spoken, innocent — more naive-sounding than any other sage, reflecting his sheltered upbringing.

### విభాండక మహర్షి — SAGE VIBHANDAKA
**Role:** Rishyashringa's father; raised his son in isolation (backstory only).
**Visual Lock:** Elderly, fierce, severely ascetic, more solitary-looking than gentler sages, deeply weathered, long unkempt beard/hair. Backstory-only appearance.
**Voice:** Male, gruff, stern, minimal dialogue.

### అగస్త్య మహర్షి — SAGE AGASTYA
**Role:** Hosts Rama's group in Aranya Khaanda, tells the Vatapi-Ilvala story, gifts celestial weapons.
**Visual Lock:** Compact but powerfully built, radiant "like the sun" (a noticeably brighter/golden-glow treatment than other forest sages), ochre robes, calm authoritative bearing. The weapon-gifting scene is a significant iconic moment — treat with the same visual weight as Vishwamitra's weapon-gifting in Baala Khaanda.
**Voice:** Male, warm, wise, authoritative — same "absolute authority" register as Vishwamitra but gentler/more grandfatherly.

### శరభంగ మహర్షి — SAGE SHARABHANGA
**Role:** Gives up his body in sacred fire and ascends to Brahmaloka in Rama's presence (early Aranya Khaanda).
**Visual Lock:** Extremely elderly and frail — more visibly aged/withered than any other sage (his defining trait is his "worn-out" body). Final moment only: steps into ritual fire, briefly emerges as a youthful radiant spirit-form before ascending.
**Voice:** Male, very frail, breathy, but deeply peaceful — at total peace with dying, never fearful.

### సుతీక్ష్ణ మహర్షి — SAGE SUTIKSHNA
**Role:** Meditating sage Rama visits after Sharabhanga.
**Visual Lock:** Elderly, deep meditation (often eyes closed, lotus posture), ochre robes — the "deepest in meditation" of the forest sages encountered. Brief appearance.
**Voice:** Male, calm, unhurried, warmly welcoming once he speaks.

### శబరి — SHABARI
**Role:** Elderly devotee of Sage Matanga; waits years for Rama, hosts him with great devotion (end of Aranya Khaanda).
**Visual Lock:** Very elderly tribal/forest-dwelling woman ascetic, simple bark/coarse-cloth clothing, deeply lined weathered face, radiant joyful expression on meeting Rama (contrast to her otherwise humble simplicity), often shown offering forest fruits. Final moment: same fire-ascension treatment as Sharabhanga.
**Voice:** Female, very elderly, frail but full of warmth — one of the warmest, most emotionally open voices in the whole series.

### మతంగ మహర్షి — SAGE MATANGA
**Role:** Shabari's late guru, referenced only (already ascended before the story's present moment).
**Visual Lock:** Referenced only through Shabari's narration and ashram details (unused fire-altar, still-damp cloths) — if shown at all, a brief golden-tinted flashback inset only, same general elderly-sage template.
**Voice:** N/A — does not speak directly.

### భరద్వాజ మహర్షి — SAGE BHARADWAJA
**Role:** Hosts Rama's group early in the exile (Ayodhya Khaanda), directs them to Chitrakuta.
**Visual Lock:** Elderly, general "wise sage" template (ochre robes, calm demeanor), gives directions/hospitality briefly.
**Voice:** Male, gentle, welcoming.

### పరశురాముడు — PARASHURAMA
**Role:** Warrior-sage avatar of Vishnu; challenges Rama after the wedding (end of Baala Khaanda).
**Visual Lock:** Fierce, muscular, matted dreadlocked hair, wild intense eyes, carries a parashu (battle axe) over one shoulder and a bow, ochre warrior-ascetic garb — visibly more aggressive/imposing than any other sage character.
**Voice:** Male, aggressive, challenging, booming — softens dramatically (same voice actor/quality) once he recognizes Rama's divinity.

---

## THE FOREST & TRIBAL WORLD (Kirata register — see style guide)

### గుహుడు — GUHA, Nishada chief
**Role:** Rama's devoted tribal friend at the Ganga crossing (Ayodhya Khaanda).
**Visual Lock:** Rugged forest/tribal king register (per style guide's Kirata rules — darker sun-weathered skin, minimal woven-cloth, chief-level ornament within the tribal register, never royal silk), bow and forest attire, warm fiercely-loyal demeanor.
**Voice:** Male, warm, rustic, devoted.

### శ్రవణకుమారుడు — SHRAVANA KUMAR
**Role:** Devoted young ascetic serving his blind parents; fatally struck by young Dasharatha's arrow (flashback only, Ayodhya Khaanda).
**Visual Lock:** Simple bark-cloth/ascetic dress, gentle dutiful bearing, carries water pots for his parents. Appears only in the one flashback — alive/devoted, then fatally wounded, dying peacefully without anger.
**Voice:** Male, young, gentle, calm even in death — no bitterness, only concern for his parents.

### శ్రవణకుమారుడి అంధ తల్లిదండ్రులు — His blind parents
**Visual Lock:** Elderly blind couple, simple ascetic forest-dweller's dress, devoted to each other and their son; peaceful hermitage life turning to grief and righteous fury on learning of his death.
**Voice:** Elderly male and female, gentle/frail shifting to powerful sorrow-driven intensity during the curse itself.

---

## VILLAINS & RAKSHASAS

### తాటక — TATAKA
**Role:** Powerful demoness (cursed yakshini) terrorizing Vishwamitra's yagna forest; killed by Rama in his first real combat (Baala Khaanda).
**Visual Lock:** Towering, significantly larger than human, wild hair, fierce fanged face, dark rough grey-green/brown skin, huge muscular build, tattered primal hide/bark clothing (older and more primal than the later "courtly" demons), clawed hands.
**Voice:** Female, guttural, roaring, primal — minimal actual dialogue, mostly roars.

### అహల్య — AHALYA
**Role:** Gautama's wife, turned to stone after Indra's deception, liberated by Rama's touch (Baala Khaanda).
**Visual Lock:** First a grey stone figure; restored — a beautiful mature woman, modest traditional dress, serene grateful expression.
**Voice:** Female, grateful and serene, used only briefly.

### గౌతమ మహర్షి — SAGE GAUTAMA
**Role:** Ahalya's sage-husband; curses her after discovering Indra's deception.
**Visual Lock:** Elderly sage, general template, distinguished in his one key scene by visible fury (sharper/more wrathful than the usual serene sage archetype), softening again within the same breath as he tempers the curse with the promise of Rama's future liberation of Ahalya.
**Voice:** Male, shifts sharply — warm/trusting, to thunderous fury, to quiet resigned tenderness, all within one scene.

### విరాధుడు — VIRADHA
**Role:** Cursed gandharva-turned-rakshasa; attacks Rama's group early in Aranya Khaanda; freed by burial (his own requested method).
**Visual Lock:** Towering mountain-like build, sunken deep-set eyes, distended belly, wrapped in bloody tiger hide, carries a trophy-hung spear (stylized/implied gore, not explicit).
**Voice:** Male, crude, threatening, boastful — softens into calm resignation once he reveals his curse and asks to be buried alive.

### ఖరుడు, దూషణుడు, త్రిశిరుడు — KHARA, DUSHANA, TRISHIRA
**Role:** Shurpanakha's brothers/commanders; lead 14,000 rakshasas against Rama in Panchavati; all killed by Rama alone (Aranya Khaanda).
**Visual Lock:** One tier above the generic rakshasa-soldier template — individually armored/detailed. Khara (eldest, most prominent): dark reddish hue, heavy mace or bow. Dushana: wields a parigha (iron club). Trishira: three-tufted/three-crested helmet (a visual nod to his name without literally giving him three heads — that trait belongs only to Ravana).
**Voice:** Khara — booming, arrogant, most vocal of the three. Dushana — gruffer, mostly a physical-combat presence. Trishira — similar to Dushana, minimal individual dialogue.

### శూర్పణఖ — SHURPANAKHA
**Role:** Ravana's sister; her mutilation triggers the war (Aranya Khaanda).
**Visual Lock:** Shapeshifting rakshasi — true monstrous form (sharp teeth, wild hair, nails "like winnowing fans," dark skin) is the DEFAULT/primary identity. **Updated per the source (E3.10):** this text has her approach Rama in her true form — there is NO attractive-disguise phase; the source's own portrait is aged, pot-bellied, coppery wire-like hair, crooked eyes, a harsh barking voice. Keep her unsettling, never gory or comic-grotesque. After the mutilation (E3.11) she keeps her face hidden — no close-up of the wounds anywhere in the series.
**Voice:** Female, falsely sweet/seductive initially, shifting to shrieking fury after rejection and mutilation.

### మారీచుడు — MARICHA
**Role:** Transforms into the golden deer to lure Rama, enabling Sita's abduction (Aranya Khaanda).
**Visual Lock:** Two distinct forms — aged demon-advisor form (grey-toned skin, gaunt, world-weary/fearful) for his Lanka court scenes, and a fully separate golden deer form (strikingly beautiful, shimmering golden fur, bejeweled-looking antlers, unnaturally beautiful — a visual cue it's magical) for the deer scenes.
**Voice:** Demon form — weary, fearful, reluctant (he knows this plan kills him). Note in scripts as "Maricha, mimicking Rama's voice" when he cries out in Rama's voice while dying — this is a trick, never actually voiced as Rama himself.

### జటాయువు — JATAYU
**Role:** Noble vulture-king; dies fighting Ravana to save Sita (Aranya Khaanda).
**Visual Lock:** Massive noble vulture/eagle-like bird, golden-brown plumage, immense wingspan, dignified regal bearing (warrior-elder, not a scavenger). Death scene: visibly wounded, feathers scattered, wings damaged, dignified even while dying.
**Voice:** Male, elderly, gravelly but noble — warm/protective on first meeting Rama's group, determined and pained during the Ravana fight and dying speech.

### అయోముఖి — AYOMUKHI
**Role:** Grotesque rakshasi who accosts Lakshmana; mutilated in self-defense (Aranya Khaanda).
**Visual Lock:** Monstrous rakshasi, distended sagging belly, deeply grotesque/misshapen features — unsettling rather than fierce, visually distinct from Shurpanakha by having no attractive-disguise phase at all.
**Voice:** Female, crude, forward, aggressive-flirtatious shifting instantly to pained shrieking — very brief role.

### కబంధుడు — KABANDHA
**Role:** Grotesque headless, legless demon (cursed gandharva Dhanu) who seizes Rama-Lakshmana; freed by cremation (Aranya Khaanda).
**Visual Lock:** No head, no legs, a torso from chest to waist, one enormous eye and a huge mouth on the belly/chest, two extremely long arms (dramatically elongated). After cremation/liberation: transforms into Dhanu, a radiant handsome gandharva in fine celestial ornaments — the polar opposite of the cursed form.
**Voice:** As Kabandha — muffled, strange, unsettling, slow and simple. As Dhanu — completely different register: clear, resonant, warm, grateful.

### రావణాసురుడు — RAVANA
**Role:** Ten-headed demon king of Lanka, primary antagonist (Aranya through Yuddha Khaanda).
**Visual Lock:** Powerfully built, ten heads in a fan/crown formation OR a single head with a ten-headed crown/halo motif — pick ONE convention at first appearance and never mix it mid-series. Twenty arms in full-power depictions (can simplify in normal conversation scenes, but stay consistent within an episode). Dark reddish-bronze skin, elaborate crown, heavy gold jewelry, dark-red-black-gold royal demon attire, fierce fanged expression capable of shifting to falsely courteous/seductive when addressing Sita. No aging across his 4-Khaanda span — identical lock throughout. **Convention locked at first appearance (E3.14):** ten heads in a fan formation, twenty arms in full-power depictions — following the source's own description ("వింశత్ భుజం దశ గ్రీవం", p. 267). Source details to keep: old scars on his chest from Indra's vajra, Airavata's tusks and Vishnu's chakra; burnished gold earrings; white teeth; a vast mouth.
**Voice:** Male, mature/powerful/deep, booming and arrogant, capable of falsely courteous tones with Sita but always with an undertone of menace and ego — the most theatrical villain voice in the series. Deliberate, grandiose pace.

### కుంభకర్ణుడు — KUMBHAKARNA
**Role:** Ravana's giant brother, famous for months-long sleep; fights and dies in the war (Yuddha Khaanda).
**Visual Lock:** Enormous giant rakshasa, significantly larger than Ravana, minimal "just-woken" wrap-clothing in his key scene, sleepy/groggy expression transitioning to battle-fury, same dark reddish-bronze tone as Ravana but single-headed.
**Voice:** Male, deep, booming, initially groggy/slow, shifting to thunderous battle-roar.

### ఇంద్రజిత్తు (మేఘనాధుడు) — INDRAJIT
**Role:** Ravana's son, master of illusion-warfare, nearly kills Lakshmana (Yuddha Khaanda).
**Visual Lock:** Young rakshasa warrior-prince, resembles Ravana in coloring but younger/leaner, elaborate distinct warrior armor/headgear, subtle magical-distortion effects around him in battle to signal his illusion mastery.
**Voice:** Male, confident, cunning, younger-sounding than Ravana but the same arrogant edge — a "worthy heir" quality.

### విభీషణుడు — VIBHISHANA
**Role:** Ravana's righteous younger brother; defects to Rama's side (Yuddha Khaanda).
**Visual Lock:** A rakshasa but visually gentler than Ravana — less fanged/fierce, calmer posture, simpler/less ostentatious royal dress, worried/earnest expression reflecting his internal conflict.
**Voice:** Male, earnest, troubled, morally serious — noticeably more restrained/thoughtful than Ravana's bombast.

### మండోదరి — MANDODARI
**Role:** Ravana's queen; pleads with him to avoid war, especially late in Yuddha Khaanda.
**Visual Lock:** Dignified demon queen, sorrowful/pleading demeanor increasing as the war progresses.
**Voice:** Female, elegant, increasingly desperate as the war progresses.

### అక్షకుమారుడు — AKSHAKUMARA
**Role:** Ravana's young son, killed fighting Hanuman in the Ashoka Vatika garden (Sundara Khaanda) — the first personal loss that shakes Ravana.
**Visual Lock:** Young rakshasa prince, slighter-built than the adult commanders, bright/intense energy, radiant "like sacred fire" when eager for battle, fine princely armor.
**Voice:** Male, young, eager, fearless, excited for his first real battle.

### జంబుమాలి — JAMBUMALI
**Role:** First named commander sent against Hanuman in the garden (Sundara Khaanda), killed.
**Visual Lock:** Rakshasa warrior-commander, donkey-drawn chariot, similar tier to Khara/Dushana/Trishira with his own armor details.
**Voice:** Male, confident, combative — brief role.

### కుంభుడు, నికుంభుడు, ప్రజంఘుడు, మకరాక్షుడు — KUMBHA, NIKUMBHA, PRAJANGHA, MAKARAKSHA
**Role:** Rakshasa commanders (Kumbhakarna's sons and others) in the war's later stages (Yuddha Khaanda), each killed by a different Rama-side hero.
**Visual Lock:** Same tier as Khara/Dushana/Trishira — generic-soldier template scaled up with individual armor/weapon details.
**Voice:** Male, generic confident-warrior register — brief individual battle roles.

### సురస — SURASA
**Role:** Naga-mother sent to test Hanuman's wit during the ocean-crossing (Sundara Khaanda).
**Visual Lock:** True/default form — regal naga woman (serpent lower body or hood motifs); test-form — enormous gaping-mouthed monster filling the sky.
**Voice:** Female, initially stern/booming (monster form), shifting to warm/impressed/maternal blessing at the end.

### సింహిక — SIMHIKA
**Role:** Shape-shifting rakshasi who seizes Hanuman's shadow mid-flight (Sundara Khaanda), killed.
**Visual Lock:** Shape-shifter emerging from the ocean, shown literally grabbing/pulling at Hanuman's shadow on the water, growing monstrous as she pulls him down.
**Voice:** Female, predatory, hissing — very brief, mostly physical.

### త్రిజట — TRIJATA
**Role:** Elderly rakshasi guard sympathetic to Sita in Ashoka Vatika; relays a calming prophetic dream (Sundara Khaanda).
**Visual Lock:** Elderly rakshasi, notably gentler/more sympathetic than the other guards — calmer wiser expression, slightly less monstrous features while still clearly a rakshasi, positioned protectively near Sita.
**Voice:** Female, elderly, calm, wise, protective.

### హరిజట, ఏకజట, అజముఖి — HARIJATA, EKAJATA, AJAMUKHI
**Role:** Sita's hostile guards in Ashoka Vatika, calmed by Trijata's dream (Sundara Khaanda).
**Visual Lock:** Hostile hungry-looking rakshasi guards, varying individual monstrous details for group distinction, aggressive predatory postures.
**Voice:** Female (all three), hungry, cruel, casually violent in threats — softened only after Trijata's account.

### సుకుడు — SUKA
**Role:** Ravana's spy assessing the vanara army; treated with mercy by Rama (Yuddha Khaanda).
**Visual Lock:** Deliberately unremarkable rakshasa (no elaborate armor/markings), nervous calculating expression.
**Voice:** Male, nervous, pleading when caught — brief role.

---

## VANARAS (Kishkindha → Yuddha Khaanda)

## VANARA DESIGN BASELINE — applies to every vanara character below, named or generic

**⚠️ Reference-locked design, confirmed by the user against specific reference images — read this before generating any vanara.** A vanara in this series is a **heroic, muscular, human-proportioned warrior with a simian (monkey) face** — never a literal ape/monkey body, never a cartoon or mascot-style "monkey person." The template is the popular devotional/cinematic Hanuman image: a powerfully built human physique (broad chest, defined muscular arms and legs, standing and moving upright like a person, not hunched or ape-postured) topped with an expressive monkey face — flattened simian nose/snout, monkey-shaped eyes, fur covering the face, head, and lower forearms/lower legs, but the main torso, chest, and limbs read as bare, muscular, golden-tan-to-reddish skin (like the reference images), not fully fur-covered like a real animal. A visible tail. Fully photorealistic/cinematic rendering per the standing realism rule — real muscle definition, real skin and fur texture, real lighting — never flat illustration or an actual zoo-photograph monkey.

**Attire and ornamentation:** a warrior's dhoti/veshti wrap (commonly saffron, red, or deep gold), gold jewelry — armlets, wrist and ankle bands, a waist belt/sash, layered necklaces — heavier and more elaborate for royalty (Sugriva, Vali) or in a devotional/glorified pose (Hanuman before Rama), simpler for common soldiers. A crown or ornate headpiece for kings (Sugriva, Vali) and senior figures when the scene calls for formal/regal bearing.

**Tilakam:** per the master "TILAKAM" section near the top of this file — every Rama-aligned vanara (Hanuman, Sugriva, Angada, Jambavantha, Nala, Nila, Tara, generic vanara soldiers) wears the Vishnu Namam.

**Individual variation is mandatory, per the "no clone armies" rule:** every named vanara below already has a distinct fur color/tone as part of their own lock (Hanuman's orange-red, Sugriva's golden-tawny, Vali's darker reddish-brown, Tara's warm golden). Generic vanara soldiers must vary further still — different face structures, body builds/heights, and fur-tone shades from each other and from the named principals — so no two vanaras in a crowd shot share the same face or build, while all clearly share this same design baseline.

### హనుమంతుడు — HANUMAN
**Role:** Vanara devotee of Rama; central figure of Sundara Khaanda, present through Yuddha Khaanda.
**Visual Lock:** Per the VANARA DESIGN BASELINE above — a powerfully muscular, human-proportioned warrior body (broad chest, defined arms/legs, bare golden-tan-to-reddish skin on torso and limbs) topped with an expressive, intelligent simian face and fur-covered head/face/lower limbs, long visible tail. Distinctive orange/reddish fur tone. Devotional ornamentation: simple gold armlets and a sash by default, hands folded in devotion when facing Rama/Sita; can carry his gada (mace) in action poses. Dynamic, powerful heroic poses in action; calm, humble, folded-hand posture in devotional moments. No age/appearance change point — but shown at dramatically different SCALES (normal vs. giant); note which scale each prompt needs while keeping the face/fur/features identical.
**Voice:** Male, ageless-but-mature, devoted/warm/humble with Rama and Sita, powerful/commanding addressing Ravana's court or in battle, capable of clever wit, energetic/quick pace generally but tender and careful when first speaking to Sita in captivity.

### సుగ్రీవుడు — SUGRIVA
**Role:** Exiled vanara king, becomes Rama's ally (Kishkindha Khaanda onward).
**Visual Lock:** Per the VANARA DESIGN BASELINE above — golden/tawny fur tone, muscular human-proportioned warrior build, athletic rather than as heavily built as Vali, simpler ornamentation than Vali but still kingly (gold armlets, waist sash, a lighter crown once he becomes king), anxious/watchful expression and posture until Vali's death, more confident/kingly bearing after.
**Voice:** Male, anxious/pleading early, growing confident and kingly after becoming king.

### వాలి — VALI
**Role:** Sugriva's older brother, powerful king of Kishkindha, killed by Rama.
**Visual Lock:** Per the VANARA DESIGN BASELINE above — darker/reddish-brown fur tone than Sugriva, more heavily muscular build, more ornamented/kingly regalia (a golden necklace, Indra's gift, as a specific identifying detail), fierce confident bearing bordering on arrogant.
**Voice:** Male, booming, confident, commanding — retains dignity even dying, raising pointed questions about Rama's justice rather than simply begging.

### తార — TARA
**Role:** Vali's wife, later Sugriva's queen; diplomatic figure who calms Lakshmana's fury.
**Visual Lock:** Per the VANARA DESIGN BASELINE above, female register — a vanara queen with the same muscular-but-graceful human-proportioned build, expressive simian face, warm golden fur tone (distinguishing her from the male vanaras' darker earth-tones), royal jewelry (necklaces, armlets, a queen's headpiece), fine draped garment rather than a plain sash. Emotionally open face capable of deep grief and sharp diplomatic wit. Fundamentally composed and clever even when circumstantially disheveled.
**Voice:** Female, grief-stricken/raw in the Vali death scene, sharp/articulate/persuasive diplomacy in the Lakshmana confrontation.

### అంగదుడు — ANGADA
**Role:** Vali's son, search-party leader.
**Visual Lock:** Per the VANARA DESIGN BASELINE above — resembles Vali in fur coloring (reddish-brown) but leaner, younger build and a less weathered, more earnest face; simpler prince's ornamentation than Vali's.
**Voice:** Male, young, earnest, slightly impulsive (like Vali but without the arrogance).

### జాంబవంతుడు — JAMBAVANTHA
**Role:** Elderly bear-being (riksha — a distinct species from vanaras), wise elder statesman.
**Visual Lock:** A distinct species design from the vanaras above, following the same photorealistic-over-cartoonish standard — a powerfully built but visibly elderly humanoid bear-being, grey-furred, bear-like face (rounder snout, small eyes, bear ears) rather than a simian one, wise elder statesman bearing and posture, simple minimal ornamentation befitting an elder sage-like figure. Distinct silhouette from the monkey-form vanaras, never confusable with them at a glance.
**Voice:** Male, elderly, wise, gravelly — a distinct "elder statesman" register from every other character.

### నలుడు, నీలుడు — NALA, NILA
**Role:** Vanara architects/builders (bridge construction).
**Visual Lock:** Per the VANARA DESIGN BASELINE above — each with his own distinct fur tone/face/build within the shared design (vary the two from each other and from the named principals), practical builder's minimal gear rather than warrior ornamentation. Background/supporting figures visually consistent with generic vanara soldiers unless a scene specifically focuses on them, at which point give each his own individualized look per this entry.
**Voice:** Minimal individual voice, practical/workmanlike tone when they speak.

### మాయావి — MAYAVI
**Role:** Rakshasa whose rivalry with Vali starts the Dundubhi backstory chain (flashback narration only).
**Visual Lock:** Generic dark-toned rakshasa build, fearful/fleeing posture in his one depicted moment. Flashback/backstory treatment only (desaturated grade).
**Voice:** Minimal — narrated backstory, little to no direct dialogue.

### దుందుభి — DUNDUBHI
**Role:** Buffalo-demon whose arrogant challenge leads to his death at Vali's hands (flashback); his skeleton appears in the "present" as proof of Vali's strength.
**Visual Lock:** Massive buffalo-form demon, dark powerful bulk, enormous horns, primal/destructive bearing — larger than the standard rakshasa template. Flashback grade; a bleached skeleton/bone-pile in present-timeline scenes.
**Voice:** Male, booming, arrogant — brief backstory dialogue only.

### సంపాతి — SAMPATI
**Role:** Jatayu's older brother; wingless vulture who reveals Sita's location in Lanka (Kishkindha Khaanda), regains his wings.
**Visual Lock:** Same general design as Jatayu (golden-brown plumage, noble bearing) but initially WITHOUT flight feathers — grounded, weathered, resigned. Final moment: wings dramatically regrow in a burst of feathers/light, triumphant flight.
**Voice:** Male, elderly, similar register to Jatayu but wearier/more resigned — lifts and brightens at the triumphant final moment.

### మతలి — MATALI
**Role:** Indra's charioteer; brings Indra's celestial chariot to Rama in the climactic Ravana battle (Yuddha Khaanda).
**Visual Lock:** Divine charioteer, fine celestial livery (subtle gold/silver, otherworldly), calm competent bearing, ornate flying chariot.
**Voice:** Male, calm, respectful, precisely helpful — a brief but pivotal voice in the final duel.

---

## SUPPORTING/BRIEF CHARACTERS

- **సుమంత్రుడు (Sumantra), royal charioteer:** Elderly loyal court official, simple charioteer's dress, calm dutiful demeanor. Male voice, steady and formal.
- **యజ్ఞపురుషుడు (Yajna Purusha):** Radiant divine figure emerging from Dasharatha's yagna fire with the golden payasam bowl (Baala Khaanda). Reddish-golden fire-toned skin, simple divine garments, minimal jewelry — one-scene, high-impact appearance. Male voice, resonant, otherworldly, brief.
- **వేశ్యలు (the courtesans sent to lure Rishyashringa):** Elegant traditional dancer's attire, graceful, period-appropriate courtly elegance — tasteful, brief backstory treatment. Female voices, melodic, persuasive.
- **దధిముఖుడు (Dadhimukha), Madhuvana's keeper:** Elderly vanara guard, comedic minor role when the search party raids the honey-garden in celebration (Sundara Khaanda close). Male voice, indignant, comic.

---

## QUICK-REFERENCE CHECKLIST (before generating any scene)

- [ ] Copied the exact Visual Lock text for every character in this scene (not paraphrased)
- [ ] Checked this episode against any Age/Appearance Change Point for these characters
- [ ] Costume matches the correct phase (royal / bark-cloth-valkala / captivity-worn)
- [ ] Location register (Ayodhya / forest-ashram / Panchavati / Kishkindha / Lanka) matches the style guide's palette+architecture rules for that place
- [ ] Ravana's head/arm-count convention matches what was used at his first appearance
- [ ] If using reference images: reused the SAME saved reference image, not freshly generated
- [ ] No character other than the Narrator is voiced aloud, per the production rule — everyone else moves/acts, never speaks on-mic

---

*This file governs every episode in every Khaanda file. Do not redefine a character's appearance inside an episode file — update it here instead, once, and every episode inherits the change.*
