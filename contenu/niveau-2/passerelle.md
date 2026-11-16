---
titre: La table de routage
nom: Passerelle, préfixe le plus long, distance administrative et métrique
idee: Pour chaque paquet, le routeur choisit dans sa table la route la plus précise ; si plusieurs sources proposent la même, il préfère la plus fiable, puis le chemin le moins coûteux.
osi: "3"
duree: [9, 18]
cle: true
prerequis: [ipv4, subnet]
retenir:
  - "1. **Préfixe le plus long** — la route la plus précise gagne (/24 bat /16, qui bat /0)."
  - "2. À préfixe égal, entre sources différentes — **distance administrative** la plus faible (connectée 0, statique 1, OSPF 110…)."
  - "3. Au sein d’un même protocole — **métrique** la plus faible."
  - "La **route par défaut** `0.0.0.0/0` attrape tout ce qui n’a pas de route plus précise."
---

## Le problème : quel chemin pour ce paquet ?

Un routeur reçoit un paquet pour `10.20.30.5`. Il a peut-être plusieurs routes qui conviennent : une vers `10.0.0.0/8`, une vers `10.20.30.0/24`, une route par défaut, et peut-être les mêmes apprises par deux protocoles différents. Laquelle choisir ?

> [!IMPORTANT] L’idée en une phrase
> Le routeur choisit d’abord la route **la plus précise** ; à précision égale, celle de la **source la plus fiable** ; et au sein d’une même source, la **moins coûteuse**.

## La table de routage

Chaque ligne de la table dit : « pour joindre **ce réseau**, envoie le paquet **à ce voisin** (ou par cette interface) ».

```cisco
R1# show ip route
Codes: C - connected, L - local, S - static, O - OSPF, * - candidate default

Gateway of last resort is 203.0.113.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.1
      10.0.0.0/8 is variably subnetted
O        10.0.0.0/8 [110/20] via 10.255.0.2, GigabitEthernet0/0/1
O        10.20.30.0/24 [110/30] via 10.255.0.6, GigabitEthernet0/0/2
C        10.255.0.0/30 is directly connected, GigabitEthernet0/0/1
L        10.255.0.1/32 is directly connected, GigabitEthernet0/0/1
```

Comment lire `[110/30]` : **110** est la distance administrative (OSPF), **30** la métrique (le coût OSPF).

## Règle 1 : le préfixe le plus long

Pour `10.20.30.5`, trois routes conviennent : `0.0.0.0/0`, `10.0.0.0/8` et `10.20.30.0/24`. Le routeur choisit **`/24`**, la plus précise : elle décrit le chemin vers un réseau plus petit, donc avec plus de certitude.

> [!TIP] L’analogie des panneaux
> Sur la route, un panneau « Lyon, centre-ville » est plus précis qu’un panneau « Lyon », lui-même plus précis que « Toutes directions ». Tu suis toujours le panneau le plus précis qui correspond à ta destination.

## Règle 2 : la distance administrative

Si deux **sources différentes** proposent exactement le même réseau (même préfixe), le routeur fait confiance à la plus fiable. Chaque source a une note : plus elle est **basse**, plus elle est crue.

| Source | Distance administrative (Cisco) |
|---|---|
| Réseau directement connecté | 0 |
| Route statique | 1 |
| EIGRP | 90 |
| OSPF | 110 |
| IS-IS | 115 |
| RIP | 120 |
| BGP externe / interne | 20 / 200 |

## Règle 3 : la métrique

Si une **même** source propose plusieurs chemins vers le même réseau, elle choisit celui qui a la **métrique** la plus faible. Chaque protocole a sa propre métrique : nombre de sauts pour RIP, coût lié au débit pour OSPF, etc. Si deux chemins ont exactement la même métrique, le routeur peut **les utiliser tous les deux** (partage de charge, ECMP).

## La passerelle des postes de travail

Un PC a aussi une table de routage, très simple : son réseau local, et une **route par défaut** vers sa passerelle. C’est la règle « tout ce qui n’est pas local va à la passerelle » vue dans les fiches précédentes.

```powershell
C:\> route print -4
Destination réseau    Masque réseau    Adr. passerelle    Adr. interface  Métrique
          0.0.0.0          0.0.0.0      192.168.1.1      192.168.1.20      25
      192.168.1.0    255.255.255.0         On-link      192.168.1.20     281
```

```topologie
titre: Le même routeur, trois routes qui conviennent pour 10.20.30.5
R1 routeur 0,1 "R1"
A routeur 2,0 "via 10.255.0.6" "10.20.30.0/24 : choisie"
B routeur 2,1 "via 10.255.0.2" "10.0.0.0/8"
C nuage 2,2 "via 203.0.113.1" "0.0.0.0/0"
R1 ++ A "le plus précis"
R1 -- B
R1 -- C
```

## Les mots à connaître

- **Table de routage** — Liste des réseaux connus par un routeur, avec pour chacun le voisin ou l’interface à utiliser.
- **Préfixe le plus long** — Règle qui fait choisir la route la plus précise ; *longest prefix match*.
- **Distance administrative** — Note de fiabilité d’une source de routes ; la plus basse l’emporte.
- **Métrique** — Coût d’un chemin selon un protocole de routage ; le plus bas l’emporte.
- **Route par défaut** — Route 0.0.0.0/0 utilisée quand aucune route plus précise ne convient ; *gateway of last resort*.

