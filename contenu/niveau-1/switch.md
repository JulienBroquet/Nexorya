---
titre: Penser comme un switch
nom: Domaines de collision et de diffusion
idee: Un switch isole chaque port (plus de collisions) mais laisse passer les broadcasts dans tout le VLAN ; seul un routeur arrête un broadcast.
osi: "2"
duree: [8, 14]
cle: true
prerequis: [mac]
retenir:
  - Hub — un seul domaine de collision. **Switch** — un domaine de collision **par port**.
  - Un **domaine de diffusion** s’arrête au **routeur** (ou à la frontière d’un VLAN).
  - Un switch de **niveau 3** est un switch qui sait aussi router entre ses VLAN.
---

## Le problème : savoir jusqu’où va une trame

Quand une trame part d’un PC, **qui la reçoit** ? Seulement son destinataire, tout le VLAN, tout le bâtiment ? La réponse dépend des équipements traversés. La comprendre permet d’expliquer pourquoi un réseau trop grand ralentit, et pourquoi on le découpe.

> [!IMPORTANT] L’idée en une phrase
> Un switch livre chaque trame individuelle **au seul port concerné**, mais il répète les broadcasts **dans tout le VLAN**. Seul un routeur arrête un broadcast.

## Hub, switch, routeur : trois comportements

| Équipement | Une trame pour un seul destinataire… | Un broadcast… |
|---|---|---|
| **Hub** (disparu aujourd’hui) | est recopiée sur **tous** les ports | est recopié sur tous les ports |
| **Switch** | va **uniquement** vers le port du destinataire (une fois la MAC apprise) | est recopié sur tous les ports **du VLAN** |
| **Routeur** | est transmise vers le bon réseau, si une route existe | **n’est pas** transmis : il s’arrête là |

Deux notions en découlent :

- **Domaine de collision** : la zone où deux appareils qui émettent en même temps se gênent. Avec un hub, c’était tout le réseau. Avec un switch, chaque port est son propre domaine — et en full duplex, il n’y a plus de collision du tout.
- **Domaine de diffusion** (*broadcast domain*) : la zone atteinte par un broadcast. C’est **tout le VLAN**, quel que soit le nombre de switches. Il s’arrête au routeur.

```topologie
titre: Deux domaines de diffusion séparés par un routeur
R routeur 2,0 "Routeur"
S1 switch 1,1 "Switch 1"
S2 switch 3,1 "Switch 2"
A pc 0.5,2 "PC A"
B pc 1.5,2 "PC B"
C pc 2.5,2 "PC C"
D pc 3.5,2 "PC D"
R -- S1
R -- S2
S1 -- A
S1 -- B
S2 -- C
S2 -- D
zone "Domaine de diffusion 1" 0.5,1 1.5,2
zone "Domaine de diffusion 2" 2.5,1 3.5,2
```

Un broadcast envoyé par A atteint B, mais ni C ni D : le routeur l’arrête.

## Pourquoi c’est important

Chaque broadcast (une requête ARP, une demande DHCP, une annonce d’imprimante…) est reçu et traité par **toutes** les machines du domaine. Avec 50 machines, c’est négligeable. Avec 2 000 machines dans un seul domaine, ces messages finissent par consommer de la bande passante et du processeur partout, et une seule panne (une boucle, un appareil qui s’emballe) touche tout le monde.

C’est pourquoi on **découpe** un grand réseau en plusieurs domaines de diffusion plus petits, avec des [VLAN](vlan.md) reliés par un routeur ou un switch de niveau 3.

## Les mots à connaître

- **Domaine de collision** — Zone dans laquelle deux émissions simultanées entrent en collision ; un port de switch en forme un à lui seul.
- **Domaine de diffusion** — Ensemble des appareils atteints par un broadcast ; il correspond à un VLAN et s’arrête au routeur.
- **Switch de niveau 3** — Switch capable de router entre ses VLAN, en plus de commuter.

## Teste-toi

**1.** Un réseau compte trois switches reliés en cascade, sans VLAN ni routeur. Combien de domaines de diffusion ?

<details><summary>Voir le corrigé</summary>

**Un seul.** Les switches recopient les broadcasts entre eux : toutes les machines reçoivent chaque broadcast. Seul un routeur (ou des VLAN distincts) crée plusieurs domaines.

</details>

**2.** Pourquoi ne met-on pas 3 000 postes dans un même VLAN ?

<details><summary>Voir le corrigé</summary>

Tous les broadcasts seraient reçus par les 3 000 postes : bruit permanent, et une boucle ou un appareil défaillant paralyserait tout le monde. On découpe en domaines de diffusion plus petits, ce qui limite aussi l’étendue des pannes et permet de filtrer entre les groupes.

