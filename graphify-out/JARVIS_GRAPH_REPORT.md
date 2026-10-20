# JARVIS graf hisoboti (tools/build_graph.py)

Qoidа: avval `graphify query "..."`, keyin faqat `source_file:source_location` dagi satrlarni o'qing. Butun HTML ni o'qimang.

- Tugunlar: 179 · Qirralar: 525 · Jamoalar: 7

## Jamoalar
- **Kalkulyatorlar** (116): Avtopoliv — Liniya hisobi, Boyler hisobi, Gidravlika hisobi, Gidrostrelka hisobi, Issiqlik almashtirgich hisobi, Kengaytiruvchi bak hisobi, Konvektor (ventilyatorli), Konvektor (ventilyatorsiz), R — Devor issiqlik qarshiligi, Radiator hisob-kitoblari
- **Domen tushunchalari** (19): Avtopoliv, Bosim / napor, Boyler / suv isitgich, CAD dvigatel / B-rep, DN (nominal diametr), Devor issiqlik qarshiligi R, G issiqlik tashuvchi sarfi, G rezba (BSP), Gidrostrelka, Hajm, Issiqlik yo'qotish Q, Kengaytiruvchi bak, Konvektor, Oqim tezligi V
- **Skill 3d-model** (17): skill 3d-model, viewer_template.html
- **Standart o'lchamlar** (17): Flanets PN16 (EN 1092-1) DN -> D tashqi, K bolt doirasi, n x teshik, bolt, G (BSP, ISO 228) quvur rezbasi — tashqi diametr, qadam, Gidrostrelka — '3D qoidasi' (klassik), List po'lat qalinliklari (standart qator), Membranali kengaytiruvchi bak — hajm -> diametr, balandlik, ulanish, Metrik bolt/gayka (ISO 4014/4017, ISO 4032, ISO 273 o'rta teshik), Mis quvur EN 1057 OD x devor, PEX / metall-plastik quvur OD x devor, PPR quvur (DIN 8077/8078) OD -> devor PN10 (SDR11) / PN20 (SDR6), Panelli radiator (EN 442) — tip -> chuqurlik, panel/konvektor soni, Po'lat quvur DN -> tashqi diametr (EN 10220 / ISO 4200), Profil quvur (kvadrat) a x a x t — keng tarqalgan, Profil quvur (to'g'ri burchak) a x b x t, Rasmda masshtab uchun ishlatiladigan ma'lum o'lchamli narsalar
- **Kutubxonalar** (8): CadQuery (OpenCascade B-rep, STEP), OpenSCAD, Pillow (rasm), build123d, manifold3d (boolean), numpy, three.js (WebGL ko'ruvchi), trimesh (mesh tahlil)
- **Skill graphify** (1): skill graphify
- **Asboblar** (1): 

## Eng bog'langan tugunlar (hub)
- `claude_skills_3d_model_references_standard_sizes` — standard-sizes.md (54 qirra) → .claude/skills/3d-model/references/standard-sizes.md:L1
- `data:3d-model/data/standard_sizes.json` — standard_sizes.json (37 qirra) → .claude/skills/3d-model/data/standard_sizes.json:L1
- `html:radiator` — Radiator hisob-kitoblari (34 qirra) → radiator.html:L1
- `html:gidravlika` — Gidravlika hisobi (30 qirra) → gidravlika.html:L1
- `html:gidrostrelka` — Gidrostrelka hisobi (24 qirra) → gidrostrelka.html:L1
- `html:kengaytiruvchi_bak` — Kengaytiruvchi bak hisobi (22 qirra) → kengaytiruvchi_bak.html:L1
- `claude_skills_3d_model_scripts_examples_gidrostrelka` — gidrostrelka.py (20 qirra) → .claude/skills/3d-model/scripts/examples/gidrostrelka.py:L1
- `html:avtopoliv` — Avtopoliv — Liniya hisobi (17 qirra) → avtopoliv.html:L1
- `html:boyler` — Boyler hisobi (16 qirra) → boyler.html:L1
- `skill:3d-model` — skill 3d-model (16 qirra) → .claude/skills/3d-model/SKILL.md:L1
- `claude_skills_3d_model_scripts_examples_radiator_panel` — radiator_panel.py (16 qirra) → .claude/skills/3d-model/scripts/examples/radiator_panel.py:L1
- `html:konvektor_ventilyatorsiz` — Konvektor (ventilyatorsiz) (15 qirra) → konvektor_ventilyatorsiz.html:L1

## Kalkulyator → standart jadval → 3D misol xaritasi
- `html:radiator` —related→ `table:panel_radiator`: radiator.html PANELS (tip/H/L -> Vt) <-> standart chuqurlik/ulanish
- `html:radiator` —related→ `table:sectional_radiator`: ALU/BIM seksiya quvvati <-> seksiya gabariti
- `html:radiator` —modeled_by→ `claude_skills_3d_model_scripts_examples_radiator_panel`: radiator 3D misoli
- `html:gidrostrelka` —related→ `table:hydraulic_separator_rule`: D = sqrt(4G/(pi V)) formulasi va 3D qoidasi
- `html:gidrostrelka` —modeled_by→ `claude_skills_3d_model_scripts_examples_gidrostrelka`: formula takrorlanadi, DN ga yaxlitlanadi
- `html:gidrostrelka` —related→ `table:steel_pipe_en10220`: hisoblangan D -> standart quvur OD
- `html:kengaytiruvchi_bak` —related→ `table:expansion_tank_membrane`: STANDARD_SIZES hajmlari bir xil
- `html:kengaytiruvchi_bak` —modeled_by→ `claude_skills_3d_model_scripts_examples_expansion_tank`: bak 3D misoli
- `html:avtopoliv` —related→ `table:ppr_pipe`: PIPE_TABLE = PPR PN20 devor qalinliklari
- `html:gidravlika` —related→ `table:ppr_pipe`: PIPE_TABLE = PPR PN20 devor qalinliklari
- `html:gidravlika` —related→ `table:steel_pipe_en10220`: DN -> ichki diametr
- `html:boyler` —related→ `table:storage_boiler`: hajm -> gabarit
- `html:radiator` —related→ `table:thread_g_bsp`: ulanish G1/2 / G1
- `table:flange_pn16_en1092` —modeled_by→ `claude_skills_3d_model_scripts_examples_pipe_flange`: flanets 3D misoli
- `table:steel_pipe_en10220` —modeled_by→ `claude_skills_3d_model_scripts_examples_pipe_flange`: quvur OD/devor

## Kalkulyatorlar (kiritma / jadval / funksiya)
- **avtopoliv.html** — Avtopoliv — Liniya hisobi
  - kiritmalar: —
  - jadvallar: PIPE_TABLE@L201
  - funksiyalar: internalD(), newRow(), newLinya(), loadSaved(), saveState(), frictionPerMeter(), computeLinya(), render()
- **boyler.html** — Boyler hisobi
  - kiritmalar: V, P, t_cold, t_hot
  - jadvallar: —
  - funksiyalar: loadSaved(), saveState(), recalc()
- **gidravlika.html** — Gidravlika hisobi
  - kiritmalar: t_pod, t_obr, bh_t1, bh_t2, bh_f1, bh_f2
  - jadvallar: PIPE_TABLE@L251
  - funksiyalar: internalD(), frictionPerMeter(), newRow(), newLinya(), loadSaved(), saveState(), computeLinya(), buildAll(), updateAll(), recalcBh()
- **gidrostrelka.html** — Gidrostrelka hisobi
  - kiritmalar: Q, t_pod, t_obr, dt-hint, V_strelka, V_potrub
  - jadvallar: —
  - funksiyalar: diameterMm(), recalc()
- **issiqlik_almashtirgich.html** — Issiqlik almashtirgich hisobi
  - kiritmalar: L, W, Dep, location, t1, t2, hours
  - jadvallar: —
  - funksiyalar: recalc()
- **kengaytiruvchi_bak.html** — Kengaytiruvchi bak hisobi
  - kiritmalar: Vsyst, Tmax, glycol, Vwr, Hst, Kb, Pmargin
  - jadvallar: EXP_TABLE@L172, GLYCOL_COL@L190, STANDARD_SIZES@L192
  - funksiyalar: expansionPercent(), recalc()
- **konvektor_ventilyatorli.html** — Konvektor (ventilyatorli)
  - kiritmalar: q_loss, t_room, t_pod, t_obr
  - jadvallar: LENGTHS@L136, SPEEDS@L137, POWER@L138
  - funksiyalar: recalc()
- **konvektor_ventilyatorsiz.html** — Konvektor (ventilyatorsiz)
  - kiritmalar: q_loss, t_room, t_pod, t_obr, width_sel
  - jadvallar: LENGTHS@L146, ROWS@L147, CORR@L161
  - funksiyalar: correction(), recalc()
- **r_devor_issiqlik.html** — R — Devor issiqlik qarshiligi
  - kiritmalar: region
  - jadvallar: MATERIALS@L160, REGIONS@L183
  - funksiyalar: newLayer(), loadSaved(), saveState(), buildAll(), updateAll()
- **radiator.html** — Radiator hisob-kitoblari
  - kiritmalar: t_pod, t_obr, t_room, q_loss, conn_type, install_type, sect_group, sect_model
  - jadvallar: CONN@L209, INSTALL@L219, ALU@L234, BIM@L240, PANELS@L253
  - funksiyalar: fillSelect(), fillSimpleSelect(), beta3(), refreshSectModel(), setMode(), recalc()

## Murod xaritasi uchun
- `graphify-out/murod-map.json` — {nodes:[{id,label,kind,group,file,line}], edges:[{from,to,rel}]}
- `graphify-out/murod-map.mmd` — Mermaid; har qanday graf vositasiga import qilish mumkin.
