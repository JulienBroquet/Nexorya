---
titre: IS-IS
nom: Intermediate System to Intermediate System
idee: IS-IS est un protocole à état de liens, cousin d’OSPF, très apprécié des opérateurs et des datacenters pour sa robustesse et sa facilité à transporter IPv4 et IPv6 ensemble.
osi: "3 (transporté directement sur la couche 2)"
duree: [6, 12]
prerequis: [ospf]
retenir:
  - Comme OSPF, IS-IS diffuse une **carte** du réseau et calcule les chemins avec **Dijkstra**.
  - Il fonctionne **directement sur la couche 2**, sans IP — il est donc indépendant de la version d’IP transportée.
  - "Hiérarchie en deux niveaux — **niveau 1** (dans une zone) et **niveau 2** (entre zones)."
  - Très utilisé comme **underlay** dans les réseaux d’opérateurs et les fabrics de datacenter.
---

## Le problème

Les opérateurs ont besoin d’un protocole à état de liens qui tienne des milliers de routeurs, se configure simplement, et transporte IPv4 et IPv6 sans tout dupliquer. IS-IS, conçu à l’origine pour la pile OSI, s’est imposé dans ce rôle.

> [!IMPORTANT] L’idée en une phrase
> IS-IS fait le même travail qu’OSPF — une carte partagée, puis un calcul de chemin — mais fonctionne directement sur Ethernet, ce qui le rend indépendant d’IP et très robuste.

## Ce qui le distingue d’OSPF

| | OSPF | IS-IS |
|---|---|---|
| Transport | dans IP (protocole 89) | directement dans la trame (couche 2) |
| IPv6 | OSPFv3, un processus séparé | les mêmes adjacences transportent IPv4 et IPv6 |
| Hiérarchie | zones autour de la zone 0 | niveaux 1 et 2 ; les frontières passent **sur les liens**, pas dans les routeurs |
| Usage typique | entreprises | opérateurs, datacenters (underlay) |

```topologie
titre: IS-IS en deux niveaux
zone "Zone 49.0001" 0,0 1,1.3
zone "Zone 49.0002" 3,0 4,1.3
A1 routeur 0,1.3 "R-A1" "niveau 1"
A2 routeur 1,0 "R-A2" "niveaux 1 et 2"
B2 routeur 3,0 "R-B2" "niveaux 1 et 2"
B1 routeur 4,1.3 "R-B1" "niveau 1"
A1 -- A2 "L1"
A2 ++ B2 "L2 : épine dorsale"
B2 -- B1 "L1"
```

## Les mots à connaître

- **IS-IS** — Protocole de routage à état de liens, issu de la pile OSI.
- **NET** — *Network Entity Title*, adresse qui identifie un routeur IS-IS (zone + identifiant système).
- **Niveau 1 / niveau 2** — Routage à l’intérieur d’une zone / entre les zones.
- **Underlay** — Réseau de transport routé sur lequel s’appuient des réseaux virtuels (VXLAN, MPLS).

## Teste-toi

**Pourquoi un pare-feu qui filtre le protocole IP 89 n’empêche-t-il pas IS-IS de fonctionner ?**

<details><summary>Voir le corrigé</summary>

Parce qu’IS-IS **n’est pas transporté dans IP** : ses messages sont directement encapsulés dans des trames de couche 2. Un filtrage IP ne le voit pas. (Pour la même raison, IS-IS ne traverse pas un routeur : ses voisins doivent être sur le même lien.)

</details>

<!-- approfondir -->

## L’adresse NET

Chaque routeur reçoit une adresse **NET**, par exemple `49.0001.0102.5525.5001.00` :

| Partie | Exemple | Signification |
|---|---|---|
| AFI + zone | `49.0001` | 49 = adresse privée ; 0001 = numéro de zone |
| System ID | `0102.5525.5001` | identifiant unique du routeur (souvent dérivé de sa loopback 10.255.255.1) |
| NSEL | `00` | toujours 00 pour un routeur |

## Configuration (Cisco IOS)

```cisco
router isis CORE
 net 49.0001.0102.5525.5001.00
 is-type level-2-only
 metric-style wide
 address-family ipv6
  multi-topology
!
interface GigabitEthernet0/0/1
 ip router isis CORE
 ipv6 router isis CORE
 isis network point-to-point
!
R1# show isis neighbors
System Id      Type Interface   IP Address      State Holdtime Circuit Id
R2             L2   Gi0/0/1     10.255.0.2      UP    27       00
R1# show ip route isis
i L2  10.255.255.2/32 [115/20] via 10.255.0.2, GigabitEthernet0/0/1
```

`metric-style wide` est indispensable : les métriques « étroites » historiques plafonnent à 63 par lien. Dans un datacenter ou un cœur d’opérateur, on choisit souvent une seule couche (`level-2-only`) pour rester simple.

## Exercice

**Pourquoi IS-IS est-il souvent choisi comme protocole d’underlay pour une fabric VXLAN ?**

<details><summary>Voir le corrigé</summary>

Il converge vite, passe très bien à l’échelle, transporte **IPv4 et IPv6 dans les mêmes adjacences**, ne dépend pas d’IP pour fonctionner, et sa configuration est compacte. Son seul rôle dans une fabric est d’assurer la joignabilité entre les loopbacks des switches ; les réseaux des clients sont transportés par l’overlay (VXLAN, EVPN).

</details>
