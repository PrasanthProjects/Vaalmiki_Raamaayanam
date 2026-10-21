"""Visual rules for the long-form episodes: photorealistic, per 00_STYLE_GUIDE.md,
with every character's look taken from 00_CHARACTER_BIBLE.md (its Visual Lock and
age stages). The bible is read at build time, so editing it updates every prompt.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STYLE = ("photorealistic live-action historical film, as in a big-budget Indian epic: cinematic lighting, "
         "natural skin texture and cloth movement, real woven fabric and real built sets, shot on a real camera "
         "lens (35mm/50mm equivalent) with naturalistic depth of field. Treta Yuga in a South Indian visual "
         "register: early Dravidian temple-era architecture and dress (veshti and angavastram for men, single-wrap "
         "drape for women, early Dravidian jewellery), never Mughal or North-Indian motifs. Forest and ashram "
         "settings are lush, green and serene with flowering trees, clear rivers, deer, peacocks and birds unless "
         "the scene says otherwise. Not flat illustration, anime, cartoon, painted storybook or glossy plastic 3D")

RESPECT = ("This is a sacred Hindu devotional scene from the Ramayana: depict every deity and character with deep "
           "reverence and faithful traditional Indian iconography. Everyone is fully and modestly dressed in "
           "traditional attire (women's drapes covering the shoulders and body); no revealing, Western, "
           "fantasy-armour or modern clothing; no sexualised or suggestive poses; no blood, wounds, gore or graphic "
           "violence (show impact through light, dust and reaction); no horror look; no comedy or caricature; no "
           "distorted or disrespectful depiction of gods; no modern objects, buildings, vehicles or technology.")

TAIL = ("No text, letters, subtitles, logos or watermarks anywhere in the frame. "
        "Audio: soft ambient atmosphere only, no speech, no singing, no music.")

VN = "white Vishnu namam (U-shaped white mark with a red centre line) on the forehead"
SN = "three horizontal ash-white Shiva lines with a red dot on the forehead (mark of allegiance to Ravana)"
KUM = "red kumkum bindi on the forehead and sindoor in the hair parting"
BOTTU = "small red kumkum dot between the eyebrows"

VANARA = ("heroic, muscular, human-proportioned warrior with an expressive monkey face, fur on the face, head, "
          "lower forearms and lower legs, bare golden-tan to reddish skin on the chest and limbs, a visible tail, "
          "standing upright like a person, never a literal ape; warrior dhoti and gold ornaments")

# Spellings used in the scene prompts -> bible key
ALIASES = {
    'Jambavan': 'JAMBAVANTHA', 'Jambavantha': 'JAMBAVANTHA', 'Sugreeva': 'SUGRIVA', 'Vasishtha': 'VASHISHTHA',
    'Viswamitra': 'VISHWAMITRA', 'Seeta': 'SITA', 'Lakshman': 'LAKSHMANA', 'Meghanada': 'INDRAJIT',
    'Shurpanakha': 'SHURPANAKHA', 'Dushana': 'KHARA', 'Trishira': 'KHARA', 'Nila': 'NALA', 'Anjana': None,
}

WOMEN = {'SITA', 'KAUSALYA', 'KAIKEYI', 'SUMITRA', 'MANTHARA', 'URMILA', 'SHABARI', 'TARA', 'MANDODARI',
         'AHALYA', 'TRIJATA', 'SHURPANAKHA', 'TATAKA', 'AYOMUKHI', 'SURASA', 'SIMHIKA', 'HARIJATA'}
RAVANA_SIDE = {'RAVANA', 'KUMBHAKARNA', 'INDRAJIT', 'KHARA', 'MARICHA', 'AKSHAKUMARA', 'JAMBUMALI', 'KUMBHA',
               'SUKA', 'VIRADHA'}
NO_MARK = {'BRAHMA', 'VISHNU', 'INDRA', 'JATAYU', 'KABANDHA', 'SURASA', 'SIMHIKA', 'SHURPANAKHA', 'TATAKA',
           'AYOMUKHI'}

# Age stages by episode (first episode of each stage). Episodes before the first entry use the first stage.
STAGES = {
    # Aranya scripts: Rama's deep-exile look after the ten years among the hermitages (E3.05 end),
    # Sita's captivity look once she is in Lanka (E3.25)
    'RAMA': [('E0.00', 'S2'), ('E1.05', 'S1'), ('E1.23', 'S2'), ('E2.18', 'S3'), ('E3.06', 'S4'), ('E6.39', 'S5')],
    'SITA': [('E0.00', 'S1'), ('E2.01', 'S2'), ('E2.18', 'S3'), ('E3.25', 'S4'), ('E6.35', 'S5')],
    'LAKSHMANA': [('E0.00', 'S2'), ('E1.05', 'S1'), ('E1.23', 'S2'), ('E2.18', 'S3'), ('E3.06', 'S4'), ('E6.39', 'S5')],
}


def ep_key(ep):
    k, n = ep[1:].split('.')
    return (int(k), int(n))


def parse_bible():
    """Return {KEY: {'lock': text, 'stages': {S1: look}}} from 00_CHARACTER_BIBLE.md."""
    text = open(os.path.join(ROOT, '00_CHARACTER_BIBLE.md'), encoding='utf-8').read()
    out = {}
    for block in re.split(r'^### ', text, flags=re.M)[1:]:
        head, body = block.split('\n', 1)
        if '—' not in head:
            continue
        eng = head.split('—', 1)[1].strip()
        m = re.search(r'\*\*Visual Lock[^*]*:\*\*\s*(.+)', body)
        if not m:
            continue
        lock = m.group(1).strip()
        stages = {s: look.strip() for s, look in
                  re.findall(r'^\|\s*(S\d)[^|]*\|[^|]*\|[^|]*\|([^|]+)\|', body, flags=re.M)}
        change = re.search(r'\*\*Change point — ([^(*]+)[^*]*\*\*\s*(.+)', body)
        for name in re.split(r',\s*', re.sub(r'\(.*?\)', '', eng)):
            words = [w for w in name.split() if w.isalpha() and w.isupper() and w not in ('SAGE', 'KING', 'QUEEN')]
            if words:
                out[words[0]] = {'lock': lock, 'stages': stages}
        if change and 'Agnisharma' in change.group(1):
            out['AGNISHARMA'] = {'lock': change.group(2).strip(), 'stages': {}}
    return out


BIBLE = parse_bible()

# Characters the scenes show but 00_CHARACTER_BIBLE.md has no entry for (deities and mythic-inset figures).
# Faithful traditional iconography; the bible wins if it ever gets its own entry.
EXTRA = {
    'SHIVA': ("Lord Shiva in traditional iconography: serene meditative face with half-closed eyes and a third eye on "
              "the forehead, three horizontal ash-white lines (vibhuti), ash-grey-blue skin, long matted jata coiled "
              "high with a crescent moon and a small stream of the Ganga, a cobra coiled around the neck, rudraksha "
              "beads, tiger-skin garment at the waist, holding a trident (trishula) with a small damaru; calm, "
              "majestic, about thirty in appearance"),
    'MANMATHA': ("Manmatha (Kama), the god of love: radiant, very handsome youthful god of about twenty-two, fair "
                 "golden skin, gentle smile, black curls under a small flower-studded gold crown, saffron and green "
                 "silk dhoti with flower garlands, holding a bow made of sugarcane strung with a line of bees and "
                 "five flower-tipped arrows"),
    'SUNDA': ("Sunda, the yaksha husband of Tataka: tall, broad-shouldered, dignified yaksha man of about thirty-five, "
              "dark curly hair to the shoulders, thick moustache, gold armlets and heavy earrings, dark-red silk dhoti; "
              "noble, not a demon"),
    'SUKETU': ("Suketu, the yaksha king and father of Tataka: elderly regal yaksha of about sixty, grey beard, "
               "kind but proud face, simple gold crown, white-and-gold silk, holding a rosary as one who did long tapas"),
    'VRITRASURA': ("Vritrasura, the mighty asura slain by Indra: a towering asura warrior with very dark skin, wild long "
                   "hair, fierce eyes, massive build, dark bronze armour and a heavy mace; imposing and grim but not a "
                   "horror creature"),
    'SUBAHU': ("Subahu, rakshasa son of Tataka and brother of Maricha: tall, powerfully built rakshasa of about thirty, "
               "dark skin, thick curling moustache, short pointed upper canines, long dark hair tied back, dark ornate "
               "armour with gold edging, a curved sword; fierce but human-faced"),
    'SUMANTRA': ("Sumantra, Dasharatha's chief minister and royal charioteer: dignified man of about sixty-five, trimmed "
                 "white beard and moustache, grey hair under a white-and-gold minister's turban, cream silk "
                 "angavastram over a white dhoti, gold earrings, tulasi beads; loyal, gentle, grave face"),
    'JABALI': ("Jabali, the learned brahmin of Dasharatha's council: lean scholar of about seventy, sharp clever face, "
               "long white beard, shaven head with a shikha tuft, white dhoti and a saffron upper cloth, sacred thread, "
               "a palm-leaf manuscript in hand"),
    'SIDDHARTHA': ("Siddhartha, a senior minister of Ayodhya: upright, outspoken man of about sixty, grey beard, white "
                   "turban, white silk with a blue-bordered angavastram, gold armlets"),
    'YUDHAJIT': ("Yudhajit, prince of Kekaya and Bharata's maternal uncle: tall, broad man of about forty-five, neatly "
                 "trimmed black beard, a northern-style gold crown, deep maroon and gold silk, a sword at the waist; "
                 "warm and dignified"),
    'ATRI': ("Sage Atri: a very ancient, radiant maharshi, long snow-white beard and matted white hair in a top-knot, "
             "bark garments with a deer skin, rudraksha beads, kamandalu and staff; serene, kind eyes"),
    'ANASUYA': ("Anasuya, wife of sage Atri: a very old, luminous woman ascetic, white hair in a simple knot, gentle "
                "wrinkled smiling face, plain off-white cotton sari with an ochre border, rudraksha beads; motherly "
                "and full of the strength of tapas"),
    'SURABHI': ("Surabhi (Kamadhenu), the divine mother of all cows: a radiant pure-white celestial cow with large "
                "gentle eyes, garlanded with flowers, softly glowing, standing among clouds; reverent traditional "
                "iconography"),
}
EXTRA.update({   # Aranya Kaanda
    'DHANU': ("Dhanu, Kabandha freed from his curse: a radiant, handsome gandharva of about thirty, glowing golden "
              "skin, long dark hair under a jewelled diadem, fine celestial silks in white and gold, garlands and "
              "bright ornaments, serene grateful face; the polar opposite of the headless cursed form"),
    'ILVALA': ("Ilvala, the rakshasa elder brother of Vatapi: in disguise a smooth, well-fed brahmin householder of about "
               "forty-five in a white dhoti with a sacred thread, a too-sweet smile; in his true form a heavy dark "
               "rakshasa with wild hair and short tusks; cunning eyes in both"),
    'VATAPI': ("Vatapi, Ilvala's younger brother, a shape-shifting rakshasa: lean, dark, sly-faced rakshasa of about "
               "thirty with wild hair; when disguised, a plain grazing ram with no human features"),
    'KASHYAPA': ("Kashyapa Prajapati, the ancient father of all beings: a vast, radiant, very old sage with a long white "
                 "beard to the waist, matted white hair in a high knot, white bark garments, a gentle cosmic calm, a "
                 "soft golden light around him"),
    'GARUDA': ("Garuda, the king of birds and Vishnu's mount: a majestic golden eagle-like divine being with a "
               "human-like noble face and a sharp curved beak, vast shining golden-red wings, a jewelled crown and "
               "armlets; reverent traditional iconography"),
    'KUBERA': ("Kubera, lord of wealth: a stout, dignified god of about fifty with a fair complexion, a full dark "
               "beard, a jewelled crown, rich yellow-gold silks and heavy gold ornaments, holding a small mace; "
               "regal and stern"),
    'TUMBURU': ("Tumburu, a gandharva (Viradha before his curse): a handsome, radiant celestial musician of about "
                "twenty-five in fine silks with a veena, garlanded, light glowing on his face"),
    'DHARMABHRUT': ("Dharmabhrut, a forest sage of Dandaka: an elderly ascetic of about seventy, white beard, matted "
                    "hair in a knot, ochre bark garments, a staff and kamandalu; kind, wise eyes"),
    'MANDAKARNI': ("Mandakarni, the sage who built the Panchapsara lake: a very lean ascetic of great austerity, "
                   "hollow-cheeked, matted hair, bark garment, seated in tapas"),
    'STHULASHIRA': ("Sage Sthulashira: a stern elderly maharshi with a large head and broad forehead, long grey beard, "
                    "matted hair, bark garments, gathering darbha grass"),
    'AKAMPANA': ("Akampana, a rakshasa survivor of Janasthana: a dusty, terrified rakshasa soldier of about thirty-five "
                 "in torn dark armour, wild hair, short tusks, fleeing for his life"),
    'YAYATI': ("King Yayati, son of Nahusha: a noble king of about fifty with a trimmed beard, gold crown and royal "
               "silks, a humble, gentle face"),
    'AGASTYA_BROTHER': ("Agastya's younger brother, a forest sage: a gentle elderly sage of about seventy, white "
                        "beard, matted hair in a knot, ochre bark garments, a warm welcoming smile; clearly a "
                        "different man from Agastya, softer and without his golden radiance"),
    'SHARABHANGA_DIVINE': ("Sage Sharabhanga after his body is given to the fire: a youthful, radiant spirit-form "
                           "of about twenty, made of soft golden light, serene face, white celestial garments, "
                           "rising upward; not withered, not old"),
    'MARICHA_YOUNG': ("Maricha in his younger days, before he renounced: a black-skinned, proud rakshasa of about "
                      "thirty with gold earrings, a swaggering powerful build, wild dark hair, fierce grin, dark "
                      "armour"),
    'RAVANA_DISGUISED': ("Ravana disguised as a wandering ascetic (parivrajaka): a single-headed, tall, broad-shouldered "
                         "man in soft saffron robes, a shaven head with a topknot, a sacred thread, a kamandalu on the "
                         "left shoulder, an ascetic's staff; a smooth, false gentleness, and only now and then a red "
                         "glint in the eyes; no crown, no extra heads or arms"),
    'KHARA': ("Khara, the eldest rakshasa commander of Janasthana: a towering rakshasa of about forty with dark reddish "
              "skin, heavy individually-detailed dark armour with gold edging, a horned helmet, a heavy mace and a "
              "great bow; booming, arrogant bearing"),
    'DUSHANA': ("Dushana, Khara's general: a burly rakshasa of about thirty-five with dark bronze skin, plain heavy "
                "armour, a thick beard, wielding a parigha (iron club); grim and gruff"),
    'TRISHIRA': ("Trishira, the third rakshasa commander: a lean, tall rakshasa of about thirty with dark skin, "
                 "dark armour and a three-crested helmet (three tufts or crests, never three heads)"),
})
# Looks added for the Aranya scripts are matched by name only from Aranya on, so the earlier kaandas' prompts
# (where these names are passing mentions) stay exactly as they were planned.
FROM_EP = {_k: 'E3.01' for _k in ('DHANU', 'ILVALA', 'VATAPI', 'KASHYAPA', 'GARUDA', 'KUBERA', 'TUMBURU', 'DHARMABHRUT',
                                  'MANDAKARNI', 'STHULASHIRA', 'AKAMPANA', 'YAYATI', 'AGASTYA_BROTHER',
                                  'SHARABHANGA_DIVINE', 'MARICHA_YOUNG', 'RAVANA_DISGUISED', 'DUSHANA', 'TRISHIRA')}
for _k, _v in EXTRA.items():
    BIBLE.setdefault(_k, {'lock': _v, 'stages': {}})
for _k in ('KHARA', 'DUSHANA', 'TRISHIRA'):   # the bible keeps the three brothers in one entry; give each his own look
    BIBLE[_k] = {'lock': EXTRA[_k], 'stages': {}}
ALIASES.update({'Manmadha': 'MANMATHA', 'Manmatha': 'MANMATHA', 'Kama': 'MANMATHA', 'Subahu': 'SUBAHU',
                'Dushana': 'DUSHANA', 'Trishira': 'TRISHIRA', 'Garuda': 'GARUDA', 'Kashyapa': 'KASHYAPA'})
NO_MARK |= {'SHIVA', 'MANMATHA', 'SUNDA', 'SUKETU', 'VRITRASURA', 'SURABHI', 'DHANU', 'ILVALA', 'VATAPI', 'GARUDA',
            'KUBERA', 'TUMBURU', 'SHARABHANGA_DIVINE', 'MARICHA_YOUNG', 'RAVANA_DISGUISED'}
WOMEN |= {'ANASUYA'}
RAVANA_SIDE |= {'SUBAHU', 'AKAMPANA', 'DUSHANA', 'TRISHIRA'}

# Places, one reference image each, so a location looks the same in every clip.
# key: (words in a scene's location register, episodes it applies to (None = every episode), description)
PLACES = {
    'AYODHYA_PALACE': (('inner palace',), None,
        "Ayodhya inner palace, the queens' quarters: an inner courtyard with a tulasi platform in the centre, carved "
        "teakwood pillars, sloped tiled roofs, lamp niches with lit brass lamps, silk curtains in deep red and gold, "
        "jasmine creepers; warm gold, cream and deep red palette"),
    'AYODHYA_COURT': (('ayodhya court', 'ayodhya, court'), None,
        "Ayodhya royal court (Dasharatha's sabha): a grand pillared mandapa of carved sandstone and teakwood in early "
        "Dravidian temple-era style, tall carved pillars with lotus capitals, sloped tiled roof beams, a raised gold "
        "and teak throne on a stepped dais under a silk canopy, brass oil lamps on tall stands, red and gold silk "
        "hangings, polished stone floor, seats for ministers and sages along both sides; warm gold and sandstone palette"),
    'FOREST_ROAD': (('forest road', 'ayodhya gate'), {'E1.06', 'E1.07'},
        "The road south from Ayodhya: a dusty footpath leaving a carved city gateway, running through green fields "
        "and into tall sal and banyan woods along the Sarayu river; ochre and forest-green palette, soft daylight"),
    'SARAYU_CAMP': (('campsite',), {'E1.06'},
        "Night camp on the south bank of the Sarayu river: a small clearing under tall trees beside the wide calm "
        "river, beds of darbha grass on the ground, a small sacred fire, kamandalus and a deer skin, river-blue water, "
        "ochre and forest-green palette"),
    'KAMA_ASHRAMA': (('riverside ashram',), {'E1.06', 'E1.07'},
        "Kamashrama, the sages' hermitage where the Sarayu meets the Ganga: thatched huts of mud and bamboo with neatly "
        "swept courtyards, a sacred fire altar (agni-kunda), deer skins and kamandalus, flowering trees, the calm "
        "riverbank in front; serene, green and sunlit"),
    'GANGA_SARAYU': (('riverbank', 'river crossing'), {'E1.06', 'E1.07'},
        "The confluence of the Ganga and the Sarayu: two wide rivers meeting under an open sky, sandy banks with reeds, "
        "a simple wooden boat at the shore, hermitages among the trees on the bank, morning mist on the water; "
        "river-blue and soft gold light"),
    'TATAKA_FOREST': (('dense forest',), {'E1.07', 'E1.08'},
        "The Tataka forest: a vast, dense, dreadful forest loud with shrilling crickets and harsh bird cries, tangled ancient trees, dry thorny "
        "undergrowth, broken branches and dust, dim filtered light, the overgrown ruins of two once-prosperous towns "
        "(Malada and Karusha) swallowed by vines; tense and foreboding but not horror"),
    # Ayodhya Kaanda (its scripts have no location column: data/2_Ayodhya_videos.txt PLACE lines point here)
    'KAIKEYI_PALACE': (('kaikeyi palace',), None,
        "Queen Kaikeyi's palace in Ayodhya: an ornate chamber of carved teak pillars with peacock and swan motifs, "
        "silk hangings in deep emerald and gold, a low swan-feather couch, brass lamps in wall niches, lattice "
        "windows; to one side the bare, unlit anger chamber (kopagriha) with a plain stone floor; rich but tense"),
    'AYODHYA_STREETS': (('ayodhya streets',), None,
        "The royal streets of Ayodhya: wide stone-paved avenues lined with tall white mansions with carved balconies, "
        "flags and flower garlands strung across, rangoli at every threshold, the palace towers at the far end; "
        "warm sandstone and white palette"),
    'TAMASA_BANK': (('tamasa bank',), None,
        "The bank of the Tamasa river, a day's journey from Ayodhya: a quiet, slow river with grassy banks, tall "
        "trees with hanging roots, a cleared resting place on the grass, cattle-grazing meadows beyond; dusk-blue and green"),
    'SHRINGAVERAPURA': (('ganga at shringaverapura',), None,
        "Shringaverapura on the Ganga, Guha's land: the wide sacred river with sandy banks, a large spreading ingudi "
        "tree on the bank with a bed of grass beneath it, simple thatched huts of Guha's forest people, wooden boats "
        "drawn up on the sand, dense forest behind; river-blue and forest-green"),
    'BHARADWAJA_ASHRAM': (('bharadwaja ashram',), None,
        "Sage Bharadwaja's hermitage at Prayaga, near where the Ganga meets the Yamuna: a large, orderly ashram of "
        "thatched mud-and-bamboo huts, a smoking fire altar, deer resting, students' seats under trees, flowering "
        "palasha trees, the two rivers glinting in the distance; serene and sunlit"),
    'CHITRAKUTA': (('chitrakuta hermitage',), None,
        "Chitrakuta: a green forested hill with rocky peaks, a neat parnashala (leaf hut of bamboo and leaves) with a "
        "swept courtyard and a small fire altar on its slope, the clear Mandakini river below with sandy steps and "
        "flat rocks, flowering trees, deer and peacocks; fresh green and river-blue, soft morning light"),
    'KEKAYA_PALACE': (('kekaya palace',), None,
        "Girivraja, the Kekaya capital in the northwest: a stone hill-palace with carved wooden balconies and sloping "
        "roofs, snow-touched mountains behind, cool clear light, rich woollen hangings; slate grey, wood brown and gold"),
    'ATRI_ASHRAM': (('atri hermitage',), None,
        "Sage Atri's hermitage: an ancient, very peaceful ashram deep in the forest, weathered thatched huts under huge "
        "old trees, a small fire altar, flowering creepers, a clear pond with lotuses; soft golden, timeless light"),
    # Aranya Kaanda (no location column either: data/3_Aranya_videos.txt PLACE lines point here)
    'DANDAKA_ASHRAMS': (('dandaka hermitages',), None,
        "The circle of sages' hermitages at the edge of the Dandaka forest: many thatched huts of mud and bamboo around "
        "smoking fire altars, sacrificial ladles laid out, great flower garlands, bowls of curd and puffed rice, deer "
        "skins on swept ground, tall old trees all round; serene, smoke-blue morning light"),
    'DANDAKA_FOREST': (('dandaka forest',), None,
        "The deep Dandaka forest: vast old-growth trees with hanging creepers, dim green light filtering down, a rough "
        "earthen path, rocky clearings and thick undergrowth, birds and deer half-hidden; wild and thick but never "
        "horror; forest-green and earth-brown"),
    'SHARABHANGA_ASHRAM': (('sharabhanga hermitage',), None,
        "Sage Sharabhanga's hermitage: a small, very old ashram of a few weathered thatched huts in a clearing, a "
        "large sacred fire altar at its centre, ascetics at austerities under the trees, darbha grass everywhere, an "
        "open sky above the clearing; still, luminous and solemn"),
    'SUTIKSHNA_ASHRAM': (('sutikshna hermitage',), None,
        "Sage Sutikshna's hermitage: a beautifully kept ashram among flowering trees, neat thatched huts, a swept "
        "courtyard with a small fire altar and deer-skin seats, deer wandering at its edge; calm, green and sunlit"),
    'PANCHAPSARA_LAKE': (('panchapsara lake',), None,
        "The Panchapsara lake in the Dandaka forest: a wide, still, mysterious lake ringed by tall trees and reeds, "
        "lotus leaves on the water, a soft glow rising from beneath its surface as if from a hidden palace; misty, "
        "blue-green, quietly magical"),
    'AGASTYA_BROTHER_ASHRAM': (('agastya brother hermitage',), None,
        "The hermitage of Agastya's brother: a quiet ashram of a few thatched huts under huge old trees, a small fire "
        "altar, a grove of trees beside it, seen at dusk with lamps lit in the huts; gentle and peaceful"),
    'AGASTYA_ASHRAM': (('agastya hermitage',), None,
        "Sage Agastya's great hermitage in a forest of pippala trees: wide inner courts with stone seats set out for "
        "the gods, many fire altars, wet bark cloths drying on lines, garlands and sacred vessels, a small Shiva-linga "
        "shrine; radiant golden light over everything; grand yet simple"),
    'PANCHAVATI': (('panchavati',), None,
        "Panchavati on the bank of the Godavari: a neat parnashala (leaf hut of bamboo poles, mud walls and a thatch of "
        "shami wood and darbha) in a level clearing, a swept courtyard with a small fire altar, the wide rushing "
        "Godavari just below with sandy banks and flat rocks, distant hills, jackfruit, mango and jamun trees, swans "
        "on the water, deer and peacocks; fresh green and river-blue"),
    'JANASTHANA_CAMP': (('janasthana camp',), None,
        "Khara's war-camp at Janasthana: a rakshasa encampment in a scorched forest clearing, dark hide tents, black "
        "and red banners, racks of spears, maces and iron clubs, smoking fires, a golden war-chariot; harsh, smoky, "
        "dark-red and black"),
    'LANKA_COURT': (('lanka court',), None,
        "Ravana's royal court in Lanka: a vast hall of gold and dark stone with towering carved pillars, a high golden "
        "throne on a stepped dais, ministers seated along both sides, gem-studded walls, burning brass lamps, deep red "
        "and gold hangings; opulent, imposing, never Mughal"),
    'LANKA_PALACE': (('lanka palace',), None,
        "Ravana's inner palace in Lanka: gilded chambers with windows of diamond lattice, crystal and gold pillars, "
        "silk-draped couches, step-wells and lotus pools in courtyards, terraces overlooking the golden city and the "
        "sea, the Pushpaka vimana on a high terrace; dazzling gold, dark stone and jewel tones"),
    'ASHOKA_VANA': (('ashoka grove',), None,
        "The Ashoka grove in Lanka: a lush pleasure garden of flowering ashoka trees with red blossoms, marble paths, "
        "lotus ponds and pavilions, high walls all round, rakshasi guards at its edges; beautiful but a prison; dusk "
        "light, deep green and red"),
    'MARICHA_ASHRAM': (('maricha hermitage',), None,
        "Maricha's hermitage across the sea: a lonely, bare hut of bark and leaves under a great banyan tree, a spare "
        "fire, a reed mat, a water-pot, a quiet shore of the sea beyond; austere, grey-green, melancholy"),
    'KRAUNCHA_FOREST': (('krauncha forest',), None,
        "The Krauncha forest: a dense, dim, menacing forest of tangled trees and dark undergrowth, a dark cave mouth "
        "in a rocky bank, strange bird calls, very little light reaching the ground; tense and shadowy but not horror"),
    'MATANGA_ASHRAM': (('matanga hermitage',), None,
        "Sage Matanga's ancient hermitage near Pampa: a quiet, very old ashram of weathered huts, a fire altar still "
        "glowing, flower garlands that never fade, bark garments hanging damp on vines, old trees and a stream; "
        "timeless, golden, deeply peaceful"),
}


def place_for(loc, ep):
    """The place reference a scene's location register points to, or None (e.g. a mythic inset)."""
    low = (loc or '').lower()
    if not low or 'mythic' in low:
        return None
    for key, (words, eps, _) in PLACES.items():
        if (eps is None or ep in eps) and any(w in low for w in words):
            return key
    return None