</details>

<!-- approfondir -->

## Comment un switch transmet : stocker ou couper

| Mode | Principe | Avantage | Inconvénient |
|---|---|---|---|
| **Store-and-forward** | Le switch reçoit la trame entière, vérifie le FCS, puis la transmet. | Les trames abîmées sont jetées immédiatement. | Latence proportionnelle à la taille de la trame. |
| **Cut-through** | Le switch commence à transmettre dès qu’il a lu l’adresse destination. | Latence très faible (utile en datacenter et en finance). | Une trame abîmée est propagée (le FCS est vérifié trop tard). |

Les switches de campus fonctionnent généralement en store-and-forward ; beaucoup de switches de datacenter en cut-through. Un switch passe obligatoirement en store-and-forward quand le port de sortie est plus rapide que le port d’entrée.

## Le plan de données en matériel

Un switch moderne ne fait pas ses décisions par logiciel : un circuit spécialisé (ASIC) consulte la table MAC, stockée dans une mémoire associative (**CAM**), en quelques nanosecondes, quel que soit le nombre d’entrées. Le processeur du switch, lui, gère le **plan de contrôle** : STP, LACP, CDP, l’administration. Quand le processeur est saturé (une boucle, un flot de broadcasts), c’est l’administration et les protocoles de contrôle qui souffrent en premier — d’où des pannes en cascade.

## Switch de niveau 3 et routage entre VLAN

Un **switch de niveau 3** possède, pour chaque VLAN, une interface virtuelle (**SVI**) qui sert de passerelle aux machines de ce VLAN. Il route entre ses VLAN en matériel, à la vitesse des ports.

```topologie
titre: Routage entre VLAN sur un switch de niveau 3
L3 l3 1,0 "Switch L3" "SVI 10 : 10.10.0.1 · SVI 20 : 10.20.0.1"
A pc 0,1 "PC VLAN 10" "10.10.0.15"
B pc 2,1 "PC VLAN 20" "10.20.0.27"
L3 -- A "accès VLAN 10"
L3 -- B "accès VLAN 20"
```

```cisco
ip routing
!
interface Vlan10
 description Utilisateurs
 ip address 10.10.0.1 255.255.255.0
!
interface Vlan20
 description Imprimantes
 ip address 10.20.0.1 255.255.255.0
```

Le PC du VLAN 10 envoie sa trame à la MAC de la SVI 10 ; le switch route le paquet vers le VLAN 20 et fabrique une nouvelle trame avec sa propre MAC de SVI 20 comme source. Les deux PC sont dans **deux domaines de diffusion** différents, même s’ils sont branchés sur le même boîtier.

> [!WARNING]
> Créer des VLAN puis activer `ip routing` sans filtrage **relie** à nouveau tous les VLAN entre eux. La séparation n’est réelle que si des listes de contrôle d’accès (ACL) ou un pare-feu limitent ce qui passe d’un VLAN à l’autre. Voir [ACL](../niveau-4/acl.md).

## Taille des domaines de diffusion : quelques repères

- **Campus** : un VLAN par usage et par étage ou bâtiment, souvent un /24 (254 adresses), rarement plus de 500 à 1 000 machines.
- **Wi-Fi** : les grands VLAN sont fréquents, mais les contrôleurs filtrent ou convertissent les broadcasts pour ne pas les diffuser sur les ondes.
- **Datacenter** : les réseaux modernes évitent d’étendre un domaine de diffusion entre baies, sauf via des technologies conçues pour cela (VXLAN avec EVPN, niveau 5).

## Exercices

**1.** Un switch reçoit une trame de 1 500 octets sur un port à 1 Gb/s et doit la transmettre sur un port à 10 Gb/s. Peut-il fonctionner en cut-through ?

<details><summary>Voir le corrigé</summary>

**Non.** S’il commençait à émettre à 10 Gb/s pendant que la trame arrive à 1 Gb/s, il manquerait de données à envoyer (*underrun*). Il doit **stocker** la trame entière avant de la transmettre.

</details>

**2.** Un PC du VLAN 10 et un PC du VLAN 20 sont branchés sur le même switch de niveau 3, sans ACL. Peuvent-ils communiquer ? Combien de domaines de diffusion ?

<details><summary>Voir le corrigé</summary>

**Oui**, ils communiquent par routage via les SVI (si chacun a la bonne passerelle). Il y a **deux domaines de diffusion** : un broadcast du VLAN 10 n’atteint pas le VLAN 20. Le routage relie les réseaux, il ne mélange pas les broadcasts.

</details>
