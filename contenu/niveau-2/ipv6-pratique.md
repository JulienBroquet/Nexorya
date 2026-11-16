---
titre: IPv6 en pratique
nom: SLAAC, DHCPv6 et double pile
idee: En IPv6, le routeur annonce le préfixe du réseau et la passerelle ; les machines se configurent seules (SLAAC), avec ou sans l’aide d’un serveur DHCPv6.
osi: "3"
duree: [9, 20]
cle: true
prerequis: [ipv6]
retenir:
  - La **passerelle** IPv6 est toujours apprise par les **annonces de routeur** (RA), jamais par DHCPv6.
  - "**SLAAC** — la machine fabrique son adresse à partir du préfixe annoncé."
  - "Les drapeaux **M** et **O** de la RA disent s’il faut aussi demander à DHCPv6 une adresse (M) ou seulement d’autres informations, comme le DNS (O)."
  - En **double pile**, IPv4 et IPv6 coexistent ; les systèmes préfèrent généralement IPv6 quand il fonctionne.
---

## Le problème : configurer des milliers de machines

En IPv4, une machine obtient son adresse, son masque, sa passerelle et son DNS par [DHCP](../niveau-3/dhcp.md). IPv6 propose une autre approche : le routeur **annonce** le réseau, et chaque machine se configure toute seule.

> [!IMPORTANT] L’idée en une phrase
> Le routeur dit « le réseau ici, c’est `2001:db8:10:20::/64`, et je suis votre passerelle ». Chaque machine complète le préfixe avec ses 64 bits d’identifiant et obtient son adresse, sans serveur.

## Comment ça marche : SLAAC

```sequence
titre: Autoconfiguration sans état (SLAAC)
PC | Routeur
note PC : crée son adresse de lien local fe80::…, vérifie qu’elle est unique
PC -> Routeur : RS : « un routeur est-il là ? » (vers ff02::2)
Routeur --> PC : RA : préfixe 2001:db8:10:20::/64, passerelle = moi (fe80::1)
note PC : fabrique 2001:db8:10:20:xxxx:xxxx:xxxx:xxxx et vérifie l’unicité (DAD)
PC -> Routeur : trafic vers Internet via fe80::1
```

1. La machine crée une **adresse de lien local** et vérifie que personne d’autre ne l’utilise.
2. Elle envoie une **sollicitation de routeur** (RS).
3. Le routeur répond par une **annonce de routeur** (RA) : préfixe, passerelle, durées de validité. Il en envoie aussi régulièrement sans qu’on le lui demande.
4. La machine fabrique son adresse **globale** et l’utilise.

## Et le DNS ? Les trois modes

| Mode | Adresse | DNS et autres options | Drapeaux de la RA |
|---|---|---|---|
| **SLAAC seul** | fabriquée par la machine | dans la RA (option RDNSS) | M=0, O=0 |
| **SLAAC + DHCPv6 sans état** | fabriquée par la machine | donnés par DHCPv6 | M=0, **O=1** |
| **DHCPv6 avec état** | attribuée par DHCPv6 | donnés par DHCPv6 | **M=1** |

Dans **tous** les cas, la passerelle vient de la RA. Un réseau sans RA n’a pas de passerelle IPv6, même avec un serveur DHCPv6 parfait.

> [!WARNING]
> **Android ne prend pas en charge DHCPv6 avec état.** Sur un réseau qui ne fournit les adresses que par DHCPv6 (M=1, sans préfixe autonome), les téléphones Android n’obtiennent pas d’adresse globale. C’est pourquoi on garde généralement SLAAC actif sur les réseaux d’utilisateurs.

## La double pile

Pendant la transition, la plupart des réseaux fonctionnent en **double pile** : chaque machine a une adresse IPv4 et une adresse IPv6. Quand un nom DNS renvoie les deux types d’adresses, les systèmes **préfèrent IPv6**, avec un mécanisme (*Happy Eyeballs*) qui bascule vite sur IPv4 si IPv6 ne répond pas.

Conséquence pratique : un réseau IPv6 **mal configuré** peut ralentir les connexions sans les casser, ce qui le rend difficile à repérer.

## Les mots à connaître

- **SLAAC** — *Stateless Address Autoconfiguration*, autoconfiguration d’une adresse IPv6 à partir du préfixe annoncé par le routeur.
- **RA** — *Router Advertisement*, annonce du routeur : préfixe, passerelle, options.
- **RS** — *Router Solicitation*, demande d’annonce envoyée par une machine.
- **DHCPv6** — Version IPv6 de DHCP, pour fournir des adresses ou seulement des options (DNS, domaine).
- **DAD** — *Duplicate Address Detection*, vérification qu’une adresse n’est pas déjà utilisée.

## Teste-toi

**1.** Un poste a une adresse IPv6 globale fournie par DHCPv6, mais aucune route par défaut IPv6. Où est le problème ?

<details><summary>Voir le corrigé</summary>

Le poste ne reçoit **pas d’annonce de routeur** (RA). La passerelle IPv6 n’est jamais fournie par DHCPv6 : il faut que le routeur envoie des RA sur ce réseau (et qu’aucun filtrage, comme RA Guard mal réglé, ne les bloque).

</details>

