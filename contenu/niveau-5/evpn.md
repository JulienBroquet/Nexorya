---
titre: EVPN
nom: Ethernet VPN
idee: EVPN utilise BGP pour que les VTEP s’annoncent les adresses MAC et IP des machines qu’ils hébergent ; le datacenter n’a plus besoin d’inonder le réseau pour apprendre où se trouvent les machines.
osi: "plan de contrôle (BGP) pour le niveau 2 et 3"
duree: [8, 18]
prerequis: [vxlan, bgp]
retenir:
  - "EVPN = **plan de contrôle** pour VXLAN (et MPLS) — les MAC et IP sont **annoncées en BGP** au lieu d’être apprises par inondation."
  - "Routes principales — **type 2** (MAC/IP d’une machine), **type 3** (participation d’un VTEP à un VNI), **type 5** (préfixe IP)."
  - "Il permet la **passerelle anycast** — la même passerelle sur tous les leafs, pour router au plus près de chaque machine."
  - Il gère le **multihoming** actif-actif et réduit fortement les broadcasts (suppression d’ARP).
---

## Le problème

Avec VXLAN seul, un VTEP qui ne connaît pas une adresse MAC doit **inonder** la trame vers tous les VTEP du segment pour la trouver, comme un switch classique. Dans un grand datacenter, cela fait beaucoup de trafic inutile, et chaque mouvement de VM met du temps à être appris.

> [!IMPORTANT] L’idée en une phrase
> Avec EVPN, chaque VTEP **annonce** en BGP les machines qu’il héberge : tous les autres savent à l’avance où envoyer le trafic, sans inonder.

## Comment ça marche

```sequence
titre: Une VM apparaît, la fabric l’apprend par BGP
VM A | Leaf 1 (VTEP) | Spine (réflecteur BGP) | Leaf 2 (VTEP)
VM A -> Leaf 1 (VTEP) : première trame (ou ARP) depuis MAC A, IP 10.1.0.15
note Leaf 1 (VTEP) : apprend localement MAC A / 10.1.0.15 dans le VNI 10100
Leaf 1 (VTEP) -> Spine (réflecteur BGP) : route EVPN type 2 : MAC A, IP 10.1.0.15, VNI 10100, via VTEP 10.255.0.11
Spine (réflecteur BGP) -> Leaf 2 (VTEP) : la route est réfléchie à tous les leafs
note Leaf 2 (VTEP) : sait que MAC A est derrière 10.255.0.11 : plus d’inondation nécessaire
```

## Les mots à connaître

- **EVPN** — Famille de routes BGP qui transporte des informations de niveau 2 et 3 (MAC, IP, préfixes) pour construire des réseaux virtuels.
- **Route type 2** — Annonce d’une adresse MAC (et souvent IP) d’une machine, avec son VTEP.
- **Réflecteur de routes** — Routeur BGP qui redistribue les routes reçues à tous ses clients, pour éviter un maillage complet ; souvent les spines.
- **Passerelle anycast** — Même adresse de passerelle configurée sur tous les leafs.

## Teste-toi

**Quel avantage concret EVPN apporte-t-il lors du déplacement d’une VM d’un serveur à un autre ?**

<details><summary>Voir le corrigé</summary>

Dès que la VM se manifeste sur son nouveau leaf, celui-ci **annonce** sa MAC et son IP en BGP ; les autres leafs mettent à jour leur table immédiatement (un numéro de séquence indique la position la plus récente). Avec la **passerelle anycast**, la VM garde la même passerelle, présente localement : le déplacement est presque transparent.

</details>

<!-- approfondir -->

## Les types de routes à connaître

| Type | Contenu | Rôle |
|---|---|---|
| 1 | segment Ethernet (ES) | multihoming : retrait rapide, aliasing |
| 2 | MAC (+ IP) d’une machine | apprentissage sans inondation, suppression d’ARP |
| 3 | VTEP participant à un VNI | construire la liste de réplication du trafic BUM |
| 4 | élection du *designated forwarder* d’un segment | multihoming : éviter les doublons |
| 5 | préfixe IP | routage entre segments et vers l’extérieur (VRF) |

## Routage dans la fabric : IRB symétrique

- Chaque leaf porte la **passerelle anycast** de chaque segment (même IP, même MAC virtuelle partout).
- Le trafic entre deux segments est **routé sur le leaf d’entrée**, puis transporté vers le leaf de sortie dans un **VNI de niveau 3** propre à la VRF (IRB symétrique).
- Résultat : routage au plus près des machines, sans passer par un point central.

## Suppression d’ARP

Comme le leaf connaît déjà l’association IP–MAC (route type 2), il **répond lui-même** aux requêtes ARP des machines locales au lieu de les inonder dans toute la fabric. Les broadcasts diminuent fortement.

## Vérifier (NX-OS)

```text
LEAF2# show bgp l2vpn evpn summary
Neighbor        V    AS MsgRcvd MsgSent   InQ OutQ Up/Down  State/PfxRcd
10.255.0.1      4 65000   21933   18211     0    0    3d02h 412
LEAF2# show bgp l2vpn evpn 10.1.0.15
Route Distinguisher: 10.255.0.11:32867
BGP routing table entry for [2]:[0]:[0]:[48]:[5254.00aa.0015]:[32]:[10.1.0.15]/272
  Path type: internal, path is valid, is best path
  AS-Path: NONE, path sourced internal to AS
    10.255.0.11 (metric 3) from 10.255.0.1 (10.255.0.1)
      Extcommunity: RT:65000:10100 ENCAP:8 Router MAC:5254.0012.0a01
LEAF2# show l2route evpn mac all
```

La route `[2]…[5254.00aa.0015]…[10.1.0.15]` est une route **type 2** : la machine `10.1.0.15` est derrière le VTEP `10.255.0.11`.

## Exercice

**Les VM d’un nouveau VNI ne communiquent pas entre leafs. `show bgp l2vpn evpn` ne montre aucune route type 3 pour ce VNI venant des autres leafs. Que vérifier ?**

<details><summary>Voir le corrigé</summary>

Sans route **type 3**, les leafs ne savent pas qui participe au VNI. Vérifier que le VNI est déclaré sous `evpn` (RD et **Route Targets** d’import/export cohérents sur tous les leafs), qu’il est membre de l’interface NVE avec la bonne méthode de réplication, et que la session BGP EVPN est active.

</details>
