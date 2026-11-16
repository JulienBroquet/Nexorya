---
titre: "Labo 4 — Plusieurs sites routés"
actif: pratique
chapeau: Trois sites, trois routeurs. Tu vas les faire découvrir leurs réseaux avec OSPF, distribuer les adresses depuis un serveur central, et donner accès à Internet par le NAT.
---

> [!IMPORTANT] Objectif
> Configurer OSPF en zone unique, un serveur DHCP central avec relais, une route par défaut propagée, et du NAT (PAT) vers Internet.

**Durée** : 1 h 30. **Fiches utiles** : [OSPF](../niveau-2/ospf.md), [DHCP](../niveau-3/dhcp.md), [NAT](../niveau-3/nat.md), [Routage statique](../niveau-2/routage-statique.md).

## La topologie

```topologie
titre: Labo 4
INT nuage 1.5,0 "Internet" "203.0.113.1"
SIEGE routeur 1.5,1.2 "R-SIEGE" "Gi0/2 : 203.0.113.2"
SRV serveur 3,1.2 "Serveur DHCP" "10.0.0.10/24"
A routeur 0.5,2.6 "R-LYON"
B routeur 2.5,2.6 "R-NANTES"
PA pc 0.5,3.8 "PC Lyon" "10.1.10.0/24"
PB pc 2.5,3.8 "PC Nantes" "10.2.10.0/24"
INT -- SIEGE
SIEGE -- SRV "10.0.0.0/24"
SIEGE -- A "10.255.0.0/30"
SIEGE -- B "10.255.0.4/30"
A -- B "10.255.0.8/30"
A -- PA
B -- PB
```

## Plan d’adressage

| Lien ou réseau | Adresses |
|---|---|
| R-SIEGE ↔ R-LYON | 10.255.0.1 / 10.255.0.2 (/30) |
| R-SIEGE ↔ R-NANTES | 10.255.0.5 / 10.255.0.6 (/30) |
| R-LYON ↔ R-NANTES | 10.255.0.9 / 10.255.0.10 (/30) |
| Serveurs siège | 10.0.0.0/24, passerelle 10.0.0.1 |
| Postes Lyon | 10.1.10.0/24, passerelle 10.1.10.1 |
| Postes Nantes | 10.2.10.0/24, passerelle 10.2.10.1 |

## Étape 1 — Adresses et OSPF

Configure les adresses des interfaces, puis OSPF sur chaque routeur :

```cisco
R-LYON(config)# router ospf 1
R-LYON(config-router)# router-id 1.1.1.2
R-LYON(config-router)# network 10.0.0.0 0.255.255.255 area 0
R-LYON(config-router)# passive-interface Gi0/0
```

`passive-interface` sur l’interface des postes : le réseau est annoncé, mais on n’envoie pas d’OSPF vers les PC.

```cisco
R-LYON# show ip ospf neighbor
R-LYON# show ip route ospf
```

Chaque routeur doit voir les réseaux des autres sites avec la lettre **O**.

## Étape 2 — DHCP central et relais

Sur le serveur, crée deux plages : `10.1.10.0/24` (passerelle 10.1.10.1) et `10.2.10.0/24` (passerelle 10.2.10.1). Sur les routeurs des sites :

```cisco
R-LYON(config)# interface Gi0/0
R-LYON(config-if)# ip helper-address 10.0.0.10
```

Passe les PC en DHCP : ils doivent recevoir une adresse de **leur** site.

## Étape 3 — Internet et NAT

```cisco
R-SIEGE(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
R-SIEGE(config)# router ospf 1
R-SIEGE(config-router)# default-information originate
R-SIEGE(config)# access-list 1 permit 10.0.0.0 0.255.255.255
R-SIEGE(config)# ip nat inside source list 1 interface Gi0/2 overload
R-SIEGE(config)# interface Gi0/2
R-SIEGE(config-if)# ip nat outside
R-SIEGE(config-if)# interface range Gi0/0 - 1
R-SIEGE(config-if-range)# ip nat inside
```

N’oublie pas `ip nat inside` sur toutes les interfaces internes, y compris celle des serveurs.

## Étape 4 — Panne et reconvergence

Lance un `ping -t` de Lyon vers le serveur DHCP, puis coupe le lien R-SIEGE ↔ R-LYON. Le trafic doit passer par Nantes après quelques secondes. Observe `show ip route` sur R-LYON avant et après.

## Questions

**1.** Pourquoi le relais DHCP est-il nécessaire ?

**2.** Les sites voient-ils la route par défaut ? Avec quel code dans la table de routage ?

**3.** Après la coupure, combien de temps la reprise a-t-elle pris ? Quel mécanisme la raccourcirait ?

<details><summary>Voir le corrigé</summary>

**1.** La demande DHCP d’un PC est un **broadcast**, qui ne traverse pas les routeurs. Le relais (`ip helper-address`) la reçoit et la transmet en **unicast** au serveur, en indiquant le réseau d’origine pour que le serveur choisisse la bonne plage.

**2.** Oui, grâce à `default-information originate` : elle apparaît comme **O\*E2 0.0.0.0/0**.

**3.** Avec les temporisateurs OSPF par défaut, si la coupure n’est pas vue directement par l’interface (par exemple à travers un switch), jusqu’à **40 secondes** (dead interval). En coupant le câble, l’interface tombe et la reprise est quasi immédiate. Pour détecter vite une panne invisible, on utilise [BFD](../niveau-2/bfd.md).

</details>

**Suite** : [Labo 5 — Sécuriser](labo-5-securite.md).
