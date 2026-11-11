"""Long videos (Long_Videos/Videos, V01, V02 …) for the Video Maker, taken from each kaanda's helper page data.

  python tools/make_long_data.py 1_Baala_Khaanda

Each video becomes a "film" for the movie mode: its ElevenLabs parts (భాగం 1, 2 …) are the scenes, its clips are the
shots. The voice is recorded one part at a time; inside a part the pictures share the recording's length by how much
each clip says. Writes src/data/long_<kaanda>_<V>.json (everything, for the page) and a slim copy for the renderer.
"""
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
MAKER = os.path.dirname(HERE)
VIDEOS = os.path.join(os.path.dirname(MAKER), 'Long_Videos', 'Videos')
KAANDA_EN = {'1_Baala_Khaanda': 'Bala', '2_Ayodhya_Khaanda': 'Ayodhya', '3_Aranya_Khaanda': 'Aranya',
             '4_Kishkinda_Khaanda': 'Kishkindha', '5_Sundhara_Khaanda': 'Sundara'}
norm = lambda t: re.sub(r'\s+', ' ', re.sub(r'[\[\(].*?[\]\)]', '', t or '')).strip()


# each part's background music mood, from its words (the same five moods and Suno prompts as the Shorts;
# a part with no music of its own plays Video_Maker/Music/music_<mood>.mp3)
MOOD_WORDS = {
    'heroic': ['యుద్ధ', 'రాక్షస', 'బాణ', 'సంహర', 'అస్త్ర', 'ధనుస్సు', 'వధ', 'ఆగ్రహ', 'సైన్య', 'పరాక్రమ'],
    'sad': ['దుఃఖ', 'ఏడ్', 'విలప', 'కన్నీ', 'బాధ', 'వేదన', 'మరణ', 'శోక'],
    'mystery': ['మాయ', 'రహస్య', 'శాప', 'భయంకర', 'వింత', 'ఆశ్చర్య'],
    'joyful': ['పెళ్ళి', 'వివాహ', 'కల్యాణ', 'సంతోష', 'ఆనంద', 'జనన', 'సంబర', 'పండుగ', 'ఉత్సవ', 'పుట్టారు'],
}


def mood_of(text):
    score = {m: sum(text.count(w) for w in ws) for m, ws in MOOD_WORDS.items()}
    best = max(score, key=score.get)
    return best if score[best] >= 3 else 'calm'


def secs_of(c):
    m = re.search(r'· (\d+) సె', c.get('label', ''))
    if m:
        return int(m.group(1))
    m = re.findall(r'(\d+):(\d\d)', c.get('time', ''))
    if len(m) == 2:
        return max(2, (int(m[1][0]) * 60 + int(m[1][1])) - (int(m[0][0]) * 60 + int(m[0][1])))
    return 6


def key(t):
    """Letters only: quotes, dandas, dashes and spaces differ between a clip's text and the ElevenLabs part."""
    return ''.join(ch for ch in norm(t) if unicodedata.category(ch)[0] in 'LMN')


def spoken(c):
    """A clip's narration, or '' when it only says the voice above runs on ("(పై నెరేషన్ కొనసాగుతుంది …)")."""
    t = (c.get('narration') or '').strip()
    return t if norm(t) else ''


