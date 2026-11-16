---
titre: IPv6
nom: Internet Protocol version 6
idee: IPv6 utilise des adresses de 128 bits — assez pour donner une adresse publique à chaque appareil — et simplifie la configuration automatique des machines.
osi: "3"
duree: [10, 20]
prerequis: [ipv4]
retenir:
  - "Une adresse IPv6 = **128 bits**, écrits en 8 groupes hexadécimaux (`2001:db8:10:20::25`)."
  - "On abrège — zéros de tête supprimés, **une seule** suite de groupes nuls remplacée par `::`."
  - Un réseau local fait presque toujours **/64** ; les 64 derniers bits identifient l’interface.
  - Chaque interface a **plusieurs adresses** — au moins une adresse de lien local `fe80::`, souvent une adresse globale.
  - Pas de broadcast — IPv6 utilise le **multicast** et le protocole **NDP**.
---

## Le problème : la pénurie d’adresses

IPv4 offre environ 4,3 milliards d’adresses. C’était énorme en 1981, c’est trop peu aujourd’hui : smartphones, objets connectés, serveurs dans le cloud… Les dernières adresses IPv4 libres ont été distribuées au début des années 2010. On a tenu grâce au [NAT](../niveau-3/nat.md), qui cache des réseaux entiers derrière une seule adresse publique, mais au prix de complications.

> [!IMPORTANT] L’idée en une phrase
> IPv6 utilise des adresses de **128 bits** au lieu de 32 : il y en a assez pour que chaque appareil de la planète ait des milliards d’adresses publiques, sans NAT.

## À quoi ressemble une adresse IPv6 ?

`2001:0db8:0010:0020:0000:0000:0000:0025`

Huit groupes de quatre chiffres hexadécimaux. Comme c’est long, on l’abrège avec deux règles :

1. On supprime les **zéros en tête** de chaque groupe : `2001:db8:10:20:0:0:0:25`.
2. On remplace **une seule** suite de groupes nuls par `::` : `2001:db8:10:20::25`.

> [!WARNING]
> Le `::` ne peut apparaître **qu’une fois** dans une adresse. Sinon, impossible de savoir combien de groupes nuls il remplace à chaque endroit.

## Partie réseau et partie interface

Comme en IPv4, une adresse IPv6 a une partie réseau et une partie machine, séparées par un **préfixe**. Mais en IPv6, la règle est simple : **un réseau local fait /64**.

```text
2001:db8:10:20 : 0000:0000:0000:0025
└── 64 bits réseau ──┘ └──── 64 bits interface ────┘
```

Un /64 contient 2⁶⁴ adresses — 18 milliards de milliards — pour un seul réseau local. On ne compte plus les adresses en IPv6 : on compte les **réseaux**.

## Plusieurs adresses par interface

En IPv6, il est normal qu’une carte réseau ait plusieurs adresses :

| Type | Commence par | Portée | Exemple |
|---|---|---|---|
| **Lien local** | `fe80::` | le lien seulement, jamais routée | `fe80::3e22:fbff:fe1a:97e` |
| **Globale** (publique) | `2000::/3` (souvent `2…` ou `3…`) | Internet | `2001:db8:10:20::25` |
| **Unique locale** (privée) | `fd00::/8` | interne à l’organisation | `fd12:3456:789a:1::25` |
| Boucle locale | `::1` | la machine elle-même | `::1` |

L’adresse de lien local existe **toujours** et sert aux échanges avec les voisins directs : découverte des routeurs, protocoles de routage.

## Pas de broadcast

IPv6 ne connaît **pas** le broadcast. Ce qu’IPv4 faisait en criant à tout le monde (ARP, par exemple), IPv6 le fait avec du **multicast** ciblé et le protocole [NDP](ndp.md). Les machines peuvent même se configurer seules : le routeur annonce le préfixe du réseau, et chaque machine fabrique son adresse.

## Les mots à connaître

- **IPv6** — Version 6 du protocole IP, avec des adresses de 128 bits.
- **Adresse de lien local** — Adresse IPv6 en fe80:: valable uniquement sur le lien, présente sur chaque interface.
- **Adresse globale** — Adresse IPv6 publique, routable sur Internet.
- **/64** — Taille standard d’un réseau local IPv6.
- **Double pile** — Fonctionnement simultané d’IPv4 et d’IPv6 sur les mêmes équipements ; *dual stack*.

## Teste-toi

**1.** Abrège l’adresse `2001:0db8:0000:0000:0001:0000:0000:0010`.

<details><summary>Voir le corrigé</summary>

`2001:db8::1:0:0:10`. On supprime les zéros de tête, puis on remplace la **plus longue** suite de groupes nuls (les groupes 3 et 4, ou 6 et 7 — à longueur égale, la première) par `::`. Les autres groupes nuls restent écrits `0`.

</details>

**2.** Pourquoi `fe80::1` peut-il exister sur toutes les interfaces d’un routeur en même temps ?

<details><summary>Voir le corrigé</summary>

Parce qu’une adresse de lien local n’est valable **que sur son lien** et n’est jamais routée. Il n’y a pas de conflit entre deux liens différents. C’est d’ailleurs une pratique courante de donner `fe80::1` aux passerelles pour les reconnaître facilement.

</details>

<!-- approfondir -->

## L’en-tête IPv6

