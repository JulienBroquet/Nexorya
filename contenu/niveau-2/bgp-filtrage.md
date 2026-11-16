---
titre: Filtrer les routes BGP
nom: Prefix-lists, route-maps et protections
idee: Un routeur BGP doit décider précisément ce qu’il accepte et ce qu’il annonce ; les prefix-lists choisissent les réseaux, les route-maps appliquent des actions (préférence, communautés) aux routes choisies.
osi: "3"
duree: [8, 20]
cle: true
prerequis: [bgp]
retenir:
  - "**En sortie** — n’annoncer que ses propres réseaux. **En entrée** — refuser les routes absurdes (adresses privées, ses propres réseaux, préfixes trop précis)."
  - Une **prefix-list** sélectionne des réseaux (avec `ge` / `le` pour les longueurs) ; une **route-map** combine conditions et actions.
  - Tout ce qui n’est pas explicitement autorisé à la fin d’une prefix-list ou d’une route-map est **refusé**.
  - "`maximum-prefix` protège le routeur d’un voisin qui envoie trop de routes."
---

## Le problème : une erreur qui touche tout Internet

En BGP, ce que tu annonces est **cru** par tes voisins, qui le réannoncent à leurs voisins. Une entreprise qui annonce par erreur des réseaux qui ne lui appartiennent pas peut attirer le trafic de millions d’utilisateurs. Inversement, accepter n’importe quoi d’un voisin peut remplir la mémoire du routeur ou détourner le trafic de l’entreprise.

> [!IMPORTANT] L’idée en une phrase
> Sur chaque session BGP, on écrit **deux listes** : ce qu’on accepte d’entendre, et ce qu’on accepte de dire. Tout le reste est refusé.

## Les deux outils

| Outil | Rôle | Analogie |
|---|---|---|
| **Prefix-list** | sélectionner des réseaux selon leur adresse et leur longueur | une liste d’invités à l’entrée |
| **Route-map** | « si la route correspond à… alors… » : accepter, refuser, ou modifier des attributs | un videur qui applique des règles et donne un bracelet de couleur |

```topologie
titre: Les filtres aux frontières de l’entreprise
E routeur 1.6,0.8 "Routeur Internet" "AS 64512"
OP1 nuage 0,0 "Opérateur A"
OP2 nuage 0,1.6 "Opérateur B"
LAN nuage 3.4,0.8 "Réseau de l’entreprise" "198.51.100.0/24"
E ++ OP1 "sortie : 198.51.100.0/24 seulement"
E ++ OP2 "sortie : 198.51.100.0/24 seulement"
E -- LAN
```

## Exemple : n’annoncer que son réseau

```cisco
ip prefix-list MES-RESEAUX seq 10 permit 198.51.100.0/24
!
router bgp 64512
 address-family ipv4
  neighbor 203.0.113.1 prefix-list MES-RESEAUX out
```

L’entreprise n’annonce que `198.51.100.0/24`. Même si une erreur de configuration faisait apparaître d’autres routes dans sa table BGP, elles ne sortiraient pas.

## Les mots à connaître

- **Prefix-list** — Liste qui sélectionne des préfixes selon leur adresse et leur longueur.
- **Route-map** — Suite de règles « condition → action » appliquée à des routes.
- **Bogon** — Préfixe qui ne devrait jamais apparaître sur Internet (adresses privées, réservées, non attribuées).
- **Détournement BGP** — Annonce, volontaire ou accidentelle, de réseaux appartenant à quelqu’un d’autre ; *BGP hijack*.

## Teste-toi

**Un opérateur t’envoie une route vers `10.0.0.0/8`. Faut-il l’accepter ?**

<details><summary>Voir le corrigé</summary>

**Non.** `10.0.0.0/8` est une plage **privée** : elle ne doit jamais circuler sur Internet. L’accepter pourrait détourner vers l’opérateur une partie de ton propre trafic interne. Les plages privées et réservées (*bogons*) sont filtrées en entrée.

</details>

<!-- approfondir -->

## Prefix-lists : `ge` et `le`

Une ligne de prefix-list compare l’**adresse** (selon la longueur indiquée) et la **longueur** du préfixe :

| Ligne | Correspond à |
|---|---|
| `permit 10.0.0.0/8` | exactement `10.0.0.0/8`, rien d’autre |
| `permit 10.0.0.0/8 le 32` | `10.0.0.0/8` et tous les préfixes plus précis inclus dedans |
| `permit 10.0.0.0/8 ge 24 le 24` | tous les /24 inclus dans `10.0.0.0/8` |
| `permit 0.0.0.0/0` | uniquement la route par défaut |
| `permit 0.0.0.0/0 le 32` | toutes les routes |
| `deny 0.0.0.0/0 ge 25` | tous les préfixes plus précis que /24 |

Une prefix-list se termine par un **refus implicite** : une route qui ne correspond à aucune ligne est refusée.

## Un filtre d’entrée réaliste

```cisco
ip prefix-list ENTREE-OPERATEUR seq 5  deny 0.0.0.0/8 le 32
ip prefix-list ENTREE-OPERATEUR seq 10 deny 10.0.0.0/8 le 32
ip prefix-list ENTREE-OPERATEUR seq 15 deny 100.64.0.0/10 le 32
ip prefix-list ENTREE-OPERATEUR seq 20 deny 127.0.0.0/8 le 32
ip prefix-list ENTREE-OPERATEUR seq 25 deny 169.254.0.0/16 le 32
ip prefix-list ENTREE-OPERATEUR seq 30 deny 172.16.0.0/12 le 32
ip prefix-list ENTREE-OPERATEUR seq 35 deny 192.168.0.0/16 le 32
ip prefix-list ENTREE-OPERATEUR seq 40 deny 224.0.0.0/3 le 32
ip prefix-list ENTREE-OPERATEUR seq 45 deny 198.51.100.0/24 le 32   ! nos propres réseaux
ip prefix-list ENTREE-OPERATEUR seq 50 deny 0.0.0.0/0 ge 25          ! trop précis
ip prefix-list ENTREE-OPERATEUR seq 100 permit 0.0.0.0/0 le 24
!
router bgp 64512
 address-family ipv4
  neighbor 203.0.113.1 prefix-list ENTREE-OPERATEUR in
  neighbor 203.0.113.1 maximum-prefix 1100000 90 restart 15
```

