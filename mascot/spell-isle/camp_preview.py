import json
R = '/tmp/claude-0/-home-user-Personal-Web/766ba0e2-b055-5d64-b369-a9ca24e260c2'
items = json.load(open('camp_items.json'))
html = []
for it in items:
    L = json.load(open(f"{R}/{it['dir']}/out/layout.json"))
    if it.get('pose'):
        e = next(b for b in L['body'] if b['name'] == it['pose'])
        k = it['size'] / 400; bx, by = it['fx'] - 200 * k, it['fy'] - 384 * k
        x = bx + (400 - e['x'] - e['w']) * k if it.get('flip') else bx + e['x'] * k
        if 'sw' in e and 'op' in e:
            sx = bx + ((400 - e.get('scx',200)) if it.get('flip') else e.get('scx',200)) * k
            html.append(f'<div style="position:absolute;left:{sx-e["sw"]*k/2}px;top:{by+(379-e["sh"]/2)*k}px;width:{e["sw"]*k}px;height:{e["sh"]*k}px;border-radius:50%;background:rgba(0,0,0,{e["op"]})"></div>')
        html.append(f'<img src="{R}/{it["dir"]}/out/{e["file"]}.png" style="position:absolute;left:{x}px;top:{by+e["y"]*k}px;width:{e["w"]*k}px;height:{e["h"]*k}px;{"transform:scaleX(-1)" if it.get("flip") else ""}">')
    else:  # prop: centred at (cx, cy), width w, rotated
        e = next(b for b in L['prop'] if b['name'] == it['item'])
        w = it['w']; h = w * e['h'] / e['w']
        html.append(f'<img src="{R}/{it["dir"]}/out/{e["file"]}.png" style="position:absolute;left:{it["cx"]-w/2}px;top:{it["cy"]-h/2}px;width:{w}px;height:{h}px;transform:rotate({it["rot"]}deg)">')
open('camp_preview.html', 'w').write(f'<html><body style="margin:0;background:#FBF8F2"><div style="position:relative;width:600px;height:640px">{open("camp.svg").read()}<div style="position:absolute;inset:0">{"".join(html)}</div></div></body></html>')
