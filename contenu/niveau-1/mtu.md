---
titre: MTU
nom: Maximum Transmission Unit
idee: La MTU est la taille maximale d’un paquet qu’un lien accepte ; quand un tunnel ou une étiquette ajoute des octets, les gros paquets peuvent ne plus passer alors que les petits passent.
osi: "2 et 3"
duree: [7, 16]
prerequis: [ethernet]
retenir:
  - La MTU Ethernet standard est de **1 500 octets** de paquet IP.
  - Les tunnels et encapsulations (VPN, VXLAN, MPLS, QinQ) **ajoutent des en-têtes** — il faut plus de place, ou des paquets plus petits.
  - "Signature d’un problème de MTU — **les petits paquets passent, les gros non** (le ping marche, les transferts se figent)."
---

## Le problème : un colis trop gros pour la boîte aux lettres

Un lien réseau accepte des paquets jusqu’à une certaine taille, comme une boîte aux lettres accepte des enveloppes jusqu’à un certain format. Cette taille maximale s’appelle la **MTU**. Tant que tout le monde respecte la même taille, aucun souci. Les problèmes commencent quand **un tronçon du chemin** accepte moins que les autres.

> [!IMPORTANT] L’idée en une phrase
> La MTU est la taille maximale d’un paquet sur un lien. Si un paquet est trop gros pour un tronçon du chemin, il doit être découpé… ou il est perdu.

## La valeur à connaître

Sur Ethernet, la MTU standard est de **1 500 octets** : c’est la taille maximale du paquet IP transporté dans une trame. Presque tous les réseaux l’utilisent, et c’est pour cela que tout se passe bien la plupart du temps.

## D’où viennent les problèmes ?

Certaines technologies **ajoutent des octets** autour du paquet :

| Technologie | Octets ajoutés (environ) |
|---|---|
| Étiquette VLAN 802.1Q | 4 (dans la trame, sans réduire le paquet IP) |
| QinQ | 8 |
| VPN IPsec | 50 à 70 |
| GRE | 24 |
| VXLAN | 50 |

Si un paquet de 1 500 octets doit traverser un tunnel VPN qui ajoute 60 octets, il ferait 1 560 octets : trop gros pour un lien à 1 500. Il faut alors soit **le découper** (fragmentation), soit **réduire** la taille des paquets en amont, soit **augmenter** la MTU des liens qui transportent le tunnel.

## Le symptôme typique

Un site distant est relié par VPN. Le `ping` fonctionne, l’ouverture de session aussi, mais **les pages lourdes ne se chargent jamais** et les transferts de fichiers se figent. Pourquoi ? Le ping et les petits échanges utilisent des petits paquets, qui passent ; les transferts utilisent des paquets pleins (1 500 octets), qui ne passent plus une fois encapsulés.

> [!TIP]
> « Petits paquets OK, gros paquets KO » : dès que tu vois ce symptôme, pense **MTU**.

## Les mots à connaître

- **MTU** — *Maximum Transmission Unit*, taille maximale d’un paquet sur un lien (1 500 octets en Ethernet standard).
- **Fragmentation** — Découpage d’un paquet trop gros en plusieurs morceaux plus petits.
- **Jumbo frames** — Trames Ethernet géantes (souvent 9 000 octets de paquet), utilisées dans les datacenters.
- **Encapsulation** — Ajout d’en-têtes autour d’un paquet, par exemple pour un tunnel.

## Teste-toi

**1.** Un ping vers un serveur distant répond, mais une copie de fichier vers ce serveur se bloque après quelques secondes. Le chemin passe par un VPN. Quelle hypothèse ?

<details><summary>Voir le corrigé</summary>

Un **problème de MTU** : les petits paquets du ping passent, mais les paquets pleins de la copie, alourdis par l’en-tête du VPN, dépassent la MTU d’un tronçon et sont perdus.

</details>

**2.** Pourquoi ne règle-t-on pas simplement la MTU à 9 000 partout ?

<details><summary>Voir le corrigé</summary>

Parce que **tout le chemin** doit l’accepter, y compris des équipements qu’on ne maîtrise pas (Internet, opérateurs). Les jumbo frames s’utilisent dans un périmètre contrôlé — datacenter, réseau de stockage — où chaque équipement est configuré de façon cohérente.

</details>

<!-- approfondir -->

## MTU, MSS et taille de trame : ne pas tout mélanger

```text
┌─────────────── trame Ethernet : 1518 octets (1522 avec VLAN) ───────────────┐
│ en-tête 14 │ ┌──────────── paquet IP = MTU : 1500 octets ────────────┐ │FCS 4│
│            │ │ en-tête IP 20 │ en-tête TCP 20 │ données = MSS : 1460 │ │     │
└────────────┴─┴───────────────┴────────────────┴──────────────────────┴─┴─────┘
```

- **MTU IP** : taille du paquet IP (1 500). C’est la valeur configurée avec `ip mtu` sur Cisco.
- **MTU de l’interface** : taille maximale de la trame utile acceptée (`mtu` sur l’interface, ou `system mtu` sur un switch).
- **MSS** (*Maximum Segment Size*) : taille maximale des **données** TCP, annoncée par chaque extrémité au début de la connexion. MTU − 40 en IPv4 (1 460), MTU − 60 en IPv6.

