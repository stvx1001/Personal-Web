import json, sys, os, numpy as np
from PIL import Image
# usage: layout.py <dir> <bodyNames json> <exprNames json> <propNames json> <row2Scale> <headScaleMode> <propScale> <noShadow csv> <palette points json>
d=sys.argv[1]; body=json.loads(sys.argv[2]); expr=json.loads(sys.argv[3]); prop=json.loads(sys.argv[4])
f2=float(sys.argv[5]); ps=float(sys.argv[7]); noshadow=sys.argv[8].split(','); palpts=json.loads(sys.argv[9])
m=json.load(open(f'{d}/out/meta.json'))
sheet=np.asarray(Image.open(f'{d}/sheet.webp').convert('RGB')).astype(float)
B=np.median(np.concatenate([sheet[:8].reshape(-1,3),sheet[-8:].reshape(-1,3)]),0); k=(sheet@B)/(B@B)
files=list(body)
s=343.1/m['Turnaround-Front']['h']
row2=[n for n in files if not n.startswith('Turn')]
ground={1:max(m[n]['y']+m[n]['h'] for n in files if n.startswith('Turn')), 2:m[row2[0]]['y']+m[row2[0]]['h']}
out={'body':[],'head':[],'prop':[]}
for n in files:
    v=m[n]; a=np.asarray(Image.open(f'{d}/out/{n}.png'))[...,3].astype(float)/255
    row=1 if n.startswith('Turn') else 2; f=1 if row==1 else f2
    feet=a[int(a.shape[0]*0.9):]; cx=(feet.sum(0)*np.arange(a.shape[1])).sum()/feet.sum() if n not in noshadow else (a.sum(0)*np.arange(a.shape[1])).sum()/a.sum()
    e=dict(name=body[n],file=n,x=round(200-cx*s*f,1),y=round(384-(ground[row]-v['y'])*s*f,1),w=round(v['w']*s*f,1),h=round(v['h']*s*f,1))
    x0,x1=v['x']//4-10,(v['x']+v['w'])//4+10; gy=ground[row]//4
    band=k[gy-14:gy+8, x0:x1]; sh=(band>0.80)&(band<0.965)
    cols=np.where(sh.sum(0)>=2)[0]; rows=np.where(sh.sum(1)>=4)[0]
    if n not in noshadow and len(cols)>20:
        e.update(sw=round(float((cols.max()-cols.min())*4*s*0.62*f)), sh=round(float(max(len(rows),4)*4*s*0.62*f)), op=round(min(float(1-band[sh].mean())*2.4,0.3),2), scx=round(float(200+((x0+cols.min()+x0+cols.max())/2*4-v['x']-cx)*s*f),1))
    out['body'].append(e)
if expr:
    hs=169/max(m[n]['h'] for n in expr)
    for n,nm in expr.items():
        w,h=m[n]['w']*hs,m[n]['h']*hs
        out['head'].append(dict(name=nm,file=n,x=round(100-w/2,1),y=round(190-h,1),w=round(w,1),h=round(h,1)))
for n,nm in prop.items():
    out['prop'].append(dict(name=nm,file=n,w=round(m[n]['w']*ps,1),h=round(m[n]['h']*ps,1)))
out['palette']=['#%02X%02X%02X'%tuple(np.median(sheet[y-5:y+5,x-5:x+5].reshape(-1,3),0).round().astype(int)) for x,y in palpts]
json.dump(out,open(f'{d}/out/layout.json','w'))
print(json.dumps(out))
