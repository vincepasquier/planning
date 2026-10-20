#!/usr/bin/env python3
"""Genere l'application HTML de visualisation du planning.

Usage: python3 -I export_html.py [--debut AAAA-MM-JJ] [--sortie fichier.html]

Page autonome : les donnees du depot sont embarquees dans le fichier, qui
s'ouvre sans serveur. A regenerer apres chaque modification des durees ou du
reseau de taches.
"""
import argparse
import json
import sys
from datetime import date

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from planifier import charger, marges, planifier  # noqa: E402

GABARIT = __file__.rsplit("/", 1)[0] + "/gabarit_planning.html"


def demarrage_defaut():
    """Date de démarrage du chantier, lue dans les données du projet."""
    try:
        import json as _j
        return _j.load(open("data/entreprises.json", encoding="utf-8"))["projet"]["demarrage_chantier"]
    except Exception:
        return date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taches", default="data/taches.json")
    ap.add_argument("--debut", default=demarrage_defaut())
    ap.add_argument("--sortie", default="data/extracted/planning.html")
    args = ap.parse_args()

    taches, _ = charger(args.taches)
    a, m, j = map(int, args.debut.split("-"))
    dates = planifier(taches, date(a, m, j))
    fin = max(f for _, f in dates.values())
    mg = marges(taches, dates, fin)

    phases = json.load(open("data/phases.json", encoding="utf-8"))["phases"]
    entreprises = json.load(open("data/entreprises.json", encoding="utf-8"))
    questions = json.load(open("data/questions-ouvertes.json", encoding="utf-8"))["questions"]
    geometrie = json.load(open("data/extracted/geometrie.json", encoding="utf-8"))
    fiches = json.load(open("data/locaux-contenu.json", encoding="utf-8"))["fiches"]
    hors_marche = sorted(f["numero"] for f in fiches if f["statut_fiche"] == "hors_marche")
    intensites = json.load(open("data/intensites.json", encoding="utf-8"))["locaux"]
    par_local = {f["numero"]: {"statut": f["statut_fiche"], "famille": f["famille_titre"],
                               "reponse": f["reponse"]} for f in fiches}
    locaux = {x["numero"]: x for x in
              json.load(open("data/extracted/locaux.json", encoding="utf-8"))["locaux"]
              if x["est_local"]}

    successeurs = {}
    for tid, t in taches.items():
        for p in t["predecesseurs"]:
            successeurs.setdefault(p["id"], []).append({"id": tid, "lien": p["lien"]})

    sortie_taches = []
    for tid, t in taches.items():
        d0, f0 = dates[tid]
        sortie_taches.append({
            "id": tid, "nom": t["designation"], "lot": t["entreprise"],
            "systeme": t["systeme"], "phase": t["phase"],
            "locaux": t["locaux"], "debut": d0.isoformat(), "fin": f0.isoformat(),
            "semaines": t.get("duree_semaines"), "statut": t["statut"],
            "dateFerme": t.get("date_connue"), "notes": t.get("notes"),
            "critique": mg[tid][1] <= 0, "margeJours": mg[tid][1],
            "pred": t["predecesseurs"], "succ": successeurs.get(tid, []),
        })
    sortie_taches.sort(key=lambda x: (x["debut"], x["lot"]))

    donnees = {
        "projet": entreprises["projet"],
        "debut": args.debut,
        "fin": max(f for _, f in dates.values()).isoformat(),
        "phases": phases,
        "taches": sortie_taches,
        "lots": entreprises["entreprises"],
        "questions": questions,
        "geometrie": geometrie,
        "horsMarche": hors_marche,
        "fiches": par_local,
        "intensites": intensites,
        "locaux": {k: {"designation": v["designation"], "niveau": v["niveau"],
                       "surface": v.get("surface_nette_m2"),
                       "hauteur": v.get("hauteur_sous_plafond_m")}
                   for k, v in locaux.items()},
    }

    html = open(GABARIT, encoding="utf-8").read()
    html = html.replace("/*__DONNEES__*/null",
                        json.dumps(donnees, ensure_ascii=False, separators=(",", ":")))
    open(args.sortie, "w", encoding="utf-8").write(html)
    ko = len(html.encode()) / 1024
    print(f"{len(sortie_taches)} taches, {len(questions)} questions -> {args.sortie} ({ko:.0f} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
