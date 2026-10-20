---
name: 3d-model
description: Rasmdan yoki berilgan o'lchamlardan ANIQ 3D model yasash (CadQuery/build123d/OpenSCAD/trimesh/three.js). Trigger - "3D model", "3d model yasa", "STEP/STL chiqar", "rasmdan model", "chizmadan model", "razmer bo'yicha model", "radiator/quvur/flanets/gidrostrelka/bak modeli", "3D print uchun", "CAD", "OpenSCAD", "cadquery". Standart o'lchamlar bazasi (DN, G rezba, EN 442 radiator, PN16 flanets, bak, boyler) va rasmdan piksel->mm o'lchash skriptlari bilan.
---

# 3D model yasash skilli

Maqsad: **tekshiriladigan** 3D model. Har o'lcham manbasi ma'lum (foydalanuvchi / standart / rasm), model parametrik,
gabarit skript bilan solishtiriladi, natija STEP + STL (+GLB) ko'rinishda.

Fayllar (hammasi `.claude/skills/3d-model/`):
- `references/image-to-dimensions.md` — rasmdan o'lcham olish usuli (etalon, setka, gomografiya, aniqlik jadvali)
- `references/standard-sizes.md` + `data/standard_sizes.json` — standart o'lchamlar bazasi
- `references/libraries.md` — kutubxonalar tanlovi va eng yaxshilaridan olingan qoidalar
- `references/cadquery-patterns.md`, `references/openscad-patterns.md` — sinovdan o'tgan kod naqshlari
- `scripts/measure_image.py`, `scripts/scale_from_image.py` — piksel o'qish va mm ga o'tkazish
- `scripts/standard_sizes.py` — jadval qidiruv (`list | show | find | nearest | md`)
- `scripts/model_template.py` — parametrik model shabloni (PARAMS -> build -> verify -> export)
- `scripts/verify_model.py` — STL/STEP gabarit/hajm/yopiqlik tekshiruvi
- `scripts/examples/*.py` — radiator_panel, pipe_flange, gidrostrelka, expansion_tank (kalkulyatorlarga bog'langan)
- `scripts/viewer_template.html` — three.js ko'ruvchi (repo HTML uslubida)

Kontekstni tejash: avval `graphify query "<savol>"` (graph.json da kalkulyator jadvallari, skill fayllari, standart jadvallar va
kutubxonalar bog'langan). Butun kalkulyator HTML ni qayta o'qimang — graphdan kerakli jadval nomi va qatorini oling.

## Ish tartibi

### 0. Kirishni tasniflang (1 daqiqa)
| Bor narsa | Yo'l |
|---|---|
| Aniq o'lchamlar (matn/chizma raqamlari) | 2 -> 3 -> 4 -> 5 |
| Rasm + ob'ekt turi standart (radiator, quvur, flanets, bak...) | 1 -> standart jadval -> 3 -> 4 -> 5 |
| Rasm + etalon narsa bor | 1 -> 2 (o'lchash) -> 3 -> 4 -> 5 |
| Faqat rasm, etalon yo'q | 1 -> nisbatlar -> foydalanuvchidan 1 ta mutlaq o'lcham so'rang (ishni to'xtatmang: taxminiy standart bilan qurib, belgilang) |
| "Ko'rinishi o'xshasin", o'lcham muhim emas | AI image-to-3D (libraries.md) tavsiya, lekin bu muhitda yo'q — CadQuery bilan soddalashtirilgan shakl |

### 1. Rasmni tahlil qiling
`Read` bilan ko'ring. Yozib qo'ying: ob'ekt, primitivlar ro'yxati, simmetriya, ko'rinish turi, ko'rinishlar soni, etalon bor/yo'q,
chizmada raqamlar bor/yo'q. Kerak bo'lsa `measure_image.py grid/crop/edges` bilan qayta ko'ring (usul: `references/image-to-dimensions.md`).

### 2. O'lchamlarni aniqlang va jadval tuzing
Har o'lcham uchun: **nom, qiymat (mm), manba, aniqlik**. Standart ob'ekt bo'lsa `standard_sizes.py nearest ...` bilan yaxlitlang.
Chuqurlik bitta rasmdan chiqmaydi — standart yoki foydalanuvchi. Jadvalni foydalanuvchiga ko'rsating (qisqa).

### 3. Dvigatelni tanlang
- Aniq o'lcham, STEP, fillet, rezba o'rni -> **CadQuery** (`model_template.py` dan nusxa).
- Foydalanuvchi `.scad` so'rasa yoki oddiy CSG -> **OpenSCAD** kodi (`openscad-patterns.md`), tekshiruv STL orqali.
- Tayyor mesh bilan ish (masshtab, boolean, repair) -> **trimesh**.
- Ko'rsatish kerak -> `viewer_template.html` ni nusxalab `?src=model.stl`.

### 4. Quring
1. `scripts/model_template.py` ni `out/<nom>.py` ga nusxalang; `PARAMS` ni 2-bosqich jadvalidan to'ldiring (`expect` ham).
2. `build()` ni yozing: avval asosiy gabarit jism, keyin teshik/ulanish/fillet. Har qadamda `bbox()` o'zgarishini bilib turing.
3. Ishga tushiring: `python3 out/<nom>.py --out out/`. `ok: false` bo'lsa `diff` ga qarab tuzating (eng ko'p sabab: boss/patrubka gabaritdan chiqadi, fillet radiusi katta, `centered` noto'g'ri).
4. Misollar tayyor bo'lsa ulardan boshlang: `examples/radiator_panel.py --type 22 --H 500 --L 1000`, `examples/pipe_flange.py --DN 50`, `examples/gidrostrelka.py --Q 50 --t_pod 80 --t_obr 60`, `examples/expansion_tank.py --V 24`.

### 5. Tekshiring va topshiring
- `verify_model.py out/<nom>.stl --expect LxWxH --tol 0.5` -> `ok: true` va `watertight: true` shart. STEP ham tekshiriladi.
- `solids == 1` (bir butun jism) — aks holda union tegmagan.
- Natija: fayl yo'llari, o'lcham jadvali (manbalari bilan), taxminiy/yaxlitlangan qiymatlar alohida belgilangan, kerak bo'lsa viewer.
- Yangi standart jadval yoki misol qo'shilsa: `data/standard_sizes.json` ga yozing, `standard_sizes.py md > references/standard-sizes.md`, keyin `python3 tools/build_graph.py` (graf yangilanadi).

## Qat'iy qoidalar
- Foydalanuvchi bergan aniq o'lcham hech qachon "yaxshilanmaydi".
- Sehrli sonlar yo'q: hammasi `PARAMS` da, standartdan olingan qiymat yonida jadval nomi izohda.
- Yaxlitlash va taxmin har doim oshkora: hisobotda `(standart)`, `(rasm ±3 %)`, `(taxmin — tasdiqlang)`.
- Model chop etilmasdan/topshirilmasdan oldin `verify_model.py` o'tishi shart; o'tmasa natija "tayyor" deb aytilmaydi.
- Katta kalkulyator HTML larni to'liq o'qimang — `graphify query` yoki graphdagi `source_location` bilan kerakli qatorlarni oling.
