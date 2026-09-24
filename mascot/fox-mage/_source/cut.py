import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as nd
src, S, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
H, W, _ = im.shape
# background: median of the border
border = np.concatenate([im[:8].reshape(-1,3), im[-8:].reshape(-1,3), im[:, :8].reshape(-1,3), im[:, -8:].reshape(-1,3)])
B = np.median(border, 0)
k = (im @ B) / (B @ B)                      # brightness relative to bg
# background = cream, cream darkened by a cast shadow, or cream lifted toward white (upscaler halo / glow)
ks = np.clip(k, 0, 1)
r1 = np.linalg.norm(im - ks[..., None] * B, axis=2)
d = 255 - B
t = np.clip(((im - B) @ d) / (d @ d), 0, 1)
r2 = np.linalg.norm(im - (B + t[..., None] * d), axis=2)
res = np.minimum(r1, r2)
# object evidence: hue off the cream line, or darker than any cast shadow
a_res = np.clip((res - 5) / 9, 0, 1)
a_k = np.clip((0.80 - k) / 0.08, 0, 1)
alpha = np.maximum(a_res, a_k)
solid = alpha > 0.5
solid = nd.binary_opening(solid, iterations=1)
# fill enclosed holes (white fur highlights read as background) but keep big pure-bg holes
filled = nd.binary_fill_holes(solid)
holes, nh = nd.label(filled & ~solid)
if nh:
    sizes = nd.sum(np.ones_like(k), holes, range(1, nh + 1))
    near_bg = nd.mean((res < 4) & (k > 0.8), holes, range(1, nh + 1))
    keep_open = [i + 1 for i in range(nh) if sizes[i] > 25 * S * S and near_bg[i] > 0.6]
    filled[np.isin(holes, keep_open)] = False
# crystals: pale regions cupped by the brown staff wood stay solid, even where the loop is open
brown = (im[..., 0] - im[..., 2] > 25) & (k < 0.85) & solid
yy, xx = np.mgrid[-5*S:5*S+1, -5*S:5*S+1]; disk = xx**2 + yy**2 <= (5*S)**2
closed = nd.binary_closing(np.pad(solid, 6*S), structure=disk)[6*S:-6*S, 6*S:-6*S]
cand, nc = nd.label(nd.binary_fill_holes(closed) & ~filled)
for i, sl in enumerate(nd.find_objects(cand), 1):
    if sl is None: continue
    sl = tuple(slice(max(s.start - 3*S, 0), s.stop + 3*S) for s in sl)
    c = cand[sl] == i
    if c.sum() < 8 * S * S: continue
    ring = nd.binary_dilation(c, iterations=2*S) & ~c & solid[sl]
    if ring.sum() and brown[sl][ring].mean() > 0.5:
        filled[sl] |= c
alpha = np.where(filled, np.maximum(alpha, (filled & ~nd.binary_erosion(filled, iterations=S)) * alpha), 0)
alpha = np.where(nd.binary_erosion(filled, iterations=max(1, S)), 1.0, alpha)
# crystal glow: inside each staff-top loop (open C-shapes, marked by hand in 1x coords),
# the white light becomes a soft white glow bounded by the convex hull of the wood
from scipy.spatial import ConvexHull
from PIL import ImageDraw
for (x0, y0, x1, y1) in json.load(open('glowboxes.json')):
    X0, Y0, X1, Y1 = x0*S, y0*S, x1*S, y1*S
    ys, xs = np.where(brown[Y0:Y1, X0:X1])
    pts = np.c_[xs, ys]; hv = pts[ConvexHull(pts).vertices]
    hm = Image.new('L', (X1-X0, Y1-Y0)); ImageDraw.Draw(hm).polygon([tuple(p) for p in hv], fill=1)
    loop = np.zeros_like(filled); loop[Y0:Y1, X0:X1] = np.asarray(hm, bool)
    loop &= ~brown
    alpha[loop] = 1.0
    filled |= loop
    glowpx = loop & (res < 6)
    im[glowpx] = im[glowpx] + (255 - im[glowpx]) * 0.7   # cream light inside the loop -> near-white glow
# feather: 1px soft rim scaled
alpha = np.clip(alpha, 0, 1)
# un-premultiply the cream out of the edge pixels
a3 = np.clip(alpha, 1e-3, 1)[..., None]
fg = np.clip((im - (1 - a3) * B) / a3, 0, 255)
fg = np.where(alpha[..., None] > 0.98, im, fg)

boxes = json.load(open('boxes.json'))
lab, n = nd.label(filled | (alpha > 0.3))
objs = nd.find_objects(lab)
com = nd.center_of_mass(np.ones_like(k), lab, range(1, n + 1))
area = nd.sum(np.ones_like(k), lab, range(1, n + 1))
meta = {}
for name, (x0, y0, x1, y1) in boxes.items():
    ids = [i + 1 for i in range(n) if area[i] >= 6 * S * S and x0 * S <= com[i][1] < x1 * S and y0 * S <= com[i][0] < y1 * S]
    m = np.isin(lab, ids)
    ys, xs = np.where(m)
    pad = 2 * S
    Y0, Y1, X0, X1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, H), max(xs.min() - pad, 0), min(xs.max() + pad + 1, W)
    a = (alpha * m)[Y0:Y1, X0:X1]
    rgba = np.dstack([fg[Y0:Y1, X0:X1], a * 255]).round().astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(f'{outdir}/{name}.png', optimize=True)
    meta[name] = dict(x=int(X0), y=int(Y0), w=int(X1 - X0), h=int(Y1 - Y0), parts=len(ids))
json.dump(meta, open(f'{outdir}/meta.json', 'w'), indent=1)
print(json.dumps(meta))
