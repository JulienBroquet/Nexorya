---
titre: VXLAN
nom: Virtual Extensible LAN
idee: VXLAN transporte des trames Ethernet dans des paquets UDP à travers un réseau routé ; on peut ainsi offrir un même segment de niveau 2 à des machines situées dans des baies différentes, sans étendre de VLAN ni de Spanning Tree.
osi: "tunnel de niveau 2 dans UDP 4789"
duree: [9, 20]
prerequis: [vlan, ecmp]
retenir:
  - "Le **VNI** (24 bits) identifie le segment — 16 millions de segments possibles, contre 4 094 VLAN."
  - Le réseau physique (**underlay**) est **routé** ; les segments (**overlay**) sont transportés dans des tunnels.
  - Les extrémités des tunnels sont des **VTEP**, souvent les switches leaf.
  - "VXLAN ajoute **50 octets** — l’underlay doit avoir une MTU plus grande (souvent 9 216)."
---

## Le problème

Dans un datacenter, une machine virtuelle doit pouvoir être déplacée d’un serveur à un autre, dans une autre baie, **sans changer d’adresse IP**. Il faut donc que son réseau de niveau 2 existe partout. Étendre un VLAN dans tout le datacenter ramène les problèmes de STP, des grands domaines de diffusion… et la limite de 4 094 VLAN quand on héberge des centaines de clients.

> [!IMPORTANT] L’idée en une phrase
> VXLAN emballe chaque trame Ethernet dans un paquet UDP et l’envoie à travers un réseau entièrement routé ; à l’arrivée, la trame est déballée comme si elle avait traversé un simple switch.

## Overlay et underlay

```topologie
titre: Deux VM du même segment dans deux baies
VM1 vm 0,1.3 "VM A" "VNI 10100"
L1 switch 1,0.6 "Leaf 1" "VTEP 10.255.0.11"
S switch 2.5,0 "Spines" "underlay routé"
L2 switch 4,0.6 "Leaf 2" "VTEP 10.255.0.12"
VM2 vm 5,1.3 "VM B" "VNI 10100"
VM1 -- L1
L1 -- S
S -- L2
L2 -- VM2
L1 .. L2 "tunnel VXLAN"
```

- **Underlay** : le réseau physique, routé (OSPF, IS-IS ou BGP), qui relie les VTEP entre eux. Il ne connaît que les adresses des VTEP.
- **Overlay** : les segments virtuels (VNI) transportés dans les tunnels. Les VM s’y voient comme si elles étaient sur le même switch.

## Les mots à connaître

- **VXLAN** — Encapsulation de trames Ethernet dans UDP pour créer des réseaux de niveau 2 virtuels sur un réseau routé.
- **VNI** — *VXLAN Network Identifier*, numéro de segment sur 24 bits.
- **VTEP** — Équipement qui encapsule et désencapsule le VXLAN.
- **Underlay / overlay** — Réseau physique de transport / réseau virtuel construit au-dessus.

## Teste-toi

**Pourquoi VXLAN utilise-t-il UDP plutôt que de transporter directement les trames dans IP ?**

<details><summary>Voir le corrigé</summary>

Parce que le **port source UDP** varie selon le flux encapsulé : les switches de l’underlay, qui hachent sur les ports, répartissent ainsi les différents flux sur tous les chemins **ECMP**. Une encapsulation sans ports serait toujours hachée de la même façon.

</details>

<!-- approfondir -->

## L’encapsulation

```text
┌──────────────┬──────────────┬─────────────┬──────────────┬────────────────────────────┐
│ Ethernet ext.│ IP externe   │ UDP         │ VXLAN        │ Trame Ethernet d’origine   │
│ 14 octets    │ 20 octets    │ 8 octets    │ 8 octets     │ (MAC VM A → MAC VM B…)     │
│              │ VTEP1→VTEP2  │ dst 4789    │ VNI = 10100  │                            │
└──────────────┴──────────────┴─────────────┴──────────────┴────────────────────────────┘
                            ≈ 50 octets ajoutés
```

## Comment un VTEP apprend où envoyer

Le VTEP doit savoir derrière quel autre VTEP se trouve chaque adresse MAC du segment. Deux approches :

| Méthode | Principe | Usage |
|---|---|---|
| **Apprentissage par inondation** | le trafic inconnu est envoyé à tous les VTEP du VNI (multicast underlay ou réplication en tête), et l’on apprend les MAC au retour | historique, petits déploiements |
| **Plan de contrôle EVPN** | les VTEP s’annoncent leurs MAC et IP en BGP | standard actuel ; voir [EVPN](evpn.md) |

## Configuration simplifiée (NX-OS, avec EVPN)

```text
feature nv overlay
feature vn-segment-vlan-based
nv overlay evpn
!
vlan 100
  vn-segment 10100
!
interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback1
  member vni 10100
    ingress-replication protocol bgp
```

## MTU : l’erreur classique

Les VM envoient des trames de 1 500 octets ; encapsulées, elles font environ 1 550 octets. Si l’underlay reste à 1 500, **les petits paquets passent, les gros sont perdus** : pings OK, transferts bloqués. Il faut une MTU d’au moins 1 550 (en pratique **9 216**) sur **tous** les liens de l’underlay. Voir [MTU](../niveau-1/mtu.md).

## Exercice

**Les VTEP se pinguent entre eux, mais deux VM du même VNI ne communiquent pas. Quelles vérifications faire ?**

<details><summary>Voir le corrigé</summary>

Que le **VNI** est identique et bien associé au bon VLAN sur les deux leafs ; que les VTEP connaissent les MAC distantes (**EVPN** : routes type 2 reçues) ; que l’**UDP 4789** n’est pas filtré ; que la **MTU** de l’underlay accepte les paquets encapsulés (tester avec un ping de grande taille sans fragmentation entre loopbacks des VTEP).

</details>
