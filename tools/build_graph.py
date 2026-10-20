#!/usr/bin/env python3
"""jarvis-calculators bilim grafi quruvchisi (graphify bilan birga ishlaydi).

graphify'ning tree-sitter o'tishi bu repodagi bir-faylli HTML kalkulyatorlarni (ichki <script>) deyarli ko'rmaydi.
Shu skript repo-ga xos tugun/qirralarni chiqaradi va graphify-out/graph.json ga (graphify sxemasida) qo'shadi:

  kalkulyator (html)  --contains-->  kiritma (input/select id), jadval (const X = [...]), funksiya
  funksiya            --uses------>  kiritma / jadval         (funksiya tanasida ishlatilsa)
  kalkulyator/jadval  --references-> domen tushunchasi (DN, dT, G, radiator, ...)
  skill (3d-model)    --contains-->  reference / script / data jadvali
  script              --imports---->  kutubxona (cadquery, trimesh, numpy, PIL)
  script/reference    --references-> data jadvali, kalkulyator (see_also, matndagi nom)
  (qo'lda) LINKS      --related---->  kalkulyator <-> standart jadval <-> 3D misol

Chiqish:
  graphify-out/graph.json        — graphify tugunlari (_origin=ast) saqlanadi, _origin=jarvis lari yangilanadi
  graphify-out/graph.html        — `graphify export html` orqali qayta chiziladi (bo'lsa)
  graphify-out/JARVIS_GRAPH_REPORT.md — navigatsiya hisobot (jamoalar, hublar, kalkulyator->jadval xaritasi)
  graphify-out/murod-map.json    — soddalashtirilgan {nodes, edges} (Murod xaritasi uchun import bazasi)
  graphify-out/murod-map.mmd     — Mermaid ko'rinishi

Ishlatish:  python3 tools/build_graph.py [--no-html]
Butun kodni qayta o'qish shart emas: har tugunda source_file + source_location (satr) bor — kerak joyga to'g'ri boriladi.
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "graphify-out"
SKILLS = ROOT / ".claude" / "skills"

# ----------------------------------------------------------------- domen tushunchalari (kalit so'z -> tugun)
CONCEPTS = {
    "dn": ("DN (nominal diametr)", r"\bDN\b|nominal|diametr"),
    "delta_t": ("ΔT harorat napori", r"t_pod|t_obr|dT\b|ΔT"),
    "flow_g": ("G issiqlik tashuvchi sarfi", r"\bG_m3h\b|0\.86\s*\*|sarf"),
    "heat_loss": ("Issiqlik yo'qotish Q", r"q_loss|\bQ\b|issiqlik"),
    "pipe": ("Quvur", r"PIPE_TABLE|quvur|pipe"),
    "radiator": ("Radiator", r"radiator|PANELS|seksiya"),
    "velocity": ("Oqim tezligi V", r"V_strelka|V_potrub|tezlik|velocity"),
    "pressure": ("Bosim / napor", r"bosim|napor|Pmargin|Hst|\bP\b"),
    "volume": ("Hajm", r"Vsyst|\bV\b|hajm|volume_l"),
    "thread_g": ("G rezba (BSP)", r"G1/2|G3/4|\bG1\b|thread_g"),
    "standard_size": ("Standart o'lcham", r"STANDARD_SIZES|standard_sizes|standart"),
    "wall_r": ("Devor issiqlik qarshiligi R", r"MATERIALS|REGIONS|qarshilig"),
    "convector": ("Konvektor", r"konvektor|LENGTHS|SPEEDS"),
    "boiler": ("Boyler / suv isitgich", r"boyler|storage_boiler"),
    "expansion_tank": ("Kengaytiruvchi bak", r"kengaytir|expansion|EXP_TABLE"),
    "hydraulic_separator": ("Gidrostrelka", r"gidrostrelka|hydraulic_separator|diameterMm"),
    "irrigation": ("Avtopoliv", r"avtopoliv|liniya|poliv"),
    "image_measure": ("Rasmdan o'lchash", r"measure_image|scale_from_image|homography|etalon|piksel"),
    "cad_engine": ("CAD dvigatel / B-rep", r"cadquery|build123d|openscad|STEP"),
}

# qo'lda bog'lanishlar: kalkulyator <-> standart jadval <-> 3D misol (graf hech qachon o'zi topolmaydigan domen bilimi)
LINKS = [
    ("html:radiator", "table:panel_radiator", "related", "radiator.html PANELS (tip/H/L -> Vt) <-> standart chuqurlik/ulanish"),
    ("html:radiator", "table:sectional_radiator", "related", "ALU/BIM seksiya quvvati <-> seksiya gabariti"),
    ("html:radiator", "script:3d-model/scripts/examples/radiator_panel.py", "modeled_by", "radiator 3D misoli"),
    ("html:gidrostrelka", "table:hydraulic_separator_rule", "related", "D = sqrt(4G/(pi V)) formulasi va 3D qoidasi"),
    ("html:gidrostrelka", "script:3d-model/scripts/examples/gidrostrelka.py", "modeled_by", "formula takrorlanadi, DN ga yaxlitlanadi"),
    ("html:gidrostrelka", "table:steel_pipe_en10220", "related", "hisoblangan D -> standart quvur OD"),
    ("html:kengaytiruvchi_bak", "table:expansion_tank_membrane", "related", "STANDARD_SIZES hajmlari bir xil"),
    ("html:kengaytiruvchi_bak", "script:3d-model/scripts/examples/expansion_tank.py", "modeled_by", "bak 3D misoli"),
    ("html:avtopoliv", "table:ppr_pipe", "related", "PIPE_TABLE = PPR PN20 devor qalinliklari"),
    ("html:gidravlika", "table:ppr_pipe", "related", "PIPE_TABLE = PPR PN20 devor qalinliklari"),
    ("html:gidravlika", "table:steel_pipe_en10220", "related", "DN -> ichki diametr"),
    ("html:boyler", "table:storage_boiler", "related", "hajm -> gabarit"),
    ("html:radiator", "table:thread_g_bsp", "related", "ulanish G1/2 / G1"),
    ("table:flange_pn16_en1092", "script:3d-model/scripts/examples/pipe_flange.py", "modeled_by", "flanets 3D misoli"),
    ("table:steel_pipe_en10220", "script:3d-model/scripts/examples/pipe_flange.py", "modeled_by", "quvur OD/devor"),
]

LIBS = {
    "cadquery": "CadQuery (OpenCascade B-rep, STEP)", "trimesh": "trimesh (mesh tahlil)", "manifold3d": "manifold3d (boolean)",
    "numpy": "numpy", "PIL": "Pillow (rasm)", "three": "three.js (WebGL ko'ruvchi)", "build123d": "build123d", "openscad": "OpenSCAD",
}

nodes: dict[str, dict] = {}
edges: list[dict] = []
AST_INDEX: dict[tuple, str] = {}   # graphify (tree-sitter) allaqachon yaratgan tugunlar: takrorlamaymiz, ularga ulanamiz


def load_ast_index():
    gpath = OUT / "graph.json"
    if not gpath.exists():
        return
    g = json.loads(gpath.read_text(encoding="utf-8"))
    for n in g.get("nodes", []):
        if n.get("_origin") == "jarvis":
            continue
        sf = n.get("source_file", "")
        lab = (n.get("norm_label") or n.get("label", "")).lower()
        AST_INDEX.setdefault((sf, lab), n["id"])
        if n.get("source_location") == "L1" and lab in (Path(sf).name.lower(), sf.lower()):
            AST_INDEX.setdefault((sf, "__file__"), n["id"])


def add_node(nid, label, kind, file, line=1, community="", **extra):
    # graphify o'zi chiqargan funksiya/sarlavha/fayl tuguni bo'lsa — shuni qaytaramiz (dublikat yo'q)
    if kind in ("function", "heading"):
        hit = AST_INDEX.get((file, label.lower()))
        if hit:
            return hit
    if kind in ("script", "reference", "tool"):
        hit = AST_INDEX.get((file, "__file__"))
        if hit:
            return hit
    if nid not in nodes:
        nodes[nid] = {"id": nid, "label": label, "_origin": "jarvis", "node_kind": kind, "file_type": "code" if file.endswith((".py", ".html", ".js")) else "document",
                      "norm_label": label.lower(), "source_file": file, "source_location": f"L{line}", "community_name": community, **extra}
    return nid


def add_edge(a, b, rel, note="", conf="EXTRACTED", score=1.0, file="", line=1):
    edges.append({"source": a, "target": b, "relation": rel, "_origin": "jarvis", "confidence": conf, "confidence_score": score,
                  "source_file": file, "source_location": f"L{line}", "weight": 1.0, **({"note": note} if note else {})})


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def concept_links(src_id, text, file, limit_kinds=None):
    for cid, (label, rx) in CONCEPTS.items():
        m = re.search(rx, text)
        if m:
            add_node(f"concept:{cid}", label, "concept", "graphify-out/JARVIS_GRAPH_REPORT.md", 1, "Domen tushunchalari")
            add_edge(src_id, f"concept:{cid}", "references", conf="INFERRED", score=0.7, file=file, line=line_of(text, m.start()))


# ----------------------------------------------------------------- 1. HTML kalkulyatorlar
def scan_html():
    for f in sorted(ROOT.glob("*.html")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        stem = f.stem
        cid = f"html:{stem}"
        title = re.search(r"<title>([^<]*)</title>", text)
        add_node(cid, title.group(1).strip() if title else stem, "calculator", f.name, 1, "Kalkulyatorlar", path=f.name)
        # kiritmalar
        for m in re.finditer(r"<(input|select)\b[^>]*\bid=\"([^\"]+)\"", text):
            iid = m.group(2)
            lab = re.search(rf"<label[^>]*for=\"{re.escape(iid)}\"[^>]*>([^<]*)", text)
            nid = add_node(f"{cid}#{iid}", f"{iid}" + (f" — {lab.group(1).strip()}" if lab and lab.group(1).strip() else ""), "input",
                           f.name, line_of(text, m.start()), "Kalkulyatorlar", input_type=m.group(1))
            add_edge(cid, nid, "contains", file=f.name, line=line_of(text, m.start()))
        # ma'lumot jadvallari
        for m in re.finditer(r"const\s+([A-Z][A-Z_0-9]{2,})\s*=\s*[\[{]", text):
            name = m.group(1)
            nid = add_node(f"{cid}::{name}", f"{name} jadvali", "data_table", f.name, line_of(text, m.start()), "Kalkulyatorlar")
            add_edge(cid, nid, "contains", file=f.name, line=line_of(text, m.start()))
        # funksiyalar va ularning bog'liqliklari
        funcs = list(re.finditer(r"function\s+([a-zA-Z_][\w]*)\s*\(", text))
        for i, m in enumerate(funcs):
            name = m.group(1)
            if name in ("num", "fmt", "row", "tNum"):
                continue  # umumiy yordamchilar — shovqin
            start = m.start()
            end = funcs[i + 1].start() if i + 1 < len(funcs) else len(text)
            body = text[start:end]
            fid = add_node(f"{cid}.{name}()", f"{name}()", "function", f.name, line_of(text, start), "Kalkulyatorlar")
            add_edge(cid, fid, "contains", file=f.name, line=line_of(text, start))
            for iid in re.findall(r"num\('([^']+)'\)|getElementById\('([^']+)'\)|tNum\([^,]+,\s*'([^']+)'", body):
                iid = next(x for x in iid if x)
                if f"{cid}#{iid}" in nodes:
                    add_edge(fid, f"{cid}#{iid}", "uses", file=f.name, line=line_of(text, start))
            for tname in re.findall(r"\b([A-Z][A-Z_0-9]{2,})\b", body):
                if f"{cid}::{tname}" in nodes:
                    add_edge(fid, f"{cid}::{tname}", "uses", file=f.name, line=line_of(text, start))
            for other in funcs:
                on = other.group(1)
                if on != name and re.search(rf"\b{on}\(", body) and f"{cid}.{on}()" in [f"{cid}.{x.group(1)}()" for x in funcs]:
                    if on not in ("num", "fmt", "row", "tNum"):
                        add_edge(fid, f"{cid}.{on}()", "calls", file=f.name, line=line_of(text, start))
        concept_links(cid, text, f.name)


# ----------------------------------------------------------------- 2. Skill fayllari
def scan_skills():
    if not SKILLS.exists():
        return
    for sk in sorted(SKILLS.iterdir()):
        if not sk.is_dir() or not (sk / "SKILL.md").exists():
            continue
        sid = f"skill:{sk.name}"
        smd = (sk / "SKILL.md").read_text(encoding="utf-8")
        desc = re.search(r"^description:\s*(.*)$", smd, re.M)
        add_node(sid, f"skill {sk.name}", "skill", f".claude/skills/{sk.name}/SKILL.md", 1, f"Skill {sk.name}",
                 description=(desc.group(1)[:160] if desc else ""))
        if sk.name == "graphify":
            continue  # tashqi plagin: faqat tugun
        for p in sorted(sk.rglob("*")):
            if p.is_dir() or p.name.startswith(".") or p.suffix == ".pyc" or "__pycache__" in p.parts:
                continue
            rel = p.relative_to(SKILLS).as_posix()
            relroot = p.relative_to(ROOT).as_posix()
            kind = "reference" if p.suffix == ".md" and p.name != "SKILL.md" else "script" if p.suffix in (".py", ".html") else "data" if p.suffix == ".json" else "doc"
            if p.name == "SKILL.md":
                continue
            nid = add_node(f"{kind}:{rel}", p.name, kind, relroot, 1, f"Skill {sk.name}")
            add_edge(sid, nid, "contains", file=relroot)
            text = p.read_text(encoding="utf-8", errors="ignore")
            if p.suffix == ".md":
                for m in re.finditer(r"^##\s+(.+)$", text, re.M):
                    hid = add_node(f"{nid}#{m.group(1).strip()[:60]}", m.group(1).strip()[:60], "heading", relroot, line_of(text, m.start()), f"Skill {sk.name}")
                    add_edge(nid, hid, "contains", file=relroot, line=line_of(text, m.start()))
            if p.suffix == ".py":
                for m in re.finditer(r"^def\s+(\w+)\(", text, re.M):
                    fid = add_node(f"{nid}.{m.group(1)}()", f"{m.group(1)}()", "function", relroot, line_of(text, m.start()), f"Skill {sk.name}")
                    add_edge(nid, fid, "contains", file=relroot, line=line_of(text, m.start()))
                for m in re.finditer(r"^(?:import|from)\s+([\w.]+)", text, re.M):
                    lib = m.group(1).split(".")[0]
                    if lib in LIBS:
                        add_node(f"lib:{lib}", LIBS[lib], "library", ".claude/skills/3d-model/references/libraries.md", 1, "Kutubxonalar")
                        add_edge(nid, f"lib:{lib}", "imports", file=relroot, line=line_of(text, m.start()))
                    elif lib == "standard_sizes":
                        tgt = AST_INDEX.get((".claude/skills/3d-model/scripts/standard_sizes.py", "__file__"), "script:3d-model/scripts/standard_sizes.py")
                        add_edge(nid, tgt, "imports", file=relroot, line=line_of(text, m.start()))
            if p.suffix == ".html" and "three" in text:
                add_node("lib:three", LIBS["three"], "library", ".claude/skills/3d-model/references/libraries.md", 1, "Kutubxonalar")
                add_edge(nid, "lib:three", "imports", file=relroot)
            if p.name == "standard_sizes.json":
                db = json.loads(text)
                for tname, t in db.items():
                    if tname.startswith("_"):
                        continue
                    tid = add_node(f"table:{tname}", t.get("title", tname), "standard_table", relroot, 1, "Standart o'lchamlar", approx=bool(t.get("approx")))
                    add_edge(nid, tid, "contains", file=relroot)
                    see = t.get("see_also", "")
                    for html in re.findall(r"([a-z_]+)\.html", see):
                        if f"html:{html}" in nodes:
                            add_edge(tid, f"html:{html}", "references", note=see[:120], file=relroot)
            # matnda tilga olingan fayllar / jadvallar
            for tname in re.findall(r"\b([a-z_]+(?:_[a-z0-9]+)+)\b", text):
                if f"table:{tname}" in nodes and kind != "data":
                    add_edge(nid, f"table:{tname}", "references", conf="INFERRED", score=0.8, file=relroot)
            for html in set(re.findall(r"\b([a-z_]+)\.html\b", text)):
                if f"html:{html}" in nodes:
                    add_edge(nid, f"html:{html}", "references", conf="INFERRED", score=0.8, file=relroot)
            for lib in LIBS:
                if p.suffix == ".md" and re.search(rf"\b{lib}\b", text, re.I):
                    add_node(f"lib:{lib}", LIBS[lib], "library", ".claude/skills/3d-model/references/libraries.md", 1, "Kutubxonalar")
                    add_edge(nid, f"lib:{lib}", "references", conf="INFERRED", score=0.6, file=relroot)
            concept_links(nid, text, relroot)
    # tools
    for p in sorted((ROOT / "tools").glob("*.py")):
        nid = add_node(f"tool:{p.name}", p.name, "tool", f"tools/{p.name}", 1, "Asboblar")
        add_edge(nid, "graphify-out", "writes", file=f"tools/{p.name}")
    add_node("graphify-out", "graphify-out/ (bilim grafi)", "artifact", "graphify-out/graph.json", 1, "Asboblar")


def resolve(nid):
    """'script:<rel>' ko'rinishidagi id ni graphify fayl tuguniga xaritalash (bo'lsa)."""
    if nid in nodes:
        return nid
    if nid.startswith("script:"):
        return AST_INDEX.get((".claude/skills/" + nid[len("script:"):], "__file__"), nid)
    return nid


def manual_links():
    for a, b, rel, note in LINKS:
        a, b = resolve(a), resolve(b)
        known = set(nodes) | set(AST_INDEX.values())
        if a in known and b in known:
            add_edge(a, b, rel, note=note, conf="EXTRACTED", score=1.0, file="tools/build_graph.py")
        else:
            print(f"ogohlantirish: LINKS tuguni yo'q: {a if a not in known else b}", file=sys.stderr)


# ----------------------------------------------------------------- 3. graphify-out ga yozish
def merge_and_write(no_html=False):
    OUT.mkdir(exist_ok=True)
    gpath = OUT / "graph.json"
    g = json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else {"directed": False, "multigraph": False, "graph": {"schema_version": 1}, "nodes": [], "links": [], "hyperedges": []}
    keep_nodes = [n for n in g.get("nodes", []) if n.get("_origin") != "jarvis"]
    keep_links = [e for e in g.get("links", []) if e.get("_origin") != "jarvis"]
    # jamoalar: mavjud maksimal id dan davom
    max_c = max([n.get("community", -1) for n in keep_nodes] + [-1])
    cids = {}
    for n in nodes.values():
        name = n.get("community_name") or "Boshqa"
        if name not in cids:
            max_c += 1
            cids[name] = max_c
        n["community"] = cids[name]
    seen = set()
    uniq = []
    known = set(nodes) | {n["id"] for n in keep_nodes}
    for e in edges:
        k = (e["source"], e["target"], e["relation"])
        if k in seen or e["source"] not in known or e["target"] not in known:
            continue
        seen.add(k)
        uniq.append(e)
    g["nodes"] = keep_nodes + list(nodes.values())
    g["links"] = keep_links + uniq
    g.setdefault("graph", {})["jarvis_builder"] = "tools/build_graph.py"
    try:
        g["built_at_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or g.get("built_at_commit")
    except Exception:
        pass
    gpath.write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    write_report(cids, uniq)
    write_murod_map(uniq)
    if not no_html:
        try:
            subprocess.run(["graphify", "export", "html", "--graph", str(gpath)], cwd=ROOT, check=False, capture_output=True, text=True, timeout=120)
        except Exception as e:
            print("graph.html yangilanmadi:", e, file=sys.stderr)
    print(f"graph.json: {len(g['nodes'])} tugun ({len(nodes)} jarvis), {len(g['links'])} qirra ({len(uniq)} jarvis), {len(cids)} jamoa")


def all_labels():
    gpath = OUT / "graph.json"
    lab = {n["id"]: n for n in nodes.values()}
    if gpath.exists():
        for n in json.loads(gpath.read_text(encoding="utf-8")).get("nodes", []):
            lab.setdefault(n["id"], n)
    return lab


def write_report(cids, uniq):
    LAB = all_labels()
    deg = defaultdict(int)
    for e in uniq:
        deg[e["source"]] += 1; deg[e["target"]] += 1
    lines = ["# JARVIS graf hisoboti (tools/build_graph.py)", "",
             "Qoidа: avval `graphify query \"...\"`, keyin faqat `source_file:source_location` dagi satrlarni o'qing. Butun HTML ni o'qimang.", "",
             f"- Tugunlar: {len(nodes)} · Qirralar: {len(uniq)} · Jamoalar: {len(cids)}", "", "## Jamoalar"]
    by_c = defaultdict(list)
    for n in nodes.values():
        by_c[n["community_name"]].append(n)
    for cname, ns in by_c.items():
        lines.append(f"- **{cname}** ({len(ns)}): " + ", ".join(sorted({n['label'] for n in ns if n['node_kind'] in ('calculator', 'skill', 'standard_table', 'library', 'concept', 'script', 'reference', 'tool')})[:14]))
    lines += ["", "## Eng bog'langan tugunlar (hub)"]
    for nid, d in sorted(deg.items(), key=lambda x: -x[1])[:12]:
        n = LAB.get(nid)
        if n:
            lines.append(f"- `{nid}` — {n['label']} ({d} qirra) → {n['source_file']}:{n['source_location']}")
    lines += ["", "## Kalkulyator → standart jadval → 3D misol xaritasi"]
    for a, b, rel, note in LINKS:
        lines.append(f"- `{resolve(a)}` —{rel}→ `{resolve(b)}`: {note}")
    lines += ["", "## Kalkulyatorlar (kiritma / jadval / funksiya)"]
    for n in nodes.values():
        if n["node_kind"] == "calculator":
            kids = [e["target"] for e in uniq if e["source"] == n["id"] and e["relation"] == "contains"]
            ins = [nodes[k]["label"].split(" — ")[0] for k in kids if nodes[k]["node_kind"] == "input"]
            tabs = [nodes[k]["label"].replace(" jadvali", "") + f"@{nodes[k]['source_location']}" for k in kids if nodes[k]["node_kind"] == "data_table"]
            fns = [nodes[k]["label"] for k in kids if nodes[k]["node_kind"] == "function"]
            lines.append(f"- **{n['source_file']}** — {n['label']}\n  - kiritmalar: {', '.join(ins) or '—'}\n  - jadvallar: {', '.join(tabs) or '—'}\n  - funksiyalar: {', '.join(fns) or '—'}")
    lines += ["", "## Murod xaritasi uchun", "- `graphify-out/murod-map.json` — {nodes:[{id,label,kind,group,file,line}], edges:[{from,to,rel}]}",
              "- `graphify-out/murod-map.mmd` — Mermaid; har qanday graf vositasiga import qilish mumkin."]
    (OUT / "JARVIS_GRAPH_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_murod_map(uniq):
    LAB = all_labels()
    used = {e["source"] for e in uniq} | {e["target"] for e in uniq}
    extra = [LAB[i] for i in used if i not in nodes and i in LAB]
    mm = {"schema": "murod-map/1", "source": "jarvis-calculators", "builder": "tools/build_graph.py",
          "nodes": [{"id": n["id"], "label": n["label"], "kind": n.get("node_kind") or "symbol", "group": n.get("community_name", ""), "file": n.get("source_file", ""), "line": n.get("source_location", "")} for n in list(nodes.values()) + extra],
          "edges": [{"from": e["source"], "to": e["target"], "rel": e["relation"], **({"note": e["note"]} if e.get("note") else {})} for e in uniq]}
    (OUT / "murod-map.json").write_text(json.dumps(mm, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # Mermaid: faqat yuqori daraja (kalkulyator, jadval, skill, misol, kutubxona, tushuncha) — o'qiladigan bo'lsin
    top_kinds = {"calculator", "standard_table", "skill", "script", "library", "concept", "reference", "tool", "artifact"}
    pool = list(nodes.values()) + extra
    ids = {n["id"]: f"n{i}" for i, n in enumerate(pool) if (n.get("node_kind") or "symbol") in top_kinds or n in extra}
    out = ["graph LR"]
    for n in pool:
        if n["id"] in ids:
            lab = n["label"].replace('"', "'")[:40]
            out.append(f'  {ids[n["id"]]}["{lab}"]')
    for e in uniq:
        if e["source"] in ids and e["target"] in ids and e["relation"] != "contains":
            out.append(f'  {ids[e["source"]]} -->|{e["relation"]}| {ids[e["target"]]}')
    (OUT / "murod-map.mmd").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    load_ast_index()
    scan_html()
    scan_skills()
    manual_links()
    merge_and_write(no_html="--no-html" in sys.argv)
