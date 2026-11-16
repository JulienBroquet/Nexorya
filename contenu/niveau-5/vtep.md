---
titre: VTEP
nom: VXLAN Tunnel Endpoint
idee: Le VTEP est le point d’entrée et de sortie des tunnels VXLAN ; il emballe les trames des machines locales et déballe celles qui arrivent des autres VTEP.
osi: "2 et 3"
duree: [5, 10]
prerequis: [vxlan]
retenir:
  - Le VTEP a une **adresse dans l’underlay** (souvent une loopback) — c’est l’adresse source et destination des tunnels.
  - "Il associe chaque **VLAN local** à un **VNI**."
  - Il peut être un switch (**VTEP matériel**) ou un hyperviseur (**VTEP logiciel**).
---

## Le problème

Le VXLAN a besoin, à chaque bout, d’un équipement qui sache **traduire** entre le monde local (une machine dans un VLAN) et le monde des tunnels (un paquet UDP vers un autre site du datacenter).

> [!IMPORTANT] L’idée en une phrase
> Le VTEP est la « gare » du VXLAN : il reçoit les trames des machines, les met dans le tunnel vers le bon VTEP distant, et fait l’inverse à l’arrivée.

## Ce que fait un VTEP

1. Il reçoit une trame d’une VM dans le VLAN 100.
2. Il sait que le VLAN 100 correspond au **VNI 10100**.
3. Il cherche derrière quel VTEP se trouve la MAC de destination (appris par EVPN).
4. Il encapsule la trame (en-têtes VXLAN, UDP, IP avec son adresse de VTEP en source) et l’envoie dans l’underlay.
5. Le VTEP distant déballe la trame et la remet dans **son** VLAN local associé au VNI 10100 (qui peut avoir un autre numéro de VLAN).

## Les mots à connaître

- **VTEP** — Extrémité de tunnel VXLAN, qui encapsule et désencapsule les trames.
- **Interface NVE** — Interface logique d’un switch qui représente son VTEP (Cisco).

## Teste-toi

**Le VNI 10100 correspond au VLAN 100 sur le leaf 1 et au VLAN 250 sur le leaf 2. Les VM peuvent-elles communiquer ?**

<details><summary>Voir le corrigé</summary>

**Oui.** Le numéro de VLAN n’a qu’une portée **locale** à chaque leaf ; c’est le **VNI** qui identifie le segment dans la fabric. Tant que les deux VLAN sont associés au même VNI, les VM sont sur le même segment.

</details>

<!-- approfondir -->

## Vérifier un VTEP (NX-OS)

```text
LEAF1# show nve interface nve1
Interface: nve1, State: Up, encapsulation: VXLAN
 Source-Interface: loopback1 (primary: 10.255.0.11)
LEAF1# show nve peers
Interface Peer-IP          State LearnType Uptime   Router-Mac
--------- ---------------  ----- --------- -------- -----------------
nve1      10.255.0.12      Up    CP        3d02h    5254.0012.0a01
LEAF1# show nve vni
Interface VNI      Multicast-group   State Mode Type [BD/VRF]
nve1      10100    UnicastBGP        Up    CP   L2 [100]
```

`LearnType CP` : le VTEP distant a été appris par le **plan de contrôle** (EVPN), et non par inondation.

## VTEP en paire (anycast VTEP)

Quand deux leafs forment une paire redondante (vPC, MLAG), ils partagent une **même adresse de VTEP** (adresse secondaire de la loopback). Les autres VTEP voient une seule destination et répartissent le trafic vers les deux leafs par ECMP ; la panne d’un leaf est transparente.

## Exercice

**Pourquoi utilise-t-on une interface loopback comme source du VTEP plutôt que l’adresse d’un lien physique ?**

<details><summary>Voir le corrigé</summary>

Une loopback est **toujours active** tant que l’équipement fonctionne, et joignable par **tous** les liens de l’underlay. Si un lien physique tombe, l’adresse du VTEP reste joignable par les autres chemins ECMP, et les tunnels ne sont pas affectés.

</details>