L’en-tête IPv6 est **fixe** (40 octets) et plus simple que celui d’IPv4 :

| Champ | Taille | Remarque |
|---|---|---|
| Version | 4 bits | 6 |
| Traffic Class | 8 bits | équivalent DSCP + ECN |
| Flow Label | 20 bits | marquage d’un flux |
| Payload Length | 16 bits | taille des données |
| **Next Header** | 8 bits | type de l’en-tête suivant (TCP 6, UDP 17, ICMPv6 58, ou un en-tête d’extension) |
| **Hop Limit** | 8 bits | équivalent du TTL |
| Source, Destination | 128 bits chacune | — |

Disparus par rapport à IPv4 : la **somme de contrôle** (les couches 2 et 4 vérifient déjà), la **fragmentation par les routeurs** (seul l’émetteur fragmente, après découverte de la MTU du chemin) et les options (remplacées par des **en-têtes d’extension** chaînés).

## Les identifiants d’interface

Les 64 bits de droite peuvent être obtenus de plusieurs façons :

| Méthode | Principe | Usage |
|---|---|---|
| **EUI-64** | dérivé de l’adresse MAC : on insère `fffe` au milieu et on inverse le 7ᵉ bit | équipements réseau, anciens systèmes |
| **Aléatoire stable** (RFC 7217) | aléatoire, mais constant pour un réseau donné | adresse principale des systèmes récents |
| **Temporaire** (RFC 8981) | aléatoire, change régulièrement | connexions sortantes, protection de la vie privée |
| **Manuelle / DHCPv6** | attribuée par l’administrateur ou un serveur | serveurs, équipements |

Exemple EUI-64 : MAC `3c:22:fb:1a:09:7e` → `3c22:fbff:fe1a:097e` → 7ᵉ bit inversé (`3c` → `3e`) → identifiant `3e22:fbff:fe1a:97e`.

## Les adresses multicast à reconnaître

| Adresse | Signification |
|---|---|
| `ff02::1` | tous les nœuds du lien |
| `ff02::2` | tous les routeurs du lien |
| `ff02::5`, `ff02::6` | routeurs OSPFv3 |
| `ff02::1:2` | agents DHCPv6 |
| `ff02::1:ff00:0/104` | **multicast de nœud sollicité** : utilisé par NDP à la place d’ARP |

## Plan d’adressage type

Une organisation reçoit généralement un **/48** de son opérateur (ou de son registre régional). Cela laisse **16 bits** pour numéroter ses réseaux : 65 536 réseaux de /64.

```text
2001:db8:abcd::/48               bloc de l'entreprise
2001:db8:abcd:SSVV::/64          SS = site (00 à FF), VV = VLAN (00 à FF)
  2001:db8:abcd:0110::/64        site 01, VLAN 10 (employés)
  2001:db8:abcd:0120::/64        site 01, VLAN 20 (voix)
  2001:db8:abcd:0210::/64        site 02, VLAN 10
```

Reprendre les numéros de site et de VLAN dans l’adresse rend le plan lisible d’un coup d’œil. Sur les liens entre routeurs, on utilise souvent des **/127** (RFC 6164).

## Configurer et vérifier (Cisco IOS)

```cisco
ipv6 unicast-routing
!
interface Vlan10
 ipv6 address 2001:db8:abcd:110::1/64
 ipv6 address fe80::1 link-local
!
R1# show ipv6 interface brief
Vlan10                 [up/up]
    FE80::1
    2001:DB8:ABCD:110::1
```

```bash
# Linux
ip -6 addr show dev eth0
ip -6 route
ping -6 2001:db8:abcd:110::1
```

```powershell
# Windows
netsh interface ipv6 show addresses
ping -6 2001:db8:abcd:110::1
```

La suite pratique — autoconfiguration SLAAC, DHCPv6, routage OSPFv3 — est détaillée dans [IPv6 en pratique](ipv6-pratique.md).

## Exercices

**1.** Quelle est l’adresse de lien local EUI-64 d’une interface dont la MAC est `00:1a:2b:3c:4d:5e` ?

<details><summary>Voir le corrigé</summary>

On coupe la MAC en deux : `001a2b` et `3c4d5e`, on insère `fffe` : `001a:2bff:fe3c:4d5e`. On inverse le 7ᵉ bit du premier octet : `00` → `02`. Résultat : **`fe80::21a:2bff:fe3c:4d5e`**.

</details>

**2.** Une entreprise a reçu `2001:db8:500::/48`. Combien de réseaux /64 peut-elle créer, et quel serait le préfixe du VLAN 30 du site 4 avec le plan « SSVV » ?

<details><summary>Voir le corrigé</summary>

64 − 48 = 16 bits → **65 536** réseaux /64. Site 04, VLAN 30 → quatrième groupe `0430` → **`2001:db8:500:430::/64`**.

</details>

**3.** Pourquoi l’absence de somme de contrôle dans l’en-tête IPv6 accélère-t-elle les routeurs ?

<details><summary>Voir le corrigé</summary>

En IPv4, chaque routeur doit **recalculer** la somme de contrôle de l’en-tête après avoir décrémenté le TTL. En IPv6, le Hop Limit est décrémenté sans aucun recalcul. Les erreurs sont détectées par le FCS Ethernet et par la somme de contrôle de TCP ou UDP (obligatoire en IPv6).

</details>
