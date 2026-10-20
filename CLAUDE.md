# jarvis-calculators

Isitish/suv ta'minoti (HVAC) kalkulyatorlari — har biri bitta mustaqil HTML fayl (`*.html`, ichki CSS+JS, tashqi kutubxona yo'q,
o'zbek tilida). Qo'shimcha: `.claude/skills/3d-model/` — rasm/aniq o'lchamdan 3D model yasash skilli, `tools/build_graph.py` — bilim grafi.

## Kontekst qoidasi (butun kodni qayta o'qimang)
1. Kod haqidagi har qanday savolda avval `graphify query "<savol>"` (yoki `graphify explain "<tugun>"`, `graphify path "A" "B"`).
   Grafda kalkulyator kiritmalari, jadvallari (`const X = [...]`), funksiyalari, skill fayllari, standart jadvallar, kutubxonalar va
   qo'lda bog'langan `kalkulyator <-> standart jadval <-> 3D misol` qirralari bor; har tugunda `source_file:source_location` (satr) bor.
2. Faqat graf ko'rsatgan satrlarni o'qing (`sed -n 'A,Bp' fayl`). Kalkulyator HTML lar 8-24 KB — to'liq o'qish taqiqlanadi.
3. Keng ko'rinish kerak bo'lsa `graphify-out/JARVIS_GRAPH_REPORT.md` (jamoalar, hublar, kalkulyator→jadval→misol xaritasi).
4. Kod yoki skill fayli o'zgargach: `graphify update .` so'ng `python3 tools/build_graph.py` (ikkalasi LLM/API siz, bir necha soniya).
5. `graphify-out/murod-map.json` va `murod-map.mmd` — Murod xaritasi uchun import bazasi; qo'lda tahrirlamang, `build_graph.py` yozadi.

## 3D model skilli
"3D model", "STEP/STL", "rasmdan model", "razmer bo'yicha" so'ralsa `.claude/skills/3d-model/SKILL.md` ni oching va uning tartibida ishlang:
rasm tahlili → o'lcham jadvali (manba bilan) → standart (`data/standard_sizes.json`) → CadQuery parametrik model → `verify_model.py` → STEP+STL.
Muhit: CadQuery 2.8, trimesh, manifold3d, numpy, Pillow o'rnatilgan; OpenSCAD/Blender yo'q (kod yoziladi, foydalanuvchi o'zida ishga tushiradi).

## Kalkulyator konvensiyalari
- Fayl nomi = mavzu (`radiator.html`, `gidrostrelka.html`...), `<title>` o'zbekcha; `:root` dagi CSS o'zgaruvchilar (dark/light) barcha fayllarda bir xil.
- JS: `(function(){ ... })()` ichida `const ids=[...]`, `num(id)`, `fmt(v,d)`, `row(container,k,v,unit,hi)`, `recalc()`. Yangi kalkulyator shu naqshda.
- Ma'lumot jadvallari `const KATTA_HARF = [...]` — graf ularni `data_table` tugun qiladi; standart o'lchamlar takrorlanmasin, `data/standard_sizes.json` ga qarang.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
