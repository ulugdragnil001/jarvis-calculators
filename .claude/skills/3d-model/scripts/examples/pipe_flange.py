#!/usr/bin/env python3
"""DN bo'yicha quvur bo'lagi + PN16 flanets (EN 1092-1 tip 11 payvand bo'yinli, soddalashtirilgan).

Bog'liq: data/standard_sizes.json -> steel_pipe_en10220, flange_pn16_en1092, metric_bolt_iso.
  python3 pipe_flange.py --DN 50 --len 300 [--out out/]
"""
import json
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from standard_sizes import find  # noqa: E402


def params(DN=50, length=300.0):
    p = find("steel_pipe_en10220", "DN", DN)
    f = find("flange_pn16_en1092", "DN", DN)
    if not p or not f:
        raise SystemExit(f"DN{DN} jadvalda yo'q")
    return {"name": f"pipe_DN{DN}_PN16_L{int(length)}", "DN": DN, "OD": p["OD"], "wall": p["wall_typical"], "len": float(length),
            "flange_D": f["D"], "flange_K": f["K"], "n": f["n_holes"], "hole_d": f["hole_d"], "flange_t": f["thickness_type11"],
            "expect": {"x": float(f["D"]), "y": float(f["D"]), "z": float(length)}}


def build(P):
    pipe = cq.Workplane("XY").circle(P["OD"] / 2).circle(P["OD"] / 2 - P["wall"]).extrude(P["len"])
    fl = (cq.Workplane("XY").circle(P["flange_D"] / 2).circle(P["OD"] / 2 - P["wall"]).extrude(P["flange_t"])
          .faces(">Z").workplane().polarArray(P["flange_K"] / 2, 0, 360, P["n"]).hole(P["hole_d"]))
    hub = cq.Workplane("XY").circle(P["OD"] / 2 + 6).circle(P["OD"] / 2 - P["wall"]).extrude(P["flange_t"] + 10)
    return pipe.union(fl).union(hub)


if __name__ == "__main__":
    a = sys.argv
    g = lambda k, d: a[a.index(k) + 1] if k in a else d
    P = params(int(g("--DN", 50)), float(g("--len", 300)))
    s = build(P)
    bb = s.val().BoundingBox()
    out = Path(g("--out", "out")); out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(s, str(out / f"{P['name']}.step")); cq.exporters.export(s, str(out / f"{P['name']}.stl"))
    print(json.dumps({"params": P, "bbox": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)]}, ensure_ascii=False, indent=1))
