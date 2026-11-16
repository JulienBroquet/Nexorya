---
titre: QinQ
nom: Empilement de VLAN (IEEE 802.1ad)
idee: QinQ ajoute une seconde étiquette VLAN par-dessus celle du client ; un opérateur peut ainsi transporter les VLAN de plusieurs clients sans qu’ils se mélangent.
osi: "2"
duree: [6, 12]
prerequis: [802-1q]
retenir:
  - Une **étiquette extérieure** (S-VLAN, celle de l’opérateur) enveloppe l’étiquette du client (C-VLAN).
  - Deux clients peuvent utiliser le **même numéro de VLAN** sans conflit, car l’opérateur les sépare par leur S-VLAN.
  - Chaque étiquette ajoute **4 octets** — la MTU du réseau de l’opérateur doit en tenir compte.
---

## Le problème : deux clients, le même VLAN 10

Un opérateur relie les sites de ses clients à travers une ville. Le client A utilise les VLAN 10 à 50 entre ses deux sites. Le client B utilise aussi le VLAN 10. Si l’opérateur transportait ces VLAN tels quels, le VLAN 10 de A et celui de B se mélangeraient. Demander aux clients de renuméroter leurs VLAN est impossible avec des centaines de clients.

> [!IMPORTANT] L’idée en une phrase
> L’opérateur ajoute **sa propre étiquette** par-dessus celle du client : une étiquette par client. À l’intérieur, le client garde ses VLAN tels quels.

## Comment ça marche

```topologie
titre: Deux clients, le même VLAN 10, aucun mélange
A1 switch 0,0 "Client A, site 1" "VLAN 10 à 50"
B1 switch 0,1 "Client B, site 1" "VLAN 10"
PE1 switch 1.5,0.5 "Opérateur"
PE2 switch 3.5,0.5 "Opérateur"
A2 switch 5,0 "Client A, site 2"
B2 switch 5,1 "Client B, site 2"
A1 -- PE1 "S-VLAN 100"
B1 -- PE1 "S-VLAN 200"
PE1 -- PE2 "trames à deux étiquettes"
PE2 -- A2
PE2 -- B2
```

1. Le client A envoie une trame du VLAN 10 (étiquette **client**, C-VLAN 10).
2. Le switch d’entrée de l’opérateur ajoute une étiquette **opérateur** : S-VLAN 100 pour le client A, S-VLAN 200 pour le client B.
3. Dans le réseau de l’opérateur, seule l’étiquette extérieure compte : les trames de A et de B voyagent dans deux « tunnels » séparés.
4. À la sortie, l’opérateur retire son étiquette et remet au client sa trame d’origine, VLAN 10 intact.

## Les mots à connaître

- **QinQ** — Technique qui empile deux étiquettes VLAN dans une même trame ; normalisée sous le nom 802.1ad.
- **S-VLAN** — VLAN de service, l’étiquette extérieure ajoutée par l’opérateur.
- **C-VLAN** — VLAN du client, l’étiquette intérieure d’origine.

## Teste-toi

**Pourquoi QinQ permet-il de dépasser la limite de 4 094 VLAN ?**

<details><summary>Voir le corrigé</summary>

Parce que chaque client dispose de ses propres 4 094 VLAN **à l’intérieur** de son S-VLAN. L’opérateur peut avoir jusqu’à 4 094 clients, chacun avec ses 4 094 VLAN : environ 16 millions de combinaisons.

</details>

<!-- approfondir -->

## Format de la trame

```text
┌─────────┬─────────┬─────────────────────┬─────────────────────┬──────┬─────────┬─────┐
│MAC dest │MAC src  │ S-tag : TPID 0x88A8 │ C-tag : TPID 0x8100 │ Type │ Données │ FCS │
│         │         │ VID = 100           │ VID = 10            │      │         │     │
└─────────┴─────────┴─────────────────────┴─────────────────────┴──────┴─────────┴─────┘
```

La norme 802.1ad utilise le TPID **0x88A8** pour l’étiquette extérieure. Certains équipements anciens utilisent 0x8100 (ou 0x9100) pour les deux : il faut alors aligner ce réglage entre les équipements de l’opérateur.

Avec deux étiquettes, la trame transportant un paquet de 1 500 octets mesure **1 526 octets** : le réseau de l’opérateur doit accepter une MTU d’au moins 1 504 octets de charge (souvent davantage, avec des jumbo frames).

## Configuration d’un port tunnel (Cisco IOS, Catalyst)

```cisco
! Port côté client A : tout ce qui entre est encapsulé dans le S-VLAN 100
interface GigabitEthernet1/0/1
 description Client A - site 1
 switchport access vlan 100
 switchport mode dot1q-tunnel
 l2protocol-tunnel cdp
 l2protocol-tunnel stp
 l2protocol-tunnel vtp
 no cdp enable
!
! MTU système pour accepter la double étiquette
system mtu 1504
```

- `switchport mode dot1q-tunnel` : le port accepte les trames du client, étiquetées ou non, et leur ajoute le S-VLAN 100.
- `l2protocol-tunnel` : transporte de façon transparente les protocoles de contrôle du client (CDP, STP, VTP) au lieu que les switches de l’opérateur les interprètent.

## Alternatives modernes

QinQ reste courant chez les opérateurs métropolitains (MAN) et pour séparer des locataires dans des bâtiments partagés. Pour des services à grande échelle, on lui préfère souvent des services Ethernet sur **MPLS** (VPLS) ou **EVPN**, qui s’appuient sur un réseau IP routé et ne dépendent pas d’un arbre STP étendu. Voir le [niveau 5](../niveau-5/index.html).

## Exercice

**Un opérateur configure correctement QinQ, mais les grosses trames d’un client sont perdues alors que les petites passent. Quelle vérification ?**

<details><summary>Voir le corrigé</summary>

La **MTU** du réseau de l’opérateur. Les deux étiquettes ajoutent 8 octets : une trame cliente pleine (1 518 + 4 de son étiquette) devient trop grande pour des liens configurés à la taille standard. Il faut augmenter la MTU sur tous les liens du chemin (`system mtu 1504` au minimum, ou des jumbo frames).

</details>
