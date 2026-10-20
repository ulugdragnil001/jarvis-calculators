#!/usr/bin/env python3
"""Piksel -> mm. Rasmdagi ma'lum o'lchamli narsa (etalon) orqali masshtab topish.

Ikki rejim:
 1) Chiziqli masshtab (kamera ob'ektga perpendikulyar, tekis ko'rinish):
      scale_from_image.py linear --ref x0,y0 x1,y1 --ref-mm 297 --measure x0,y0 x1,y1 [--measure ...]
 2) Gomografiya (perspektiva bor, etalon to'rtburchak — A4, plitka, karta):
      scale_from_image.py homography --quad x1,y1 x2,y2 x3,y3 x4,y4 --quad-mm 210 297 \
          --points x,y[,label] ... [--measure x0,y0 x1,y1 ...]
    quad nuqtalari tartibi: yuqori-chap, yuqori-o'ng, pastki-o'ng, pastki-chap (soat yo'nalishida).
    Natija: har nuqta etalon tekisligidagi mm koordinatasi; --measure juftlar orasidagi mm masofa.

 3) JSON rejim (ko'p o'lchamni bir yo'la):  scale_from_image.py json spec.json
    spec = {"mode":"linear","ref":[[x0,y0],[x1,y1]],"ref_mm":297,
            "measure":{"width":[[..],[..]],"height":[[..],[..]]}}

Natijalar JSON ko'rinishda chiqadi — keyingi bosqich (model_template.py PARAMS) ga to'g'ridan-to'g'ri kiritish uchun.
Eslatma: etalon va o'lchanayotgan narsa BIR tekislikda bo'lsa aniqlik ±1-2 %. Chuqurlik bo'yicha farq bo'lsa xato oshadi.
"""
import json
import math
import sys

import numpy as np


def _pt(s):
    x, y = s.split(",")[:2]
    return float(x), float(y)


def linear_scale(ref_a, ref_b, ref_mm):
    px = math.dist(ref_a, ref_b)
    if px == 0:
        raise ValueError("etalon nuqtalari bir xil")
    return ref_mm / px  # mm per px


def homography(src_pts, dst_pts):
    """4 ta (x,y) -> 4 ta (X,Y) uchun 3x3 H matritsasi (DLT)."""
    A = []
    for (x, y), (X, Y) in zip(src_pts, dst_pts):
        A.append([-x, -y, -1, 0, 0, 0, x * X, y * X, X])
        A.append([0, 0, 0, -x, -y, -1, x * Y, y * Y, Y])
    A = np.asarray(A, dtype=float)
    _, _, vt = np.linalg.svd(A)
    H = vt[-1].reshape(3, 3)
    return H / H[2, 2]


def apply_h(H, p):
    v = H @ np.array([p[0], p[1], 1.0])
    return (v[0] / v[2], v[1] / v[2])


def run_linear(ref, ref_mm, measures, labels=None):
    k = linear_scale(ref[0], ref[1], ref_mm)
    out = {"mode": "linear", "mm_per_px": round(k, 5), "px_per_mm": round(1 / k, 4), "measures": {}}
    for i, (a, b) in enumerate(measures):
        name = labels[i] if labels and i < len(labels) else f"m{i+1}"
        px = math.dist(a, b)
        out["measures"][name] = {"px": round(px, 1), "mm": round(px * k, 2)}
    return out


def run_homography(quad, quad_mm, points, measures, labels=None):
    W, Hm = quad_mm
    dst = [(0, 0), (W, 0), (W, Hm), (0, Hm)]
    H = homography(quad, dst)
    out = {"mode": "homography", "quad_mm": [W, Hm], "points": {}, "measures": {}}
    for p in points:
        X, Y = apply_h(H, (p[0], p[1]))
        out["points"][p[2] if len(p) > 2 else f"{int(p[0])},{int(p[1])}"] = {"X_mm": round(X, 2), "Y_mm": round(Y, 2)}
    for i, (a, b) in enumerate(measures):
        name = labels[i] if labels and i < len(labels) else f"m{i+1}"
        A, B = apply_h(H, a), apply_h(H, b)
        out["measures"][name] = {"mm": round(math.dist(A, B), 2), "dx_mm": round(B[0] - A[0], 2), "dy_mm": round(B[1] - A[1], 2)}
    # o'z-o'zini tekshirish: etalon burchaklari qaytarilganda mm ga tushishi kerak
    back = [apply_h(H, q) for q in quad]
    out["self_check_mm"] = [[round(x, 2), round(y, 2)] for x, y in back]
    return out


def main(a):
    if len(a) < 2:
        print(__doc__)
        return 1
    mode = a[1]
    if mode == "json":
        spec = json.load(open(a[2], encoding="utf-8"))
        if spec["mode"] == "linear":
            names = list(spec["measure"].keys())
            res = run_linear([tuple(p) for p in spec["ref"]], spec["ref_mm"], [tuple(map(tuple, v)) for v in spec["measure"].values()], names)
        else:
            names = list(spec.get("measure", {}).keys())
            res = run_homography([tuple(p) for p in spec["quad"]], spec["quad_mm"], spec.get("points", []),
                                 [tuple(map(tuple, v)) for v in spec.get("measure", {}).values()], names)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0

    def grab(flag, n=None):
        if flag not in a:
            return []
        i = a.index(flag) + 1
        vals = []
        while i < len(a) and not a[i].startswith("--"):
            vals.append(a[i]); i += 1
        return vals

    measures_raw = []
    i = 0
    while i < len(a):
        if a[i] == "--measure":
            measures_raw.append((_pt(a[i + 1]), _pt(a[i + 2]))); i += 3
        else:
            i += 1
    if mode == "linear":
        ref = [_pt(s) for s in grab("--ref")]
        ref_mm = float(grab("--ref-mm")[0])
        res = run_linear(ref, ref_mm, measures_raw)
    elif mode == "homography":
        quad = [_pt(s) for s in grab("--quad")]
        qmm = [float(v) for v in grab("--quad-mm")]
        pts = []
        for s in grab("--points"):
            parts = s.split(",")
            pts.append((float(parts[0]), float(parts[1]), parts[2]) if len(parts) > 2 else (float(parts[0]), float(parts[1])))
        res = run_homography(quad, qmm, pts, measures_raw)
    else:
        print(__doc__)
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
