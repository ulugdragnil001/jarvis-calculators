# Graph Report - jarvis-calculators  (2026-10-20)

## Corpus Check
- 21 files · ~21,840 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 146 nodes · 246 edges · 13 communities (9 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4398d8dc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CLAUDE.md
- .claude/CLAUDE.md
- README.md
- standard_sizes.py
- json
- Standart o'lchamlar bazasi
- build_graph.py
- measure_image.py
- scale_from_image.py
- CadQuery naqshlari (shu muhitda CadQuery 2.8 bilan sinovdan o'tgan)
- Bosqichlar
- Ish tartibi
- openscad-patterns.md

## God Nodes (most connected - your core abstractions)
1. `Standart o'lchamlar bazasi` - 19 edges
2. `find()` - 11 edges
3. `nearest()` - 9 edges
4. `CadQuery naqshlari (shu muhitda CadQuery 2.8 bilan sinovdan o'tgan)` - 9 edges
5. `main()` - 7 edges
6. `load()` - 7 edges
7. `main()` - 7 edges
8. `concept_links()` - 7 edges
9. `scan_skills()` - 7 edges
10. `Ish tartibi` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Standart o'lchamlar bazasi` --references--> `find()`  [INFERRED]
  .claude/skills/3d-model/references/standard-sizes.md → .claude/skills/3d-model/scripts/standard_sizes.py
- `4. Quring` --references--> `bbox()`  [INFERRED]
  .claude/skills/3d-model/SKILL.md → .claude/skills/3d-model/scripts/model_template.py
- `Eng yaxshilardan "nusxa olingan" dizayn qoidalari (skillga singdirilgan)` --references--> `verify()`  [INFERRED]
  .claude/skills/3d-model/references/libraries.md → .claude/skills/3d-model/scripts/model_template.py
- `params()` --calls--> `find()`  [EXTRACTED]
  .claude/skills/3d-model/scripts/examples/pipe_flange.py → .claude/skills/3d-model/scripts/standard_sizes.py
- `params()` --calls--> `find()`  [EXTRACTED]
  .claude/skills/3d-model/scripts/examples/expansion_tank.py → .claude/skills/3d-model/scripts/standard_sizes.py

## Import Cycles
- None detected.

## Communities (13 total, 4 thin omitted)

### Community 3 - "standard_sizes.py"
Cohesion: 0.15
Nodes (16): build(), params(), build(), diameter_mm(), params(), build(), params(), build() (+8 more)

### Community 4 - "json"
Cohesion: 0.14
Nodes (12): 3D model yasovchi eng yaxshi kutubxonalar — nima uchun, qachon, qanday, Eng yaxshilardan "nusxa olingan" dizayn qoidalari (skillga singdirilgan), Minimal kod yodnomalari, apply_cli(), bbox(), build(), export(), verify() (+4 more)

### Community 5 - "Standart o'lchamlar bazasi"
Cohesion: 0.11
Nodes (18): copper_pipe_en1057 — Mis quvur EN 1057 OD x devor, expansion_tank_membrane — Membranali kengaytiruvchi bak — hajm -> diametr, balandlik, ulanish *(taxminiy)*, flange_pn16_en1092 — Flanets PN16 (EN 1092-1) DN -> D tashqi, K bolt doirasi, n x teshik, bolt, hydraulic_separator_rule — Gidrostrelka — '3D qoidasi' (klassik) *(taxminiy)*, metric_bolt_iso — Metrik bolt/gayka (ISO 4014/4017, ISO 4032, ISO 273 o'rta teshik), panel_radiator — Panelli radiator (EN 442) — tip -> chuqurlik, panel/konvektor soni *(taxminiy)*, pex_multilayer_pipe — PEX / metall-plastik quvur OD x devor, ppr_pipe — PPR quvur (DIN 8077/8078) OD -> devor PN10 (SDR11) / PN20 (SDR6) (+10 more)

### Community 6 - "build_graph.py"
Cohesion: 0.30
Nodes (10): add_edge(), add_node(), concept_links(), line_of(), manual_links(), merge_and_write(), scan_html(), scan_skills() (+2 more)

### Community 7 - "measure_image.py"
Cohesion: 0.29
Nodes (9): cmd_crop(), cmd_edges(), cmd_grid(), cmd_info(), cmd_mark(), cmd_profile(), draw_grid(), _font() (+1 more)

### Community 8 - "scale_from_image.py"
Cohesion: 0.29
Nodes (7): apply_h(), homography(), linear_scale(), main(), _pt(), run_homography(), run_linear()

### Community 9 - "CadQuery naqshlari (shu muhitda CadQuery 2.8 bilan sinovdan o'tgan)"
Cohesion: 0.20
Nodes (9): 2D eskizdan (rasmdagi kontur) ekstruziya, Asosiy jismlar, Boolean, joylashtirish, oyna, CadQuery naqshlari (shu muhitda CadQuery 2.8 bilan sinovdan o'tgan), Fillet / chamfer / shell, Revolve, loft, sweep, Tekshirish va eksport, Teshik, naqsh, rezba o'rni (+1 more)

### Community 10 - "Bosqichlar"
Cohesion: 0.22
Nodes (8): 1. Rasmni o'qish va ob'ektni aniqlash, 2. Etalonni tanlash, 3. Piksellarni aniq o'qish, 4. Piksel -> mm, 5. Standartga yaxlitlash va chuqurlik, 6. Aniqlik va belgilash, Bosqichlar, Rasmdan aniq o'lcham olish usuli

### Community 11 - "Ish tartibi"
Cohesion: 0.22
Nodes (8): 0. Kirishni tasniflang (1 daqiqa), 1. Rasmni tahlil qiling, 2. O'lchamlarni aniqlang va jadval tuzing, 3. Dvigatelni tanlang, 3D model yasash skilli, 5. Tekshiring va topshiring, Ish tartibi, Qat'iy qoidalar

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Standart o'lchamlar bazasi` connect `Standart o'lchamlar bazasi` to `standard_sizes.py`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Why does `find()` connect `standard_sizes.py` to `Standart o'lchamlar bazasi`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Should `Standart o'lchamlar bazasi` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._