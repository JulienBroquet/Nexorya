---
titre: Gestion du changement
nom: Changer le réseau sans le casser
idee: La plupart des pannes viennent d’une modification ; un changement bien préparé décrit ce qu’on fait, comment on vérifie et comment on revient en arrière.
osi: "transversal"
duree: [7, 14]
cle: true
prerequis: [diagnostic]
retenir:
  - "Tout changement a — un **objectif**, un **impact** estimé, un **plan pas à pas**, des **vérifications**, un **plan de retour arrière**."
  - "Sauvegarder **avant**, vérifier **après**, documenter **toujours**."
  - "Sur un équipement distant, prévoir un **filet** (`reload in`, `commit confirmed`)."
  - Un changement raté se termine par une **analyse sans recherche de coupable**.
---

## Le problème : « je n’ai changé qu’une ligne »

Un vendredi à 17 h, un administrateur ajoute une ligne à une ACL sur le routeur d’une agence, à distance. La ligne est fausse, la connexion SSH tombe, l’agence est coupée tout le week-end, et personne d’autre ne sait ce qui a été fait.

> [!IMPORTANT] L’idée en une phrase
> Avant de toucher au réseau, on sait **ce qu’on va faire**, **comment on saura que ça marche**, et **comment on revient en arrière** si ce n’est pas le cas.

## La fiche de changement

| Rubrique | Exemple |
|---|---|
| **Objectif** | autoriser l’agence de Lyon à joindre le nouveau serveur ERP |
| **Équipements** | R-LYON-01 |
| **Impact** | aucune coupure attendue ; risque : perte d’accès à l’agence si l’ACL est fausse |
| **Fenêtre** | mardi 19 h – 19 h 30 |
| **Plan** | 1. sauvegarde ; 2. `reload in 10` ; 3. ajout de la ligne ; 4. vérifications ; 5. `reload cancel` ; 6. enregistrement |
| **Vérifications** | test HTTPS vers l’ERP depuis l’agence, compteurs de l’ACL, accès Internet de l’agence |
| **Retour arrière** | retirer la ligne ; si l’accès est perdu, redémarrage automatique au bout de 10 min |
| **Communication** | équipe ERP et responsable d’agence prévenus |

## Les mots à connaître

- **Changement** — Toute modification apportée à la configuration ou à l’infrastructure.
- **Fenêtre de maintenance** — Créneau convenu pendant lequel un impact est accepté.
- **Plan de retour arrière** — Procédure qui ramène à l’état précédent.
- **Post-mortem** — Analyse écrite d’un incident pour en tirer des améliorations.

## Teste-toi

**Pourquoi définir les vérifications avant le changement, et pas après ?**

<details><summary>Voir le corrigé</summary>

Parce qu’après, on vérifie souvent seulement ce qu’on pensait modifier, et l’on oublie les **effets de bord** (l’accès Internet de l’agence, la voix…). Les décider à froid, avant, oblige à réfléchir à tout ce qui pourrait être touché — et à relever l’état « avant » pour pouvoir comparer.

</details>

<!-- approfondir -->

## Les filets de sécurité

```cisco
! Cisco IOS : redémarrage programmé si l'on perd la main
R-LYON-01# copy running-config startup-config
R-LYON-01# reload in 10
R-LYON-01# configure terminal
R-LYON-01(config)# ... modifications ...
R-LYON-01(config)# end
! Tout fonctionne ? On annule le redémarrage puis on enregistre.
R-LYON-01# reload cancel
R-LYON-01# copy running-config startup-config
```

```text
# Junos : la validation est annulée automatiquement si elle n'est pas confirmée
[edit]
admin@r1# commit confirmed 5
# ... vérifications ...
admin@r1# commit
```

Autres bonnes pratiques :

- **Archiver** la configuration avant/après (`archive` sur Cisco, Git avec l’automatisation) et comparer (`show archive config differences`).
- Utiliser `configure replace` pour revenir proprement à une configuration complète sauvegardée.
- Garder un **accès hors bande** (console, réseau de gestion séparé, modem 4G) aux sites importants.

## Relever l’état « avant »

Avant le changement, noter ce qui doit rester identique : voisins OSPF/BGP, nombre de routes, interfaces up, tables MAC, sessions VPN. Après, comparer. Un écart inattendu (un voisin en moins, 200 routes de moins) se voit immédiatement.

```cisco
show ip ospf neighbor
show ip route summary
show ip interface brief | include up
show crypto session brief
```

## Les catégories de changement

| Type | Exemple | Validation |
|---|---|---|
| **Standard** | ajouter un port d’accès dans un VLAN existant | procédure pré-approuvée, sans comité |
| **Normal** | nouveau VLAN sur un site, nouvelle règle de pare-feu | relecture par un pair, fenêtre planifiée |
| **Majeur** | migration du cœur, changement de protocole de routage | comité, plan détaillé, répétition en laboratoire |
| **Urgent** | correctif de sécurité critique, contournement de panne | validation rapide, documentation a posteriori |

## Le post-mortem

Quand un changement provoque un incident, on écrit une analyse : chronologie, cause, impact, ce qui a bien fonctionné, ce qui a manqué, et des **actions** concrètes (une vérification ajoutée à la procédure, un test automatique, une formation). On ne cherche pas un coupable : on cherche ce qui, dans le processus, a permis l’erreur.

## Exercice

**Rédige le plan de retour arrière d’un changement qui remplace la route par défaut d’un site (du lien MPLS vers un lien SD-WAN), réalisé à distance.**

<details><summary>Voir le corrigé</summary>

1. Sauvegarde de la configuration et relevé de la table de routage avant.
2. `reload in 15` (ou équivalent) avant toute modification.
3. Ajouter la nouvelle route avec une **distance administrative plus élevée** (route flottante), vérifier qu’elle est valide.
4. Basculer en retirant l’ancienne route (ou en inversant les distances) ; vérifier l’accès au siège, à Internet, la voix.
5. Si tout est bon : `reload cancel`, enregistrement. Sinon : remettre l’ancienne route ; si l’accès est perdu, le redémarrage automatique restaure la configuration enregistrée.

</details>
