#!/usr/bin/env python3
"""Panelli radiator (EN 442 tip 11/21/22/33) — standart o'lchamlardan parametrik model.

Bog'liq: radiator.html (PANELS jadvali: tip, balandlik, uzunlik -> quvvat),
         data/standard_sizes.json -> panel_radiator (chuqurlik, ulanish G1/2, 50 mm qadam).

  python3 radiator_panel.py --type 22 --H 500 --L 1000 [--out out/]
"""
import json
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from standard_sizes import find, load  # noqa: E402

G12_OD = 20.955       # G1/2 tashqi diametr (thread_g_bsp)
PLATE_T = 1.2         # panel list qalinligi (EN 442 ~1.2 mm)
PANEL_T = 12.0        # bitta suv paneli qalinligi (ikki list + kanal)
CONV_T = 25.0         # konvektor qanot paketi balandligi (chuqurlikda)


def params(rtype="22", H=500, L=1000):
    t = find("panel_radiator", "type", rtype)
    if not t:
        raise SystemExit(f"Noma'lum tip {rtype}")
    db = load()["panel_radiator"]
    if H not in db["heights"]:
        print(f"Ogohlantirish: H={H} standart emas {db['heights']}", file=sys.stderr)
    return {"name": f"radiator_t{rtype}_H{H}_L{L}", "type": rtype, "H": float(H), "L": float(L),
            "D": float(t["depth"]), "panels": int(t["panels"]), "convectors": int(t["convectors"]),
            "conn_d": G12_OD, "conn_spacing": float(H) - 50.0, "expect": {"x": float(L), "y": float(t["depth"]), "z": float(H)}}


def build(P):
    L, H, D = P["L"], P["H"], P["D"]
    n, c = P["panels"], P["convectors"]
    # Chuqurlik bo'ylab stek: panel, konvektor, panel, konvektor ... (jami aniq D ga teng)
    conv_t = (D - n * PANEL_T) / c if c else 0.0
    gap = (D - n * PANEL_T) / (n - 1) if (c == 0 and n > 1) else 0.0
    body, y = None, 0.0
    for i in range(n):
        panel = cq.Workplane("XY").box(L, PANEL_T, H, centered=(True, False, False)).translate((0, y, 0))
        body = panel if body is None else body.union(panel)
        y += PANEL_T
        if i < c:
            conv = cq.Workplane("XY").box(L - 60, conv_t, H - 60, centered=(True, False, False)).translate((0, y, 30))
            body = body.union(conv)
            y += conv_t
        elif gap:
            y += gap
    # orqa/old panellarni yuqori-pastki to'siq bilan bog'lash (haqiqiy radiatorda yon qopqoq va grill)
    if n > 1:
        top = cq.Workplane("XY").box(L, D, 2, centered=(True, False, False)).translate((0, 0, H - 2))
        side = cq.Workplane("XY").box(2, D, H, centered=(True, False, False))
        body = body.union(top).union(side.translate((-L / 2 + 1, 0, 0))).union(side.translate((L / 2 - 1, 0, 0)))
    # G1/2 ulanish: ikki yon tomonda, yuqori/pastki (markazlararo = H-50)
    s = P["conn_spacing"]
    for z in (H / 2 - s / 2, H / 2 + s / 2):
        for x in (-L / 2, L / 2):
            boss = cq.Workplane("YZ").circle(P["conn_d"] / 2 + 2).extrude(12).translate((x - (12 if x > 0 else 0), D / 2, z))
            body = body.union(boss)
            hole = cq.Workplane("YZ").circle(P["conn_d"] / 2).extrude(14).translate((x - (12 if x > 0 else 0) - 1, D / 2, z))
            body = body.cut(hole)
    return body


if __name__ == "__main__":
    a = sys.argv
    g = lambda k, d: a[a.index(k) + 1] if k in a else d
    P = params(g("--type", "22"), int(g("--H", 500)), int(g("--L", 1000)))
    shape = build(P)
    bb = shape.val().BoundingBox()
    out = Path(g("--out", "out")); out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(out / f"{P['name']}.step"))
    cq.exporters.export(shape, str(out / f"{P['name']}.stl"))
    rep = {"params": P, "bbox": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)]}
    rep["note"] = "Gabarit L x D x H standart jadvalga teng bo'lishi kerak (ulanish bosslari korpus ichida)."
    print(json.dumps(rep, ensure_ascii=False, indent=1))
