#!/usr/bin/env python3
"""Standart o'lchamlar bazasi (data/standard_sizes.json) bilan ishlash.

CLI:
  standard_sizes.py list                       # jadvallar ro'yxati
  standard_sizes.py show <table>               # jadvalni chiqarish
  standard_sizes.py nearest <table> <col> <v>  # eng yaqin standart qator (masalan: nearest steel_pipe_en10220 OD 60)
  standard_sizes.py find <table> <col> <v>     # aniq moslik
  standard_sizes.py json <table>               # jadvalni JSON ko'rinishda (boshqa skriptlar uchun)
  standard_sizes.py md                         # butun bazani Markdown (references/standard-sizes.md ni yangilash)

Python:
  from standard_sizes import load, nearest, find
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "standard_sizes.json"


def load() -> dict:
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def _tables(db: dict):
    return {k: v for k, v in db.items() if not k.startswith("_")}


def rows_as_dicts(table: dict):
    cols = table.get("columns")
    if cols:
        return [dict(zip(cols, r)) for r in table.get("rows", [])]
    if "values" in table:
        return [{"value": v} for v in table["values"]]
    return []


def find(table_name: str, col: str, value, db: dict | None = None):
    db = db or load()
    t = db[table_name]
    for r in rows_as_dicts(t):
        if str(r.get(col)).lower() == str(value).lower():
            return r
    return None


def nearest(table_name: str, col: str, value: float, db: dict | None = None, prefer: str = "any"):
    """Eng yaqin qator. prefer: 'any' | 'up' (kattaroq yoki teng) | 'down' (kichikroq yoki teng)."""
    db = db or load()
    t = db[table_name]
    best, best_d = None, None
    for r in rows_as_dicts(t):
        v = r.get(col, r.get("value"))
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if prefer == "up" and v < value:
            continue
        if prefer == "down" and v > value:
            continue
        d = abs(v - value)
        if best_d is None or d < best_d:
            best, best_d = r, d
    return best


def to_markdown(db: dict) -> str:
    out = ["# Standart o'lchamlar bazasi", "",
           f"Manba fayl: `data/standard_sizes.json` (bu fayl `standard_sizes.py md` bilan avtomatik hosil qilinadi — qo'lda tahrirlamang).",
           "", db["_meta"]["note"], "", "Qidiruv: `standard_sizes.py nearest <jadval> <ustun> <qiymat> [up|down]`, `find`, `show`.", ""]
    for name, t in _tables(db).items():
        out.append(f"## {name} — {t.get('title', '')}" + (" *(taxminiy)*" if t.get("approx") else ""))
        out.append("")
        if "columns" in t:
            cols = t["columns"]
            out.append("| " + " | ".join(str(c) for c in cols) + " |")
            out.append("|" + "---|" * len(cols))
            for r in t.get("rows", []):
                out.append("| " + " | ".join(str(c) for c in r) + " |")
        if "values" in t:
            out.append("`" + ", ".join(str(v) for v in t["values"]) + "`")
        for k in ("heights", "lengths"):
            if k in t:
                out.append(f"- {k}: `{', '.join(str(v) for v in t[k])}`")
        for k in ("rules", "connection", "mounting"):
            if k in t:
                for kk, vv in t[k].items():
                    out.append(f"- {k}.{kk}: {vv}")
        for k in ("note", "see_also"):
            if k in t:
                out.append(f"- {k}: {t[k]}")
        out.append("")
    return "\n".join(out)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    db = load()
    cmd = argv[1]
    if cmd == "md":
        print(to_markdown(db))
        return 0
    if cmd == "list":
        for k, v in _tables(db).items():
            flag = " (approx)" if v.get("approx") else ""
            print(f"{k:28s} {v.get('title','')}{flag}")
        return 0
    name = argv[2]
    if name not in db:
        print(f"Jadval topilmadi: {name}. 'list' bilan ko'ring.", file=sys.stderr)
        return 2
    t = db[name]
    if cmd == "show":
        print(t.get("title", name), "(taxminiy)" if t.get("approx") else "")
        for k in ("columns",):
            if k in t:
                print("  ", " | ".join(str(c) for c in t[k]))
        for r in t.get("rows", []):
            print("  ", " | ".join(str(c) for c in r))
        if "values" in t:
            print("  ", t["values"])
        for k in ("rules", "connection", "mounting", "heights", "lengths", "note", "see_also"):
            if k in t:
                print(f"  {k}: {t[k]}")
        return 0
    if cmd == "json":
        print(json.dumps(t, ensure_ascii=False, indent=1))
        return 0
    if cmd in ("nearest", "find"):
        col, val = argv[3], argv[4]
        if cmd == "find":
            r = find(name, col, val, db)
        else:
            prefer = argv[5] if len(argv) > 5 else "any"
            r = nearest(name, col, float(val), db, prefer)
        print(json.dumps(r, ensure_ascii=False) if r else "null")
        return 0 if r else 1
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
