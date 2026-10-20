# Planning de réalisation — Centrale PAC 18 MW (20.133)

Ordonnancement des travaux de la centrale `CADFR - GP - Z17 - Centrale
Conforama - 20133`, parcelles 404 / 113 à 1763 Granges-Paccot (ZI Englisberg),
phase SIA 51 (projet d'exécution).

L'objet de ce dépôt n'est pas de dire **quand**, mais **qui avant qui** — et
surtout **pourquoi**. Chaque lien entre deux tâches porte sa justification.

## État

| | |
|---|---|
| Tâches | 62 |
| Liens de dépendance | 108 |
| Rangs d'ordonnancement | 11, sans cycle |
| Durée calculée | 48 semaines (réception au plus tôt 05.11.2027) |
| Dates fermes | 1 (épreuve accumulateur, 30.11.2026) |
| Questions ouvertes | 27 posées, 9 résolues |
| Lots non adjugés | 3 (calorifugeage des conduites, levage, Ansermot) |
| Périmètre non communiqué | 1 (STAP) |

Version 1.9 — les 36 locaux de la maquette sont relevés lot par lot avec le
maître d'ouvrage : 139 affectations relevées, 2 supposées. Le chantier ouvre
aux entreprises techniques en décembre 2026, le bâtiment étant réceptionné à
la mi-novembre.

### Corrections apportées en v0.2

- **Les PAC sont des machines NH3 (ammoniac)**, fournies par Wettstein. Le CO2
  est le fluide du froid process, chez Despraz. La v0.1 supposait à tort des
  PAC au CO2.
- **Le refroidissement des locaux techniques appartient à Despraz** (circuit
  froid CO2, armoires à brassage d'air), et non à la ventilation de Hälg.
- **La ventilation de sécurité CO2/NH3 est un prérequis dur** à la charge des
  fluides frigorigènes.
- Ajout de la **STAP**, des **vases d'expansion** (7 × 5'000 L) et des
  **chaufferies mobiles gaz** (2 × 2.5 MW), absents de la v0.1.

## Contenu

```
data/
  entreprises.json        Les 12 lots, leurs prestations, leur statut
  phases.json             Les 7 phases de réalisation
  taches.json             Les tâches et leurs liens — le cœur du dépôt
  questions-ouvertes.json Ce qui doit être tranché, par priorité
  documents.json          Les 9 schémas reçus, avec leur niveau de maturité
  matrice-locaux-lots.json  Qui passe où, relevé local par local
  intensites.json         Occupation réelle ou simple passage, et limites par local
  locaux-contenu.json     Les fiches de relevé, une par local
  armoires.json           Les 15 armoires de commande et leurs emplacements
  extracted/locaux.json   37 locaux extraits de la maquette ARC, avec métrés
  extracted/planning.csv  Le planning daté, une ligne par lot et par local
  extracted/planning_msproject.xml  Le même planning, ouvrable dans MS Project
  raw/                    Maquettes IFC brutes (non versionnées)
docs/
  regles-enchainement.md  La logique du réseau, expliquée
  plans/                  Plans PDF (non versionnés)
scripts/
  extract_locaux.py       IFC -> liste des locaux + métrés
  valider.py              Contrôle du réseau et calcul des rangs
  planifier.py            Calcul des dates au plus tôt, export CSV
  export_msproject.py     Export MSPDI XML, liens et raisons compris
  export_excel.py         Export et réimport du classeur Excel
  export_html.py          Génération de la page de visualisation
  gabarit_planning.html   Gabarit de cette page
  extract_geometrie.py    IFC -> emprise au sol des locaux, redressée
  coactivite.py           Conflits de co-activité, local par local
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

Calculer les dates et exporter le planning par lot et par local :

```bash
python3 -I scripts/planifier.py --csv data/extracted/planning.csv
python3 -I scripts/planifier.py --par lot       # regroupé par entreprise
python3 -I scripts/planifier.py --par local     # regroupé par local
python3 -I scripts/planifier.py --par critique  # le chemin critique seul
```

Produire les trois livrables :

```bash
python3 -I scripts/export_msproject.py   # .xml pour MS Project
python3 -I scripts/export_excel.py       # .xlsx quatre onglets
python3 -I scripts/export_html.py        # page de visualisation
python3 -I scripts/coactivite.py         # conflits de co-activité
```

La date de démarrage est lue dans `data/entreprises.json`, champ
`projet.demarrage_chantier` ; `--debut` permet de la forcer.

```bash
```

Reprendre les durées corrigées par les entreprises :

```bash
python3 -I scripts/export_excel.py --reimporter planning.xlsx
```

Aucune dépendance externe : un fichier IFC est du texte STEP (ISO-10303-21),
lisible directement.

## Qui est la source

Le dépôt est la source, MS Project est une vue : on corrige ici, on réexporte.
Ce partage tient tant que la structure bouge. Le jour où un planificateur
reprend le fichier dans MS Project et le fait vivre, l'inverse devient vrai —
et ce dépôt garde alors ce que MS Project ne sait pas stocker : la raison de
chaque lien, les métrés, les questions ouvertes et les scripts d'extraction.

## Pourquoi les IFC ne sont pas versionnés

GitHub refuse tout fichier de plus de 100 Mio, et git stocke chaque version
d'un binaire intégralement — cinq révisions d'une maquette laisseraient
plusieurs gigaoctets dans l'historique, définitivement. Un IFC est une donnée
d'entrée, pas du code source : il n'offre ni diff ni fusion.

Les maquettes restent donc sur OneDrive. Ce dépôt ne versionne que ce qui a de
la valeur à suivre dans le temps : les **données extraites** (quelques
centaines de kilo-octets, diffables d'un indice à l'autre) et la **logique
d'enchaînement**.

## Où se joue la date

Deux chaînes courent en parallèle et se rejoignent sur les essais. La chaîne
électricité et régulation porte le chemin critique ; le montage des machines
n'a plus que sept jours de marge. Les deux arrivent pratiquement ensemble, ce
qui est sain mais ne laisse aucune réserve de part ni d'autre.

## Les trois points les plus urgents

1. **Trois lots non adjugés** — calorifugeage, entreprise de levage, Ansermot.
   Le calorifugeage suit immédiatement la seule date ferme du dossier
   (30.11.2026) et porte environ 500 m² d'isolation en hauteur sur
   l'accumulateur.
2. **Q-24 — chacun son tour.** Les tâches de réseaux décrites à l'échelle du
   bâtiment peuvent encore se superposer dans un local qui n'admet qu'une
   entreprise. Les durées des petits locaux techniques sont donc sous-estimées.
3. **La STAP**, dans le périmètre du projet mais absente de la maquette et des
   adjudications.

## Sources

Maquettes :

- `ENGLI-51-ARC-CENT-000_complet.ifc` — Riforma Architecture SA, Vectorworks
  Architect 2025, IFC4, 15.07.2026
- `ENGLI-51-ELE-CENT-000.ifc` — Groupe E Connect SA, Autodesk Revit 2024,
  IFC4, 11.03.2026

Schémas Groupe E — Direction Solutions Energie (voir `data/documents.json`
pour la liste complète et les niveaux de maturité) : synoptique hydraulique
chaud (EXE), expansion (EXE), ventilation de sécurité CO2/NH3 (pré-EXE),
froid process (AO), ventilation hygiénique (AO), ventilation WC (AO),
refroidissement local MT (mise à l'enquête), concept MCR, liste des armoires
de commandes.

Liste des adjudications et limites de prestation communiquées par le maître
d'ouvrage.
