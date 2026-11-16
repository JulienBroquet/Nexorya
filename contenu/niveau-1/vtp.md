---
titre: VTP
nom: VLAN Trunking Protocol (Cisco)
idee: VTP recopie automatiquement la liste des VLAN d’un switch vers tous les autres ; pratique, mais un switch mal préparé peut effacer les VLAN de tout le réseau.
osi: "2"
duree: [6, 12]
prerequis: [802-1q]
retenir:
  - VTP synchronise la **liste des VLAN** (pas les ports) entre switches Cisco d’un même domaine.
  - En VTP v1/v2, la base au **numéro de révision le plus haut gagne**, même si elle est vide.
  - Beaucoup d’entreprises le mettent en mode **transparent** ou **off** ; VTP v3 limite le risque avec un serveur primaire unique.
---

## Le problème : créer le même VLAN sur 50 switches

Pour qu’un VLAN traverse le réseau, il doit exister sur **chaque** switch du chemin. Avec 50 switches, créer un VLAN signifie 50 connexions et 50 configurations — avec un risque d’oubli à chaque fois.

> [!IMPORTANT] L’idée en une phrase
> VTP diffuse la liste des VLAN depuis un switch « serveur » vers tous les autres : on crée le VLAN une fois, il apparaît partout.

## Comment ça marche

| Mode | Peut créer des VLAN ? | Se synchronise ? | Relaie les annonces ? |
|---|---|---|---|
| **Server** | oui | oui | oui |
| **Client** | non | oui | oui |
| **Transparent** | oui, localement | non | oui |
| **Off** (v3) | oui, localement | non | non |

Chaque modification incrémente un **numéro de révision**. Un switch qui reçoit une base de révision **plus élevée** que la sienne la remplace entièrement.

## L’incident classique

Un switch récupéré dans un laboratoire est branché en production. Il est en mode server, avec le même nom de domaine VTP et un **numéro de révision plus élevé** — mais avec seulement trois VLAN. Quelques secondes plus tard, tous les switches adoptent sa base : les autres VLAN **disparaissent**, et les ports qui y appartenaient deviennent inactifs. Une partie du site perd le réseau.

> [!WARNING]
> Avant de brancher un switch d’occasion ou de laboratoire, remets son numéro de révision à zéro (par exemple en changeant son nom de domaine VTP, ou en le passant en mode transparent), ou utilise VTP v3.

## Les mots à connaître

- **VTP** — *VLAN Trunking Protocol*, protocole Cisco qui synchronise la liste des VLAN entre switches.
- **Domaine VTP** — Nom partagé par les switches qui se synchronisent entre eux.
- **Numéro de révision** — Compteur incrémenté à chaque modification ; la base la plus récente gagne.

## Teste-toi

**Pourquoi le mode transparent est-il souvent préféré en entreprise ?**

<details><summary>Voir le corrigé</summary>

Parce qu’il **supprime le risque** d’effacement massif : chaque switch garde sa propre liste de VLAN. La création des VLAN sur tous les switches est alors faite par l’administrateur ou, mieux, par un outil d’automatisation.

</details>

<!-- approfondir -->

## Les versions

| Version | Apports |
|---|---|
| v1 / v2 | synchronisation des VLAN 1 à 1005 ; la révision la plus haute gagne |
| **v3** | un seul **serveur primaire** peut écrire (les autres serveurs sont secondaires) ; support des VLAN étendus et de MST ; mot de passe caché ; mode **off** |

En VTP v3, un switch ajouté avec une révision plus haute **ne peut pas** écraser la base s’il n’est pas déclaré primaire. Devenir primaire est une action explicite (`vtp primary`), ce qui supprime l’incident classique.

## Configuration et vérification (Cisco IOS)

```cisco
! Option sûre : chaque switch gère ses VLAN
vtp mode transparent
!
! Ou VTP v3 avec un serveur primaire
vtp domain CAMPUS
vtp version 3
vtp mode server
vtp password Un-Secret-Solide hidden
! puis, en mode privilégié, sur le seul switch qui doit écrire :
! vtp primary vlan
```

```cisco
SW1# show vtp status
VTP Version capable             : 1 to 3
VTP version running             : 3
VTP Domain Name                 : CAMPUS
VTP Operating Mode              : Client
Number of existing VLANs        : 12
Configuration Revision          : 27
Primary ID                      : 00aa.0b00.0001
```

## Élagage (pruning)

Le **VTP pruning** évite d’envoyer le trafic inondé (broadcasts, unicast inconnu) d’un VLAN vers un switch qui n’a aucun port dans ce VLAN. On obtient le même résultat, de façon plus prévisible, en **limitant la liste des VLAN autorisés** sur chaque trunk.

## Exercice

**Un switch client VTP v2 est déplacé dans un autre bâtiment et rebranché un mois plus tard. Entre-temps, sa révision est restée à 40 alors que le domaine est passé à 55. Y a-t-il un risque ?**

<details><summary>Voir le corrigé</summary>

**Non** dans ce cas : sa révision (40) est **plus basse** que celle du domaine (55), il adoptera la base du domaine. Le danger survient quand le switch ajouté a une révision **plus haute**. Mais l’incident montre qu’on ne contrôle pas facilement ces numéros : c’est un argument pour VTP v3 ou le mode transparent.

</details>
