---
titre: IPv4
nom: Internet Protocol version 4
idee: IPv4 donne à chaque machine une adresse de 32 bits composée d’une partie réseau et d’une partie machine ; les routeurs lisent la partie réseau pour faire avancer le paquet.
osi: "3"
duree: [10, 20]
prerequis: [osi]
retenir:
  - "Une adresse IPv4 = **32 bits**, écrits en 4 octets décimaux (`192.168.1.20`)."
  - Le **masque** (ou préfixe `/24`) sépare la **partie réseau** de la **partie machine**.
  - "Deux machines du **même réseau** se parlent directement ; sinon, elles passent par la **passerelle**."
  - Les plages **privées** (10/8, 172.16/12, 192.168/16) ne circulent pas sur Internet sans **NAT**.
---

## Le problème : trouver une machine dans le monde entier

Une adresse MAC suffit pour livrer une trame sur le réseau local. Mais elle ne dit rien de **l’endroit** où se trouve la machine : impossible, à partir d’une adresse MAC, de savoir s’il faut aller vers Paris ou vers Tokyo. Il faut une adresse **organisée** comme une adresse postale : d’abord la ville et la rue (le réseau), puis le numéro (la machine).

> [!IMPORTANT] L’idée en une phrase
> Une adresse IPv4 contient **deux parties** : le numéro du réseau, que les routeurs utilisent pour trouver le chemin, et le numéro de la machine dans ce réseau.

## À quoi ressemble une adresse IPv4 ?

`192.168.1.20` : quatre nombres de 0 à 255, séparés par des points. Chaque nombre représente **8 bits** (un octet), soit 32 bits au total. Il existe environ 4,3 milliards d’adresses IPv4 possibles — moins que le nombre d’appareils connectés aujourd’hui, d’où l’arrivée d’IPv6.

## Partie réseau et partie machine

Le **masque** indique où s’arrête la partie réseau. On l’écrit de deux façons :

- en notation décimale : `255.255.255.0` ;
- en notation **CIDR**, plus courante : `/24`, qui signifie « les 24 premiers bits désignent le réseau ».

| Adresse | Masque | Réseau | Machine |
|---|---|---|---|
| 192.168.1.20/24 | 255.255.255.0 | 192.168.1 | 20 |
| 10.20.30.40/16 | 255.255.0.0 | 10.20 | 30.40 |
| 10.20.30.40/8 | 255.0.0.0 | 10 | 20.30.40 |

Dans chaque réseau, deux adresses sont réservées : la **première** désigne le réseau lui-même (`192.168.1.0`) et la **dernière** est l’adresse de **broadcast** (`192.168.1.255`), qui atteint toutes les machines du réseau.

## Même réseau ou pas ? La décision de chaque machine

Avant d’envoyer un paquet, une machine compare la partie réseau de l’adresse de destination avec la sienne :

- **même réseau** : elle envoie directement le paquet à la machine (elle cherche son adresse MAC avec [ARP](arp.md)) ;
- **réseau différent** : elle confie le paquet à sa **passerelle** (le routeur).

```topologie
titre: Deux réseaux reliés par un routeur
A pc 0,0 "PC A" "192.168.1.20/24"
B pc 0,1 "PC B" "192.168.1.30/24"
SW1 switch 1,0.5 "Switch"
R routeur 2.5,0.5 "Routeur" ".1 | .1"
SW2 switch 4,0.5 "Switch"
S serveur 5,0.5 "Serveur" "10.0.0.50/24"
A -- SW1
B -- SW1
SW1 -- R "192.168.1.0/24"
R -- SW2 "10.0.0.0/24"
SW2 -- S
```

- A → B : même réseau `192.168.1.0/24`, échange direct par le switch.
- A → Serveur : réseau différent, A envoie le paquet au routeur (sa passerelle `192.168.1.1`), qui le fait suivre vers `10.0.0.0/24`.

## Adresses publiques et adresses privées

Certaines plages sont **réservées aux réseaux internes** et ne sont jamais acheminées sur Internet :

| Plage privée | Notation | Usage typique |
|---|---|---|
| 10.0.0.0 à 10.255.255.255 | 10.0.0.0/8 | grandes entreprises |
| 172.16.0.0 à 172.31.255.255 | 172.16.0.0/12 | entreprises, cloud |
| 192.168.0.0 à 192.168.255.255 | 192.168.0.0/16 | maisons, petites entreprises |

Pour sortir sur Internet, ces adresses sont traduites en adresse publique par le routeur ou le pare-feu : c’est le [NAT](../niveau-3/nat.md).

Deux autres plages à reconnaître : `127.0.0.1` (*localhost*, la machine elle-même) et `169.254.x.x` (adresse que s’attribue une machine quand **aucun serveur DHCP** ne lui a répondu).

## Les mots à connaître

- **Adresse IPv4** — Adresse de 32 bits, écrite en quatre octets décimaux, qui identifie une interface sur un réseau IP.
- **Masque de sous-réseau** — Valeur qui indique quels bits de l’adresse désignent le réseau ; par exemple 255.255.255.0.
- **CIDR** — Notation du masque par un nombre de bits après une barre oblique : /24, /16…
- **Adresse de réseau** — Première adresse d’un réseau, qui désigne le réseau lui-même.
- **Adresse de broadcast** — Dernière adresse d’un réseau, qui atteint toutes ses machines.
- **Adresse privée** — Adresse réservée aux réseaux internes, non acheminée sur Internet.

## Teste-toi

**1.** Le PC `192.168.1.20/24` veut joindre `192.168.2.5`. Envoie-t-il le paquet directement ou à sa passerelle ?

