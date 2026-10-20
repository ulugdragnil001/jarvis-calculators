#!/usr/bin/env python3
"""Rasmdan o'lcham olishga yordam beruvchi vositalar (Pillow + numpy, OpenCV shart emas).

Claude rasmni ko'rganda piksel koordinatalarini "ko'z bilan" aniq aytolmaydi.
Shu skript rasm ustiga koordinatali setka chizadi, kerakli joyni kattalashtiradi,
konturlarni ajratadi — natijaviy rasmni qayta ko'rib aniq pikselni o'qish mumkin.

  measure_image.py info  in.jpg
  measure_image.py grid  in.jpg out.png [--step 50]            # har 50 px da chiziq + koordinata yozuvi
  measure_image.py crop  in.jpg out.png x0 y0 x1 y1 [--zoom 3] # kesib kattalashtirish (setka bilan)
  measure_image.py edges in.jpg out.png                        # kontur (FIND_EDGES) + setka
  measure_image.py mark  in.jpg out.png x,y[,label] ...        # nuqtalarni belgilab tekshirish
  measure_image.py profile in.jpg x0 y0 x1 y1                  # chiziq bo'ylab yorqinlik — chekka qayerda o'zgaradi
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _font(size=12):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_grid(im: Image.Image, step: int = 50, origin=(0, 0), scale: float = 1.0) -> Image.Image:
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size
    f = _font(11)
    ox, oy = origin
    x = 0
    while x < w:
        src_x = int(ox + x / scale)
        major = (src_x % (step * 2)) == 0
        d.line([(x, 0), (x, h)], fill=(255, 0, 0) if major else (255, 140, 0), width=1)
        d.text((x + 2, 2), str(src_x), fill=(255, 255, 0), font=f)
        x += int(step * scale)
    y = 0
    while y < h:
        src_y = int(oy + y / scale)
        major = (src_y % (step * 2)) == 0
        d.line([(0, y), (w, y)], fill=(255, 0, 0) if major else (255, 140, 0), width=1)
        d.text((2, y + 2), str(src_y), fill=(0, 255, 255), font=f)
        y += int(step * scale)
    return im


def cmd_info(src):
    im = Image.open(src)
    print(f"size={im.size[0]}x{im.size[1]} mode={im.mode} format={im.format}")
    exif = getattr(im, "getexif", lambda: {})()
    if exif:
        for k in (271, 272, 37386, 41486, 41487):  # Make, Model, FocalLength, FocalPlaneXRes, YRes
            if k in exif:
                print(f"exif[{k}]={exif[k]}")


def cmd_grid(src, dst, step):
    im = Image.open(src)
    draw_grid(im, step).save(dst)
    print(f"ok {dst} size={im.size} step={step}")


def cmd_crop(src, dst, x0, y0, x1, y1, zoom):
    im = Image.open(src).convert("RGB")
    box = (int(x0), int(y0), int(x1), int(y1))
    c = im.crop(box)
    c = c.resize((int(c.width * zoom), int(c.height * zoom)), Image.LANCZOS)
    step = 10 if zoom >= 3 else 20
    draw_grid(c, step, origin=(box[0], box[1]), scale=zoom).save(dst)
    print(f"ok {dst} crop={box} zoom={zoom} (setka yozuvlari ASL rasm pikselida)")


def cmd_edges(src, dst):
    im = Image.open(src).convert("L").filter(ImageFilter.GaussianBlur(1)).filter(ImageFilter.FIND_EDGES)
    im = im.point(lambda p: 255 if p > 25 else 0).convert("RGB")
    draw_grid(im, 50).save(dst)
    print(f"ok {dst}")


def cmd_mark(src, dst, pts):
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    f = _font(13)
    for p in pts:
        parts = p.split(",")
        x, y = float(parts[0]), float(parts[1])
        label = parts[2] if len(parts) > 2 else f"{int(x)},{int(y)}"
        d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=(255, 0, 0), width=2)
        d.line([(x - 10, y), (x + 10, y)], fill=(255, 0, 0))
        d.line([(x, y - 10), (x, y + 10)], fill=(255, 0, 0))
        d.text((x + 6, y + 6), label, fill=(255, 255, 0), font=f)
    im.save(dst)
    print(f"ok {dst} {len(pts)} nuqta")


def cmd_profile(src, x0, y0, x1, y1):
    import numpy as np
    im = np.asarray(Image.open(src).convert("L"), dtype=float)
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    xs = np.linspace(x0, x1, n)
    ys = np.linspace(y0, y1, n)
    vals = im[np.clip(ys.astype(int), 0, im.shape[0] - 1), np.clip(xs.astype(int), 0, im.shape[1] - 1)]
    grad = np.abs(np.diff(vals))
    idx = [i for i in np.argsort(grad)[-6:][::-1] if grad[i] > 0]
    print("Kuchli chekkalar (piksel, |delta|):")
    for i in sorted(idx):
        print(f"  x={xs[i]:.0f} y={ys[i]:.0f}  delta={grad[i]:.0f}")


def main(a):
    if len(a) < 3:
        print(__doc__)
        return 1
    cmd, src = a[1], a[2]
    if cmd == "info":
        cmd_info(src)
    elif cmd == "grid":
        step = int(a[a.index("--step") + 1]) if "--step" in a else 50
        cmd_grid(src, a[3], step)
    elif cmd == "crop":
        zoom = float(a[a.index("--zoom") + 1]) if "--zoom" in a else 3.0
        cmd_crop(src, a[3], *map(float, a[4:8]), zoom)
    elif cmd == "edges":
        cmd_edges(src, a[3])
    elif cmd == "mark":
        cmd_mark(src, a[3], a[4:])
    elif cmd == "profile":
        cmd_profile(src, *map(float, a[3:7]))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
