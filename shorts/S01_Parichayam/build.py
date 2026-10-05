"""Local story edit: existing Telugu narration, cinematic stills, gentle dissolves."""
from pathlib import Path
import subprocess, json, wave, math

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SOURCE=ROOT/'production/E0.01_parichayam'
FF=ROOT/'production/tools/ffmpeg.exe'
LOGO=ROOT/'assets/branding/puranamrutham-telugu-logo.png'
ASSETS='assets/images/E0.01_parichayam/'
PLAN=[
 (0,'పురాణామృతం','పురాణాలు • ఇతిహాసాలు\nఅమృత గాథలు','production/E0.01_parichayam/cinematic-v2/river.png'),
 (1,'శ్రీమద్రామాయణం','సంపూర్ణ వాల్మీకి రామాయణం\nమన ప్రయాణం మొదలు','production/E0.01_parichayam/cinematic-v2/river.png'),
 (2,'ఆదికావ్యం','24,000 శ్లోకాలు\nఆరు కాండలు + ఉత్తర కాండ','production/E0.01_parichayam/cinematic-v2/manuscripts.png'),
 (7,'మనిషిగా ఎలా బతకాలి?','మన జీవితానికి దారి చూపిన\nశ్రీరామచంద్రుడు',ASSETS+'scene-07-humanity-family.png'),
 (8,'మన జీవితంలో రామాయణం','బంధాలు • ధర్మం • మాటపై నిబద్ధత\nతరతరాలకు మార్గదర్శనం',ASSETS+'scene-08-living-ramayana-tradition.png'),
 (9,'హనుమ సన్నిధి','యత్ర యత్ర రఘునాథ కీర్తనం,\nతత్ర తత్ర కృతమస్తకాంజలిం ।\nబాష్పవారి పరిపూర్ణలోచనం,\nమారుతిం నమత రాక్షసాంతకం ॥',ASSETS+'scene-09-hanuman-listening.png'),
 (12,'వాల్మీకి వందనం','కూజంతం రామరామేతి\nమధురం మధురాక్షరం ।\nఆరుహ్య కవితాశాఖాం\nవందే వాల్మీకి కోకిలం ॥',ASSETS+'scene-12-closing-verse-background.png'),
 (13,'రామాయణం అనే పేరు','రాముడి ఆయనం\nవాల్మీకి మహర్షి మహాకావ్యం',ASSETS+'scene-13-valmiki-writing.png'),
 (14,'తర్వాతి భాగంలో…','వాల్మీకి మహర్షి ఎవరు?\nఈ మహాకావ్యం ఎలా పుట్టింది?',ASSETS+'scene-14-next-episode-end-card.png'),
 (15,'మన ప్రయాణం కొనసాగుతుంది','వాల్మీకి మహర్షి కథ — భాగం 1\nపురాణామృతంతో కలిసి సాగుదాం',ASSETS+'scene-14-next-episode-end-card.png'),
]

def run(args):
    r=subprocess.run([str(FF),'-hide_banner','-loglevel','error','-y',*map(str,args)],cwd=P,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr)

for d in ('audio','clips','exports'): (P/d).mkdir(exist_ok=True)
styles='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Nirmala UI,67,&H009EDAF2,&H00FFFFFF,&H00201510,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,8,70,100,1140,1
Style: Caption,Nirmala UI,47,&H00FFFFFF,&H00FFFFFF,&H00201510,&H90000000,0,0,0,0,100,100,0,0,1,1,1,8,65,95,1270,1
Style: Label,Nirmala UI,38,&H00D5E4EB,&H00FFFFFF,&H00201510,&H80000000,0,0,0,0,100,100,0,0,1,1,1,8,90,110,360,1
Style: Footer,Nirmala UI,35,&H00D5E4EB,&H00FFFFFF,&H00201510,&H80000000,0,0,0,0,100,100,0,0,1,1,1,8,90,110,1590,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
timeline=[]
script=['# S01 — పరిచయం: మన జీవితానికి రామాయణం\n',
        'A self-contained vertical story adapted from E0.01. Uses existing standard Telugu narration; no new online speech request. The complete verses are retained.\n',
        'Story: welcome → the epic → human values → living tradition → Hanuman → Valmiki → next episode.\n']
