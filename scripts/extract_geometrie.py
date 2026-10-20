#!/usr/bin/env python3
"""Extrait l'emprise au sol de chaque local d'un fichier IFC, par niveau.

Usage: python3 -I extract_geometrie.py <fichier.ifc> [sortie.json]

Resout la chaine de placement (IfcLocalPlacement) et le profil extrude
(IfcExtrudedAreaSolid -> IfcArbitraryClosedProfileDef) pour produire, pour
chaque IfcSpace, un polygone en coordonnees du projet, en metres.

Hypothese : batiment d'axe Z vertical. Les locaux dont la geometrie n'est pas
un profil extrude sont signales et ignores.
"""
import json
import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from extract_locaux import decode_step, number, parse, refs, text  # noqa: E402


def matrice(ent, pid, cache):
    """Transformation 2D cumulee d'un IfcLocalPlacement : (cos, sin, tx, ty)."""
    if pid in cache:
        return cache[pid]
    typ, args = ent.get(pid, (None, None))
    if typ != "IFCLOCALPLACEMENT":
        return (1.0, 0.0, 0.0, 0.0)
    parent = refs(args[0])
    base = matrice(ent, parent[0], cache) if parent else (1.0, 0.0, 0.0, 0.0)
    local = axe2(ent, (refs(args[1]) or [None])[0])
    cache[pid] = composer(base, local)
    return cache[pid]


def axe2(ent, aid):
    """IfcAxis2Placement3D -> (cos, sin, tx, ty) dans le plan XY."""
    if not aid:
        return (1.0, 0.0, 0.0, 0.0)
    typ, args = ent.get(aid, (None, None))
    if typ not in ("IFCAXIS2PLACEMENT3D", "IFCAXIS2PLACEMENT2D"):
        return (1.0, 0.0, 0.0, 0.0)
    tx, ty = 0.0, 0.0
    loc = refs(args[0])
    if loc:
        coords = coordonnees(ent, loc[0])
        if coords:
            tx, ty = coords[0], coords[1] if len(coords) > 1 else 0.0
    c, s = 1.0, 0.0
    # Axis2Placement3D : arg 1 = Axis (Z), arg 2 = RefDirection (X).
    # Axis2Placement2D : arg 1 = RefDirection.
    idx = 2 if typ == "IFCAXIS2PLACEMENT3D" else 1
    if len(args) > idx:
        d = refs(args[idx])
        if d:
            v = coordonnees(ent, d[0])
            if v and (v[0] or (len(v) > 1 and v[1])):
                n = math.hypot(v[0], v[1] if len(v) > 1 else 0.0)
                if n:
                    c, s = v[0] / n, (v[1] if len(v) > 1 else 0.0) / n
    return (c, s, tx, ty)


def coordonnees(ent, pid):
    typ, args = ent.get(pid, (None, None))
    if typ not in ("IFCCARTESIANPOINT", "IFCDIRECTION") or not args:
        return None
    inner = args[0].strip().lstrip("(").rstrip(")")
    vals = [number(v) for v in inner.split(",")]
    return [v for v in vals if v is not None]


def composer(a, b):
    """Compose deux transformations 2D : a appliquee apres b."""
    ca, sa, xa, ya = a
    cb, sb, xb, yb = b
    return (ca * cb - sa * sb, sa * cb + ca * sb,
            xa + ca * xb - sa * yb, ya + sa * xb + ca * yb)


def appliquer(m, x, y):
    c, s, tx, ty = m
    return (c * x - s * y + tx, s * x + c * y + ty)


def profil(ent, pid):
    """IfcArbitraryClosedProfileDef -> liste de points 2D, dans l'ordre."""
    typ, args = ent.get(pid, (None, None))
    if typ != "IFCARBITRARYCLOSEDPROFILEDEF":
        return None
    courbe = refs(args[2]) if len(args) > 2 else []
    if not courbe:
        return None
    ctyp, cargs = ent.get(courbe[0], (None, None))
    if ctyp == "IFCPOLYLINE":
        pts = [coordonnees(ent, p) for p in refs(cargs[0])]
        return [(p[0], p[1]) for p in pts if p and len(p) >= 2]
    if ctyp != "IFCINDEXEDPOLYCURVE":
        return None
    liste = refs(cargs[0])
    if not liste:
        return None
    ltyp, largs = ent.get(liste[0], (None, None))
    if ltyp != "IFCCARTESIANPOINTLIST2D":
        return None
    bruts = largs[0].strip()
    pts = [tuple(float(v) for v in couple.split(","))
           for couple in __import__("re").findall(r"\(([^()]+)\)", bruts)]
    # Suivre l'ordre des segments plutot que l'ordre de la liste
    indices = [int(i) for i in __import__("re").findall(
        r"IFCLINEINDEX\(\(([0-9]+),", cargs[1])] if len(cargs) > 1 else []
    if indices:
        suite = [pts[i - 1] for i in indices if 0 < i <= len(pts)]
        if len(suite) >= 3:
            return suite
    return pts if len(pts) >= 3 else None


