---
titre: NDP
nom: Neighbor Discovery Protocol (IPv6)
idee: NDP est la boîte à outils d’IPv6 pour le réseau local — trouver l’adresse MAC d’un voisin (comme ARP), découvrir les routeurs et vérifier qu’une adresse est libre.
osi: "3"
duree: [7, 14]
prerequis: [ipv6, arp]
retenir:
  - NDP utilise des messages **ICMPv6** — RS, RA, NS, NA et Redirect.
  - "**NS/NA** remplacent ARP — on demande la MAC d’un voisin, en **multicast ciblé** plutôt qu’en broadcast."
  - "**RS/RA** permettent aux machines de trouver les routeurs et le préfixe du réseau."
  - Bloquer ICMPv6 sur un réseau IPv6 **casse** le réseau — NDP en dépend.
---

## Le problème : IPv6 n’a ni ARP ni broadcast

En IPv4, ARP trouve l’adresse MAC d’un voisin en criant à tout le monde. IPv6 n’a pas de broadcast. Il lui faut un autre moyen de trouver ses voisins, ses routeurs, et de vérifier que son adresse n’est pas déjà prise.

> [!IMPORTANT] L’idée en une phrase
> NDP réunit en un seul protocole ce que faisaient ARP, la découverte de routeur et la détection de doublons — avec des messages ICMPv6 envoyés en multicast ciblé.

## Les cinq messages

| Message | Type ICMPv6 | Rôle | Équivalent IPv4 |
|---|---|---|---|
| **RS** — Router Solicitation | 133 | « Y a-t-il un routeur ? » | — |
| **RA** — Router Advertisement | 134 | « Je suis un routeur, voici le préfixe » | DHCP (en partie) |
| **NS** — Neighbor Solicitation | 135 | « Qui a cette adresse IPv6 ? » | requête ARP |
| **NA** — Neighbor Advertisement | 136 | « C’est moi, voici ma MAC » | réponse ARP |
| Redirect | 137 | « Passe plutôt par cet autre routeur » | ICMP Redirect |

## Trouver la MAC d’un voisin

```sequence
titre: Résolution d’adresse en IPv6
PC A (2001:db8::a) | PC B (2001:db8::b)
PC A (2001:db8::a) -> PC B (2001:db8::b) : NS vers ff02::1:ff00:b : « qui a 2001:db8::b ? »
PC B (2001:db8::b) --> PC A (2001:db8::a) : NA : « c’est moi, MAC 3c:22:fb:1a:09:7e »
note PC A (2001:db8::a) : enregistre dans son cache de voisins
```

La sollicitation n’est pas envoyée à tout le monde, mais à une adresse **multicast de nœud sollicité**, calculée à partir des derniers bits de l’adresse recherchée. Seules les machines dont l’adresse se termine de la même façon la traitent : les autres ne sont pas dérangées.

## Les mots à connaître

- **NDP** — *Neighbor Discovery Protocol*, ensemble de messages ICMPv6 qui gère le voisinage en IPv6.
- **NS / NA** — Sollicitation et annonce de voisin, équivalents de la requête et de la réponse ARP.
- **Multicast de nœud sollicité** — Adresse multicast ciblée utilisée pour chercher un voisin sans déranger tout le réseau.
- **Cache de voisins** — Équivalent IPv6 du cache ARP.

## Teste-toi

**Un pare-feu interne bloque tout le trafic ICMPv6 « pour la sécurité ». Que se passe-t-il pour les machines IPv6 derrière lui ?**

<details><summary>Voir le corrigé</summary>

Selon l’endroit du filtrage, les machines ne trouvent plus leurs voisins (NS/NA), ni leur routeur (RS/RA) : **IPv6 cesse de fonctionner**. Le blocage gêne aussi la découverte de la MTU du chemin. On filtre ICMPv6 de façon sélective, jamais en bloc (RFC 4890).

</details>

<!-- approfondir -->

## Détection d’adresse dupliquée (DAD)

Avant d’utiliser une nouvelle adresse, une machine envoie un **NS** pour sa propre adresse, avec l’adresse source `::` (non spécifiée). Si quelqu’un répond par un **NA**, l’adresse est déjà prise : la machine ne l’utilise pas. L’adresse reste à l’état *tentative* pendant ce test (environ une seconde).

## Les états du cache de voisins

| État | Signification |
|---|---|
| INCOMPLETE | NS envoyé, pas encore de réponse |
| REACHABLE | joignabilité confirmée récemment |
| STALE | entrée ancienne, utilisable ; sera revérifiée au prochain envoi |
| DELAY / PROBE | revérification en cours |

NDP vérifie activement la joignabilité des voisins (*Neighbor Unreachability Detection*), là où ARP se contentait d’un cache à durée fixe.

## Commandes utiles

```bash
# Linux
$ ip -6 neigh
fe80::1 dev eth0 lladdr 00:aa:0b:00:00:01 router REACHABLE
2001:db8:abcd:110::40 dev eth0 lladdr 3c:22:fb:1a:09:7e STALE
```

```powershell
# Windows
PS> Get-NetNeighbor -AddressFamily IPv6 | Where-Object State -ne Unreachable
```

```cisco
R1# show ipv6 neighbors
IPv6 Address                    Age Link-layer Addr State Interface
2001:DB8:ABCD:110::40             0 3c22.fb1a.097e  REACH Vl10
FE80::3E22:FBFF:FE1A:97E          2 3c22.fb1a.097e  STALE Vl10
```

## Sécurité

NDP n’est pas authentifié par défaut, et souffre donc des mêmes faiblesses qu’ARP : fausses RA (une machine se déclare routeur), faux NA (usurpation de voisin). Les protections se placent sur les switches — **RA Guard**, **ND Inspection**, **DHCPv6 Guard**, regroupées chez Cisco sous le nom *First Hop Security*. Voir [Protéger les ports](../niveau-4/protection-ports.md).

## Exercice

**Calcule l’adresse multicast de nœud sollicité de `2001:db8:abcd:110::4:25`.**

<details><summary>Voir le corrigé</summary>

On prend les **24 derniers bits** de l’adresse : `…:0004:0025` → `04:0025`. On les ajoute à `ff02::1:ff00:0/104` : **`ff02::1:ff04:25`**. Côté Ethernet, cette adresse multicast correspond à la MAC `33:33:ff:04:00:25`.

</details>
