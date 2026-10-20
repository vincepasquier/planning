#!/usr/bin/env python3
"""Liste les conflits de co-activité : trop d'entreprises dans un local à la fois.

Usage: python3 -I coactivite.py [--debut AAAA-MM-JJ] [--seuil N]

Pour chaque semaine et chaque local, compte les lots présents. Un local dont la
fiche porte « chacun son tour » n'en admet qu'un : tout chevauchement y est un
conflit. Les autres sont signalés au-delà du seuil.
"""
import argparse
import json
import sys
from datetime import date, timedelta

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from planifier import charger, planifier  # noqa: E402


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
    ap.add_argument("--seuil", type=int, default=3)
    args = ap.parse_args()

    taches, _ = charger(args.taches)
    a, m, j = map(int, args.debut.split("-"))
    D0 = date(a, m, j)
    dates = planifier(taches, D0)
    fin = max(f for _, f in dates.values())

    locaux = {x["numero"]: x for x in json.load(open("data/extracted/locaux.json", encoding="utf-8"))["locaux"] if x["est_local"]}
    try:
        intensites = json.load(open("data/intensites.json", encoding="utf-8"))["locaux"]
    except FileNotFoundError:
        intensites = {}
    ponctuel = lambda n, lot: intensites.get(n, {}).get(lot) == "ponctuel"
    fiches = {f["numero"]: f for f in json.load(open("data/locaux-contenu.json", encoding="utf-8"))["fiches"]}
    chacun_son_tour = {n for n, f in fiches.items()
                       if "chacun son tour" in (f.get("reponse", {}).get("co_activite_possible") or "").lower()}
    limites = {}
    try:
        limites = json.load(open("data/intensites.json", encoding="utf-8")).get("limites", {})
    except FileNotFoundError:
        pass

    semaines = (fin - D0).days // 7 + 1
    conflits = {}
    for s in range(semaines):
        d = D0 + timedelta(weeks=s)
        for n in locaux:
            lots = {taches[i]["entreprise"] for i in taches
                    if n in taches[i]["locaux"] and dates[i][0] <= d <= dates[i][1]
                    and not ponctuel(n, taches[i]["entreprise"])}
            # Un local relevé porte sa propre limite ; le conflit commence un lot au-dessus.
            seuil = limites[n] + 1 if n in limites else (2 if n in chacun_son_tour else args.seuil)
            if len(lots) >= seuil:
                c = conflits.setdefault(n, {"semaines": [], "lots": set(), "seuil": seuil})
                c["semaines"].append(d)
                c["lots"] |= lots

    if not conflits:
        print("Aucun conflit de co-activité.")
        return 0
    total = sum(len(c["semaines"]) for c in conflits.values())
    print(f"{len(conflits)} locaux en conflit, {total} semaines-locaux au total "
          f"(seuil {args.seuil}, ou 2 là où l'on passe chacun son tour)\n")
    print(f"{'LOCAL':<14}{'DÉSIGNATION':<26}{'SEM':>4}{'MAX':>5}  PÉRIODE                 LOTS")
    print("-" * 112)
    for n, c in sorted(conflits.items(), key=lambda kv: -len(kv[1]["semaines"])):
        d0, d1 = min(c["semaines"]), max(c["semaines"])
        tag = f" (max {limites[n]})" if n in limites else (" *" if n in chacun_son_tour else "")
        print(f"{n.replace('CENT.',''):<14}{(locaux[n]['designation'] or '')[:25]:<26}"
              f"{len(c['semaines']):>4}{len(c['lots']):>5}  {d0} à {d1}  {', '.join(sorted(c['lots']))}{tag}")
    print("\n* local où le maître d'ouvrage a déclaré qu'on passe chacun son tour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
