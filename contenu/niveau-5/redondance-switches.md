---
titre: Redondance de switches
nom: Stacking, MLAG et Cisco vPC
idee: Deux switches peuvent se présenter comme un seul aux équipements voisins ; un serveur ou un switch d’accès s’y relie par un agrégat de deux liens, et survit à la perte d’un des deux switches.
osi: "2"
duree: [8, 16]
cle: true
prerequis: [lacp, stp]
retenir:
  - "**Stacking** — plusieurs switches forment **un seul** équipement (un plan de contrôle, une configuration)."
  - "**MLAG / vPC** — deux switches **restent indépendants** mais présentent un agrégat commun aux voisins."
  - Dans les deux cas, plus de port bloqué par STP — les deux liens sont **actifs**.
  - "Le lien entre les deux switches (**peer-link**) et un lien de surveillance (**keepalive**) sont essentiels pour éviter le « split-brain »."
---

## Le problème

Un serveur a deux cartes réseau, reliées à deux switches pour la redondance. Avec un design classique, STP bloque un des chemins, ou le serveur doit gérer seul ses deux cartes en actif-secours. On voudrait que le serveur voie **un seul agrégat** de deux liens, tous deux actifs, alors qu’ils arrivent sur **deux switches différents**.

> [!IMPORTANT] L’idée en une phrase
> Les deux switches s’entendent pour se présenter comme **un seul partenaire LACP** : le serveur (ou le switch d’accès) fait un agrégat normal vers « un » équipement qui, en réalité, en est deux.

## Les approches

| Technologie | Principe | Plan de contrôle | Exemple |
|---|---|---|---|
| **Stacking** | switches reliés par des câbles de pile, gérés comme un seul | **un seul** | Cisco StackWise sur les Catalyst 9200/9300 |
| **Châssis virtuel** | deux switches de distribution fusionnés logiquement | un seul | Cisco StackWise Virtual (Catalyst 9500/9600) |
| **MLAG / vPC** | deux switches indépendants qui coordonnent l’agrégat | **deux** (configurations séparées) | Cisco vPC (Nexus, NX-OS), MLAG Arista |
| **EVPN multihoming** | agrégat multi-équipements annoncé en EVPN | distribué | fabrics EVPN-VXLAN |

```topologie
titre: Un serveur relié à une paire vPC
N1 switch 0.5,0 "Nexus 1"
N2 switch 2.5,0 "Nexus 2"
SRV serveur 1.5,1.3 "Serveur" "agrégat LACP de 2 liens"
N1 == N2 "peer-link"
N1 ++ SRV
N2 ++ SRV
```

## Les mots à connaître

- **Stacking** — Regroupement de plusieurs switches en un seul équipement logique.
- **MLAG** — *Multi-Chassis Link Aggregation*, agrégat de liens réparti sur deux switches.
- **vPC** — *Virtual Port Channel*, MLAG des switches Cisco Nexus.
- **Peer-link** — Lien entre les deux switches d’une paire MLAG/vPC, pour synchroniser leurs états et transporter le trafic si nécessaire.
- **Split-brain** — Situation où les deux membres d’une paire, ne se voyant plus, se croient chacun seul maître.

## Teste-toi

**Quelle est la différence majeure entre un stack et une paire vPC lors d’une mise à jour logicielle ?**

<details><summary>Voir le corrigé</summary>

Un **stack** a un seul plan de contrôle : la mise à jour concerne l’ensemble, et nécessite souvent un redémarrage de tous les membres (ou une procédure spécifique). Une **paire vPC** a deux équipements indépendants : on met à jour l’un, puis l’autre, sans coupure pour les équipements reliés aux deux.

</details>

<!-- approfondir -->

## Les éléments d’une paire vPC (NX-OS)

```text
feature vpc
feature lacp
vpc domain 10
  peer-keepalive destination 10.99.0.32 source 10.99.0.31 vrf management
  peer-switch
  peer-gateway
  auto-recovery
!
interface port-channel1
  description peer-link
  switchport mode trunk
  vpc peer-link
!
interface port-channel20
  description Serveur ESX-01
  switchport mode trunk
  vpc 20
!
interface Ethernet1/20
  channel-group 20 mode active
```

| Élément | Rôle |
|---|---|
| **Peer-keepalive** | lien de surveillance (souvent par la gestion) : permet de savoir si l’autre switch est vivant quand le peer-link tombe |
| **Peer-link** | synchronise les tables MAC, l’état des vPC ; transporte le trafic des machines raccordées à un seul switch |
| `peer-switch` | les deux switches émettent les mêmes BPDU : la paire apparaît comme une seule racine STP |
| `peer-gateway` | chaque switch route aussi le trafic adressé à la MAC de l’autre (certains équipements visent une MAC réelle plutôt que la MAC HSRP) |

## La règle de boucle du vPC

Un paquet reçu par le peer-link **n’est pas renvoyé** sur un port vPC dont le membre local est actif : le switch voisin l’a déjà livré. Conséquence : un équipement relié à **un seul** switch de la paire (*orphan port*) dépend du peer-link ; on évite ces raccordements autant que possible.

## Vérifier

```text
N1# show vpc brief
vPC domain id                     : 10
Peer status                       : peer adjacency formed ok
vPC keep-alive status             : peer is alive
Configuration consistency status  : success
vPC role                          : primary
id    Port   Status Consistency Reason          Active vlans
--    ----   ------ ----------- ------          ------------
20    Po20   up     success     success         10,20,30
```

`Consistency : success` est indispensable : des paramètres différents entre les deux switches (VLAN autorisés, mode, MTU) suspendent le vPC (incohérences de type 1).

## Exercices

**1.** Le peer-link d’une paire vPC tombe, mais le peer-keepalive fonctionne. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

Le **secondaire**, qui voit grâce au keepalive que le primaire est vivant, **suspend ses ports vPC** pour éviter un split-brain (deux switches qui transmettraient chacun sans coordination). Le trafic passe entièrement par le primaire. Les équipements correctement raccordés aux deux switches restent connectés.

</details>

**2.** Un serveur relié en vPC perd la moitié de ses paquets depuis l’ajout d’un VLAN, ajouté seulement sur le Nexus 1. Explique.

<details><summary>Voir le corrigé</summary>

La configuration des deux membres du vPC n’est plus **cohérente** : le VLAN n’existe pas (ou n’est pas autorisé) côté Nexus 2. Selon le type d’incohérence, ce VLAN est suspendu sur le vPC, ou le trafic haché vers le Nexus 2 est perdu. Ajouter le VLAN sur **les deux** switches, et vérifier `show vpc consistency-parameters`.

</details>
