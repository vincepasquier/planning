# Règles d'enchaînement — Centrale Englisberg (20.133)

Ce document explique la logique du réseau de tâches. Les données vivent dans
`data/taches.json` ; chaque lien y porte sa raison. C'est cette raison qui
compte : dans six mois, quand une entreprise contestera un enchaînement, c'est
elle qui servira d'argument.

## Le pivot : la manutention

Quatre PAC et un accumulateur à **N-2**, deux niveaux sous terre. Tant que les
machines ne sont pas descendues et posées, **l'itinéraire de manutention doit
rester libre**.

La tâche `T-WET-040` (pose de la PAC 4) commande à elle seule **9 tâches
successeurs** — c'est le point le plus contraignant de tout le réseau.

L'erreur classique sur ce type de chantier : laisser l'électricien poser ses
chemins de câbles dans les circulations parce qu'il est disponible, et
découvrir trois semaines plus tard qu'une machine ne passe plus. La maquette
électrique contient **905 segments de chemin de câbles** — de quoi boucher un
couloir.

### La contrainte de gabarit (à valider — Q-02)

Les métrés extraits de la maquette architecturale révèlent un écart qui n'est
pas visible sur un plan d'étage :

| Local | Surface | Hauteur sous plafond |
|---|---|---|
| PAC 1 à 4 | 191–193 m² | **7,00 m** |
| TGBT | 86 m² | **7,00 m** |
| MT | 173 m² | **7,00 m** |
| Accumulateur | 212 m² | **7,00 m** |
| Circulations N-2 (itinéraire) | 209 + 220 m² | **4,10 m** |
| Quais 1 et 2 (N-1) | 105 + 38 m² | **2,62 m** |

**Le gabarit limite n'est pas la hauteur du local de destination, mais celle de
l'itinéraire.** Une machine haute de plus de ~4 m ne passe pas par la
circulation N-2 : il faut une trémie depuis le couvert, ou un montage sur
place. C'est la question la plus urgente du dossier.

## Ordre de passage des réseaux

Règle : **le plus encombrant et le moins déformable passe en premier.**

1. **Ventilation** (Hälg) — gaines volumineuses et rigides
2. **Hydraulique chaud et froid** (Entretec) — gros diamètres, pentes imposées
3. **CO2** (Despraz) — acier haute pression, tracé contraint, propreté exigée
4. **Chemins de câbles et IEG** (Groupe E Tech) — le plus adaptable, il contourne

Le sanitaire (Riedo Clima) est très localisé — 3,5 m² de sanitaire et 9,1 m² de
vestiaire — donc hors conflit, avec une large marge de calage.

## Règles dures

Ces liens ne se négocient pas.

| Règle | Raison |
|---|---|
| Socles mûrs **avant** pose des PAC | Mise en charge sur béton jeune |
| Machines posées **avant** tous réseaux | Itinéraire de manutention |
| Machines posées **avant** raccordements | Le raccordement se relève sur l'ouvrage réel, pas sur le plan |
| **Rinçage hydraulique avant** raccordement définitif aux PAC | Sinon on encrasse des échangeurs neufs |
| Soudures CO2 terminées **avant** épreuve | Une seule reprise invalide l'épreuve |
| Épreuve **avant** tirage au vide **avant** charge | Séquence frigorifique non négociable |
| **Refroidissement des locaux électriques avant** mise en service des variateurs | Les variateurs ne tournent pas sans leur froid |
| TGBT sous tension **avant** tout essai | Rien ne démarre sans puissance |
| Épreuve **avant** calorifugeage | Une reprise de fuite impose de déshabiller |
| Sondes et doigts de gant **avant** calorifugeage | Sinon on rouvre l'isolation |
| Charge CO2 **en dernier** | Produit coûteux ; toute réouverture impose un retrait |
| Portes du chemin de manutention **en dernier** | Après le dernier colis lourd |

## Une subtilité de modélisation

`T-GET-080` (mise sous tension du TGBT) dépend de `T-HAL-020` (refroidissement
des locaux électriques), alors que `T-HAL-030` (mise en service de la
ventilation) dépend de `T-GET-080`. Cela ressemble à une boucle, et c'en serait
une si l'on confondait installation et mise en service.

Le réseau distingue les deux : Hälg **installe** son refroidissement avant la
mise sous tension, et le **met en service** après. C'est ce qui lève la
circularité — à condition qu'une alimentation provisoire existe (Q-07).

## Limite de prestation Wettstein / Despraz / Entretec

Confirmée par le maître d'ouvrage : **Wettstein livre et pose les PAC dans
leurs locaux uniquement.** Le CO2 (Despraz) et l'hydraulique chaud (Entretec)
viennent se raccorder sur les machines, dans le local.

La limite physique est donc nette. Ce qui ne l'est pas encore : **qui éprouve
et qui garantit l'étanchéité du circuit CO2 complet, machine incluse** (Q-03).
En CO2 transcritique, l'étanchéité est une performance du circuit entier, pas
de chacun de ses tronçons.

## Ce que le modèle ne contient pas

- **Aucune durée validée.** Les classes (`semaine`, `quinzaine`, `mois`) sont
  des ordres de grandeur posés par défaut, à remplacer par les retours des
  entreprises.
- **Une seule date ferme** : l'épreuve de pression de l'accumulateur,
  30.11.2026 (Bilfinger).
- **Aucun délai de livraison** — or c'est probablement là que se trouve le
  chemin critique réel (Q-04).
- **Les moyens de levage** sont à la charge des entreprises. Elles se
  débrouillent, mais la réservation de la rampe et du couvert reste à
  coordonner.
