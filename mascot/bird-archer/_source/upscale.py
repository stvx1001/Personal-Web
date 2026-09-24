import ncnn, numpy as np, sys, time
from PIL import Image
src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
net = ncnn.Net(); net.opt.use_vulkan_compute = False; net.opt.num_threads = 4
net.load_param(f'esr/models/{model}.param'); net.load_model(f'esr/models/{model}.bin')
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)/255.
H, W, _ = img.shape; S = 4; T = 192; P = 12
out = np.zeros((H*S, W*S, 3), np.float32)
t0 = time.time()
for y in range(0, H, T):
  for x in range(0, W, T):
    y0, x0 = max(y-P,0), max(x-P,0); y1, x1 = min(y+T+P,H), min(x+T+P,W)
    tile = np.ascontiguousarray(img[y0:y1, x0:x1].transpose(2,0,1))
    ex = net.create_extractor(); ex.input('data', ncnn.Mat(tile))
    _, o = ex.extract('output'); o = np.array(o).transpose(1,2,0)
    ty, tx = (y-y0)*S, (x-x0)*S; h, w = min(T,H-y)*S, min(T,W-x)*S
    out[y*S:y*S+h, x*S:x*S+w] = o[ty:ty+h, tx:tx+w]
Image.fromarray((np.clip(out,0,1)*255+.5).astype(np.uint8)).save(dst)
print('done', out.shape, round(time.time()-t0,1), 's')
