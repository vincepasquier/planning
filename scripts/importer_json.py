#!/usr/bin/env python3
"""Réintègre dans le dépôt les modifications faites dans la page.

Usage:
  python3 -I importer_json.py planning-centrale-20133-AAAA-MM-JJ.json
  python3 -I importer_json.py donnees.json          # le fichier de l'artefact
  python3 -I importer_json.py planning.html         # une page enregistrée
  python3 -I importer_json.py FICHIER --essai       # montre les écarts sans rien écrire

Réécrit data/taches.json, entreprises.json, phases.json, intensites.json,
questions-ouvertes.json et les fiches de locaux-contenu.json. Les métadonnées
de ces fichiers (versions, notes de correction) sont conservées.
"""
import argparse
import json
import re
from pathlib import Path


def lire(chemin):
    texte = Path(chemin).read_text(encoding="utf-8")
    if chemin.endswith((".html", ".htm")):
        m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', texte, re.S)
        if not m:
            raise SystemExit("Aucune donnée de planning dans cette page.")
        texte = m.group(1)
    etat = json.loads(texte)
    if "etat" in etat and "base" in etat:          # un brouillon de la page
        etat = etat["etat"]
    if not str(etat.get("schema", "")).startswith("planning-centrale"):
        raise SystemExit("Ce fichier ne vient pas de l'éditeur de planning.")
    return etat


def charger(p):
    return json.load(open(p, encoding="utf-8"))


def ecrire(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ecarts(avant, apres):
    a = {t["id"]: t for t in avant}
    b = {t["id"]: t for t in apres}
    lignes = [f"  + {i}  {b[i]['entreprise']:<16}{b[i]['designation']}" for i in b if i not in a]
    lignes += [f"  - {i}  {a[i]['entreprise']:<16}{a[i]['designation']}" for i in a if i not in b]
    for i in a.keys() & b.keys():
        x, y = a[i], b[i]
        diff = [k for k in ("designation", "entreprise", "duree_semaines", "locaux", "predecesseurs",
                            "date_connue", "debut_au_plus_tot", "phase", "statut", "notes")
                if x.get(k) != y.get(k)]
        if diff:
            detail = ", ".join(f"durée {x.get(k)} -> {y.get(k)} sem." if k == "duree_semaines" else k for k in diff)
            lignes.append(f"  ~ {i}  {y['entreprise']:<16}{detail}")
    return sorted(lignes, key=lambda s: s[4:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier")
    ap.add_argument("--essai", action="store_true", help="afficher les écarts sans rien écrire")
    args = ap.parse_args()
    etat = lire(args.fichier)

    t_doc = charger("data/taches.json")
    e_doc = charger("data/entreprises.json")
    lots_avant = {l["code"] for l in e_doc["entreprises"]}
    lots_apres = {l["code"] for l in etat["lots"]}
    diff = ecarts(t_doc["taches"], etat["taches"])

    print(f"Données du {etat.get('maj', '?')} : {len(etat['taches'])} tâches, {len(etat['lots'])} entreprises")
    for code in sorted(lots_apres - lots_avant):
        print(f"  + entreprise {code}")
    for code in sorted(lots_avant - lots_apres):
        print(f"  - entreprise {code}")
    if e_doc["projet"].get("demarrage_chantier") != etat["projet"].get("demarrage_chantier"):
        print(f"  ~ ouverture du chantier : {e_doc['projet'].get('demarrage_chantier')} -> "
              f"{etat['projet'].get('demarrage_chantier')}")
    print("\n".join(diff) if diff else "  aucune tâche modifiée")
    if args.essai:
        print("\n(essai : rien n'a été écrit)")
        return 0

    anciennes = {t["id"]: t for t in t_doc["taches"]}
    for t in etat["taches"]:
        a = anciennes.get(t["id"], {})
        if "duree_classe" in a:
            t.setdefault("duree_classe", a["duree_classe"])
    t_doc["taches"] = etat["taches"]
    t_doc["importe_depuis_la_page"] = etat.get("maj")
    ecrire("data/taches.json", t_doc)

    e_doc["projet"] = etat["projet"]
    e_doc["entreprises"] = etat["lots"]
    ecrire("data/entreprises.json", e_doc)

    p_doc = charger("data/phases.json")
    p_doc["phases"] = etat["phases"]
    ecrire("data/phases.json", p_doc)

    ecrire("data/intensites.json", etat["intensites"])

    q_doc = charger("data/questions-ouvertes.json")
    q_doc["questions"] = etat["questions"]
    ecrire("data/questions-ouvertes.json", q_doc)

    f_doc = charger("data/locaux-contenu.json")
    for f in f_doc["fiches"]:
        n = etat["fiches"].get(f["numero"])
        if n:
            f["statut_fiche"] = n.get("statut", f["statut_fiche"])
            f["reponse"] = n.get("reponse", f["reponse"])
    ecrire("data/locaux-contenu.json", f_doc)
    print("\nDépôt mis à jour. Relancer valider.py, puis les exports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