## Teste-toi

**1.** Un routeur a les routes `172.16.0.0/16` et `172.16.5.0/24`. Par où part un paquet pour `172.16.5.9` ? Et pour `172.16.6.9` ?

<details><summary>Voir le corrigé</summary>

`172.16.5.9` → route **/24** (la plus précise). `172.16.6.9` → seule la **/16** convient.

</details>

**2.** OSPF et une route statique annoncent tous deux `10.50.0.0/24`. Laquelle est installée ?

<details><summary>Voir le corrigé</summary>

La **route statique** : même préfixe, et sa distance administrative (1) est plus faible que celle d’OSPF (110).

</details>

<!-- approfondir -->

## L’ordre exact des décisions

La distance administrative et la métrique servent à **remplir** la table ; le préfixe le plus long sert à la **consulter** :

1. Chaque source (connectée, statique, OSPF, BGP…) propose ses meilleurs chemins **selon sa métrique**.
2. Pour un **même préfixe** (même réseau, même longueur), le routeur n’installe que la proposition de la source à la **plus petite distance administrative**.
3. Au moment de transmettre un paquet, le routeur cherche dans la table l’entrée au **préfixe le plus long** qui contient la destination.

Conséquence importante : une route OSPF `/24` **bat** une route statique `/16` pour une destination incluse dans le `/24`. La distance administrative ne compare que des routes **identiques**.

## Route flottante : un secours statique

En donnant à une route statique une distance administrative **plus grande** que celle du protocole de routage, on crée une route de secours qui n’apparaît que si la route dynamique disparaît.

```cisco
! Route principale apprise par OSPF (AD 110).
! Secours : route statique vers un lien 4G, AD 250, invisible tant qu'OSPF fonctionne.
ip route 10.0.0.0 255.0.0.0 192.0.2.1 250
```

## Partage de charge à coût égal (ECMP)

```cisco
R1# show ip route 10.40.0.0
Routing entry for 10.40.0.0/16
  Known via "ospf 1", distance 110, metric 3, type intra area
  Routing Descriptor Blocks:
  * 10.255.0.2, from 10.255.255.2, via GigabitEthernet0/0/1
      Route metric is 3, traffic share count is 1
    10.255.0.6, from 10.255.255.3, via GigabitEthernet0/0/2
      Route metric is 3, traffic share count is 1
```

Deux chemins de même coût sont installés. Comme pour l’agrégation de liens, le routeur répartit **par flux** (hachage des adresses et ports), pour ne pas désordonner les paquets d’une même connexion. Voir [ECMP](../niveau-5/ecmp.md).

## Récursivité et route de dernier recours

Une route statique peut désigner un prochain saut **non directement connecté** : le routeur cherche alors comment joindre ce prochain saut (recherche récursive). C’est le cas des routes BGP, dont le prochain saut est souvent une adresse loopback lointaine.

La ligne `Gateway of last resort is …` indique la route par défaut active. Si elle affiche `not set`, tout paquet sans route précise est **jeté** (avec un ICMP Destination Unreachable).

## Commandes de diagnostic

```cisco
R1# show ip route 10.20.30.5          ! quelle route est utilisée pour cette adresse ?
R1# show ip route longer-prefixes 10.20.0.0 255.255.0.0
R1# show ip cef 10.20.30.5            ! ce que le matériel utilise réellement
R1# traceroute 10.20.30.5 source Loopback0
```

`show ip route <adresse>` applique la règle du préfixe le plus long et montre **la** route choisie : c’est la commande à retenir pour répondre à « par où part ce paquet ? ».

## Exercices

**1.** Un routeur possède : `S 10.0.0.0/8 [1/0]`, `O 10.10.0.0/16 [110/20]`, `S* 0.0.0.0/0 [1/0]`. Par où partent les paquets pour 10.10.4.4, 10.99.1.1 et 172.16.0.1 ?

<details><summary>Voir le corrigé</summary>

- `10.10.4.4` → **OSPF /16** (plus précis que la statique /8, même si sa distance administrative est plus grande).
- `10.99.1.1` → **statique /8**.
- `172.16.0.1` → **route par défaut**.

</details>

**2.** On configure `ip route 10.50.0.0 255.255.255.0 10.255.0.9 130` alors qu’OSPF annonce aussi `10.50.0.0/24`. Laquelle est installée ? Que se passe-t-il si OSPF perd ce réseau ?

<details><summary>Voir le corrigé</summary>

La route **OSPF** (AD 110 < 130). La statique est une **route flottante** : elle n’est pas installée tant qu’OSPF fournit la route. Si OSPF la perd, la statique (AD 130) apparaît et prend le relais.

</details>

**3.** Après l’ajout d’une route statique `10.0.0.0/8` sur un routeur, l’accès à `10.20.30.0/24`, appris par OSPF, fonctionne toujours. Un collègue s’en étonne : la statique n’a-t-elle pas une meilleure distance administrative ? Explique.

<details><summary>Voir le corrigé</summary>

La distance administrative ne départage que des routes vers **le même préfixe**. `/8` et `/24` sont deux entrées différentes de la table ; pour une destination dans `10.20.30.0/24`, la règle du **préfixe le plus long** choisit la route OSPF /24.

</details>
