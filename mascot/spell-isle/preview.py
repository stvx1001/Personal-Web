import json, sys
A = json.load(open('anchors.json'))
R = '/tmp/claude-0/-home-user-Personal-Web/766ba0e2-b055-5d64-b369-a9ca24e260c2'
chars = json.load(open('chars.json'))
imgs = []
for c in chars:
    L = json.load(open(f"{R}/{c['dir']}/out/layout.json"))
    e = next(b for b in L['body'] if b['name'] == c['pose'])
    k = c['size'] / 400; ax, ay = A[c['anchor']]
    bx, by = ax - 200 * k, ay - 384 * k
    x = bx + e['x'] * k; y = by + e['y'] * k; w = e['w'] * k; h = e['h'] * k
    if c.get('flip'): x = bx + (400 - e['x'] - e['w']) * k
    sh = ''
    if 'sw' in e:
        sx = bx + (e.get('scx', 200) if not c.get('flip') else 400 - e.get('scx', 200)) * k
        sh = f'<div style="position:absolute;left:{sx - e["sw"]*k/2}px;top:{by + (379 - e["sh"]/2)*k}px;width:{e["sw"]*k}px;height:{e["sh"]*k}px;border-radius:50%;background:rgba(0,0,0,{e["op"]});filter:blur(2px)"></div>'
    imgs.append(sh + f'<img src="{R}/{c["dir"]}/out/{e["file"]}.png" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{"transform:scaleX(-1);" if c.get("flip") else ""}">')
logo = '<div style="position:absolute;left:{}px;top:{}px;width:430px;height:118px;border:3px dashed #F0569A;transform:rotate(-6deg);font:700 28px sans-serif;color:#F0569A;display:flex;align-items:center;justify-content:center">PIXEL SPELL logo</div>'.format(*json.load(open('logo.json')))
open('preview.html', 'w').write(f'<html><body style="margin:0;background:#FBF8F2"><div style="position:relative;width:1440px;height:1000px;overflow:hidden">{open("isle.svg").read()}<div style="position:absolute;inset:0">{logo}{"".join(imgs)}</div></div></body></html>')
