"""Shared visual locks for the YouTube Shorts Google Flow prompts.

Character looks follow traditional Hindu iconography and 00_CHARACTER_BIBLE.md
(faces, costumes, tilakam, age stages), rendered in the Shorts style below
instead of the long-form series' photorealism. Change STYLE here to restyle
every prompt; RESPECT is appended to every prompt and should never be removed.
"""

STYLE = ("traditional Indian devotional epic art brought to life as premium cinematic 3D animation, "
         "inspired by classical Indian temple murals and traditional devotional paintings of Hindu gods, "
         "stylized (not photorealistic) characters with divine, graceful, dignified features faithful to "
         "traditional Hindu iconography, rich jewel-tone colours with temple-gold accents, ancient South Indian "
         "temple-era architecture and forests, volumetric god rays, soft glowing divine light, high detail, "
         "smooth fluid motion, reverent devotional mood")

RESPECT = ("This is a sacred Hindu devotional scene from the Valmiki Ramayana: depict every deity and character "
           "with deep reverence and faithful traditional Indian iconography. Everyone is fully and modestly dressed "
           "in traditional Indian attire (women in properly draped silk or cotton sarees covering the shoulders and "
           "body, men in dhoti with angavastram or bark-cloth); no revealing, Western, fantasy-armour or modern "
           "clothing; no sexualised or suggestive poses; no blood, wounds, gore or graphic violence; no horror or "
           "jump-scare look; no comedy, cartoon exaggeration or caricature; no distorted, mocking or disrespectful "
           "depiction of gods; no modern objects, buildings, vehicles or technology.")

TAIL = ("No text, letters, subtitles, logos or watermarks anywhere in the frame. "
        "Audio: soft ambient atmosphere only, no speech, no singing, no music.")

VN = "white Vishnu namam with a red centre line on the forehead"
SN = "three horizontal ash-white Shiva lines with a red dot on the forehead"
KUM = "red kumkum bindi on the forehead and sindoor in the hair parting"
VANARA = ("noble heroic vanara warrior in traditional devotional iconography: human-proportioned muscular body "
          "standing upright, expressive kind monkey face, fur on face, head and lower limbs, long tail, "
          "never a realistic animal ape")