def axe_dominant(niveaux):
    """Orientation dominante des murs, modulo 90 degres, ponderee par les longueurs.

    Les aretes sont regroupees par tranche d'un demi-degre ; la tranche qui
    totalise le plus de metres donne l'axe du batiment.
    """
    poids = {}
    for locs in niveaux.values():
        for loc in locs:
            p = loc["polygone"]
            for i in range(len(p)):
                (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
                dx, dy = x1 - x0, y1 - y0
                long = math.hypot(dx, dy)
                if long < 0.5:
                    continue
                a = math.degrees(math.atan2(dy, dx)) % 90.0
                poids[round(a * 2) / 2] = poids.get(round(a * 2) / 2, 0.0) + long
    if not poids:
        return 0.0
    a = max(poids.items(), key=lambda kv: kv[1])[0]
    return math.radians(a - 90 if a > 45 else a)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    ent = parse(src)

    echelle = 1.0
    for typ, args in ent.values():
        if typ == "IFCSIUNIT" and len(args) >= 3 and "LENGTHUNIT" in args[1]:
            echelle = {"MILLI": .001, "CENTI": .01, "DECI": .1}.get(args[2].strip("."), 1.0)
            break

    etage = {}
    for typ, args in ent.values():
        if typ == "IFCRELAGGREGATES" and len(args) >= 6:
            p = refs(args[4])
            if p and ent.get(p[0], ("",))[0] == "IFCBUILDINGSTOREY":
                nom = text(ent[p[0]][1][2]) or p[0]
                for c in refs(args[5]):
                    etage[c] = nom

    cache, niveaux, ignores = {}, {}, []
    for eid, (typ, args) in ent.items():
        if typ != "IFCSPACE" or len(args) < 8:
            continue
        if text(args[4]) != "Pièces individuelles":
            continue
        numero, designation = text(args[2]), text(args[3])
        rep = refs(args[6]) if len(args) > 6 else []
        pts = None
        if rep:
            _, pargs = ent.get(rep[0], (None, [""] * 3))
            for sr in refs(pargs[2] if len(pargs) > 2 else ""):
                styp, sargs = ent.get(sr, (None, None))
                if styp != "IFCSHAPEREPRESENTATION" or text(sargs[2]) != "SweptSolid":
                    continue
                for item in refs(sargs[3]):
                    ityp, iargs = ent.get(item, (None, None))
                    if ityp != "IFCEXTRUDEDAREASOLID":
                        continue
                    brut = profil(ent, (refs(iargs[0]) or [None])[0])
                    if not brut:
                        continue
                    m = composer(matrice(ent, (refs(args[5]) or [None])[0], cache),
                                 axe2(ent, (refs(iargs[1]) or [None])[0]))
                    pts = [appliquer(m, x, y) for x, y in brut]
                    break
                if pts:
                    break
        if not pts:
            ignores.append(numero)
            continue
        niv = etage.get(eid, "?")
        niveaux.setdefault(niv, []).append({
            "numero": numero, "designation": designation,
            "polygone": [[round(x * echelle, 3), round(y * echelle, 3)] for x, y in pts],
        })

    # Les coordonnees IFC sont celles du site : le batiment y arrive en biais.
    # On le redresse sur son axe dominant pour retrouver la lecture des plans.
    angle = axe_dominant(niveaux)
    if angle:
        ca, sa = math.cos(-angle), math.sin(-angle)
        for locs in niveaux.values():
            for loc in locs:
                loc["polygone"] = [[x * ca - y * sa, x * sa + y * ca] for x, y in loc["polygone"]]

    sortie = {"unite": "m", "source": src.rsplit("/", 1)[-1],
              "redressement_deg": round(math.degrees(angle), 2), "niveaux": {}}
    for niv, locs in sorted(niveaux.items()):
        xs = [p[0] for l in locs for p in l["polygone"]]
        ys = [p[1] for l in locs for p in l["polygone"]]
        sortie["niveaux"][niv] = {
            "bbox": [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)],
            "locaux": sorted(locs, key=lambda l: l["numero"] or ""),
        }

    blob = json.dumps(sortie, ensure_ascii=False, separators=(",", ":"))
    total = sum(len(v["locaux"]) for v in sortie["niveaux"].values())
    if dst:
        open(dst, "w", encoding="utf-8").write(blob + "\n")
        print(f"{total} locaux sur {len(sortie['niveaux'])} niveaux -> {dst}"
              + (f"  (ignores : {', '.join(filter(None, ignores))})" if ignores else ""))
    else:
        print(blob)


if __name__ == "__main__":
    main()
