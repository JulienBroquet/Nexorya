---
titre: MPLS
nom: Multiprotocol Label Switching
idee: MPLS fait circuler les paquets dans le réseau d’un opérateur grâce à de courtes étiquettes ; il permet de construire, pour chaque client, un réseau privé virtuel isolé des autres.
osi: "« 2,5 » — entre l’Ethernet et l’IP"
duree: [9, 20]
prerequis: [ospf, bgp]
retenir:
  - Une **étiquette** de 4 octets est ajoutée devant le paquet IP ; les routeurs du cœur décident d’après elle.
  - "Rôles — **CE** (routeur du client), **PE** (bordure de l’opérateur), **P** (cœur de l’opérateur)."
  - "Le **L3VPN MPLS** isole chaque client dans une **VRF** sur les PE ; MP-BGP transporte ses routes."
  - Les clients peuvent utiliser les **mêmes adresses privées** sans conflit.
---

## Le problème : un opérateur, des milliers de clients

Un opérateur transporte le trafic de milliers d’entreprises. Chacune veut que ses sites se parlent comme sur un réseau privé, avec ses propres adresses (souvent les mêmes `10.x.x.x` que les autres clients), et sans jamais voir le trafic des autres.

> [!IMPORTANT] L’idée en une phrase
> À l’entrée du réseau de l’opérateur, chaque paquet reçoit une **étiquette** qui indique à la fois le chemin à suivre et le client auquel il appartient ; les routeurs du cœur ne lisent que cette étiquette.

## Les rôles

```topologie
titre: Un VPN MPLS d’opérateur
CEA1 routeur 0,0 "CE client A" "site Paris"
CEB1 routeur 0,1 "CE client B" "site Paris"
PE1 routeur 1.5,0.5 "PE1"
P1 routeur 3,0.5 "P"
PE2 routeur 4.5,0.5 "PE2"
CEA2 routeur 6,0 "CE client A" "site Lyon"
CEB2 routeur 6,1 "CE client B" "site Lyon"
CEA1 -- PE1
CEB1 -- PE1
PE1 -- P1 "étiquettes"
P1 -- PE2 "étiquettes"
PE2 -- CEA2
PE2 -- CEB2
zone "Réseau de l’opérateur" 1.5,0.5 4.5,0.5
```

| Rôle | Où | Ce qu’il fait |
|---|---|---|
| **CE** (*Customer Edge*) | chez le client | routeur ordinaire, ne connaît pas MPLS |
| **PE** (*Provider Edge*) | bordure de l’opérateur | sépare les clients dans des **VRF**, ajoute et retire les étiquettes |
| **P** (*Provider*) | cœur de l’opérateur | commute selon les étiquettes, ignore tout des clients |

## Les mots à connaître

- **MPLS** — Technique d’acheminement par étiquettes utilisée dans les réseaux d’opérateurs.
- **Étiquette** — Petit champ de 4 octets qui détermine le traitement d’un paquet dans le réseau MPLS ; *label*.
- **L3VPN** — Réseau privé virtuel de niveau 3 construit par l’opérateur sur MPLS.
- **CE / PE / P** — Routeurs du client, de bordure de l’opérateur et de cœur de l’opérateur.

## Teste-toi

**Les clients A et B utilisent tous deux `10.1.0.0/16`. Comment l’opérateur évite-t-il le conflit ?**

<details><summary>Voir le corrigé</summary>

Sur les PE, chaque client a sa propre **VRF**, c’est-à-dire sa propre table de routage : `10.1.0.0/16` existe deux fois, dans deux tables séparées. Dans le cœur, les paquets portent une étiquette différente selon le client. Les deux réseaux ne se rencontrent jamais.

</details>

<!-- approfondir -->

## L’étiquette

```text
┌────────────────────────┬─────┬───┬─────────┐
│ Valeur de l’étiquette  │ TC  │ S │  TTL    │
│ 20 bits                │ 3 b │1 b│ 8 bits  │
└────────────────────────┴─────┴───┴─────────┘
```

- **TC** : classe de trafic (QoS).
- **S** : fin de pile ; plusieurs étiquettes peuvent être empilées.

Dans un L3VPN, un paquet porte en général **deux** étiquettes :

1. l’étiquette **de transport** (externe) : comment aller jusqu’au PE de sortie, distribuée par **LDP** ou **segment routing** ;
2. l’étiquette **de service** (interne) : à quelle VRF remettre le paquet sur le PE de sortie, distribuée par **MP-BGP**.

Les routeurs P échangent seulement l’étiquette externe. L’avant-dernier routeur la retire souvent (*penultimate hop popping*), pour que le PE de sortie n’ait qu’à lire l’étiquette de service.

## Comment les routes des clients circulent

1. Le CE annonce ses réseaux au PE (statique, BGP, OSPF).
2. Le PE les place dans la VRF du client, leur ajoute un **Route Distinguisher** (pour les rendre uniques) et des **Route Targets** (pour indiquer quelles VRF doivent les importer).
3. Il les envoie aux autres PE en **MP-BGP** (famille VPNv4), avec l’étiquette de service.
4. Les autres PE importent les routes dans les VRF dont les Route Targets correspondent.

## Vu du client

Pour l’entreprise cliente, le L3VPN est un **grand routeur** : chaque site annonce ses réseaux à l’opérateur et reçoit ceux des autres sites. Les points à négocier :

- le **protocole** CE–PE (souvent eBGP) et les préfixes annoncés ;
- les **classes de service** : marquage DSCP attendu par l’opérateur et capacité par classe ;
- la **redondance** : deux CE, deux PE, deux liens physiquement distincts ;
- la **supervision** du contrat (latence, pertes, disponibilité).

## Exercice

**Pourquoi les routeurs P n’ont-ils pas besoin de connaître les routes des clients ?**

<details><summary>Voir le corrigé</summary>

Parce qu’ils ne décident qu’**à partir de l’étiquette de transport**, qui indique le chemin vers le PE de sortie. Les routes des clients ne sont connues que des PE. Cela permet au cœur de rester simple et rapide, même avec des millions de routes de clients.

</details>
