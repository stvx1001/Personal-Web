# Campfire: the About illustration. Same flat-SVG rules as isle.py (fills + gradients, no filters).
import json, math, re
src = open('isle.py').read()
helpers = src.split('def build(')[0]            # P, poly, box, land, sparkle, tree ... without the island build
helpers = helpers.replace('U = 54;', 'U = 43;').replace('OX, OY = 533, 330', 'OX, OY = 300, 200').replace('W, H = 1440, 1000', 'W, H = 600, 640')
exec(helpers)
def stroke_line(a, b, col, w, cap='round'):
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}"/>')
def log(a, b, w=18):
    stroke_line(a, b, '#6E4630', w); stroke_line((a[0], a[1] - w * 0.22), (b[0], b[1] - w * 0.22), '#8C5B3C', w * 0.55)
    for p in (a, b):
        out.append(f'<ellipse cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{w*0.42:.1f}" ry="{w*0.5:.1f}" fill="#E9C08A"/>')
        out.append(f'<ellipse cx="{p[0]:.1f}" cy="{p[1]:.1f}" rx="{w*0.22:.1f}" ry="{w*0.27:.1f}" fill="#C9955E"/>')
def flame(cx, by, w, h, col):
    out.append(f'<path d="M{cx:.1f} {by-h:.1f} C{cx+w*0.2:.1f} {by-h*0.62:.1f} {cx+w*0.62:.1f} {by-h*0.5:.1f} {cx+w*0.5:.1f} {by-h*0.2:.1f} '
               f'C{cx+w*0.45:.1f} {by:.1f} {cx-w*0.45:.1f} {by:.1f} {cx-w*0.5:.1f} {by-h*0.2:.1f} C{cx-w*0.62:.1f} {by-h*0.5:.1f} {cx-w*0.2:.1f} {by-h*0.62:.1f} {cx:.1f} {by-h:.1f}Z" fill="{col}"/>')
N = 8
land(0, N, 0, N, -1.4, 0)
CT = (N / 2, N / 2)
fx, fy = P(*CT, 0)
# warm glow on the grass
for rx, ry, o in ((150, 74, 0.10), (104, 52, 0.12), (66, 33, 0.14)):
    out.append(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="{rx}" ry="{ry}" fill="#FFC845" fill-opacity="{o}"/>')
# stone ring (back half first)
stones = []
for i in range(10):
    a = i / 10 * 2 * math.pi
    sx, sy = P(CT[0] + 1.15 * math.cos(a), CT[1] + 1.15 * math.sin(a), 0)
    stones.append((sy, sx, i))
def stone(sx, sy, i):
    r = 13 + (i % 3) * 2
    out.append(f'<ellipse cx="{sx:.1f}" cy="{sy+2:.1f}" rx="{r:.1f}" ry="{r*0.62:.1f}" fill="#8E8A99"/>')
    out.append(f'<ellipse cx="{sx-2:.1f}" cy="{sy-2:.1f}" rx="{r*0.8:.1f}" ry="{r*0.46:.1f}" fill="#B9B5C4"/>')
for sy, sx, i in sorted(stones):
    if sy < fy: stone(sx, sy, i)
# logs in a teepee, flames, embers
log((fx - 44, fy + 6), (fx + 30, fy - 16)); log((fx + 44, fy + 6), (fx - 30, fy - 16)); log((fx - 8, fy + 16), (fx + 6, fy - 26), 16)
flame(fx, fy - 2, 86, 150, '#F0569A'); flame(fx - 4, fy - 4, 66, 118, '#FF8A3D'); flame(fx + 2, fy - 6, 44, 84, '#FFC845'); flame(fx, fy - 8, 20, 42, '#FFF4D6')
for (dx, dy, s, c) in ((-30, -150, 7, '#FFC845'), (22, -176, 5, '#F0569A'), (40, -128, 6, '#FFC845'), (-10, -200, 4, '#FF8A3D'), (-44, -104, 5, '#F0569A')):
    out.append(f'<rect x="{fx+dx:.1f}" y="{fy+dy:.1f}" width="{s}" height="{s}" rx="1" fill="{c}"/>')
for sy, sx, i in sorted(stones):
    if sy >= fy: stone(sx, sy, i)
# firewood pile, front-left of the ring
px, py = P(6.5, 6.5, 0)
for j, (dx, dy) in enumerate(((0, 0), (22, 4), (44, 8), (11, -14), (33, -10), (22, -28))):
    a = (px + dx - 26, py + dy + 10); b = (px + dx + 18, py + dy - 12)
    log(a, b, 16)
# a couple of grass tufts
for (tx, ty) in (P(6.8, 1.2), P(1.1, 2.4), P(6.4, 6.6)):
    for k in (-6, 0, 6):
        out.append(f'<path d="M{tx+k:.1f} {ty:.1f} Q{tx+k-2:.1f} {ty-10:.1f} {tx+k+3:.1f} {ty-16:.1f} Q{tx+k+2:.1f} {ty-7:.1f} {tx+k+4:.1f} {ty:.1f}Z" fill="#5DB24B"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{"".join(defs)}</defs>{"".join(out)}</svg>'
open('camp.svg', 'w').write(svg)
print(len(svg), 'fire', (round(fx), round(fy)), 'pile', (round(px), round(py)))
