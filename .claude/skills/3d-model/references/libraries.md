# 3D model yasovchi eng yaxshi kutubxonalar — nima uchun, qachon, qanday

Tanlov qoidasi (SKILL.md 3-bosqich): **aniq o'lcham kerak -> B-rep (CadQuery/build123d)**;
**oddiy CSG va tez skript -> OpenSCAD**; **mesh tahrir/tekshirish -> trimesh + manifold3d**;
**brauzerda ko'rsatish -> three.js**; **faqat rasm bor, o'lcham yo'q, "ko'rinishi o'xshasin" -> AI image-to-3D (TRELLIS.2 / Hunyuan3D)**;
**organik/vizual render -> Blender bpy**. Ushbu muhitda CadQuery 2.8, trimesh 5.1, manifold3d 3.5, numpy, Pillow o'rnatilgan (OpenSCAD/Blender yo'q).

| Kutubxona | Yadro | Kuchli tomoni | Zaif tomoni | Chiqish |
|---|---|---|---|---|
| **CadQuery** (`pip install cadquery`) | OpenCascade (OCP) | Parametrik, selektorlar (`faces(">Z")`), fillet/chamfer, STEP aniq, BoundingBox tekshiruv | O'rnatish og'ir (~200 MB), murakkab yuzalar qiyin | STEP, STL, 3MF, DXF, SVG |
| **build123d** (`pip install build123d`) | OpenCascade | CadQuery'ning yangi avlodi: builder + algebra API, joint/assembly, sheet-metal, `Location` tizimi | Yoshroq ekotizim | STEP, STL, 3MF, GLTF |
| **OpenSCAD** (`openscad` CLI, `solidpython2`) | CGAL/Manifold CSG | Eng sodda til, LLM uchun xato kam, kutubxonalar (BOSL2, MCAD), `$fn` | Fillet qiyin, STEP yo'q, faqat mesh | STL, 3MF, AMF, DXF |
| **trimesh** (`pip install trimesh`) | numpy | STL/OBJ/GLB o'qish-yozish, bbox, hajm, watertight, boolean (manifold3d orqali), repair | B-rep emas, aniq fillet yo'q | STL, OBJ, GLB, PLY, 3MF |
| **manifold3d** | Manifold | Tez va kafolatli-manifold boolean | Faqat mesh | mesh |
| **three.js** (CDN) | WebGL | Brauzerda STL/GLB ko'rsatish, repo HTML uslubiga mos (`scripts/viewer_template.html`) | Modellashtirish uchun emas | ekran |
| **Blender bpy** | Blender | Render, modifier, organik shakl, animatsiya | O'lcham aniqligi uchun noqulay, og'ir | hammasi |
| **FreeCAD** (Part/PartDesign, `freecadcmd`) | OpenCascade | GUI + Python, TechDraw chizma, assembly | Skriptlash CadQuery'dan noqulay | STEP, IGES, STL |
| **pythonOCC / OCP** | OpenCascade | Eng past daraja, hamma narsa mumkin | Ko'p kod | STEP |
| **Open3D / PyVista** | — | Nuqta buluti, skanerdan mesh, vizual tahlil | Modellashtirish emas | PLY, mesh |
| **COLMAP / Meshroom** | fotogrammetriya | 20+ fotodan haqiqiy mesh (masshtabsiz) | GPU, ko'p rasm, masshtabni etalon bilan berish kerak | OBJ/PLY |
| **TRELLIS.2** (Microsoft, MIT) | diffuziya | Bitta rasmdan eng sifatli ochiq model, PBR | 16+ GB VRAM | GLB |
| **Hunyuan3D 2.x** (Tencent) | diffuziya | Yengilroq, tekstura alohida bosqich | Litsenziya cheklovlari (EU/UK/KR) | GLB |
| **TripoSR / Stable Fast 3D** | feed-forward | Tez (soniyalar), CPU da ham | Sifat past, o'lcham yo'q | GLB |

## Eng yaxshilardan "nusxa olingan" dizayn qoidalari (skillga singdirilgan)

1. **CadQuery/build123d: hamma narsa parametr.** `PARAMS` lug'ati, `build(P)` funksiyasi, `verify()` — `scripts/model_template.py`.
2. **CadQuery selektorlari** ("`>Z`", "`|Z`", "`%CIRCLE`") bilan qirra/yuza tanlash — indeks bilan emas (indeks tessellyatsiyada o'zgaradi).
3. **OpenSCAD odatlari:** `$fn=64..128` aylanalar uchun, `module` + nomli parametr, `difference(){ ... }` da kesuvchi jismni ±0.01 (epsilon) uzaytirish (z-fighting oldini olish).
4. **build123d:** `Location`/`Pos`/`Rot` bilan joylashtirish, `BuildPart` kontekst menejeri, `Mode.SUBTRACT`.
5. **trimesh:** export oldidan `is_watertight`, `fix_normals()`, `merge_vertices()`; GLB ga chiqarish uchun `mesh.export("x.glb")`.
6. **three.js:** `camera.up = (0,0,1)` (CAD Z-up), `Box3.setFromObject` bilan gabaritni ekranda ko'rsatish — o'lcham tekshiruvi vizual ham bo'ladi.
7. **AI image-to-3D natijasi hech qachon yakuniy emas:** uni faqat *shakl ma'lumotnomasi* sifatida ishlating, keyin o'lchamlarni B-rep da qayta quring (AI mesh masshtabsiz va nosimmetrik bo'ladi).
8. **Fotogrammetriya:** sahnaga etalon (A4, chizg'ich, ArUco) qo'ying; mesh chiqqach `trimesh` da etalon bo'yicha `apply_scale`.

## Minimal kod yodnomalari

```python
# CadQuery — qarang references/cadquery-patterns.md (sinovdan o'tgan)
import cadquery as cq
r = cq.Workplane("XY").box(100, 50, 20).faces(">Z").workplane().hole(10).edges("|Z").fillet(3)
cq.exporters.export(r, "r.step"); cq.exporters.export(r, "r.stl")
bb = r.val().BoundingBox(); print(bb.xlen, bb.ylen, bb.zlen)

# build123d (o'rnatilgan bo'lsa)
from build123d import *
with BuildPart() as p:
    Box(100, 50, 20)
    with Locations((0, 0, 10)): Hole(5)
    fillet(p.edges().filter_by(Axis.Z), 3)
export_step(p.part, "p.step")

# trimesh tekshiruv
import trimesh; m = trimesh.load("r.stl"); print(m.extents, m.is_watertight, m.volume)

# OpenSCAD (CLI: openscad -o out.stl model.scad)
# module plate(L=100,W=50,T=20,d=10){ difference(){ cube([L,W,T],center=true); cylinder(h=T+0.02,d=d,center=true,$fn=96); } }
```

Manbalar: CadQuery docs (cadquery.readthedocs.io), build123d docs (build123d.readthedocs.io), OpenSCAD cheatsheet (openscad.org/cheatsheet), trimesh docs (trimesh.org), three.js docs (threejs.org/docs), TRELLIS (github.com/microsoft/TRELLIS), Hunyuan3D (github.com/Tencent/Hunyuan3D-2).
