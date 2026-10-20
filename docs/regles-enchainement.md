# Règles d'enchaînement — Centrale PAC 18 MW, Granges-Paccot (20.133)

`CADFR - GP - Z17 - Centrale Conforama - 20133`
Parcelles 404 / 113, 1763 Granges-Paccot (ZI Englisberg). Phase SIA 51.

Les données vivent dans `data/taches.json` ; chaque lien y porte sa raison.
C'est cette raison qui compte : dans six mois, face à une entreprise qui
contestera un enchaînement, c'est elle qui servira d'argument.

Ce document décrit l'état du réseau après le relevé des locaux mené avec le
maître d'ouvrage. Plusieurs règles générales que j'avais posées au départ se
sont révélées fausses ; elles sont signalées comme telles plutôt que
supprimées, parce que l'erreur renseigne.

## Les deux fluides

| Fluide | Rôle | Entreprise |
|---|---|---|
| **NH3** (ammoniac) | Fluide des PAC 1 et 2 | Wettstein |
| **CO2** | Froid process et refroidissement des locaux | Despraz |
| Eau, PN16, 11 bars | Hydraulique chaud vers accumulateur, CAD et ZI | Entretec |

L'ammoniac impose son régime de sécurité : la ventilation de secours extrait
**5'500 m³/h par local PAC** en cas de fuite NH3 et **12'100 m³/h** en cas de
fuite CO2, par une cheminée dédiée. Aucun fluide frigorigène n'entre dans le
bâtiment avant que ce système soit éprouvé.

## Le périmètre réel

Deux PAC sur quatre. **Les PAC 3 et 4 sont posées dans 5 à 10 ans**, et avec
elles sortent quatre locaux : N-2.12 et N-2.15 (les machines), N-2.13
(variateurs 3-4) et N-2.14 (centrale froid n°2). Les schémas prévoyaient déjà
les réserves, ce que le marquage « (réserve) » des départs froid laissait
entendre.

## Deux chaînes, et non plus un pivot

Le planning ne tient plus à un seul goulot. Deux chaînes courent en parallèle
et se rejoignent sur les essais :

1. **Montage des machines** — Wettstein, 15 semaines par local, les deux
   montages bout à bout. Puis raccordements, épreuves et charges.
2. **Électricité et régulation** — livraison MT/TGBT en février 2027, pose,
   puis automates MCR, raccordement de l'instrumentation et essais de boucles.

La seconde porte aujourd'hui le chemin critique. La première n'a plus que
**sept jours de marge** : les deux arrivent pratiquement ensemble, ce qui est
sain mais fragile. Un retard de part ou d'autre se paie immédiatement.

## Ce que le relevé a corrigé

**La manutention n'est pas le pivot.** J'avais bâti tout le réseau sur l'idée
qu'une PAC arrive d'un bloc et qu'il faut lui garder un itinéraire libre. Faux :
c'est un **montage complet dans le local**, pièce par pièce. La contrainte de
gabarit tombe — la porte 20 (3,50 × 4,00 m) ne limite pas la machine — et les
réseaux ne sont plus asservis à la libération d'un passage. Ce qui commande,
c'est l'occupation du local pendant 3,5 mois.

**L'ordre des réseaux dans les galeries est l'inverse de ma règle.** J'avais
posé « le plus encombrant et le moins déformable d'abord », donc ventilation
puis hydraulique. Le maître d'ouvrage dit : **hydraulique et sanitaire, puis
ventilation**. IEG ne passe pas par les galeries mais par en dessous, et sort
donc du conflit.

**Les deux branches du froid sont indépendantes.** Le refroidissement des
locaux techniques n'attend pas l'échangeur de la PAC 2 : il se fait dès que le
réseau CO2 et la centrale froid n°1 sont en place. Ce seul lien valait onze
semaines.

**Chacun son tour.** Dans les locaux techniques, une seule entreprise à la
fois. Le réseau ne sait l'exprimer que là où les tâches sont découpées par
local ; partout où elles restent décrites à l'échelle du bâtiment — ventilation,
câblage IEG, froid des locaux — rien n'empêche encore deux lots de s'y
superposer. C'est la limite connue du modèle (Q-24).

## Règles dures

| Règle | Raison |
|---|---|
| Socle préfabriqué en place **avant** le montage | Pas de maturation à attendre, mais le socle d'abord |
| Wettstein seul dans le local **pendant 3,5 mois** | Montage complet sur place |
| Wettstein sorti **avant** Entretec et Despraz | Puis ces deux-là ensemble, 4 semaines confondues |
| **Rinçage hydraulique avant** raccordement définitif aux PAC | Sinon on encrasse des échangeurs neufs |
| Expansion en place et raccordée **avant** mise en eau | Pas de remplissage sans expansion |
| Dans les galeries : **hydraulique et sanitaire, puis ventilation** | Règle du maître d'ouvrage |
| Soudures terminées **avant** épreuve | Une reprise invalide l'épreuve |
| Épreuve **avant** tirage au vide **avant** charge | Séquence frigorifique |
| **Ventilation de secours et détection gaz en service AVANT toute charge** | Sécurité des personnes |
| Sectorisation coupe-feu achevée **avant** essais des clapets | Un clapet ne vaut que dans une paroi étanche |
| **Froid des locaux avant** mise en charge nominale des variateurs | 70 kW à évacuer par local |
| TGBT sous tension **avant** tout essai | Rien ne démarre sans puissance |
| Épreuve **avant** calorifugeage, sondes **avant** calorifugeage | Sinon on déshabille, ou on rouvre |
| Charges NH3 et CO2 **en dernier** | Produits coûteux et dangereux |

## Les limites de prestation relevées

Un planning vaut par les interfaces qu'il nomme.

- **Wettstein / Entretec / Despraz** : Wettstein monte la machine dans le
  local ; les deux autres viennent s'y raccorder, ensemble, 4 semaines.
- **Groupe E Tech INFRA / TABLEAU** : INFRA pose les cellules et transformateurs
  MT/BT et tire les rails d'énergie **jusque dans le local TGBT**, où sa
  prestation s'arrête. TABLEAU y pose les tableaux. IEG câble tout ce qui n'est
  pas du rail.
- **Spirotec / levage / Entretec** : Spirotec fournit les 7 vases d'expansion de
  5'000 L, une entreprise de levage les met en place, Entretec les raccorde.

## Ce qui reste ouvert

- **Trois lots non adjugés** : calorifugeage, entreprise de levage, Ansermot.
  Le premier suit immédiatement la seule date ferme du dossier.
- **La STAP**, qui figure au titre du synoptique chaud et dans la liste des
  armoires, mais ni dans la maquette ni dans les adjudications.
- **Le phasage étape 1 / final** des départs CAD et ZI.
- **Les réceptions réglementaires liées à l'ammoniac**, le cas échéant.
- **L'accumulateur** : 8 m de diamètre, 9 m isolé, 19 m de haut, monté sur
  place. Son calorifugeage représente environ 500 m² en hauteur, et le lot n'est
  pas adjugé.
- **Les délais de livraison** des PAC, des groupes froid et des variateurs. Seul
  celui du matériel électrique est connu : février 2027, et il coûte une
  semaine sur la date de réception.