META = ('pick ONE', 'never mix', 'can simplify', 'stay consistent', 'Switch permanently', 'scheme as Rama',
        'from S1 onward', 'Production Bible', 'first appearance', 'note which', 'deliberate distinguishing',
        'Single continuous appearance', 'Progressive visual aging', 'No aging across', 'identical lock',
        'change point', 'following the source')


def clean_lock(lock):
    lock = re.sub(r'\*\*Convention locked[^*]*:\*\*', '', lock)
    lock = re.sub(r'\([^)]*(?:deliberate|see |Reference|Stage|E\d\.\d)[^)]*\)', '', lock)
    lock = ' '.join(x for x in re.split(r'(?<=[.;])\s+', lock) if not any(m in x for m in META))
    lock = lock.replace('Per the VANARA DESIGN BASELINE above — ', '').replace('Per the VANARA DESIGN BASELINE above', '')
    lock = re.sub(r'\s*\(Reference spec only[^)]*\)', '', lock)
    lock = re.sub(r'\*\*Convention locked[^*]*\*\*', '', lock)
    return re.sub(r'\s+', ' ', lock.replace('**', '')).strip()


def mark_for(key):
    if key in NO_MARK:
        return ''
    if key in WOMEN:
        return KUM
    if key in RAVANA_SIDE:
        return SN
    return VN


