# CadQuery naqshlari (shu muhitda CadQuery 2.8 bilan sinovdan o'tgan)

Barcha o'lchamlar mm. `cq.Workplane("XY")` — Z yuqoriga. `box()` default markazda; `centered=(True, False, False)` bilan Y va Z ni 0 dan boshlash.

## Asosiy jismlar
```python
import cadquery as cq
box  = cq.Workplane("XY").box(L, W, H)                       # markazda
box0 = cq.Workplane("XY").box(L, W, H, centered=(True, False, False))  # Y,Z 0 dan
cyl  = cq.Workplane("XY").circle(D/2).extrude(H)             # Z bo'ylab
tube = cq.Workplane("XY").circle(OD/2).circle(OD/2 - t).extrude(L)   # ichi bo'sh quvur
side = cq.Workplane("YZ").circle(d/2).extrude(L)             # X bo'ylab (YZ tekislikdan)
sph  = cq.Workplane("XY").sphere(R)
```

## Teshik, naqsh, rezba o'rni
```python
r = (cq.Workplane("XY").box(120, 80, 6)
     .faces(">Z").workplane()
     .rect(96, 56, forConstruction=True).vertices().hole(9.0))     # 4 burchak teshigi (M8 -> 9.0)
fl = (cq.Workplane("XY").circle(165/2).circle(60.3/2 - 3.6).extrude(20)
      .faces(">Z").workplane().polarArray(125/2, 0, 360, 4).hole(18))  # PN16 DN50 flanets
cb = cq.Workplane("XY").box(60, 60, 10).faces(">Z").workplane().cboreHole(6.6, 11, 6.5)   # M6 cbore
cs = cq.Workplane("XY").box(60, 60, 10).faces(">Z").workplane().cskHole(5.5, 11, 90)     # M5 csk
```

## Fillet / chamfer / shell
```python
r = r.edges("|Z").fillet(5)         # faqat vertikal qirralar
r = r.faces(">Z").edges().chamfer(1)
cup = cq.Workplane("XY").circle(40).extrude(60).faces(">Z").shell(-1.5)   # 1.5 mm devor, ustki ochiq
```

## Revolve, loft, sweep
```python
vase = cq.Workplane("XZ").polyline([(0,0),(30,0),(35,40),(25,80),(0,80)]).close().revolve(360, (0,0,0), (0,1,0))
dome = (cq.Workplane("XY").circle(140).workplane(offset=35).circle(100)
        .workplane(offset=15).circle(20).loft(ruled=False))
path = cq.Workplane("XZ").spline([(0,0),(50,20),(100,0)])
swept = cq.Workplane("XY").circle(5).sweep(path)
```

## Boolean, joylashtirish, oyna
```python
a = a.union(b); a = a.cut(c); a = a.intersect(d)
b2 = b.translate((x, y, z)); b3 = b.rotate((0,0,0), (0,0,1), 90)
m  = part.mirror("YZ")     # X bo'yicha oyna
asm = cq.Assembly().add(a, name="a", color=cq.Color("red")).add(b, name="b", loc=cq.Location((0,0,20)))
asm.save("asm.step")
```

## 2D eskizdan (rasmdagi kontur) ekstruziya
```python
pts = [(0,0),(100,0),(100,40),(60,40),(60,70),(0,70)]      # scale_from_image.py dan mm
prof = cq.Workplane("XY").polyline(pts).close().extrude(12)
# yoki Sketch API bilan: cq.Sketch().rect(50,30).vertices().fillet(4)
```

## Tekshirish va eksport
```python
bb = r.val().BoundingBox(); (bb.xlen, bb.ylen, bb.zlen, bb.xmin, bb.zmax)
vol = sum(s.Volume() for s in r.solids().vals()); n = len(r.solids().vals())   # 1 bo'lishi kerak
cq.exporters.export(r, "r.step")
cq.exporters.export(r, "r.stl", tolerance=0.01, angularTolerance=0.1)
cq.exporters.export(r, "r.svg", opt={"projectionDir": (1, -1, 1)})           # chizma ko'rinish
```

## Tez-tez uchraydigan xatolar
- `hole()` workplane markazidan teshadi; naqsh uchun avval `rect(..., forConstruction=True).vertices()` yoki `pushPoints([...])`.
- `faces(">Z").workplane()` — yangi tekislik markazi yuzaning markazida; `centerOption="CenterOfBoundBox"` o'zgartirish mumkin.
- Fillet radiusi qirra uzunligi/yarim qalinlikdan katta bo'lsa OCC xato beradi — radiusni kamaytiring.
- `union` natijasi 2 ta solid bo'lsa (teginmaydi) `solids().vals()` > 1 — geometriyani tekshiring.
- `extrude(-h)` teskari yo'nalish; `both=True` ikki tomonga.
