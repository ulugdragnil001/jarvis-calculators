#!/usr/bin/env python3
"""Gidrostrelka (gidravlik ajratgich) — gidrostrelka.html formulasi + '3D qoidasi' dan 3D model.

gidrostrelka.html:  G = 0.86*Q/dT [m3/h];  D = sqrt(4*(G/3600)/(pi*V)) [m]
Bu yerda shu formula takrorlanadi, so'ng D standart quvurga (EN 10220) yuqoriga yaxlitlanadi.
  python3 gidrostrelka.py --Q 50 --t_pod 80 --t_obr 60 [--V_strelka 0.1 --V_potrub 0.9] [--out out/]
"""
import json
import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from standard_sizes import nearest  # noqa: E402


def diameter_mm(G_m3h, V):
    return math.sqrt(4 * (G_m3h / 3600) / (math.pi * V)) * 1000


def params(Q_kw=50, t_pod=80, t_obr=60, V_strelka=0.1, V_potrub=0.9):
    dT = t_pod - t_obr
    G = 0.86 * Q_kw / dT
    D_calc = diameter_mm(G, V_strelka)
    d_calc = diameter_mm(G, V_potrub)
    D_std = nearest("steel_pipe_en10220", "OD", D_calc, prefer="up")
    d_std = nearest("steel_pipe_en10220", "OD", d_calc, prefer="up")
    D = D_std["OD"]; d = d_std["OD"]
    return {"name": f"gidrostrelka_Q{Q_kw}_DN{D_std['DN']}", "Q_kw": Q_kw, "dT": dT, "G_m3h": round(G, 3),
            "D_calc": round(D_calc, 1), "D": D, "D_wall": D_std["wall_typical"], "DN": D_std["DN"],
            "d_calc": round(d_calc, 1), "d": d, "d_wall": d_std["wall_typical"], "dn": d_std["DN"],
            "nozzle_spacing": 3 * D, "end_margin": 1.5 * D, "nozzle_len": 1.5 * d}


def build(P):
    D, d = P["D"], P["d"]
    H = 2 * P["end_margin"] + 3 * P["nozzle_spacing"]   # 4 ta patrubka: 2 chapda, 2 o'ngda
    P["H"] = H
    body = cq.Workplane("XY").circle(D / 2).extrude(H)
    cap = cq.Workplane("XY").circle(D / 2).workplane(offset=-0.15 * D).circle(D / 4).loft()
    body = body.union(cap.translate((0, 0, 0))).union(cap.mirror("XY").translate((0, 0, H)))
    z0 = P["end_margin"]
    zs = [z0 + i * P["nozzle_spacing"] for i in range(4)]
    ln = P["nozzle_len"]
    for i, z in enumerate(zs):
        side = -1 if i % 2 == 0 else 1   # chap: kirish/qaytish (qozon), o'ng: tizim
        noz = cq.Workplane("YZ").circle(d / 2).extrude(D / 2 + ln).translate((0, 0, z))
        if side < 0:
            noz = noz.mirror("YZ")
        body = body.union(noz)
    inner = cq.Workplane("XY").circle(D / 2 - P["D_wall"]).extrude(H - 2 * P["D_wall"]).translate((0, 0, P["D_wall"]))
    body = body.cut(inner)
    for i, z in enumerate(zs):
        side = -1 if i % 2 == 0 else 1
        bore = cq.Workplane("YZ").circle(d / 2 - P["d_wall"]).extrude(D / 2 + ln + 1).translate((0, 0, z))
        if side < 0:
            bore = bore.mirror("YZ")
        body = body.cut(bore)
    return body


if __name__ == "__main__":
    a = sys.argv
    g = lambda k, dflt: float(a[a.index(k) + 1]) if k in a else dflt
    P = params(g("--Q", 50), g("--t_pod", 80), g("--t_obr", 60), g("--V_strelka", 0.1), g("--V_potrub", 0.9))
    s = build(P)
    bb = s.val().BoundingBox()
    out = Path(a[a.index("--out") + 1]) if "--out" in a else Path("out"); out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(s, str(out / f"{P['name']}.step")); cq.exporters.export(s, str(out / f"{P['name']}.stl"))
    print(json.dumps({"params": P, "bbox": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]}, ensure_ascii=False, indent=1))
