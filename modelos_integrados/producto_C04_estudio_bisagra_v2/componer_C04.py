from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent
canvas=Image.new('RGB',(1800,620),'#12171d')
d=ImageDraw.Draw(canvas)
font='/System/Library/Fonts/Supplemental/Arial.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
title=ImageFont.truetype(bold,30)
label=ImageFont.truetype(bold,22)
small=ImageFont.truetype(font,16)
d.text((24,14),'C04 | Estudio de una compuerta y su ventilador interno',font=title,fill='#f3f5f7')
for i,(state,caption) in enumerate([('cerrado','1  Cerrado'),('elevado','2  Elevación de 10 mm'),('abierto','3  Giro de 110°')]):
 img=Image.open(p/f'C04_{state}.png').convert('RGB')
 img.thumbnail((590,430))
 x=i*600+(600-img.width)//2
 canvas.paste(img,(x,80))
 d.text((i*600+22,520),caption,font=label,fill='#f3f5f7')
d.text((24,564),'Vista de inspección: carrocería y conducto ocultos. Mecanismo preliminar con interferencias pendientes.',font=small,fill='#f1b76a')
d.text((24,592),'Las imágenes muestran posiciones CAD; no demuestran funcionamiento, resistencia ni prestaciones de vuelo.',font=small,fill='#a5afb8')
canvas.save(p/'C04_tres_estados.png')