def parts_of(v):
    """Which ElevenLabs part each spoken clip belongs to: each clip's text is found in the parts in story order
    (start, middle or end of it, so a changed word does not lose it); clips not found go with the clip before."""
    keys = [key(p) for p in v['tts']]
    whole, starts = '', []
    for k in keys:
        starts.append(len(whole))
        whole += k
    part_at = lambda pos: max(i for i, s in enumerate(starts) if s <= pos)
    clips = v['clips']
    anchor, ptr = [], 0
    for c in clips:
        k = key(spoken(c))
        hit = None
        if k:
            n = min(25, len(k))
            for off in (0, max(0, len(k) // 2 - n // 2), len(k) - n):
                probe = k[off:off + n]
                pos = whole.find(probe, ptr)
                if pos < 0:
                    pos = whole.find(probe)
                if pos >= 0:
                    hit = part_at(pos)
                    ptr = max(ptr, pos)
                    break
        anchor.append(hit)
    # fill: a clip without an anchor takes the previous anchor's part (or the next one's if it comes first)
    out, last = [], 0
    for i, a in enumerate(anchor):
        if a is not None:
            last = a
        out.append(last if a is None else a)
    for i in range(len(out) - 1, -1, -1):   # never go backwards
        if i + 1 < len(out) and out[i] > out[i + 1]:
            out[i] = out[i + 1]
    # the channel bumper clip is its own part (భాగం … · 🎬 ఇంట్రో క్లిప్): the channel intro video with its own voice
    intro = next((i for i, lab in enumerate(v['ttsLabels']) if 'ఇంట్రో' in lab), None)
    if intro is not None:
        for i, c in enumerate(clips):
            if 'బంపర్' in c.get('label', ''):
                out[i] = intro
    return out


def main(kaanda):
    html = open(os.path.join(VIDEOS, f'{kaanda}_VIDEOS_HELPER.html'), encoding='utf-8').read()
    data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
                      .group(1).replace(r'<\/', '</'))
    out_dir = os.path.join(MAKER, 'src', 'data')
    ke = KAANDA_EN[kaanda]
    prompts = json.load(open(os.path.join(out_dir, 'music_prompts.json'), encoding='utf-8'))['moods']
    for v in data['slokas']:
        part = parts_of(v)
        scenes = []
        for i, lab in enumerate(v['ttsLabels']):
            mood = mood_of(v['tts'][i])
            scenes.append({'si': i + 1, 'title': lab.split(' · ')[0], 'refs': '', 'loc': '', 'mood': mood,
                           'moodLabel': prompts[mood]['label'], 'suno': prompts[mood]['prompt'], 'songstyle': '',
                           'voiceLabel': lab, 'voiceText': v['tts'][i], 'shots': []})
        t = 0
        for no, (c, p) in enumerate(zip(v['clips'], part), 1):
            text = spoken(c)
            sec = secs_of(c)
            cap = re.findall(r'«([^»]+)»', c.get('note') or '')
            bumper = 'బంపర్' in c.get('label', '')
            scenes[p]['shots'].append({
                'no': no, 'planStart': t, 'sec': sec, 'fixedSec': 0 if text else sec, 'kind': c.get('kind', 'image'),
                'refs': '', 'pic': re.split(r' (?:Correct anatomy|Lighting|Cinematography|Camera)', re.sub(r'^.*?(Scene|The frame shows): ', '', c.get('imagePrompt', '')))[0][:300],
                'label': c.get('label', ''), 'bumper': bumper,
                'lines': [{'who': 'N', 'label': 'కథకుడు', 'voice': '', 'text': text, 'song': False,
                           'est': max(2, round(len(text.split()) / 2.1 + 0.6))}] if text else [],
                'music': [], 'fx': [], 'cap': cap, 'img': c.get('imagePrompt', ''), 'end': c.get('endImagePrompt', ''), 'vid': c.get('videoPrompt', ''),
                'ref': c.get('refs', []), 'advice': c.get('advice', '')})
            t += sec
        film = {'id': f'Long-{ke}-{v["n"]}', 'mode': 'long', 'kanda': kaanda, 'kandaEn': ke, 'file': v['n'],
                'sarga': 0, 'title': f"{v['headline']} | {v['badge']}", 'covers': v.get('title', ''), 'next': '',
                'songnote': '', 'planLength': t, 'scenes': [s for s in scenes if s['shots']],
                'thumbPrompt': v.get('thumbPrompt', ''), 'desc': v.get('desc', ''), 'ytTitle': v.get('title', '')}
        name = f'long_{kaanda}_{v["n"]}'
        json.dump(film, open(os.path.join(out_dir, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        # the renderer needs no prompts or upload text: a slim copy keeps the studio bundle small
        slim = {**film, 'thumbPrompt': '', 'desc': '', 'scenes': [{**s, 'voiceText': '', 'shots': [
            {**x, 'img': '', 'end': '', 'vid': '', 'advice': ''} for x in s['shots']]} for s in film['scenes']]}
        os.makedirs(os.path.join(out_dir, 'slim'), exist_ok=True)
        json.dump(slim, open(os.path.join(out_dir, 'slim', name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print(f"{name}: {len(film['scenes'])} parts, {sum(len(s['shots']) for s in film['scenes'])} clips, plan {int(t // 60)}:{int(t % 60):02d}")
    sys.path.insert(0, HERE)
    from make_movie_data import write_index
    write_index(out_dir)


if __name__ == '__main__':
    main(sys.argv[1])
