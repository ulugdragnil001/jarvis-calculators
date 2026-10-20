#!/usr/bin/env python3
"""Tayyor modelni (STL/OBJ/GLB/STEP) tekshirish: gabarit, hajm, yopiqlik, maqsad o'lchamga moslik.

  verify_model.py model.stl                       # gabarit, hajm, watertight
  verify_model.py model.stl --expect 600x500x100  # maqsad L x W x H (mm), tartib muhim emas
  verify_model.py model.stl --expect 600x500x100 --tol 0.5     # ruxsat etilgan farq, mm (default 0.5)
  verify_model.py model.step                      # STEP: cadquery orqali (aniq B-rep gabarit)

Chiqish: JSON + exit code 0 (OK) / 1 (farq tol dan katta yoki mesh yopiq emas).
"""
import json
import sys
from pathlib import Path


def bbox_step(path):
    import cadquery as cq
    shape = cq.importers.importStep(str(path))
    bb = shape.val().BoundingBox()
    vol = sum(s.Volume() for s in shape.solids().vals())
    return {"extents": [bb.xlen, bb.ylen, bb.zlen], "volume_mm3": vol, "solids": len(shape.solids().vals()), "watertight": True}


def bbox_mesh(path):
    import trimesh
    m = trimesh.load(str(path), force="mesh")
    ext = m.extents.tolist()
    return {"extents": ext, "volume_mm3": float(m.volume) if m.is_watertight else None,
            "watertight": bool(m.is_watertight), "faces": int(len(m.faces)), "euler": int(m.euler_number)}


def main(a):
    if len(a) < 2:
        print(__doc__); return 1
    path = Path(a[1])
    info = bbox_step(path) if path.suffix.lower() in (".step", ".stp") else bbox_mesh(path)
    info["file"] = str(path)
    info["extents"] = [round(v, 3) for v in info["extents"]]
    ok = True
    if "--expect" in a:
        tol = float(a[a.index("--tol") + 1]) if "--tol" in a else 0.5
        exp = sorted(float(v) for v in a[a.index("--expect") + 1].lower().split("x"))
        got = sorted(info["extents"])
        diffs = [round(g - e, 3) for g, e in zip(got, exp)]
        info["expect_sorted"] = exp
        info["diff_mm"] = diffs
        ok = all(abs(d) <= tol for d in diffs)
        info["dims_ok"] = ok
    if info.get("watertight") is False:
        ok = False
    info["ok"] = ok
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
