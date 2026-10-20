# Planning de réalisation — Centrale PAC 18 MW (20.133)

Ordonnancement des travaux de la centrale `CADFR - GP - Z17 - Centrale
Conforama - 20133`, parcelles 404 / 113 à 1763 Granges-Paccot (ZI Englisberg),
phase SIA 51 (projet d'exécution).

L'objet de ce dépôt n'est pas de dire **quand**, mais **qui avant qui** — et
surtout **pourquoi**. Chaque lien entre deux tâches porte sa justification.

## État

| | |
|---|---|
| Tâches | 59 |
| Liens de dépendance | 90 |
| Rangs d'ordonnancement | 15, sans cycle |
| Dates fermes | 1 (épreuve accumulateur, 30.11.2026) |
| Questions ouvertes | 19, dont 4 critiques |
| Lots non adjugés | 2 (calorifugeage, Ansermot) |
| Périmètre non communiqué | 1 (STAP) |

Version 0.2 — intègre 9 schémas Groupe E. Ossature à valider avec les
entreprises.

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
  armoires.json           Les 15 armoires de commande et leurs emplacements
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

## Les quatre points les plus urgents

1. **Q-13 — Contradiction de documents.** La maquette nomme N-2.09 et N-2.14
   « Commande », les schémas Groupe E « Centrale froid n°1 et n°2 ». Si ce sont
   des centrales froid, c'est Despraz qui occupe ces locaux, pas Groupe E Tech.
2. **Q-02 — Gabarit de passage.** Les locaux PAC font 7,00 m sous plafond, les
   circulations qui y mènent 4,10 m. Dimensions hors-tout des machines, des
   cellules TGBT et des 7 vases de 5'000 L ?
3. **Q-06 — Calorifugeage non adjugé.** Il suit immédiatement la seule date
   ferme du dossier (30.11.2026, dans six semaines).
4. **Q-19 — Maturité des études.** L'hydraulique est en exécution ; le froid
   process est encore en appel d'offres et le refroidissement du local MT n'a
   jamais dépassé la mise à l'enquête (juillet 2025). Or ces systèmes
   conditionnent la mise sous tension et la charge des fluides.

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
