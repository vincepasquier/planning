#!/usr/bin/env python3
"""Exporte le reseau de taches au format MS Project (MSPDI XML).

Usage: python3 -I export_msproject.py [--debut AAAA-MM-JJ] [--sortie fichier.xml]

Produit un .xml que MS Project ouvre nativement (Fichier > Ouvrir), avec :
  - les phases en taches recapitulatives,
  - les durees,
  - les liens de dependance et leur type (FD -> FS, DD -> SS),
  - les entreprises en ressources affectees,
  - la RAISON de chaque lien dans les notes de la tache.

C'est ce dernier point qui compte : MS Project n'a pas de champ pour justifier
un lien. Les notes le conservent.
"""
import argparse
import sys
from datetime import date
from xml.etree import ElementTree as ET

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from planifier import charger, planifier  # noqa: E402

NS = "http://schemas.microsoft.com/project"
# MSPDI : 0 = FF, 1 = FS (fin-debut), 2 = SF, 3 = SS (debut-debut)
TYPE_LIEN = {"FD": "1", "DD": "3", "FF": "0"}
HEURES_PAR_SEMAINE = 40


def sub(parent, tag, texte=None):
    e = ET.SubElement(parent, tag)
    if texte is not None:
        e.text = str(texte)
    return e


def horodatage(d, heure="08:00:00"):
    return f"{d.isoformat()}T{heure}"


