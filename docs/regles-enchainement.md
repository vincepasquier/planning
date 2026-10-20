# Règles d'enchaînement — Centrale PAC 18 MW, Granges-Paccot (20.133)

`CADFR - GP - Z17 - Centrale Conforama - 20133`
Parcelles 404 / 113, 1763 Granges-Paccot (ZI Englisberg). Phase SIA 51.

Ce document explique la logique du réseau. Les données vivent dans
`data/taches.json` ; chaque lien y porte sa raison. C'est cette raison qui
compte : dans six mois, face à une entreprise qui contestera un enchaînement,
c'est elle qui servira d'argument.

## Les deux fluides frigorigènes

C'est la clé de lecture du dossier, et elle a été corrigée en v0.2 :

| Fluide | Rôle | Entreprise |
|---|---|---|
| **NH3** (ammoniac) | Fluide des PAC 1 à 4 | **Wettstein** |
| **CO2** | Froid process **et** refroidissement des locaux techniques | **Despraz** |
| Eau, PN16, 11 bars | Hydraulique chaud vers accumulateur, CAD et ZI | Entretec |

Deux conséquences majeures :

**1. Le refroidissement des locaux électriques appartient à Despraz, pas à
Hälg.** Le circuit froid CO2 à 16/21 °C alimente des armoires de
refroidissement à brassage d'air : MT 97 kW, variateurs/commande 70 kW, locaux
PAC 55 kW chacun, pompage 25 kW, hydraulique chaud 15 kW, TGBT 10 kW. Hälg
traite l'air (hygiénique, WC, sécurité), pas le froid.

**2. L'ammoniac impose un régime de sécurité.** NH3 est toxique et
inflammable. La ventilation de secours extrait **5'500 m³/h par local PAC** en
cas de fuite NH3 et **12'100 m³/h** en cas de fuite CO2, par une cheminée
d'extraction dédiée.

## Le pivot : la manutention

Quatre PAC, un accumulateur et sept vases d'expansion de 5'000 L à **N-2**,
deux niveaux sous terre. Tant que ces colis ne sont pas descendus et posés,
**l'itinéraire de manutention doit rester libre**.

`T-WET-040` (pose de la PAC 4) commande à elle seule **9 tâches successeurs** —
le point le plus contraignant du réseau.

L'erreur classique : laisser l'électricien poser ses chemins de câbles dans les
circulations parce qu'il est disponible, et découvrir trois semaines plus tard
qu'une machine ne passe plus. La maquette électrique contient **905 segments de
chemin de câbles**.

### La contrainte de gabarit (Q-02)

Les métrés de la maquette architecturale révèlent un écart invisible sur un
plan d'étage :

