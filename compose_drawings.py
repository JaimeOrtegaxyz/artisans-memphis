"""Compose one lightweight overview drawing per keycap. Requires Pillow.
Run render_drawings.py in Blender first, then: python3 compose_drawings.py
"""
import json, math, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'drawings'
PAPER=(250,249,245); INK=(36,43,48); MUTED=(111,117,119); RULE=(212,214,210)

def font(size,bold=False,mono=False):
    names=(['/System/Library/Fonts/Supplemental/Courier New.ttf','DejaVuSansMono.ttf'] if mono else
           ['/System/Library/Fonts/Supplemental/Arial Bold.ttf','DejaVuSans-Bold.ttf'] if bold else
           ['/System/Library/Fonts/Supplemental/Arial.ttf','DejaVuSans.ttf'])
    for name in names:
        try: return ImageFont.truetype(name,size)
        except OSError: pass
    return ImageFont.load_default(size=size)
F=font(24); SMALL=font(21); MONO=font(22,mono=True)

def sheet(row):
    im=Image.new('RGB',(2400,1800),PAPER); d=ImageDraw.Draw(im)
    def text(x,y,label,f=F,color=INK,anchor='la'):
        d.text((x,y),label,font=f,fill=color,anchor=anchor)
    def line(points,color=RULE,width=2): d.line(points,fill=color,width=width)
    def arrow(p,angle):
        a=math.radians(angle); ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
        d.polygon([p,(p[0]+ux*12+vx*4,p[1]+uy*12+vy*4),(p[0]+ux*12-vx*4,p[1]+uy*12-vy*4)],fill=MUTED)
    def hdim(x0,x1,y,edge_y,label):
        for x in (x0,x1): line([(x,edge_y),(x,y+9)],MUTED,1)
        line([(x0,y),(x1,y)],MUTED,1); arrow((x0,y),0); arrow((x1,y),180)
        box=d.textbbox((0,0),label,font=MONO); w=box[2]-box[0]
        d.rectangle(((x0+x1-w)/2-12,y-17,(x0+x1+w)/2+12,y+17),fill=PAPER)
        text((x0+x1)/2,y,label,MONO,anchor='mm')
    def vdim(x,y0,y1,edge_x,label):
        for y in (y0,y1): line([(edge_x,y),(x-9,y)],MUTED,1)
        line([(x,y0),(x,y1)],MUTED,1); arrow((x,y0),90); arrow((x,y1),270)
        label_im=Image.new('RGBA',(250,48),(0,0,0,0)); ld=ImageDraw.Draw(label_im)
        ld.text((125,24),label,font=MONO,fill=INK,anchor='mm')
        label_im=label_im.rotate(90,expand=True)
        im.paste(label_im,(round(x-45),round((y0+y1)/2-label_im.height/2)),label_im)
    def view(key,cx,cy):
        pic=Image.open(OUT/row['views'][key]).convert('RGBA')
        im.paste(pic,(cx-pic.width//2,cy-pic.height//2),pic)

    number=row['number']; title=row['title']
    text(120,45,'MEMPHIS / ARTISAN KEYCAPS',SMALL,MUTED)
    text(120,84,title.upper(),font(48,bold=True))
    text(2280,48,'MC-'+number, font(30,mono=True),anchor='ra')
    text(2280,91,'ORTHOGRAPHIC OVERVIEW  /  REV 03',SMALL,MUTED,anchor='ra')
    line([(120,162),(2280,162)])
    for x,y,label in [(120,205,'01 / TOP'),(1320,205,'02 / UNDERSIDE'),(120,1080,'03 / FRONT'),(1320,1080,'04 / RIGHT SIDE')]:
        text(x,y,label,SMALL,MUTED)
    view('top',620,575); view('underside',1780,575)
    view('front',620,1350); view('right',1780,1350)
    ppmm=row['view_pixels']/row['ortho_scale_mm']; half=9*ppmm
    hdim(620-half,620+half,942,883,'18 mm')
    hdim(620-7.5*ppmm,620+7.5*ppmm,249,318,'15 mm deck')
    text(620,983,'FRONT EDGE',font(18,mono=True),MUTED,anchor='ma')
    text(1780,939,'MX-STYLE SOCKET / PROTOTYPE',MONO,anchor='ma')
    text(1780,980,'Viewed from below. Switch fit requires testing.',SMALL,MUTED,anchor='ma')
    line([(120,1037),(2280,1037)])
    h=row['overall_height_mm']; sh=row['shell_height_mm']; bottom=1350+h*ppmm/2
    vdim(263,1350-h*ppmm/2,bottom,310,f'{h:g} mm')
    vdim(1415,bottom-sh*ppmm,bottom,1470,f'{sh:g} mm')
    text(620,1604,'OVERALL HEIGHT',MONO,anchor='ma')
    text(1780,1604,'SHELL HEIGHT / ~8.6° WALL DRAFT',MONO,anchor='ma')
    line([(120,1681),(2280,1681)])
    text(120,1710,'DESIGN REFERENCE — NOT FOR MANUFACTURE',font(23,bold=True))
    text(2280,1710,'UNITS: mm  /  DISPLAY SCALE: NOT FIXED',MONO,MUTED,anchor='ra')
    text(120,1750,'Heights measured from the modeled skirt bottom. Footprint and deck dimensions are nominal.',SMALL,MUTED)
    text(2280,1750,'Glaze pattern omitted for clarity. No tolerances specified.',SMALL,MUTED,anchor='ra')
    file=OUT/(number+'_'+row['slug']+'.png'); im.save(file,dpi=(300,300))
    print(file)

for row in json.loads((OUT/'dimensions.json').read_text()): sheet(row)