`maximum-prefix 1100000 90 restart 15` : avertir à 90 % de la limite, couper la session si elle est dépassée, et réessayer 15 minutes plus tard. Cela protège la mémoire du routeur si l’opérateur envoie par erreur des millions de routes.

Beaucoup d’entreprises n’ont pas besoin de la table complète : elles demandent seulement une **route par défaut** à chaque opérateur, ou la route par défaut plus les réseaux de l’opérateur (*partial routes*).

## Route-maps : conditions et actions

```cisco
ip prefix-list CLOUD-PREFERE seq 10 permit 203.0.113.128/25
!
route-map ENTREE-A permit 10
 match ip address prefix-list CLOUD-PREFERE
 set local-preference 300           ! ce réseau : préférer l'opérateur A
route-map ENTREE-A permit 20
 set local-preference 150           ! le reste : préférence moyenne
!
route-map SORTIE-B permit 10
 match ip address prefix-list MES-RESEAUX
 set as-path prepend 64512 64512    ! rendre B moins attirant pour le trafic entrant
!
router bgp 64512
 address-family ipv4
  neighbor 203.0.113.1 route-map ENTREE-A in
  neighbor 192.0.2.1 route-map SORTIE-B out
```

Fonctionnement d’une route-map :

- les **séquences** sont évaluées dans l’ordre (10, 20…) ; la première dont les conditions (`match`) correspondent s’applique ;
- `permit` accepte la route (et applique les `set`), `deny` la refuse ;
- une séquence **sans `match`** correspond à tout ;
- une route qui ne correspond à **aucune** séquence est **refusée** (refus implicite).

> [!WARNING]
> Oublier la séquence finale `permit` sans condition (la séquence 20 ci-dessus) est l’erreur la plus fréquente : la route-map ne laisse alors passer **que** les routes explicitement citées, et toutes les autres disparaissent.

## Les communautés

Une **communauté** est une étiquette (`65001:120`) attachée à une route. Les opérateurs publient la signification des leurs : « ne pas annoncer à tel partenaire », « baisser la préférence », « *blackhole* » (jeter tout le trafic vers ce préfixe, pour absorber une attaque). C’est le moyen standard d’agir **chez son opérateur** sans y avoir accès.

```cisco
route-map SORTIE-A permit 10
 match ip address prefix-list MES-RESEAUX
 set community 65001:80 additive
!
router bgp 64512
 address-family ipv4
  neighbor 203.0.113.1 send-community
```

## Sécuriser l’origine : RPKI

Les filtres manuels ne suffisent pas à l’échelle d’Internet. Le **RPKI** permet au titulaire d’un réseau de publier une attestation signée (**ROA**) : « le préfixe `198.51.100.0/24` peut être annoncé par l’AS 64512, au plus en /24 ». Les routeurs qui valident le RPKI rejettent les annonces **invalides**. Publier des ROA pour ses propres réseaux est aujourd’hui une bonne pratique de base, et de nombreux opérateurs l’exigent.

## Vérifier l’effet d’un filtre

```cisco
R1# show ip bgp neighbors 203.0.113.1 advertised-routes   ! ce que j'annonce
R1# show ip bgp neighbors 203.0.113.1 received-routes     ! avant filtre (si soft-reconfiguration inbound)
R1# show ip bgp neighbors 203.0.113.1 routes              ! après filtre
R1# show ip prefix-list ENTREE-OPERATEUR detail           ! compteurs de correspondances
R1# clear ip bgp 203.0.113.1 soft in                      ! réappliquer un filtre sans couper la session
```

## Exercices

**1.** Écris une prefix-list qui autorise uniquement les /24 inclus dans `198.51.100.0/22`.

<details><summary>Voir le corrigé</summary>

`ip prefix-list LES-24 seq 10 permit 198.51.100.0/22 ge 24 le 24`. Elle correspond aux quatre /24 : `198.51.100.0`, `.101.0`, `.102.0`, `.103.0`, et à rien d’autre.

</details>

**2.** Une route-map appliquée en entrée ne contient qu’une séquence : `permit 10` avec `match ip address prefix-list CLOUD` et `set local-preference 300`. Que deviennent les autres routes de l’opérateur ?

<details><summary>Voir le corrigé</summary>

Elles sont **refusées** : elles ne correspondent à aucune séquence, et la route-map se termine par un refus implicite. L’entreprise ne reçoit plus que les réseaux de la liste CLOUD. Il faut ajouter une séquence `route-map … permit 20` sans `match`.

</details>

**3.** Pourquoi refuser en entrée les préfixes plus précis que /24 ?

<details><summary>Voir le corrigé</summary>

Par convention, les préfixes plus précis que /24 (en IPv4) ne sont **pas acceptés** sur Internet : ils gonfleraient les tables de tous les routeurs. Une annonce /25 venant d’un opérateur est donc anormale (erreur, ou tentative de détournement, puisqu’un préfixe plus précis l’emporte toujours). Les refuser protège l’entreprise.

</details>
