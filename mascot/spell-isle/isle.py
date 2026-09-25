# Spell Isle: isometric footer diorama for Pixel Spell, emitted as flat SVG (fills + linear gradients only,
# so Figma imports it as editable vectors). Grid: x right-down, y left-down, z up.
import json, math
U = 54; C = math.cos(math.pi / 6); S = 0.5
OX, OY = 533, 330
W, H = 1440, 1000
def P(x, y, z=0): return (OX + (x - y) * U * C, OY + (x + y) * U * S - z * U)
def pts(ps): return ' '.join(f'{a:.1f},{b:.1f}' for a, b in ps)
out = []; defs = []; gid = [0]
def poly(ps, fill, extra=''): out.append(f'<polygon points="{pts(ps)}" fill="{fill}" {extra}/>')
def grad(c1, c2, x1=0, y1=0, x2=0, y2=1):
    gid[0] += 1; g = f'g{gid[0]}'
    defs.append(f'<linearGradient id="{g}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    return f'url(#{g})'
def shade(h, f):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(v * f))) for v in (r, g, b))
def box(x0, x1, y0, y1, z0, z1, top, left=None, right=None, gtop=None):
    # visible faces: top (z1), left-front (y = y1), right-front (x = x1)
    left = left or shade(top, 0.82); right = right or shade(top, 0.68)
    poly([P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], left)
    poly([P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], right)
    poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], gtop or top)

GRASS = '#8CCB5E'; LIP = '#6DB33F'
STRATA = ['#F6CF78', '#EDBC5E', '#E2A94C', '#D69740', '#C98636', '#BC7630']
def land(x0, x1, y0, y1, z0, z1, top=GRASS):
    # dirt in horizontal strata, then a grass lip, then the grass top
    n = len(STRATA); lip = 0.32
    zs = [z1 - lip - (z1 - lip - z0) * i / n for i in range(n + 1)]
    for i in range(n):
        a, b = zs[i + 1], zs[i]; c = STRATA[i]
        poly([P(x0, y1, a), P(x1, y1, a), P(x1, y1, b), P(x0, y1, b)], c)
        poly([P(x1, y0, a), P(x1, y1, a), P(x1, y1, b), P(x1, y0, b)], shade(c, 0.86))
    poly([P(x0, y1, z1 - lip), P(x1, y1, z1 - lip), P(x1, y1, z1), P(x0, y1, z1)], LIP)
    poly([P(x1, y0, z1 - lip), P(x1, y1, z1 - lip), P(x1, y1, z1), P(x1, y0, z1)], shade(LIP, 0.85))
    # scalloped grass edge hanging over the dirt
    for t in range(int((x1 - x0) * 2)):
        xa = x0 + t * 0.5
        poly([P(xa, y1, z1 - lip), P(xa + 0.5, y1, z1 - lip), P(xa + 0.25, y1, z1 - lip - 0.16)], LIP)
    for t in range(int((y1 - y0) * 2)):
        ya = y0 + t * 0.5
        poly([P(x1, ya, z1 - lip), P(x1, ya + 0.5, z1 - lip), P(x1, ya + 0.25, z1 - lip - 0.16)], shade(LIP, 0.85))
    poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], grad('#9BD66B', top, 0, 0, 1, 1))

def sparkle(cx, cy, r, fill='#FFFFFF'):
    k = r * 0.28
    out.append(f'<path d="M{cx:.1f} {cy-r:.1f} Q{cx+k:.1f} {cy-k:.1f} {cx+r:.1f} {cy:.1f} Q{cx+k:.1f} {cy+k:.1f} {cx:.1f} {cy+r:.1f} Q{cx-k:.1f} {cy+k:.1f} {cx-r:.1f} {cy:.1f} Q{cx-k:.1f} {cy-k:.1f} {cx:.1f} {cy-r:.1f}Z" fill="{fill}"/>')
def face_center(x0, x1, y, z0, z1):  # centre of a left-front face
    a = P((x0 + x1) / 2, y, (z0 + z1) / 2); return a
def rface_center(x, y0, y1, z0, z1):
    return P(x, (y0 + y1) / 2, (z0 + z1) / 2)
