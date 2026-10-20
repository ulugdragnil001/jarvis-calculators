# OpenSCAD naqshlari (oddiy CSG, tez skript, 3D chop etish)

Qachon: shakl faqat quti/silindr/teshiklardan iborat, STEP kerak emas, foydalanuvchi `.scad` so'ragan yoki
OpenSCAD o'rnatilgan (bu muhitda yo'q; kodni yozib, foydalanuvchi o'zida `openscad -o out.stl model.scad` qiladi).

```openscad
// ---------- PARAMETRLAR (mm) ----------
L = 120; W = 80; T = 6;          // plita
hole_d = 9;  margin = 12;        // M8 -> ISO 273 o'rta 9.0
corner_r = 5;
$fn = 96;                        // aylana sifati (64..128)
eps = 0.01;                      // kesuvchi jismni uzaytirish

// ---------- MODULLAR ----------
module rounded_box(l, w, t, r) {
  linear_extrude(t) offset(r) offset(-r) square([l, w], center = true);
}
module plate() {
  difference() {
    rounded_box(L, W, T, corner_r);
    for (x = [-1, 1], y = [-1, 1])
      translate([x * (L/2 - margin), y * (W/2 - margin), -eps])
        cylinder(h = T + 2*eps, d = hole_d);
  }
}
module tube(od, wall, h) { difference() { cylinder(h = h, d = od); translate([0,0,-eps]) cylinder(h = h + 2*eps, d = od - 2*wall); } }
module flange_pn16_dn50() {                          // D165 K125 4x18
  difference() { cylinder(h = 20, d = 165); translate([0,0,-eps]) cylinder(h = 21, d = 53.1);
    for (a = [0:90:359]) rotate(a) translate([62.5, 0, -eps]) cylinder(h = 21, d = 18); }
}
module revolve_profile() { rotate_extrude() polygon([[0,0],[30,0],[35,40],[25,80],[0,80]]); }

plate();
// echo(str("bbox ", L, "x", W, "x", T));   // gabaritni konsolga chiqarish
```

Qoidalar:
- Barcha sonlar yuqoridagi parametr blokida; modullar nomli parametr oladi.
- `difference()` ichida kesuvchi jismni `eps` ga uzaytiring, aks holda yupqa qatlam qoladi.
- `offset(r) offset(-r)` 2D da burchak yumaloqlash — `minkowski` dan ancha tez.
- Fillet 3D da yo'q: BOSL2 (`include <BOSL2/std.scad>`, `cuboid(..., rounding=3)`) ishlating.
- Eksport: `openscad -o model.stl model.scad`; `-D "L=200"` bilan parametrni tashqaridan berish.
- Tekshiruv: chiqqan STL ni `scripts/verify_model.py model.stl --expect LxWxT` bilan solishtiring.