CHARS = {
    'VALMIKI': f"Sage Valmiki: venerable elderly rishi, long flowing white beard and matted hair tied up, serene meditative face, ochre bark-cloth robe and upper cloth, rudraksha beads, {VN}",
    'NARADA': f"Sage Narada (Devarshi Narada) in traditional iconography: ageless radiant sage with white beard and tall hair-knot (shikha), white-and-saffron robes, always holding his golden veena (Mahati), cheerful divine face, often floating gently in the air, {VN}",
    'RAMA_S2': f"Prince Rama, avatar of Lord Vishnu, in traditional iconography: deep blue (neela-megha) divine skin, gentle serene smile, large lotus-like eyes, long dark hair, graceful noble build, yellow-gold silk dhoti with angavastram, simple gold earrings, armbands and necklace, Kodanda bow and quiver, subtle divine glow, {VN}",
    'RAMA_S3': f"Rama in early exile, avatar of Lord Vishnu: deep blue divine skin, calm serene face, large lotus-like eyes, hair tied up in coiled jata, light beard, saffron-ochre bark-cloth dhoti and upper cloth, no jewellery, Kodanda bow and quiver, subtle divine glow, {VN}",
    'RAMA_S4': f"Rama in deep exile, avatar of Lord Vishnu: deep blue divine skin, calm composed face, large lotus-like eyes, full coiled jata, beard, saffron-ochre bark-cloth dhoti and upper cloth, no jewellery, Kodanda bow and quiver, subtle divine glow, {VN}",
    'RAMA_S5': f"King Sri Rama (Rama Pattabhishekam iconography): deep blue divine skin, serene smiling face, golden kireetam crown, yellow silk pitambara and royal jewellery, Kodanda bow, radiant divine aura, {VN}",
    'SITA_S2': f"Goddess Sita, incarnation of Goddess Lakshmi, in traditional iconography: warm golden-fair skin, gentle divine graceful face, long dark braid with jasmine flowers, rich red-and-gold silk saree fully and modestly draped with pallu over the shoulder, traditional gold jewellery, {KUM}",
    'SITA_S3': f"Goddess Sita in exile, incarnation of Lakshmi: warm golden-fair skin, gentle divine face, single long braid, simple saffron cotton saree fully and modestly draped with pallu over the shoulder, minimal jewellery, {KUM}",
    'SITA_S4': f"Goddess Sita in captivity, incarnation of Lakshmi: warm golden-fair skin, sorrowful but serene and dignified, loose braid, simple worn saffron saree fully and modestly draped, {KUM}",
    'SITA_ASHOKA': f"Goddess Sita in captivity, incarnation of Lakshmi: warm golden-fair skin, sorrowful but serene and dignified, loose braid, simple worn saffron saree fully and modestly draped, seated under a flowering Ashoka tree, {KUM}",
    'LAKSHMANA': f"Lakshmana in traditional iconography: golden-fair skin, youthful, lean strong build, shorter hair, always clean-shaven, devoted alert face, saffron-ochre bark-cloth dhoti and upper cloth in exile (gold-bordered silk in the palace), bow and quiver, {VN}",
    'BHARATA': f"Bharata: young prince, fair skin, gentle refined devoted face, medium build, simple white ascetic dhoti and upper cloth, no crown, {VN}",
    'DASHARATHA': f"King Dasharatha: elderly king in his sixties, white hair and beard, regal but aged, red-and-gold royal silk with angavastram, golden crown, {VN}",
    'KAIKEYI': f"Queen Kaikeyi: striking queen around forty, rich silk saree fully and modestly draped, bold traditional gold jewellery, proud posture, {KUM}",
    'KAUSALYA': f"Queen Kausalya: dignified motherly queen in her fifties, deep maroon silk saree fully draped with pallu, simple elegant gold jewellery, {KUM}",
    'SUMITRA': f"Queen Sumitra: gentle quiet queen in her fifties, green silk saree fully draped, understated gold jewellery, {KUM}",
    'GUHA': f"Guha the Nishada chief: rugged forest king, dark sun-weathered skin, woven cotton dhoti and upper cloth, chief ornaments of beads, shells and copper, bow, warm loyal smile, {VN}",
    'SUMANTRA': f"Sumantra the charioteer: middle-aged royal charioteer-minister, greying hair, white dhoti and angavastram, {VN}",
    'VASHISHTHA': f"Sage Vashishtha: venerable elderly royal guru, white beard and matted hair tied up, calm authoritative face, white robes, {VN}",
    'BHARADWAJA': f"Sage Bharadwaja: venerable elderly rishi, white beard, ochre robes, calm kind face, {VN}",
    'SHARABHANGA': f"Sage Sharabhanga: extremely old frail rishi, ochre robes, radiant tapas glow, {VN}",
    'SUTIKSHNA': f"Sage Sutikshna: elderly rishi in deep meditation, lotus posture, ochre robes, {VN}",
    'AGASTYA': f"Sage Agastya: short, powerfully built venerable rishi glowing golden like the sun, ochre robes, kamandalu, calm authority, {VN}",
    'RISHIS': "a group of venerable forest rishis in ochre and white robes with white beards and kamandalus, most with white Vishnu namam and some with three ash-white Shiva lines",
    'VIRADHA': "Viradha the rakshasa: towering mountain-like demon, sunken eyes, big belly, wearing a tiger-skin garment, carrying a huge spear, fierce but not horror, no gore",
    'SHURPANAKHA': "Shurpanakha the rakshasi: fully clothed in a dark traditional garment, wild coppery hair, fierce crooked eyes, long nails, dark skin, menacing but not horror, never gory or comic",
    'KHARA': f"Khara, Dushana and Trishira: three rakshasa commanders in traditional ornate dark armour and dhotis, dark reddish skin, Khara with a heavy mace, Dushana with an iron club, Trishira in a three-crested helmet, {SN}",
    'RAKSHASAS': f"an army of varied rakshasa soldiers in traditional dark dhotis and ornate armour, fierce but not horror, different builds, some with moustaches, {SN}",
    'MARICHA': f"Maricha the rakshasa: gaunt aged demon with grey-toned skin, fearful world-weary face, dark dhoti and upper cloth, {SN}",
    'GOLDEN_DEER': "the magical golden deer (Maya Mriga): shimmering golden fur dotted with silver, jewel-like glowing antlers, unnaturally beautiful",
    'RAVANA': f"Ravana in traditional iconography: majestic powerful ten-headed rakshasa king, ten crowned heads in a fan formation, twenty arms only when shown in full power, dark reddish-bronze skin, tall golden crowns, heavy gold jewellery, dark red-black-gold royal silk and armour, proud fierce face, regal not monstrous, {SN}",
    'JATAYU': "Jatayu, the noble divine vulture-king: massive bird with golden-brown plumage, immense wingspan, small golden crown ornament, dignified elder-warrior bearing",
    'KABANDHA': "Kabandha the cursed demon: huge headless legless torso with one large eye and a mouth on its chest, two very long arms, eerie but not gory",
    'GANDHARVA': "a radiant handsome celestial gandharva in shining silk and gold ornaments, glowing divine light",
    'SHABARI': f"Shabari the devotee: very elderly forest-dwelling woman ascetic, deeply lined face glowing with devotion and joy, simple saffron cotton saree fully draped, holding a basket of forest berries, {KUM}",
    'HANUMAN': f"Lord Hanuman in traditional devotional iconography: {VANARA}, vermilion-orange fur, kind devoted eyes, gold crown-like headpiece, gold armlets, red dhoti and sash, holding his golden gada (mace) when in action, hands joined in namaskar before Rama, {VN}",
    'SUGRIVA': f"Sugriva the vanara king: {VANARA}, golden-tawny fur, athletic build, gold armlets, red-gold dhoti and waist sash, light crown once king, {VN}",
    'VALI': f"Vali the vanara king: {VANARA}, darker reddish-brown fur, heavily muscular, kingly gold crown and Indra's golden necklace, dhoti and sash, proud bearing, {VN}",
    'TARA': f"Queen Tara: graceful vanara queen, warm golden fur, wise expressive face, silk saree-style garment fully and modestly draped, royal necklaces and queen's headpiece, {KUM}",
    'VANARAS': f"a vast army of varied vanara warriors in traditional dhotis and sashes, different fur tones and builds, {VN}",
    'SAMPATI': "Sampati: an enormous aged vulture with burnt, featherless wings, wise eyes",
    'NALA': f"Nala the vanara architect: {VANARA}, sandy-brown fur, simple dhoti and builder's sash, {VN}",
    'AKSHA': f"Akshakumara: young rakshasa prince in gleaming traditional armour and dhoti, {SN}",
    'INDRAJIT': f"Indrajit: young lean rakshasa warrior-prince resembling Ravana, ornate traditional armour and headgear, shimmering illusion-magic around him, {SN}",
    'VIBHISHANA': f"Vibhishana: gentle calm rakshasa noble with softer features, simple royal silk dhoti and angavastram, earnest devoted face, {VN} (after joining Rama)",
    'SAMUDRA': "Samudra Raja, the ocean god in traditional iconography: majestic deity rising from the waves, blue-green skin, crown of pearls and coral, silk garments, palms joined",
    'AGNI': "Agni Deva, the fire god in traditional iconography: radiant deity with golden-red skin and flames rising as hair, red silk garments and gold ornaments, calm protective face",
    'DEVAS': "radiant celestial devas on clouds in traditional silk and gold crowns, showering flowers",
    'BRAHMA': "Lord Brahma in traditional iconography: four-faced, four-armed creator god seated on a pink lotus, white beards, white-and-gold silk, holding Vedas, kamandalu and japamala, golden aura",
    'VISHNU': "Lord Maha Vishnu in traditional iconography: blue-skinned four-armed god holding Shankha (conch), Sudarshana Chakra, Kaumodaki gada and lotus, yellow pitambara silk, ornate golden kireetam, Kaustubha jewel, golden-blue divine glow",
    'PEOPLE': "devout people of ancient Ayodhya in traditional South Indian clothing (men in dhoti and angavastram, women in fully draped sarees), each with a red kumkum mark",
}

# Crowd keys: no reference image, never listed as Flow ingredients.
GROUPS = {'RISHIS', 'RAKSHASAS', 'VANARAS', 'DEVAS', 'PEOPLE'}