position=0.0
for index,(sid,title,caption,img) in enumerate(PLAN):
    ident=f'{sid:02}'
    wav=P/'audio'/f'{ident}.wav'
    if not wav.exists(): run(['-i',SOURCE/'audio'/f'{ident}.mp3','-ac','1','-ar','24000',wav])
    with wave.open(str(wav)) as w: speech=w.getnframes()/w.getframerate()
    duration=math.ceil((speech+1.4)*30)/30
    frames=round(duration*30)
    start=position
    narration_file='00-bumper.txt' if sid==0 else '15-outro.txt' if sid==15 else f'scene-{ident}.txt'
    dialogue=(SOURCE/'narration'/narration_file).read_text(encoding='utf-8').strip()
    timeline.append(dict(scene=sid,start=round(start,3),duration=duration,speech_start=round(start+0.7,3),speech_duration=speech,image=img,dialogue=dialogue,title=title))
    script += [f'\n## {index+1}. {title}\n',f'**Dialogue:** {dialogue}\n',f'**Visual:** {img}\n',f'**Edit:** slow camera move, 0.6-second dissolve; preserve speech and pause.\n']
    position+=duration-(0.6 if index<len(PLAN)-1 else 0)
    label='తర్వాతి భాగం • E1.01' if sid>=14 else 'పరిచయం • కథా ప్రయాణం'
    events=[('Title',title),('Caption',caption.replace('\n',r'\N')),('Label',label),('Footer','సంపూర్ణ వాల్మీకి రామాయణం')]
    ass=P/f'{ident}.ass'
    ass.write_text(styles+'\n'.join(f'Dialogue: 0,0:00:00.00,0:10:00.00,{style},,0,0,0,,{text}' for style,text in events),encoding='utf-8')
    delta=0.008 if sid==2 else 0.055
    z=f'1+{delta}*on/{frames-1}' if index%2==0 else f'1+{delta}-{delta}*on/{frames-1}'
    graph=(
      '[0:v]split[bg][fg];[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=20,scale=1080:1920,eq=brightness=-0.18:saturation=0.65,setsar=1[b];'
      f"[fg]scale=2160:-2,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1080x608:fps=30,setsar=1[f];"
      '[b][f]overlay=0:460:shortest=1,drawbox=x=0:y=0:w=1080:h=345:color=0x250505@0.94:t=fill,'
      'drawbox=x=0:y=1080:w=1080:h=840:color=0x100a07@0.65:t=fill,'
      'drawbox=x=80:y=345:w=920:h=2:color=0xdcb36a:t=fill,'
      'drawbox=x=80:y=1540:w=920:h=2:color=0xdcb36a@0.6:t=fill[l];'
      '[1:v]crop=iw*0.90:ih*0.46:iw*0.06:ih*0.23,scale=800:-2,setsar=1[logo];'
      f'[l][logo]overlay=140:95:eof_action=repeat,ass={ident}.ass[v];'
      f'[2:a]adelay=700:all=1,apad,atrim=duration={duration},loudnorm=I=-18:TP=-2:LRA=9,aresample=24000[a]'
    )
    clip=P/'clips'/f'{ident}.mp4'
    if not clip.exists():
        run(['-loop','1','-i',ROOT/img,'-i',LOGO,'-i',wav,'-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-map','[a]','-t',duration,'-r','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',clip])
    print('Scene ready',ident,flush=True)

(P/'SCRIPT_AND_DIALOGUE.md').write_text('\n'.join(script),encoding='utf-8')
(P/'scene_plan.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')

# Render only boundary dissolves, then concatenate the non-overlapping scene interiors.
# This avoids buffering a whole multi-minute, ten-input xfade graph in memory.
parts=[]
for i,item in enumerate(timeline):
    ident=f"{item['scene']:02}"
    start=0.6 if i else 0
    end=item['duration']-(0.6 if i<len(timeline)-1 else 0)
    core=P/'clips'/f'core_{ident}.mp4'
    run(['-ss',start,'-i',P/'clips'/f'{ident}.mp4','-t',end-start,'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','24000','-b:a','160k',core])
    parts.append(core)
    if i<len(timeline)-1:
        nextid=f"{timeline[i+1]['scene']:02}"
        transition=P/'clips'/f'blend_{ident}_{nextid}.mp4'
        run(['-ss',item['duration']-0.6,'-t','0.6','-i',P/'clips'/f'{ident}.mp4','-t','0.6','-i',P/'clips'/f'{nextid}.mp4',
             '-filter_complex_threads','1','-filter_complex',
             '[0:v]settb=AVTB,setpts=PTS-STARTPTS[a];[1:v]settb=AVTB,setpts=PTS-STARTPTS[b];[a][b]xfade=transition=fade:duration=0.6:offset=0[v];[0:a][1:a]acrossfade=d=0.6:c1=tri:c2=tri[s]',
             '-map','[v]','-map','[s]','-t','0.6','-r','30','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','24000','-b:a','160k',transition])
        parts.append(transition)
    print('Transition edit ready',ident,flush=True)

(P/'concat.txt').write_text(''.join("file '"+p.relative_to(P).as_posix()+"'\n" for p in parts),encoding='utf-8')
out=P/'exports/Parichayam_Story_Short.mp4'
run(['-f','concat','-safe','0','-i','concat.txt','-vf',f'fade=t=in:st=0:d=0.5,fade=t=out:st={position-0.7}:d=0.7','-af',f'afade=t=out:st={position-0.7}:d=0.7','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',out])
run(['-i',out,'-f','null','NUL'])
run(['-i',out,'-vn','-ar','24000','-c:a','pcm_s16le',P/'exports/Parichayam_Narration.wav'])
run(['-i',out,'-vf','fps=1/12,scale=270:480,tile=4x4','-frames:v','1',P/'exports/review.jpg'])
(P/'exports/validation.json').write_text(json.dumps(dict(planned_duration_seconds=position,full_decode='passed',resolution='1080x1920',fps=30,transition='0.6 second cross-dissolve with speech-safe padding',speech='existing local te-IN-MohanNeural',published=False),indent=2),encoding='utf-8')
print('DONE',out,flush=True)
