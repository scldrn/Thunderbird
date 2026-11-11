"""Raster estimate of CAD cover silhouette over a nominal circular aperture.

Vertical projection of tessellated faces, not flow or installed pressure loss.
"""
from pathlib import Path
import gzip,json,math
from PIL import Image,ImageDraw,ImageChops
HERE=Path(__file__).resolve().parent
XC,YC,R=-160.,-76.,42.


def raster_coverage(vertices,triangles,n,center=(XC,YC),radius=R):
 xc,yc=center;r=radius
 mask=Image.new('L',(n,n),0);draw=ImageDraw.Draw(mask)
 def conv(v):return ((v[0]-(xc-r))/(2*r)*(n-1),((yc+r)-v[1])/(2*r)*(n-1))
 verts=[conv(v) for v in vertices]
 for triangle in triangles:
  points=[verts[i] for i in triangle]
  if max(v[0] for v in points)<0 or min(v[0] for v in points)>=n or max(v[1] for v in points)<0 or min(v[1] for v in points)>=n:continue
  draw.polygon(points,fill=255)
 aperture=Image.new('L',(n,n),0);ImageDraw.Draw(aperture).ellipse((0,0,n-1,n-1),fill=255)
 overlap=ImageChops.multiply(mask,aperture)
 ap_count=aperture.histogram()[255];over_count=overlap.histogram()[255]
 result={'pixels':n,'aperture_pixels':ap_count,'overlap_pixels':over_count,'covered_fraction':over_count/ap_count,
         'circle_raster_area_mm2':ap_count*(2*r/n)**2,'analytic_circle_area_mm2':math.pi*r*r}
 return result,aperture,overlap


def evaluate(name,path,label,n,save):
 with gzip.open(HERE/path,'rt') as f:data=json.load(f)
 item=next(v for v in data['items'] if v['name']==label)
 result,aperture,overlap=raster_coverage(item['vertices'],item['triangles'],n)
 if save:
  img=Image.new('RGB',(n,n),(25,30,36));img.paste((55,75,88),(0,0,n,n),aperture)
  img.paste((235,102,64),(0,0,n,n),overlap);img.save(HERE/f'PROYECCION_{name}.png')
 return result


def main():
 configs=[('deslizante','C06_deslizante_evaluacion_mallas.json.gz','compuerta_C03'),
          ('bisagra','C06_evaluacion_mallas.json.gz','compuerta')]
 out={'scope':'proyeccion vertical XY de malla de tapa sobre circulo nominal D84, no caudal ni CFD; teselacion 0,4mm',
      'center_mm':[XC,YC],'diameter_mm':2*R,'results':{}}
 for name,path,label in configs:out['results'][name]=[evaluate(name,path,label,n,n==672) for n in (336,672,1344)]
 (HERE/'PROYECCION.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PROYECCION_COMPLETA',flush=True)
 for name,values in out['results'].items():print(name,[round(x['covered_fraction'],6) for x in values],flush=True)

if __name__=='__main__':main()
