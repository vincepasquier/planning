#!/usr/bin/env python3
"""Extrait la liste des locaux (IfcSpace) d'un fichier IFC vers du JSON.

Usage: python3 -I extract_locaux.py <fichier.ifc> [sortie.json]

Lit les IfcSpace, leur rattachement a un IfcBuildingStorey et leurs
quantites Qto_SpaceBaseQuantities (surface nette, hauteur sous plafond).
Aucune dependance externe : le fichier IFC est du texte STEP (ISO-10303-21).
"""
import json
import re
import sys


def decode_step(s):
    """Decode les echappements ISO-10303-21 (\\X\\HH et \\X2\\....\\X0\\)."""
    def utf16(m):
        return bytes.fromhex(m.group(1)).decode("utf-16-be", "replace")
    s = re.sub(r"\\X2\\((?:[0-9A-Fa-f]{4})+)\\X0\\", utf16, s)
    s = re.sub(r"\\X\\([0-9A-Fa-f]{2})",
               lambda m: bytes.fromhex(m.group(1)).decode("latin-1"), s)
    return s.replace("\\\\", "\\").replace("''", "'")


def split_args(body):
    """Decoupe les arguments d'une entite STEP en respectant () et ''."""
    out, depth, cur, in_str = [], 0, [], False
    i = 0
    while i < len(body):
        c = body[i]
        if in_str:
            if c == "'":
                if i + 1 < len(body) and body[i + 1] == "'":
                    cur.append("''")
                    i += 2
                    continue
                in_str = False
            cur.append(c)
        elif c == "'":
            in_str = True
            cur.append(c)
        elif c == "(":
            depth += 1
            cur.append(c)
        elif c == ")":
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    return out


def text(arg):
    """Valeur texte d'un argument STEP, ou None."""
    arg = arg.strip()
    if arg.startswith("'") and arg.endswith("'") and len(arg) >= 2:
        return decode_step(arg[1:-1])
    return None


def number(arg):
    try:
        return float(arg.strip().rstrip("."))
    except ValueError:
        return None


def refs(arg):
    return re.findall(r"#(\d+)", arg)


def parse(path):
    """Retourne {id: (TYPE, [args])} pour la section DATA."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    if "DATA;" in raw:
        raw = raw.split("DATA;", 1)[1]
    entities = {}
    pattern = re.compile(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*?)\)\s*;", re.S)
    for m in pattern.finditer(raw):
        entities[m.group(1)] = (m.group(2), split_args(m.group(3)))
    return entities


# Quantites retenues et nom lisible
WANTED = {
    "NetFloorArea": "surface_nette_m2",
    "GrossFloorArea": "surface_brute_m2",
    "FinishCeilingHeight": "hauteur_sous_plafond_m",
    "NetPerimeter": "perimetre_net_m",
    "NetVolume": "volume_net_m3",
}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    ent = parse(src)

    # Facteur d'echelle des longueurs -> metres (IFCSIUNIT LENGTHUNIT)
    scale = 1.0
    for typ, args in ent.values():
        if typ == "IFCSIUNIT" and len(args) >= 3 and "LENGTHUNIT" in args[1]:
            prefix = args[2].strip(".")
            scale = {"MILLI": 0.001, "CENTI": 0.01, "DECI": 0.1}.get(prefix, 1.0)
            break

    # Etage de rattachement de chaque espace (IfcRelAggregates)
    storey_of = {}
    for typ, args in ent.values():
        if typ == "IFCRELAGGREGATES" and len(args) >= 6:
            parent = refs(args[4])
            if parent and ent.get(parent[0], ("",))[0] == "IFCBUILDINGSTOREY":
                label = text(ent[parent[0]][1][2]) or parent[0]
                for child in refs(args[5]):
                    storey_of[child] = label

    # Quantites par espace (IfcRelDefinesByProperties -> IfcElementQuantity)
    quantities = {}
    for typ, args in ent.values():
        if typ != "IFCRELDEFINESBYPROPERTIES" or len(args) < 6:
            continue
        qset = refs(args[5])
        if not qset or ent.get(qset[0], ("",))[0] != "IFCELEMENTQUANTITY":
            continue
        qargs = ent[qset[0]][1]
        values = {}
        for qid in refs(qargs[5] if len(qargs) > 5 else ""):
            qtyp, qa = ent.get(qid, (None, None))
            if not qtyp or not qa:
                continue
            key = WANTED.get(text(qa[0]) or "")
            if not key:
                continue
            val = number(qa[3]) if len(qa) > 3 else None
            if val is None:
                continue
            if qtyp == "IFCQUANTITYLENGTH":
                val *= scale
            values[key] = round(val, 3)
        if values:
            for target in refs(args[4]):
                quantities.setdefault(target, {}).update(values)

    locaux = []
    for eid, (typ, args) in ent.items():
        if typ != "IFCSPACE":
            continue
        kind = text(args[4]) if len(args) > 4 else None
        entry = {
            "ifc_id": "#" + eid,
            "guid": text(args[0]),
            "numero": text(args[2]),
            "designation": text(args[3]),
            "niveau": storey_of.get(eid),
            # Code de categorie de surface, type SIA 416 (SU, SD, SP, VB...) - a confirmer
            "code_surface": text(args[7]) if len(args) > 7 else None,
            "granularite": kind,
            "est_local": kind == "Pièces individuelles",
        }
        entry.update(quantities.get(eid, {}))
        locaux.append(entry)

    locaux.sort(key=lambda r: (r["niveau"] or "", r["numero"] or ""))
    out = {
        "source": src.rsplit("/", 1)[-1],
        "nb_espaces": len(locaux),
        "nb_locaux_reels": sum(1 for r in locaux if r["est_local"]),
        "locaux": locaux,
    }
    blob = json.dumps(out, ensure_ascii=False, indent=2)
    if dst:
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(blob + "\n")
        print(f"{out['nb_locaux_reels']} locaux reels / {len(locaux)} espaces -> {dst}")
    else:
        print(blob)


if __name__ == "__main__":
    main()