def stage_of(key, ep):
    for start, stage in reversed(STAGES.get(key, [])):
        if ep_key(ep) >= ep_key(start):
            return stage
    return STAGES[key][0][1] if key in STAGES else None


def character(key, ep):
    """Full look for one character in one episode, or None if the bible has no entry."""
    entry = BIBLE.get(key)
    if not entry:
        return None
    lock = clean_lock(entry['lock'])
    stage = stage_of('RAMA' if key == 'LAKSHMANA' else key, ep) if key in STAGES else None
    if stage:
        look = BIBLE.get('RAMA' if key == 'LAKSHMANA' else key, {}).get('stages', {}).get(stage)
        if look:
            lock = lock.rstrip(' .;') + f'. In this episode: {look.strip().rstrip(".")}.'
    if key in ('HANUMAN', 'SUGRIVA', 'VALI', 'TARA', 'ANGADA', 'NALA', 'NILA') and 'human-proportioned' not in lock:
        lock = f'{VANARA}; {lock}'
    mark = mark_for(key)
    name = key.replace('_', ' ').title()
    return f"{name}: {lock.rstrip(' .;')}" + (f"; {mark}" if mark else '')


NAMES = None


def names_in(text):
    """Bible keys mentioned in a scene prompt, in order of first mention."""
    global NAMES
    if NAMES is None:
        NAMES = {k.title(): k for k in BIBLE}
        NAMES.update({a: k for a, k in ALIASES.items() if k})
    found = []
    for m in re.finditer(r"\b([A-Z][a-z]+)\b", text):
        k = NAMES.get(m.group(1))
        if k and k not in found:
            found.append(k)
    return found