<details><summary>Voir le corrigé</summary>

**À sa passerelle.** Avec un /24, son réseau est `192.168.1.0` : seules les adresses `192.168.1.x` sont dans son réseau. `192.168.2.5` est dans un autre réseau.

</details>

**2.** Combien de machines peut-on adresser dans un réseau /24 ?

<details><summary>Voir le corrigé</summary>

8 bits pour la partie machine = 256 adresses, moins l’adresse de réseau et le broadcast = **254 machines**.

</details>

<!-- approfondir -->

## L’en-tête IPv4

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-------+-------+---------------+-------------------------------+
|Version|  IHL  |  DSCP   |ECN  |        Longueur totale        |
+-------+-------+---------------+-----+-------------------------+
|        Identification         |Flags|  Décalage de fragment   |
+---------------+---------------+-----+-------------------------+
|      TTL      |   Protocole   |     Somme de contrôle d’en-tête |
+---------------+---------------+-------------------------------+
|                        Adresse IP source                      |
+---------------------------------------------------------------+
|                     Adresse IP destination                    |
+---------------------------------------------------------------+
|                   Options (rares) + bourrage                  |
+---------------------------------------------------------------+
```

| Champ | Rôle | À retenir |
|---|---|---|
| IHL | longueur de l’en-tête en mots de 32 bits | 5 = 20 octets, sans options |
| DSCP / ECN | qualité de service, notification de congestion | voir [DSCP](../niveau-5/dscp.md) |
| Identification, Flags, Décalage | fragmentation | bit **DF** = ne pas fragmenter |
| **TTL** | durée de vie : chaque routeur le décrémente ; à 0, le paquet est jeté et un ICMP *Time Exceeded* est renvoyé | empêche les boucles de routage infinies ; base de `traceroute` |
| Protocole | contenu : 1 ICMP, 6 TCP, 17 UDP, 47 GRE, 50 ESP, 89 OSPF | démultiplexage |
| Somme de contrôle | protège **l’en-tête** seulement, recalculée à chaque routeur (le TTL change) | — |

Les valeurs initiales de TTL révèlent souvent le système d’origine : **64** (Linux, macOS), **128** (Windows), **255** (équipements réseau). Un `ping` qui revient avec un TTL de 118 vient probablement d’une machine Windows située à 10 routeurs.

## Calculer l’adresse de réseau : le ET logique

Une machine calcule son réseau en appliquant un **ET bit à bit** entre son adresse et son masque :

```text
Adresse   192.168.1.77   = 11000000.10101000.00000001.01001101
Masque    255.255.255.192 = 11111111.11111111.11111111.11000000
ET        192.168.1.64   = 11000000.10101000.00000001.01000000
```

Elle fait le même calcul avec l’adresse de destination. Si les deux résultats sont égaux, la destination est locale. Toute la mécanique du découpage en sous-réseaux est détaillée dans [Subnetting, CIDR et VLSM](subnet.md).

## Plages spéciales (RFC 6890)

| Plage | Usage |
|---|---|
| 0.0.0.0/8 | « cette machine » (source au démarrage DHCP) ; `0.0.0.0/0` = route par défaut |
| 127.0.0.0/8 | boucle locale |
| 169.254.0.0/16 | lien local (APIPA), sans DHCP |
| 100.64.0.0/10 | CGNAT chez les opérateurs |
| 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 | documentation (utilisées dans Nexorya) |
| 224.0.0.0/4 | [multicast](multicast.md) |
| 255.255.255.255 | broadcast limité au lien local |

## Configurer et vérifier (Cisco IOS et systèmes)

```cisco
interface GigabitEthernet0/0/1
 description LAN utilisateurs
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0/0   203.0.113.2     YES manual up                    up
GigabitEthernet0/0/1   192.168.1.1     YES manual up                    up
```

```bash
# Linux
ip -4 addr show dev eth0
sudo ip addr add 192.168.1.50/24 dev eth0
ip route            # la ligne "default via" est la passerelle
```

```powershell
# Windows
Get-NetIPConfiguration
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.1.50 -PrefixLength 24 -DefaultGateway 192.168.1.1
```

## Exercices

**1.** Un ping revient avec `TTL=57`. Combien de routeurs, au minimum, sépare-t-on de la machine distante, et de quel type de système s’agit-il probablement ?

<details><summary>Voir le corrigé</summary>

Le TTL initial le plus probable est **64** (Linux ou macOS) : 64 − 57 = **7 routeurs**. Un TTL initial de 128 supposerait 71 routeurs, ce qui est invraisemblable.

</details>

**2.** Une machine a l’adresse `172.20.5.9/12`. Est-ce une adresse privée ? Quelle est l’adresse de son réseau ?

<details><summary>Voir le corrigé</summary>

**Oui**, elle est dans `172.16.0.0/12` (172.16 à 172.31). Avec un /12, le masque est 255.240.0.0 : le deuxième octet 20 ET 240 = 16. Réseau : **172.16.0.0/12**.

</details>

**3.** Le PC A est configuré en `192.168.1.20/24`, le PC B en `192.168.1.30/25`. A peut-il joindre B ? Et B peut-il joindre A ?

<details><summary>Voir le corrigé</summary>

A (/24) considère `.30` comme local : il l’envoie directement. B (/25, réseau `192.168.1.0`, adresses .0 à .127) considère aussi `.20` comme local. **Les deux échanges fonctionnent ici**, mais par chance. Si B avait l’adresse `.200/25`, il placerait A hors de son réseau et passerait par sa passerelle : la communication deviendrait asymétrique ou échouerait. Un masque incohérent est un défaut à corriger même quand « ça marche ».

</details>