## Fragmentation et découverte de la MTU du chemin

En IPv4, un routeur peut **fragmenter** un paquet trop gros, sauf si le bit **DF** (*Don’t Fragment*) est positionné. Aujourd’hui, presque tous les paquets TCP ont le bit DF : on utilise la **découverte de la MTU du chemin** (*PMTUD*).

```sequence
titre: Découverte de la MTU du chemin (PMTUD)
PC | Routeur (tunnel MTU 1400) | Serveur
PC -> Routeur (tunnel MTU 1400) : paquet de 1500 octets, bit DF
Routeur (tunnel MTU 1400) --> PC : ICMP « fragmentation nécessaire, MTU 1400 »
note PC : mémorise MTU 1400 vers ce serveur
PC -> Routeur (tunnel MTU 1400) : paquets de 1400 octets
Routeur (tunnel MTU 1400) -> Serveur : les paquets passent
```

En IPv6, les routeurs **ne fragmentent jamais** : la PMTUD (via ICMPv6 *Packet Too Big*) est obligatoire.

**Le piège du trou noir** : si un pare-feu bloque **tout** l’ICMP, le message « fragmentation nécessaire » n’arrive jamais. Le PC continue d’envoyer des paquets de 1 500 octets, qui disparaissent sans explication. On appelle cela un *PMTUD black hole*. Il ne faut **jamais** bloquer l’ICMP type 3 code 4 (IPv4) ni l’ICMPv6 type 2.

## Les remèdes (Cisco IOS)

```cisco
! 1. Réduire la MTU IP de l'interface tunnel et ajuster le MSS TCP au passage
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360
!
! 2. Augmenter la MTU des liens qui transportent une encapsulation (switch Catalyst)
system mtu 9198
! (sur d'autres plateformes : "mtu 9216" sous l'interface)
```

- `ip tcp adjust-mss` réécrit la valeur MSS dans les paquets SYN qui traversent le routeur : les deux extrémités utilisent alors des segments assez petits, **même si l’ICMP est bloqué ailleurs**. C’est la protection la plus robuste pour le TCP sur les VPN.
- Pour VXLAN ou MPLS dans un réseau maîtrisé, on préfère **augmenter** la MTU du réseau de transport (souvent 9 216) pour que les paquets de 1 500 octets des machines passent sans changement.

## Diagnostiquer avec ping

On envoie des pings de taille croissante **en interdisant la fragmentation** :

```powershell
C:\> ping -f -l 1472 10.20.0.10
Réponse de 10.20.0.10 : octets=1472 temps=21 ms TTL=62
C:\> ping -f -l 1473 10.20.0.10
Le paquet doit être fragmenté, mais l’indicateur DF est activé.
```

```bash
# Linux : -M do interdit la fragmentation, -s fixe la taille des données
ping -M do -s 1472 10.20.0.10
```

1 472 octets de données + 8 octets d’en-tête ICMP + 20 octets d’en-tête IP = **1 500**. Si la limite trouvée est plus basse (1 372, par exemple), un tronçon du chemin a une MTU de 1 400.

Sur Cisco : `ping 10.20.0.10 size 1500 df-bit` (la taille inclut ici les en-têtes IP et ICMP).

## MTU et protocoles de routage

OSPF compare la MTU des deux voisins pendant l’échange de bases de données. Si elles diffèrent, la relation reste bloquée à l’état **ExStart/Exchange**. Une MTU incohérente entre deux routeurs se voit donc aussi… dans les protocoles de routage. Voir [OSPF](../niveau-2/ospf.md).

## Exercices

**1.** Dans un datacenter VXLAN, les machines virtuelles ont une MTU de 1 500 et le réseau physique aussi. Les pings passent, les transferts SSH se figent. Que corriger ?

<details><summary>Voir le corrigé</summary>

VXLAN ajoute environ **50 octets** : un paquet de 1 500 octets devient environ 1 550 octets sur le réseau physique, qui n’accepte que 1 500. Il faut **augmenter la MTU du réseau physique** à au moins 1 550 (en pratique 9 216 sur tous les liens de la fabric). Réduire la MTU des VM est une alternative moins propre.

</details>

**2.** `ping -f -l 1472` échoue, mais `ping -f -l 1422` réussit et `ping -f -l 1423` échoue. Quelle est la MTU du chemin ?

<details><summary>Voir le corrigé</summary>

1 422 + 8 + 20 = **1 450 octets**. Un tronçon du chemin (probablement un tunnel) n’accepte que des paquets de 1 450 octets.

</details>

**3.** Après l’ajout d’une règle « bloquer tout ICMP » sur un pare-feu, certains sites Web ne se chargent plus via le VPN de l’entreprise. Explique.

<details><summary>Voir le corrigé</summary>

La règle bloque les messages ICMP « fragmentation nécessaire » : la **découverte de la MTU du chemin** ne fonctionne plus. Les serveurs continuent d’envoyer des paquets de 1 500 octets, trop gros pour le tunnel, qui disparaissent : c’est un **trou noir PMTUD**. Il faut autoriser l’ICMP nécessaire (type 3 code 4, ICMPv6 type 2) et, par sécurité, appliquer `ip tcp adjust-mss` sur le tunnel.

</details>
