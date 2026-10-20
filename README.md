# Planning de réalisation — Centrale Englisberg (20.133)

Ordonnancement des travaux de la centrale ENGLISBERG, bâtiment CENTRALE,
phase SIA 51 (projet d'exécution).

L'objet de ce dépôt n'est pas de dire **quand**, mais **qui avant qui** — et
surtout **pourquoi**. Chaque lien entre deux tâches porte sa justification.

## État

| | |
|---|---|
| Tâches | 47 |
| Liens de dépendance | 65 |
| Rangs d'ordonnancement | 15, sans cycle |
| Dates fermes | 1 (épreuve accumulateur, 30.11.2026) |
| Questions ouvertes | 12, dont 3 critiques |
| Lots non adjugés | 2 (calorifugeage, Ansermot) |

Version 0.1 — ossature à valider avec les entreprises.

## Contenu

```
data/
  entreprises.json        Les 11 lots, leurs prestations, leur statut
  phases.json             Les 7 phases de réalisation
  taches.json             Les tâches et leurs liens — le cœur du dépôt
  questions-ouvertes.json Ce qui doit être tranché, par priorité
  extracted/locaux.json   37 locaux extraits de la maquette ARC, avec métrés
  raw/                    Maquettes IFC brutes (non versionnées)
docs/
  regles-enchainement.md  La logique du réseau, expliquée
  plans/                  Plans PDF (non versionnés)
scripts/
  extract_locaux.py       IFC -> liste des locaux + métrés
  valider.py              Contrôle du réseau et calcul des rangs
```

## Utilisation

Extraire les locaux d'une maquette IFC :

```bash
python3 -I scripts/extract_locaux.py data/raw/MAQUETTE.ifc data/extracted/locaux.json
```

Valider le réseau et afficher l'ordonnancement par rangs :

```bash
python3 -I scripts/valider.py data/taches.json
```

Aucune dépendance externe : un fichier IFC est du texte STEP (ISO-10303-21),
lisible directement.

## Pourquoi les IFC ne sont pas versionnés

GitHub refuse tout fichier de plus de 100 Mio, et git stocke chaque version
d'un binaire intégralement — cinq révisions d'une maquette laisseraient
plusieurs gigaoctets dans l'historique, définitivement. Un IFC est une donnée
d'entrée, pas du code source : il n'offre ni diff ni fusion.

Les maquettes restent donc sur OneDrive. Ce dépôt ne versionne que ce qui a de
la valeur à suivre dans le temps : les **données extraites** (quelques
centaines de kilo-octets, diffables d'un indice à l'autre) et la **logique
d'enchaînement**.

## Les trois points les plus urgents

1. **Q-02 — Gabarit de passage.** Les locaux PAC font 7,00 m sous plafond, les
   circulations qui y mènent 4,10 m. Dimensions hors-tout des machines ?
2. **Q-06 — Calorifugeage non adjugé.** Il suit immédiatement une date ferme
   (30.11.2026).
3. **Q-03 — Garantie du circuit CO2.** La limite physique est claire, la
   responsabilité de l'étanchéité d'ensemble ne l'est pas.

## Sources

- `ENGLI-51-ARC-CENT-000_complet.ifc` — Riforma Architecture SA, Vectorworks
  Architect 2025, IFC4, 15.07.2026
- `ENGLI-51-ELE-CENT-000.ifc` — Groupe E Connect SA, Autodesk Revit 2024,
  IFC4, 11.03.2026
- Liste des adjudications communiquée par le maître d'ouvrage
