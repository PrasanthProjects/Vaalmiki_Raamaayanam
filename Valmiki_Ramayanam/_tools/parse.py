import re, sys, json
def deva2telugu(s):
    out=[]
    for ch in s:
        c=ord(ch)
        if 0x0900<=c<=0x097F and ch not in '।॥':
            out.append(chr(c-0x0900+0x0C00))
        else: out.append(ch)
    return ''.join(out)
DIG=str.maketrans('०१२३४५६७८९','0123456789')
def parse(path):
    t=open(path,encoding='utf-8').read()
    poem=re.search(r'<poem>(.*?)</poem>',t,re.S).group(1)
    poem=poem.translate(DIG)
    # split on verse markers
    parts=re.split(r'॥\s*(\d+)-(\d+)-(\d+)\s*॥',poem)
    verses=[]
    for i in range(1,len(parts),4):
        body=parts[i-1]
        lines=[l.strip() for l in body.strip().split('\n') if l.strip() and 'सर्गः ॥' not in l and 'काण्डे' not in l]
        verses.append((int(parts[i+2]),[deva2telugu(l) for l in lines]))
    return verses
if __name__=='__main__':
    v=parse(sys.argv[1])
    json.dump(v,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    nums=[n for n,_ in v]
    print(len(v), nums==list(range(1,len(v)+1)))