def spell_block(x, y, z, s=1.0, col='#FFC845'):
    box(x, x + s, y, y + s, z, z + s, col, shade(col, 0.9), shade(col, 0.76))
    cx, cy = face_center(x, x + s, y + s, z, z + s); sparkle(cx, cy, s * U * 0.26)
    cx, cy = rface_center(x + s, y, y + s, z, z + s); sparkle(cx, cy, s * U * 0.22, '#FFF4D6')
    for (a, b) in ((0.12, 0.12), (0.88, 0.12), (0.12, 0.88), (0.88, 0.88)):
        px, py = P(x + s * a, y + s, z + s * b); out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{s*2.6:.1f}" fill="#FFFFFF" fill-opacity="0.85"/>')
def bricks(x0, x1, y0, y1, z0, z1):
    B = '#C8553D'
    box(x0, x1, y0, y1, z0, z1, '#D9694F', B, shade(B, 0.8))
    # mortar: courses on both visible faces
    for zc in (z0 + (z1 - z0) / 2,):
        a, b = P(x0, y1, zc), P(x1, y1, zc); out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#8E3A2A" stroke-width="2"/>')
        a, b = P(x1, y0, zc), P(x1, y1, zc); out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#7A3124" stroke-width="2"/>')
    for i, xa in enumerate([x0 + 0.5 * k for k in range(1, int((x1 - x0) * 2))]):
        zlo, zhi = (z0, z0 + (z1 - z0) / 2) if i % 2 else (z0 + (z1 - z0) / 2, z1)
        a, b = P(xa, y1, zlo), P(xa, y1, zhi); out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#8E3A2A" stroke-width="2"/>')
    for i, ya in enumerate([y0 + 0.5 * k for k in range(1, int((y1 - y0) * 2))]):
        zlo, zhi = (z0, z0 + (z1 - z0) / 2) if i % 2 else (z0 + (z1 - z0) / 2, z1)
        a, b = P(x1, ya, zlo), P(x1, ya, zhi); out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#7A3124" stroke-width="2"/>')
def tree(x, y, z, big=1.0):
    box(x - 0.18, x + 0.18, y - 0.18, y + 0.18, z, z + 1.0 * big, '#8A5A3B', '#7A4E33', '#643F29')
    g = ['#4FA044', '#5DB24B', '#72C257']
    box(x - 0.8 * big, x + 0.8 * big, y - 0.8 * big, y + 0.8 * big, z + 0.9 * big, z + 1.9 * big, g[1], g[0], shade(g[0], 0.82))
    box(x - 0.55 * big, x + 0.55 * big, y - 0.55 * big, y + 0.55 * big, z + 1.9 * big, z + 2.6 * big, g[2], g[1], shade(g[1], 0.82))
def fence(pts_):
    for (xa, ya), (xb, yb) in zip(pts_, pts_[1:]):
        for zr in (0.35, 0.62):
            a, b = P(xa, ya, zr), P(xb, yb, zr)
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>')
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]+3:.1f}" x2="{b[0]:.1f}" y2="{b[1]+3:.1f}" stroke="#D9D2C4" stroke-width="2"/>')
    for (xa, ya) in pts_:
        box(xa - 0.09, xa + 0.09, ya - 0.09, ya + 0.09, 0, 0.8, '#FFFFFF', '#EEE8DC', '#D9D2C4')

