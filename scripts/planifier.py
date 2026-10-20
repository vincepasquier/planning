#!/usr/bin/env python3
"""Calcule les dates de debut et de fin de chaque tache.

Usage: python3 -I planifier.py [--debut AAAA-MM-JJ] [--csv sortie.csv]

Passe avant (early start / early finish) sur le reseau de taches, en semaines
pleines, a partir d'une date de demarrage. Les taches portant une date_connue
sont ancrees a cette date. Les resultats sont des DATES AU PLUS TOT : une tache
peut toujours etre decalee tant qu'elle ne retarde pas ses successeurs.

Les durees sont des propositions a faire valider par les entreprises.
"""
import argparse
import csv
import json
import sys
from datetime import date, timedelta


def lundi(d):
    """Ramene une date au lundi de sa semaine."""
    return d - timedelta(days=d.weekday())


def charger(path):
    data = json.load(open(path, encoding="utf-8"))
    return {t["id"]: t for t in data["taches"]}, data


def ordonner(taches):
    """Tri topologique ; leve une erreur en cas de cycle."""
    restant = {i: {p["id"] for p in t["predecesseurs"]} for i, t in taches.items()}
    ordre = []
    while restant:
        pret = [i for i, deps in restant.items() if not (deps - set(ordre))]
        if not pret:
            raise SystemExit("CYCLE: " + ", ".join(sorted(restant)))
        for i in sorted(pret):
            ordre.append(i)
            del restant[i]
    return ordre


def planifier(taches, debut):
    """Passe avant. Retourne {id: (date_debut, date_fin)}."""
    dates = {}
    for tid in ordonner(taches):
        t = taches[tid]
        d0 = debut
        for p in t["predecesseurs"]:
            pd, pf = dates[p["id"]]
            # Fin-Debut : on demarre la semaine suivant la fin du predecesseur.
            # Debut-Debut : on demarre au plus tot en meme temps que lui.
            d0 = max(d0, pf + timedelta(days=3) if p["lien"] == "FD" else pd)
        if t.get("date_connue"):
            a, m, j = map(int, t["date_connue"].split("-"))
            fixe = date(a, m, j)
            # Une date ferme ancre la FIN de la tache.
            semaines = t.get("duree_semaines") or 1
            d0 = lundi(fixe) - timedelta(weeks=semaines - 1)
        d0 = lundi(d0)
        semaines = t.get("duree_semaines") or 1
        fin = d0 + timedelta(weeks=semaines) - timedelta(days=3)  # vendredi
        dates[tid] = (d0, fin)
    return dates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taches", default="data/taches.json")
    ap.add_argument("--debut", default=date.today().isoformat(),
                    help="date de demarrage du planning (AAAA-MM-JJ)")
    ap.add_argument("--csv", help="exporte le resultat en CSV")
    ap.add_argument("--par", choices=["date", "lot", "local"], default="date")
    args = ap.parse_args()

    taches, _ = charger(args.taches)
    a, m, j = map(int, args.debut.split("-"))
    dates = planifier(taches, date(a, m, j))

    lignes = []
    for tid, (d0, f) in dates.items():
        t = taches[tid]
        for local in (t["locaux"] or ["*"]):
            lignes.append({
                "lot": t["entreprise"], "local": local, "tache": t["designation"],
                "id": tid, "debut": d0.isoformat(), "fin": f.isoformat(),
                "semaines": t.get("duree_semaines"), "phase": t["phase"],
                "statut": t["statut"],
            })

    cles = {"date": lambda r: (r["debut"], r["lot"]),
            "lot": lambda r: (r["lot"], r["debut"]),
            "local": lambda r: (r["local"], r["debut"])}
    lignes.sort(key=cles[args.par])

    fin_projet = max(f for _, f in dates.values())
    print(f"Demarrage {args.debut}  ->  fin au plus tot {fin_projet.isoformat()}  "
          f"({len(taches)} taches)\n")
    print(f"{'LOT':<14}{'LOCAL':<16}{'DEBUT':<12}{'FIN':<12}{'SEM':>4}  TACHE")
    print("-" * 118)
    vus = set()
    for r in lignes:
        if r["id"] in vus and args.par == "date":
            continue
        vus.add(r["id"])
        loc = r["local"] if r["local"] != "*" else "(tous)"
        alerte = " [!]" if r["statut"] in ("BLOQUE", "non_adjuge", "HORS_PERIMETRE_CONNU") else ""
        print(f"{r['lot']:<14}{loc:<16}{r['debut']:<12}{r['fin']:<12}{r['semaines']:>4}  "
              f"{r['tache'][:46]}{alerte}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(lignes[0]), delimiter=";")
            w.writeheader()
            w.writerows(lignes)
        print(f"\n{len(lignes)} lignes (lot x local) exportees vers {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
