#!/usr/bin/env python3
"""Parametrik 3D model shabloni (CadQuery). Har yangi model shu fayldan nusxa olib boshlanadi.

Qoidalar:
  * Barcha o'lchamlar PARAMS ichida, mm da, nomi bilan. Kodda "sehrli son" bo'lmasin.
  * build(P) -> cq.Workplane. Faqat geometriya. Hech narsa chop etmaydi.
  * verify(P, shape) gabaritni PARAMS dagi kutilgan qiymat bilan solishtiradi (tol = 0.05 mm).
  * export(): STEP (aniq, CAD uchun) + STL (ko'rish/chop etish) + GLB ixtiyoriy (three.js viewer).

Ishlatish:
  python3 model_template.py                      # PARAMS bilan quradi, tekshiradi, out/ ga yozadi
  python3 model_template.py --set L=800 --set H=500   # parametrlarni buyruq qatoridan o'zgartirish
  python3 model_template.py --json params.json   # scale_from_image.py natijasidan olingan o'lchamlar
"""
import json
import sys
from pathlib import Path

import cadquery as cq

# ---------------------------------------------------------------- PARAMS (mm)
PARAMS = {
    "name": "plate_with_holes",
    "L": 120.0,        # uzunlik (X)
    "W": 80.0,         # kenglik (Y)
    "T": 6.0,          # qalinlik (Z)
    "hole_d": 9.0,     # ISO 273 o'rta: M8 -> 9.0 (data/standard_sizes.json metric_bolt_iso)
    "hole_margin": 12.0,
    "corner_r": 5.0,
    "expect": {"x": 120.0, "y": 80.0, "z": 6.0},   # verify() uchun kutilgan gabarit
}


# ---------------------------------------------------------------- GEOMETRY
def build(P: dict) -> cq.Workplane:
    L, W, T = P["L"], P["W"], P["T"]
    m = P["hole_margin"]
    plate = (
        cq.Workplane("XY")
        .box(L, W, T)                       # markazda
        .edges("|Z").fillet(P["corner_r"])  # vertikal qirralar
        .faces(">Z").workplane()
        .rect(L - 2 * m, W - 2 * m, forConstruction=True)
        .vertices()
        .hole(P["hole_d"])                  # 4 burchakdagi teshiklar
    )
    return plate


# ---------------------------------------------------------------- VERIFY / EXPORT
def bbox(shape: cq.Workplane):
    bb = shape.val().BoundingBox()
    return {"x": round(bb.xlen, 3), "y": round(bb.ylen, 3), "z": round(bb.zlen, 3)}


def verify(P: dict, shape: cq.Workplane, tol: float = 0.05) -> dict:
    got = bbox(shape)
    exp = P.get("expect") or {}
    diff = {k: round(got[k] - exp[k], 3) for k in exp}
    ok = all(abs(v) <= tol for v in diff.values())
    vol = sum(s.Volume() for s in shape.solids().vals())
    return {"bbox": got, "expect": exp, "diff": diff, "volume_mm3": round(vol, 1),
            "solids": len(shape.solids().vals()), "ok": ok}


def export(P: dict, shape: cq.Workplane, out_dir: Path, glb: bool = False) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / P["name"]
    files = []
    cq.exporters.export(shape, str(base.with_suffix(".step")))
    files.append(str(base.with_suffix(".step")))
    cq.exporters.export(shape, str(base.with_suffix(".stl")), tolerance=0.01, angularTolerance=0.1)
    files.append(str(base.with_suffix(".stl")))
    if glb:
        try:
            import trimesh
            trimesh.load(str(base.with_suffix(".stl"))).export(str(base.with_suffix(".glb")))
            files.append(str(base.with_suffix(".glb")))
        except Exception as e:  # trimesh yo'q bo'lsa GLB tashlab ketiladi
            print("GLB export o'tkazib yuborildi:", e, file=sys.stderr)
    (out_dir / f"{P['name']}.params.json").write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
    return files


def apply_cli(P: dict, argv: list[str]) -> dict:
    P = dict(P)
    i = 0
    while i < len(argv):
        if argv[i] == "--set":
            k, v = argv[i + 1].split("=", 1)
            P[k] = type(P.get(k, 0.0))(v) if not isinstance(P.get(k), (dict, str)) else v
            i += 2
        elif argv[i] == "--json":
            P.update(json.load(open(argv[i + 1], encoding="utf-8")))
            i += 2
        else:
            i += 1
    return P


if __name__ == "__main__":
    P = apply_cli(PARAMS, sys.argv[1:])
    shape = build(P)
    rep = verify(P, shape)
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("out")
    rep["files"] = export(P, shape, out, glb="--glb" in sys.argv)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    sys.exit(0 if rep["ok"] else 1)
