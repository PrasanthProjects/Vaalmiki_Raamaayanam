"""The one page that links every sarga's Shorts page (and the long-video pages).

usage:  python hub.py        writes publish/hub.html from data/pages.json
After publishing a new sarga page, add its link to data/pages.json, run this, and republish the hub.
"""
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
# Gita Press sarga counts (the text the Shorts follow)
KANDAS = [('1_Bala_Kanda', 'బాలకాండ', 77), ('2_Ayodhya_Kanda', 'అయోధ్యకాండ', 119), ('3_Aranya_Kanda', 'అరణ్యకాండ', 75),
          ('4_Kishkindha_Kanda', 'కిష్కింధకాండ', 67), ('5_Sundara_Kanda', 'సుందరకాండ', 68),
          ('6_Yuddha_Kanda', 'యుద్ధకాండ', 128), ('7_Uttara_Kanda', 'ఉత్తరకాండ', 111)]


def main():
    pages = json.load(open(os.path.join(TOOLS, 'data', 'pages.json'), encoding='utf-8'))
    data = {'kandas': [{'dir': d, 'te': te, 'sargas': n, 'pages': pages['shorts'].get(d, {})} for d, te, n in KANDAS],
            'long': pages['long'], 'other': pages.get('other', [])}
    for k in data['kandas']:
        for s in k['pages']:
            assert 1 <= int(s) <= k['sargas'], f"{k['dir']}: no sarga {s}"
            assert os.path.isdir(os.path.join(ROOT, k['dir'], f'Sarga_{int(s):03d}')), (k['dir'], s)
    tpl = open(os.path.join(TOOLS, 'hub_template.html'), encoding='utf-8').read()
    out = tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    os.makedirs(os.path.join(TOOLS, 'publish'), exist_ok=True)
    open(os.path.join(TOOLS, 'publish', 'hub.html'), 'w', encoding='utf-8', newline='\n').write(out)
    print('hub:', sum(len(k['pages']) for k in data['kandas']), 'sarga pages,', sum(1 for x in data['long'] if x[2]), 'long-video pages,', len(data['other']), 'other')


if __name__ == '__main__':
    main()