| Local | Surface | Hauteur sous plafond |
|---|---|---|
| PAC 1 à 4, TGBT, MT, Accumulateur | 86–212 m² | **7,00 m** |
| Circulations N-2 (l'itinéraire) | 209 + 220 m² | **4,10 m** |
| Quais 1 et 2 (N-1) | 105 + 38 m² | **2,62 m** |

**Le gabarit limite est celui de l'itinéraire, pas celui du local de
destination.** S'y ajoutent, à l'intérieur même des locaux, des pièces lourdes
à manutentionner : circulateurs Grundfos NBG 200-150 de **484 kg**, vannes de
régulation RTK de **401 kg**.

## Ordre de passage des réseaux

Règle : **le plus encombrant et le moins déformable passe en premier.**

1. **Ventilation** (Hälg, sections 41, 42, 43) — gaines volumineuses et rigides
2. **Hydraulique chaud** (Entretec, sections 00 à 07) — gros diamètres, pentes
3. **CO2** (Despraz, sections 25 à 29) — tracé contraint, propreté exigée
4. **Chemins de câbles et IEG** (Groupe E Tech) — le plus adaptable, il contourne

Le sanitaire (Riedo Clima) est très localisé — 3,5 m² de sanitaire et 9,1 m² de
vestiaire — donc hors conflit.

## Règles dures

| Règle | Raison |
|---|---|
| Socles mûrs **avant** pose des PAC | Mise en charge sur béton jeune |
| Colis lourds posés **avant** tous réseaux | Itinéraire de manutention |
| Machines posées **avant** raccordements | Le raccordement se relève sur l'ouvrage réel, pas sur le plan |
| **Rinçage hydraulique avant** raccordement définitif aux PAC | Sinon on encrasse des échangeurs neufs |
| Expansion en service **avant** mise en eau | Pas de remplissage sans expansion |
| Soudures terminées **avant** épreuve | Une seule reprise invalide l'épreuve |
| Épreuve **avant** tirage au vide **avant** charge | Séquence frigorifique non négociable |
| **Ventilation de secours et détection gaz en service AVANT toute charge NH3 ou CO2** | Sécurité des personnes. Aucun fluide frigorigène n'entre dans le bâtiment avant |
| Sectorisation coupe-feu achevée **avant** essais des clapets | Un clapet ne vaut que dans une paroi étanche |
| **Refroidissement CO2 des locaux avant** mise en charge nominale des variateurs | 70 kW à évacuer par local variateurs/commande |
| TGBT sous tension **avant** tout essai | Rien ne démarre sans puissance |
| Épreuve **avant** calorifugeage | Une reprise de fuite impose de déshabiller |
| Sondes et doigts de gant **avant** calorifugeage | Sinon on rouvre l'isolation |
| Charges NH3 et CO2 **en dernier** | Produits coûteux et dangereux ; toute réouverture impose un retrait |
| Portes du chemin de manutention **en dernier** | Après le dernier colis lourd |

## La boucle du refroidissement (Q-07)

Il existe une circularité apparente : les locaux électriques sont refroidis par
les centrales froid CO2, qui ont besoin d'électricité pour tourner.

Le réseau la résout en deux temps, en s'appuyant sur le **free-cooling**
mentionné au schéma de refroidissement du local MT :

1. `T-HAL-010` installe la ventilation hygiénique et son free-cooling
2. `T-GET-080` met le MT et le TGBT sous tension, refroidis par free-cooling
3. `T-DES-020` met le froid CO2 des locaux en service
4. `T-GET-090` monte les variateurs en charge nominale

**Cette hypothèse doit être validée.** Si le free-cooling ne suffit pas à la
première mise sous tension, il faut une alimentation provisoire et la séquence
change.

## Le levier : les chaufferies mobiles (Q-15)

Le synoptique chaud prévoit **deux chaufferies mobiles gaz de 2.5 MW** avec
échangeurs PN6/PN25. Si elles peuvent alimenter le CAD en attendant les PAC,
**la date de livraison de chaleur se découple de la mise en service des
machines** — et la mise en service des PAC quitte le chemin critique
contractuel.

C'est potentiellement la marge la plus précieuse du dossier. Elle mérite d'être
confirmée avant tout calage de dates.

## Maturité des études : un écart de trois niveaux

| Système | Phase | Date |
|---|---|---|
| Hydraulique chaud | **Exécution** | 18.09.2026 |
| Expansion | **Exécution** | 12.10.2026 |
| Ventilation sécurité CO2/NH3 | Pré-exécution | 16.10.2026 |
| Ventilation hygiénique | Appel d'offres | 25.03.2026 |
| Ventilation WC | Appel d'offres | 22.05.2026 |
| Froid process CO2 | Appel d'offres | 09.06.2026 |
| Refroidissement local MT | **Mise à l'enquête** | 10.07.2025 |

L'hydraulique est en exécution ; le froid et la sécurité, qui conditionnent la
mise sous tension et la charge des fluides, ne le sont pas. Le refroidissement
du local MT n'a jamais dépassé la mise à l'enquête, en juillet 2025.

C'est un risque de planning autant qu'un risque technique (Q-19).

## Contradictions entre documents

| Local | Maquette ARC (Riforma) | Schémas Groupe E |
|---|---|---|
| N-2.09 | Commande 1 et 2 | **Centrale froid n°1** |
| N-2.14 | Commande 3 et 4 | **Centrale froid n°2** |
| N-2.05 | Hydraulique circuit int. | **Local intro CO2** |

Ce n'est pas un détail de nomenclature : si N-2.09 et N-2.14 sont des centrales
froid, c'est **Despraz** qui occupe ces deux locaux et non Groupe E Tech
(Q-13). La liste des armoires place d'ailleurs les coffrets PAC en N-2.08 et
N-2.13, pas en N-2.09 ni N-2.14.

Par ailleurs, le numéro N-2.05 est attribué deux fois dans la maquette, à deux
locaux de 34,6 et 128,0 m² (Q-08).

## Ce que le modèle ne contient pas

- **Aucune durée validée.** Les classes (`semaine`, `quinzaine`, `mois`,
  `trimestre`) sont des ordres de grandeur posés par défaut.
- **Une seule date ferme** : épreuve de pression de l'accumulateur, 30.11.2026.
- **Aucun délai de livraison** — or c'est probablement là que se trouve le
  chemin critique réel (Q-04).
- **La STAP**, qui figure au titre du synoptique chaud et dans la liste des
  armoires, mais n'est ni dans la maquette ni dans les adjudications (Q-18).
- **Le phasage étape 1 / final**, visible sur les départs CAD et ZI, dont le
  contenu reste à préciser (Q-14).
- **Les éventuelles réceptions réglementaires liées à l'ammoniac** (Q-20).
- **Les moyens de levage** sont à la charge des entreprises, mais la
  réservation de la rampe et du couvert reste à coordonner.
