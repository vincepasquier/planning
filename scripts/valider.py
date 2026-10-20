#!/usr/bin/env python3
"""Valide le reseau de taches et calcule l'ordonnancement par rangs.

Usage: python3 -I valider.py [data/taches.json]

Verifie les references, detecte les cycles, puis affiche les taches
groupees par rang topologique : le rang 0 peut demarrer tout de suite,
le rang N attend la fin du rang N-1. Sans durees, le rang est la
reponse a "qui avant qui".
"""
import json
import sys
from collections import defaultdict


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/taches.json"
    taches = json.load(open(path, encoding="utf-8"))["taches"]
    par_id = {t["id"]: t for t in taches}

    # References
    casse = [(t["id"], p["id"]) for t in taches
             for p in t["predecesseurs"] if p["id"] not in par_id]
    if casse:
        print("REFERENCES CASSEES:")
        for a, b in casse:
            print(f"  {a} -> {b} (inexistant)")
        return 1

    # Rangs par parcours en largeur sur les predecesseurs
    restant = {t["id"]: {p["id"] for p in t["predecesseurs"]} for t in taches}
    rang = {}
    niveau = 0
    while restant:
        pret = [i for i, deps in restant.items() if not (deps - set(rang))]
        if not pret:
            print("CYCLE DETECTE entre:", ", ".join(sorted(restant)))
            return 1
        for i in pret:
            rang[i] = niveau
            del restant[i]
        niveau += 1

    # Successeurs, pour reperer les taches les plus contraignantes
    succ = defaultdict(list)
    for t in taches:
        for p in t["predecesseurs"]:
            succ[p["id"]].append(t["id"])

    groupes = defaultdict(list)
    for i, n in rang.items():
        groupes[n].append(i)

    print(f"{len(taches)} taches, {sum(len(t['predecesseurs']) for t in taches)} liens, "
          f"{niveau} rangs, aucun cycle\n")
    for n in sorted(groupes):
        print(f"--- RANG {n} " + "-" * 56)
        for i in sorted(groupes[n]):
            t = par_id[i]
            alerte = "  [!]" if t["statut"] in ("BLOQUE", "non_adjuge") else ""
            date = f"  <{t['date_connue']}>" if t.get("date_connue") else ""
            print(f"  {i:<12} {t['entreprise']:<14} {t['designation'][:46]:<47}{date}{alerte}")
    print()

    verrous = sorted(succ.items(), key=lambda kv: -len(kv[1]))[:5]
    print("Taches les plus contraignantes (nombre de successeurs directs):")
    for i, s in verrous:
        print(f"  {len(s):>2}  {i:<12} {par_id[i]['designation'][:56]}")

    bloques = [t for t in taches if t["statut"] in ("BLOQUE", "non_adjuge")]
    if bloques:
        print(f"\n{len(bloques)} tache(s) sur lot non adjuge:")
        for t in bloques:
            print(f"  {t['id']:<12} {t['entreprise']:<14} {t['designation'][:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