def build(z_off=0):
    # ---- back to front ----
    # floating brick ledge (back-left), with a spell block on it
    bricks(1.0, 5.0, 0.2, 2.2, 3.0, 3.6)
    spell_block(3.3, 0.6, 3.6, 1.0, '#FFC845')
    # main island and the raised tier
    land(0, 16, 0, 8, -4.0, 0)
    def gshadow(x, y, rx, ry, o=0.13):
        cx, cy = P(x, y, 0.01); out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" fill="#2E4A1E" fill-opacity="{o}"/>')
    poly([P(1.4, 0.6, 0.01), P(5.4, 0.6, 0.01), P(5.4, 2.6, 0.01), P(1.4, 2.6, 0.01)], '#2E4A1E', 'fill-opacity="0.08"')   # brick ledge footprint
    gshadow(5.3, 3.8, 34, 14); gshadow(6.6, 3.8, 34, 14)   # spell blocks
    tree(6.8, 0.9, 0, 1.0)
    land(9, 16, 0, 4, 0, 1.2)
    # stacked brand slabs on the tier
    box(10.0, 15.0, 0.4, 2.2, 1.2, 1.85, '#F0569A')
    box(10.6, 14.2, 0.4, 2.2, 1.85, 2.5, '#5BB8B4')
    box(11.2, 13.4, 0.5, 2.1, 2.5, 3.15, '#FFC845')
    tree(15.2, 0.8, 1.2, 0.85)
    # flag with the Pixel Spell sparkle
    box(14.6, 14.8, 3.0, 3.2, 1.2, 5.3, '#FFFFFF', '#EEE8DC', '#D9D2C4')
    top = P(14.7, 3.1, 5.35); out.append(f'<circle cx="{top[0]:.1f}" cy="{top[1]:.1f}" r="8" fill="#FFC845"/>')
    a, b, c = P(14.8, 3.1, 5.15), P(16.6, 3.1, 4.75), P(14.8, 3.1, 4.25)
    poly([a, (b[0], b[1]), c], '#F0569A'); sparkle((a[0] + b[0] + c[0]) / 3 - 4, (a[1] + b[1] + c[1]) / 3, 11)
    # fence along the tier's front edge
    fence([(11.2, 4.0), (12.6, 4.0), (14.0, 4.0), (15.4, 4.0)])
    # path from the front-left edge to the tier step
    path = [(2, 7), (3, 7), (3, 6), (4, 6), (5, 6), (5, 5), (6, 5), (7, 5), (8, 5), (8, 4), (9, 4)]
    for (cx, cy) in path:
        poly([P(cx, cy, 0.005), P(cx + 1, cy, 0.005), P(cx + 1, cy + 1, 0.005), P(cx, cy + 1, 0.005)], '#EFD9A0')
    box(9.4, 11.0, 4.0, 5.0, 0, 0.6, '#EFD9A0', '#D9BC7C', '#C4A566')   # step up to the tier
    tree(1.2, 4.2, 0, 0.9)
    # floating spell blocks over the path
    spell_block(4.7, 3.2, 2.3, 0.9, '#FFC845')
    spell_block(6.0, 3.2, 2.3, 0.9, '#5BB8B4')
    # cauldron by the front right
    cx, cy = P(12.2, 6.2, 0)
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy+4:.1f}" rx="44" ry="16" fill="#000000" fill-opacity="0.14"/>')
    out.append(f'<path d="M{cx-40:.1f} {cy-52:.1f} Q{cx-44:.1f} {cy+2:.1f} {cx:.1f} {cy+4:.1f} Q{cx+44:.1f} {cy+2:.1f} {cx+40:.1f} {cy-52:.1f} Z" fill="{grad("#3A3550", "#211E30")}"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy-52:.1f}" rx="42" ry="14" fill="#2B2740"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy-52:.1f}" rx="34" ry="10" fill="#8BE36A"/>')
    for (bx, by, br) in ((-12, -66, 7), (8, -74, 5), (16, -60, 4), (-2, -88, 4)):
        out.append(f'<circle cx="{cx+bx:.1f}" cy="{cy+by:.1f}" r="{br}" fill="#B9F59A"/>')
    # front corner pixel blocks (pink left, yellow front)
    box(13.4, 16, 5.4, 8, -4.4, 0.6, '#FFC845', shade('#FFC845', 0.9), shade('#FFC845', 0.76))
    for (bx0, bx1, by1, col) in ((13.4, 16, 8, '#FFFFFF'),):
        for (a, b) in ((0.08, 0.5), (0.92, 0.5), (0.08, -3.6), (0.92, -3.6)):
            px, py = P(bx0 + (bx1 - bx0) * a, by1, b); out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="{col}" fill-opacity="0.9"/>')
    sparkle(*P(14.7, 6.7, 0.61), 22)

build()
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{"".join(defs)}</defs>{"".join(out)}</svg>'
open('isle.svg', 'w').write(svg)
anchors = {k: P(*v) for k, v in {
    'bird': (3.0, 1.2, 3.6), 'fox': (6.2, 6.0, 0), 'cat': (12.3, 3.3, 1.2), 'wolf': (10.9, 6.6, 0)}.items()}
json.dump(anchors, open('anchors.json', 'w'))
print(len(svg), anchors)
