---
titre: "Labo 2 — Des VLAN qui se parlent"
actif: pratique
chapeau: Tu vas séparer un réseau en trois VLAN sur deux switches, les relier par un trunk, puis les faire communiquer à travers un routeur.
---

> [!IMPORTANT] Objectif
> Créer des VLAN, configurer ports d’accès et trunk 802.1Q, puis mettre en place un routage inter-VLAN (« routeur sur un bâton ») avec une passerelle par VLAN.

**Durée** : 1 heure. **Fiches utiles** : [VLAN](../niveau-1/vlan.md), [802.1Q](../niveau-1/802-1q.md), [La passerelle](../niveau-2/passerelle.md).

## La topologie

```topologie
titre: Labo 2
R1 routeur 1.5,0 "R1" "Gi0/0 : sous-interfaces"
SW1 switch 0.5,1.2 "SW1"
SW2 switch 2.5,1.2 "SW2"
A pc 0,2.4 "PC-Admin" "VLAN 10"
B pc 1,2.4 "PC-Compta" "VLAN 20"
C pc 2,2.4 "PC-Admin2" "VLAN 10"
D imprimante 3,2.4 "Imprimante" "VLAN 30"
R1 == SW1 "trunk"
SW1 == SW2 "trunk"
SW1 -- A
SW1 -- B
SW2 -- C
SW2 -- D
```

| VLAN | Nom | Réseau | Passerelle |
|---|---|---|---|
| 10 | ADMIN | 192.168.10.0/24 | 192.168.10.1 |
| 20 | COMPTA | 192.168.20.0/24 | 192.168.20.1 |
| 30 | IMPRIMANTES | 192.168.30.0/24 | 192.168.30.1 |

## Étape 1 — Créer les VLAN (sur SW1 et SW2)

```cisco
SW1# configure terminal
SW1(config)# vlan 10
SW1(config-vlan)# name ADMIN
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name COMPTA
SW1(config-vlan)# vlan 30
SW1(config-vlan)# name IMPRIMANTES
```

## Étape 2 — Ports d’accès

```cisco
SW1(config)# interface Fa0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# interface Fa0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20
```

Même principe sur SW2 (PC-Admin2 en VLAN 10, imprimante en VLAN 30).

## Étape 3 — Les trunks

```cisco
SW1(config)# interface Gi0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,30
```

À faire sur le lien SW1–SW2 (des deux côtés) et sur le lien SW1–R1.

**Test intermédiaire** : PC-Admin (192.168.10.11) doit joindre PC-Admin2 (192.168.10.12) à travers le trunk. PC-Admin ne doit **pas** joindre PC-Compta.

## Étape 4 — Le routage inter-VLAN

```cisco
R1(config)# interface Gi0/0
R1(config-if)# no shutdown
R1(config-if)# interface Gi0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config-subif)# interface Gi0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
R1(config-subif)# interface Gi0/0.30
R1(config-subif)# encapsulation dot1Q 30
R1(config-subif)# ip address 192.168.30.1 255.255.255.0
```

Donne à chaque PC la passerelle de son VLAN. PC-Compta doit maintenant joindre l’imprimante.

## Vérifier

```cisco
SW1# show vlan brief
SW1# show interfaces trunk
R1#  show ip interface brief
R1#  show ip route connected
```

## Questions

**1.** Avant l’étape 4, pourquoi PC-Admin ne joint-il pas PC-Compta, alors qu’ils sont sur le même switch ?

**2.** Tu oublies d’autoriser le VLAN 30 sur le trunk SW1–SW2. Quel symptôme ?

**3.** En mode simulation, observe une trame entre SW1 et R1. Qu’a-t-elle de particulier ?

<details><summary>Voir le corrigé</summary>

**1.** Les VLAN sont des **réseaux séparés** : le switch ne fait jamais passer une trame d’un VLAN à l’autre. Et les deux PC sont dans des sous-réseaux IP différents : il faut un **routeur**.

**2.** L’imprimante, sur SW2, devient injoignable depuis tout le monde (y compris sa passerelle) : son VLAN ne traverse plus le trunk. `show interfaces trunk` le montre dans la liste des VLAN autorisés.

**3.** Elle porte une **étiquette 802.1Q** avec le numéro de VLAN : c’est ce qui permet au routeur de savoir à quelle sous-interface elle appartient.

</details>

## Pour aller plus loin

Remplace le routeur par un **switch de niveau 3** avec des interfaces `interface vlan 10` (SVI) et `ip routing`. C’est la solution utilisée en entreprise : quel avantage par rapport au routeur sur un bâton ?

**Suite** : [Labo 3 — Redondance sans boucle](labo-3-redondance.md).
