#!/usr/bin/env python3
"""Génère l'éditeur de planning (page HTML autonome) et son fichier de données.

Usage: python3 -I export_html.py [--sortie fichier.html]

Produit deux fichiers :
  data/extracted/planning.html   la page, données embarquées : elle s'ouvre
                                 seule, hors ligne, sans serveur
  data/extracted/donnees.json    les mêmes données, publiées à côté de la page :
                                 c'est ce fichier que la page réécrit quand on
                                 l'enregistre depuis claude.ai

AVANT de régénérer après des modifications faites dans la page publiée,
récupérer donnees.json de l'artefact et l'importer avec importer_json.py :
sinon la page régénérée écrase les modifications.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

GABARIT = Path(__file__).with_name("gabarit_planning.html")
SCHEMA = "planning-centrale/1"
CHAMPS_TACHE = ("id", "designation", "entreprise", "systeme", "phase", "locaux", "duree_semaines",
                "date_connue", "debut_au_plus_tot", "predecesseurs", "statut", "notes")


def charger(chemin):
    return json.load(open(chemin, encoding="utf-8"))


def etat_editable():
    """L'état que la page modifie, exporte et importe."""
    taches = charger("data/taches.json")["taches"]
    entreprises = charger("data/entreprises.json")
    fiches = charger("data/locaux-contenu.json")["fiches"]
    intensites = charger("data/intensites.json")
    return {
        "schema": SCHEMA,
        "maj": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "projet": entreprises["projet"],
        "phases": charger("data/phases.json")["phases"],
        "lots": entreprises["entreprises"],
        "taches": [{k: t.get(k) for k in CHAMPS_TACHE} for t in taches],
        "fiches": {f["numero"]: {"statut": f["statut_fiche"], "famille": f["famille_titre"],
                                 "reponse": f["reponse"]} for f in fiches},
        "intensites": intensites,
        "questions": charger("data/questions-ouvertes.json")["questions"],
    }


def donnees_statiques():
    """Ce que la page affiche sans jamais le modifier : la géométrie et les locaux."""
    locaux = {x["numero"]: x for x in charger("data/extracted/locaux.json")["locaux"] if x["est_local"]}
    return {
        "geometrie": charger("data/extracted/geometrie.json"),
        "locaux": {k: {"designation": v["designation"], "niveau": v["niveau"],
                       "surface": v.get("surface_nette_m2"), "hauteur": v.get("hauteur_sous_plafond_m")}
                   for k, v in locaux.items()},
    }


def dans_script(obj):
    """JSON sûr à l'intérieur d'une balise script : aucun « </ » ne doit y figurer."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default="data/extracted/planning.html")
    args = ap.parse_args()

    etat = etat_editable()
    html = GABARIT.read_text(encoding="utf-8")
    for jeton, valeur in (("__STATIQUE__", dans_script(donnees_statiques())),
                          ("__DONNEES__", dans_script(etat))):
        assert html.count(jeton) == 1, jeton
        html = html.replace(jeton, valeur)
    Path(args.sortie).write_text(html, encoding="utf-8")
    Path(args.sortie).with_name("donnees.json").write_text(
        json.dumps(etat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(etat['taches'])} tâches, {len(etat['lots'])} entreprises -> {args.sortie} "
          f"({len(html.encode()) / 1024:.0f} Ko) + donnees.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
