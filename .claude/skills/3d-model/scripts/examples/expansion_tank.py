#!/usr/bin/env python3
"""Membranali kengaytiruvchi bak — hajmdan standart gabarit (data: expansion_tank_membrane).

Bog'liq: kengaytiruvchi_bak.html (STANDARD_SIZES, hisoblangan hajm -> katalog hajmi).
  python3 expansion_tank.py --V 24 [--out out/]
"""
import json
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from standard_sizes import find, nearest  # noqa: E402


def params(V=24):
    r = find("expansion_tank_membrane", "volume_l", V) or nearest("expansion_tank_membrane", "volume_l", V, prefer="up")
    th = find("thread_g_bsp", "size", r["connection"])
    return {"name": f"exp_tank_{int(r['volume_l'])}L", "V": r["volume_l"], "D": float(r["diameter"]), "H": float(r["height"]),
            "conn": r["connection"], "conn_d": th["major_d"], "wall": 1.5, "legs": 3, "leg_h": 20.0,
            "expect": {"x": float(r["diameter"]), "y": float(r["diameter"]), "z": float(r["height"])}}


def build(P):
    D, H = P["D"], P["H"]
    dome = D * 0.18
    cyl_h = H - 2 * dome - P["leg_h"]
    body = cq.Workplane("XY").circle(D / 2).extrude(cyl_h).translate((0, 0, P["leg_h"] + dome))
    # ellipsoid qopqoqlar: sfera bo'lagini masshtablash o'rniga loft (D/2 -> 0.25 D)
    top = (cq.Workplane("XY").workplane(offset=P["leg_h"] + dome + cyl_h).circle(D / 2)
           .workplane(offset=dome * 0.7).circle(D * 0.35).workplane(offset=dome * 0.3).circle(D * 0.08).loft(ruled=False))
    bot = (cq.Workplane("XY").workplane(offset=P["leg_h"] + dome).circle(D / 2)
           .workplane(offset=-dome * 0.7).circle(D * 0.35).workplane(offset=-dome * 0.3).circle(D * 0.08).loft(ruled=False))
    body = body.union(top).union(bot)
    neck = cq.Workplane("XY").circle(P["conn_d"] / 2 + 3).extrude(P["leg_h"] + 2).cut(
        cq.Workplane("XY").circle(P["conn_d"] / 2).extrude(P["leg_h"] + 2))
    body = body.union(neck)
    valve = cq.Workplane("XY").workplane(offset=H - 6).circle(5).extrude(6)
    body = body.union(valve)
    return body


if __name__ == "__main__":
    a = sys.argv
    V = float(a[a.index("--V") + 1]) if "--V" in a else 24
    P = params(V)
    s = build(P)
    bb = s.val().BoundingBox()
    out = Path(a[a.index("--out") + 1]) if "--out" in a else Path("out"); out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(s, str(out / f"{P['name']}.step")); cq.exporters.export(s, str(out / f"{P['name']}.stl"))
    print(json.dumps({"params": P, "bbox": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]}, ensure_ascii=False, indent=1))
