# jarvis-calculators

Isitish va suv ta'minoti uchun mustaqil HTML kalkulyatorlar (o'zbek tilida): radiator, gidrostrelka, gidravlika, boyler,
kengaytiruvchi bak, issiqlik almashtirgich, konvektor (ventilyatorli/siz), devor issiqlik qarshiligi, avtopoliv.
Har fayl brauzerda to'g'ridan-to'g'ri ochiladi, tashqi kutubxona talab qilmaydi.

## 3D model skilli (`.claude/skills/3d-model/`)
Rasmdan yoki aniq o'lchamdan tekshiriladigan 3D model (STEP + STL) yasash: standart o'lchamlar bazasi
(DN quvur, G rezba, EN 442 radiator, PN16 flanets, bak, boyler...), rasmdan piksel→mm o'lchash skriptlari,
CadQuery parametrik shablon, gabarit tekshiruvi, three.js ko'ruvchi. Misollar kalkulyatorlarga bog'langan:

```
python3 .claude/skills/3d-model/scripts/examples/radiator_panel.py --type 22 --H 500 --L 1000 --out out/
python3 .claude/skills/3d-model/scripts/examples/gidrostrelka.py --Q 50 --t_pod 80 --t_obr 60 --out out/
python3 .claude/skills/3d-model/scripts/verify_model.py out/radiator_t22_H500_L1000.stl --expect 1000x100x500
```
Talab: `pip install cadquery trimesh manifold3d numpy pillow`.

## Bilim grafi (graphify + tools/build_graph.py)
`graphify-out/graph.json` — kalkulyatorlar, ularning kiritma/jadval/funksiyalari, skill fayllari, standart jadvallar va
kutubxonalar o'zaro bog'langan graf. `graphify query "savol"` bilan so'rang; yangilash: `graphify update . && python3 tools/build_graph.py`.
`graphify-out/murod-map.json|.mmd` — tashqi (Murod) xaritasi uchun eksport.