def construire(taches, dates, phases, debut, nom_projet):
    ET.register_namespace("", NS)
    racine = ET.Element(f"{{{NS}}}Project")
    sub(racine, "Name", nom_projet)
    sub(racine, "Title", nom_projet)
    sub(racine, "StartDate", horodatage(debut))
    sub(racine, "ScheduleFromStart", "1")
    sub(racine, "CalendarUID", "1")
    sub(racine, "DefaultTaskType", "1")          # duree fixe
    sub(racine, "DurationFormat", "7")           # jours
    sub(racine, "MinutesPerDay", "480")
    sub(racine, "MinutesPerWeek", "2400")
    sub(racine, "DaysPerMonth", "20")
    sub(racine, "NewTasksAreManual", "0")

    # Calendrier standard, lundi-vendredi 8h-12h / 13h-17h
    cals = sub(racine, "Calendars")
    cal = sub(cals, "Calendar")
    sub(cal, "UID", "1")
    sub(cal, "Name", "Standard")
    sub(cal, "IsBaseCalendar", "1")
    sub(cal, "BaseCalendarUID", "-1")
    semaine = sub(cal, "WeekDays")
    for jour in range(1, 8):
        wd = sub(semaine, "WeekDay")
        sub(wd, "DayType", str(jour))
        ouvre = jour not in (1, 7)  # 1 = dimanche, 7 = samedi
        sub(wd, "DayWorking", "1" if ouvre else "0")
        if ouvre:
            horaires = sub(wd, "WorkingTimes")
            for d0, f0 in (("08:00:00", "12:00:00"), ("13:00:00", "17:00:00")):
                wt = sub(horaires, "WorkingTime")
                sub(wt, "FromTime", d0)
                sub(wt, "ToTime", f0)

    # Ressources : une par entreprise
    lots = sorted({t["entreprise"] for t in taches.values()})
    uid_lot = {lot: i + 1 for i, lot in enumerate(lots)}
    res = sub(racine, "Resources")
    for lot, uid in uid_lot.items():
        r = sub(res, "Resource")
        sub(r, "UID", str(uid))
        sub(r, "ID", str(uid))
        sub(r, "Name", lot)
        sub(r, "Type", "1")
        sub(r, "CalendarUID", "1")

    # Taches : une recapitulative par phase, puis ses taches
    noeud_taches = sub(racine, "Tasks")
    uid, ident = 0, 0
    uid_tache = {}
    lignes = []
    par_phase = {}
    for tid, t in taches.items():
        par_phase.setdefault(t["phase"], []).append(tid)

    for ph in phases:
        code = ph["code"]
        if code not in par_phase:
            continue
        uid += 1
        ident += 1
        lignes.append(("recap", uid, ident, ph, None))
        for tid in sorted(par_phase[code], key=lambda i: dates[i][0]):
            uid += 1
            ident += 1
            uid_tache[tid] = uid
            lignes.append(("tache", uid, ident, ph, tid))

    for genre, u, i, ph, tid in lignes:
        n = sub(noeud_taches, "Task")
        sub(n, "UID", str(u))
        sub(n, "ID", str(i))
        sub(n, "Active", "1")
        sub(n, "Manual", "0")
        sub(n, "CalendarUID", "1")
        if genre == "recap":
            enfants = par_phase[ph["code"]]
            d0 = min(dates[c][0] for c in enfants)
            f0 = max(dates[c][1] for c in enfants)
            sub(n, "Name", f"{ph['code']} - {ph['titre']}")
            sub(n, "OutlineLevel", "1")
            sub(n, "Summary", "1")
            sub(n, "Start", horodatage(d0))
            sub(n, "Finish", horodatage(f0, "17:00:00"))
            sub(n, "Notes", ph["description"])
            continue

        t = taches[tid]
        d0, f0 = dates[tid]
        semaines = t.get("duree_semaines") or 1
        sub(n, "Name", t["designation"])
        sub(n, "OutlineLevel", "2")
        sub(n, "Summary", "0")
        sub(n, "Type", "1")
        sub(n, "DurationFormat", "7")
        sub(n, "Duration", f"PT{semaines * HEURES_PAR_SEMAINE}H0M0S")
        sub(n, "Start", horodatage(d0))
        sub(n, "Finish", horodatage(f0, "17:00:00"))
        sub(n, "ConstraintType", "4" if t.get("date_connue") else "0")
        if t.get("date_connue"):
            sub(n, "ConstraintDate", horodatage(d0))

        notes = [f"[{tid}]  Lot : {t['entreprise']}  |  Systeme : {t['systeme']}",
                 f"Locaux : {', '.join(t['locaux'])}",
                 f"Statut : {t['statut']}"]
        if t.get("notes"):
            notes += ["", t["notes"]]
        if t["predecesseurs"]:
            notes += ["", "RAISONS DES LIENS :"]
            for pr in t["predecesseurs"]:
                notes.append(f"  <- {pr['id']} ({pr['lien']}) : {pr['raison']}")
        sub(n, "Notes", "\n".join(notes))

        for pr in t["predecesseurs"]:
            if pr["id"] not in uid_tache:
                continue
            pl = sub(n, "PredecessorLink")
            sub(pl, "PredecessorUID", str(uid_tache[pr["id"]]))
            sub(pl, "Type", TYPE_LIEN.get(pr["lien"], "1"))
            sub(pl, "CrossProject", "0")
            sub(pl, "LinkLag", "0")
            sub(pl, "LagFormat", "7")

    # Affectations des entreprises
    affect = sub(racine, "Assignments")
    for a, (genre, u, _, _, tid) in enumerate(lignes, start=1):
        if genre != "tache":
            continue
        t = taches[tid]
        d0, f0 = dates[tid]
        asg = sub(affect, "Assignment")
        sub(asg, "UID", str(a))
        sub(asg, "TaskUID", str(u))
        sub(asg, "ResourceUID", str(uid_lot[t["entreprise"]]))
        sub(asg, "Units", "1")
        sub(asg, "Start", horodatage(d0))
        sub(asg, "Finish", horodatage(f0, "17:00:00"))
    return racine


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--taches", default="data/taches.json")
    ap.add_argument("--phases", default="data/phases.json")
    ap.add_argument("--debut", default=date.today().isoformat())
    ap.add_argument("--sortie", default="data/extracted/planning_msproject.xml")
    args = ap.parse_args()

    import json
    taches, _ = charger(args.taches)
    phases = json.load(open(args.phases, encoding="utf-8"))["phases"]
    a, m, j = map(int, args.debut.split("-"))
    debut = date(a, m, j)
    dates = planifier(taches, debut)

    racine = construire(taches, dates, phases,
                        debut, "Centrale PAC 18 MW - Granges-Paccot (20.133)")
    arbre = ET.ElementTree(racine)
    ET.indent(arbre, space="  ")
    arbre.write(args.sortie, encoding="UTF-8", xml_declaration=True)
    liens = sum(len(t["predecesseurs"]) for t in taches.values())
    print(f"{len(taches)} taches, {liens} liens, {len(phases)} phases -> {args.sortie}")
    print("Ouvrir dans MS Project : Fichier > Ouvrir > selectionner le .xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