**2.** Pourquoi garder SLAAC sur un réseau Wi-Fi d’employés, même si on dispose d’un serveur DHCPv6 ?

<details><summary>Voir le corrigé</summary>

Parce que certains systèmes, notamment **Android**, ne savent pas obtenir d’adresse par DHCPv6 avec état. Sans SLAAC, ils n’auraient pas d’adresse IPv6 globale.

</details>

<!-- approfondir -->

## Configuration d’un routeur (Cisco IOS)

```cisco
ipv6 unicast-routing
!
interface Vlan10
 ipv6 address 2001:db8:abcd:110::1/64
 ipv6 address fe80::1 link-local
 ! SLAAC + DNS dans la RA (RFC 8106) — selon la version, la commande varie
 ipv6 nd ra dns server 2001:db8:abcd:99::53
 ! Option : SLAAC + DHCPv6 sans état pour le DNS
 ipv6 nd other-config-flag
 ipv6 dhcp relay destination 2001:db8:abcd:99::547
!
interface Vlan99
 description Serveurs : adresses fixes, pas d'autoconfiguration
 ipv6 address 2001:db8:abcd:199::1/64
 ipv6 nd prefix 2001:db8:abcd:199::/64 no-autoconfig
 ipv6 nd managed-config-flag
```

```cisco
R1# show ipv6 interface Vlan10 | include ND|hosts
  ND advertised reachable time is 0 (unspecified)
  ND router advertisements are sent every 200 seconds
  ND router advertisements live for 1800 seconds
  Hosts use stateless autoconfig for addresses.
  Hosts use DHCP to obtain other (non-address) information.
```

## Vérifier côté client

```bash
# Linux : adresses et origine
$ ip -6 addr show dev eth0
    inet6 2001:db8:abcd:110:5e1d:4a7f:9c2b:11e3/64 scope global dynamic mngtmpaddr
    inet6 2001:db8:abcd:110:a81b:2cff:fe33:9f01/64 scope global temporary dynamic
    inet6 fe80::a81b:2cff:fe33:9f01/64 scope link
$ ip -6 route show default
default via fe80::1 dev eth0 proto ra metric 100
```

- `proto ra` : la route par défaut vient bien d’une annonce de routeur.
- `temporary` : adresse temporaire utilisée pour les connexions sortantes (vie privée).
- La passerelle est une adresse **de lien local** : c’est normal en IPv6.

```powershell
PS> Get-NetIPAddress -AddressFamily IPv6 | Select IPAddress, PrefixOrigin, SuffixOrigin
2001:db8:abcd:110:5e1d:4a7f:9c2b:11e3   RouterAdvertisement   Random
fe80::5e1d:4a7f:9c2b:11e3                WellKnown            Link
```

## Routage IPv6 : OSPFv3 en bref

Le routage IPv6 fonctionne comme en IPv4 ; les protocoles ont leur version IPv6 (OSPFv3, EIGRP pour IPv6, MP-BGP). Les échanges entre voisins utilisent les adresses **de lien local**.

```cisco
ipv6 router ospf 1
 router-id 10.255.0.1
!
interface GigabitEthernet0/0/0
 ipv6 ospf 1 area 0
!
R1# show ipv6 route ospf
O   2001:DB8:ABCD:210::/64 [110/2]
     via FE80::2, GigabitEthernet0/0/0
```

Le *router-id* reste un nombre de 32 bits écrit comme une adresse IPv4 : sur un routeur sans aucune adresse IPv4, il faut le configurer à la main. Voir [OSPF](ospf.md).

## Sécurité spécifique

- Une machine qui envoie de **fausses RA** peut se déclarer passerelle de tout le réseau, même dans un réseau « IPv4 seulement » : les systèmes activent IPv6 par défaut. La protection s’appelle **RA Guard** : voir [Protéger les ports](../niveau-4/protection-ports.md).
- Désactiver IPv6 sur les postes n’est pas recommandé par les éditeurs de systèmes ; il vaut mieux le **maîtriser** (RA Guard, filtrage, supervision).

## Exercices

**1.** Sur un VLAN, les drapeaux de la RA sont M=0 et O=1, et le préfixe a l’indicateur « autonomous ». Comment un poste obtient-il son adresse et son DNS ?

<details><summary>Voir le corrigé</summary>

**Adresse par SLAAC** (préfixe autonome, M=0), **DNS par DHCPv6 sans état** (O=1), passerelle par la RA. C’est un mode courant en entreprise, compatible avec Android si le DNS est aussi annoncé dans la RA (RDNSS).

</details>

**2.** Des utilisateurs se plaignent de connexions lentes à démarrer vers certains sites depuis qu’IPv6 a été activé. Le ping IPv6 vers Internet échoue, IPv4 fonctionne. Explique et propose une démarche.

<details><summary>Voir le corrigé</summary>

Les postes reçoivent une adresse IPv6 et une passerelle (RA), donc ils **tentent d’abord IPv6**, qui n’aboutit pas ; ils basculent ensuite sur IPv4 après un délai. Vérifier la route IPv6 par défaut du routeur vers l’opérateur, le pare-feu IPv6, puis tester avec `traceroute -6`. En attendant la correction, on peut cesser d’annoncer le préfixe sur ce VLAN plutôt que de laisser une connectivité IPv6 cassée.

</details>
