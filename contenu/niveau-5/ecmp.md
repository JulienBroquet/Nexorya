---
titre: ECMP
nom: Equal-Cost Multi-Path
idee: Quand plusieurs chemins ont exactement le même coût, le routeur les utilise tous en même temps, en répartissant les flux ; c’est la base des datacenters modernes.
osi: "3"
duree: [6, 12]
prerequis: [ospf]
retenir:
  - ECMP installe **plusieurs prochains sauts** pour une même destination quand leurs coûts sont égaux.
  - La répartition se fait **par flux** (hachage des adresses et des ports) pour garder les paquets dans l’ordre.
  - "Une fabric **leaf-spine** repose sur ECMP — chaque leaf joint chaque autre leaf par tous les spines."
---

## Le problème

Un switch a quatre liens de 100 Gb/s vers quatre switches de cœur. Si le routage n’en utilisait qu’un, on gaspillerait 75 % de la capacité, et une panne demanderait une reconvergence. On veut utiliser **tous** les liens en même temps.

> [!IMPORTANT] L’idée en une phrase
> Si plusieurs chemins ont le même coût, le routeur les garde tous et répartit les flux entre eux ; si l’un tombe, les flux se répartissent sur les autres.

## La fabric leaf-spine

```topologie
titre: Leaf-spine — chaque leaf est relié à chaque spine
S1 switch 1,0 "Spine 1"
S2 switch 3,0 "Spine 2"
L1 switch 0,1.3 "Leaf 1"
L2 switch 1.33,1.3 "Leaf 2"
L3 switch 2.66,1.3 "Leaf 3"
L4 switch 4,1.3 "Leaf 4"
S1 -- L1
S1 -- L2
S1 -- L3
S1 -- L4
S2 -- L1
S2 -- L2
S2 -- L3
S2 -- L4
```

Entre deux leafs, il y a autant de chemins de même coût que de spines (ici deux). Le trafic est réparti sur tous ; ajouter un spine ajoute de la capacité.

## Les mots à connaître

- **ECMP** — Utilisation simultanée de plusieurs chemins de même coût vers une destination.
- **Leaf-spine** — Architecture de datacenter où chaque switch d’accès (leaf) est relié à tous les switches de cœur (spine).
- **Hachage** — Calcul qui attribue chaque flux à un chemin, à partir de ses adresses et ports.

## Teste-toi

**Pourquoi ECMP répartit-il par flux plutôt que paquet par paquet ?**

<details><summary>Voir le corrigé</summary>

Pour que les paquets d’une même connexion suivent **le même chemin** et arrivent **dans l’ordre**. Des chemins de latences légèrement différentes désordonneraient les paquets, ce que TCP interprète comme des pertes.

</details>

<!-- approfondir -->

## Vérifier

```cisco
LEAF1# show ip route 10.40.3.0
Routing entry for 10.40.3.0/24
  Known via "ospf 1", distance 110, metric 3
  * 10.255.1.0, via Ethernet1/49
    10.255.2.0, via Ethernet1/50
LEAF1# show ip load-sharing
LEAF1# show ip cef exact-route 10.40.1.15 10.40.3.20     ! quel lien pour ce couple ?
```

## Les limites

- **Flux éléphants** : quelques très gros flux peuvent tomber sur le même lien et le saturer pendant que les autres sont peu chargés. Solutions : plus de flux parallèles, hachage incluant plus de champs, techniques de répartition dynamique (*flowlet*).
- **Polarisation** : si tous les routeurs utilisent la même fonction de hachage, les flux qui ont pris le lien 1 au premier niveau prennent aussi le lien 1 au niveau suivant. On varie le hachage (*seed*) par équipement.
- **Coût vraiment égal** : un lien plus lent avec le même coût (mauvaise référence de bande passante) reçoit autant de flux que les autres. En BGP, l’ECMP demande `maximum-paths` et des attributs identiques.

## Exercice

**Dans une fabric à 4 spines, un leaf perd son lien vers le spine 2. Que deviennent les flux qui passaient par ce lien ?**

<details><summary>Voir le corrigé</summary>

Le chemin par le spine 2 disparaît de la table : il reste **trois** chemins de même coût, et les flux concernés sont redistribués sur eux (rehachage). La capacité vers les autres leafs baisse d’un quart, sans coupure prolongée.

</details>
