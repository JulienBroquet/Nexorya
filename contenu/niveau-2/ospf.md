---
titre: OSPF
nom: Open Shortest Path First
idee: Avec OSPF, chaque routeur reçoit la carte complète du réseau, puis calcule lui-même le chemin le plus rapide vers chaque destination ; après une panne, la carte est mise à jour en quelques secondes.
osi: "3 (protocole IP 89)"
duree: [12, 30]
prerequis: [passerelle]
retenir:
  - OSPF est un protocole **à état de liens** — chaque routeur connaît la topologie et calcule les chemins avec l’algorithme de **Dijkstra**.
  - La métrique est un **coût** inversement proportionnel au débit — un lien rapide coûte moins cher.
  - "Les voisins doivent s’accorder — **zone**, **réseau et masque**, **temporisateurs**, **MTU**, authentification."
  - On découpe les grands réseaux en **zones** autour de la zone **0** (backbone).
---

## Le problème : choisir le chemin le plus rapide, et vite

Le [routage statique](routage-statique.md) ne s’adapte pas aux pannes, et [RIP](rip.md) choisit mal ses chemins et réagit lentement. Une entreprise avec plusieurs bâtiments et des liens redondants a besoin d’un protocole qui **connaît la vitesse des liens**, qui **réagit en secondes** et qui fonctionne avec **toutes les marques** d’équipements.

> [!IMPORTANT] L’idée en une phrase
> Chaque routeur OSPF décrit ses propres liens à tous les autres. Tous obtiennent ainsi **la même carte** du réseau, et chacun calcule dessus ses meilleurs chemins.

> [!TIP] L’analogie du GPS
> RIP, c’est demander son chemin aux passants, qui ne connaissent que la direction à prendre. OSPF, c’est un GPS : chaque routeur a la **carte complète** avec la vitesse de chaque route, et calcule lui-même l’itinéraire le plus rapide.

## Comment ça marche, étape par étape

1. **Trouver ses voisins.** Chaque routeur envoie des messages **Hello** toutes les 10 secondes sur ses interfaces OSPF. Deux routeurs qui s’entendent et sont compatibles deviennent **voisins**.
2. **Échanger la carte.** Les voisins s’échangent la description de tous les liens qu’ils connaissent (les **LSA**). Chaque routeur construit une **base de données** de la topologie, identique chez tous.
3. **Calculer.** Chaque routeur applique l’algorithme de **Dijkstra** (« plus court chemin d’abord », d’où le nom *Shortest Path First*) pour trouver le meilleur chemin vers chaque réseau.
4. **Réagir.** Si un lien tombe, les routeurs concernés envoient immédiatement une mise à jour ; tous recalculent. La convergence prend quelques secondes.

## Le coût : la vitesse compte

Le coût d’un lien vaut, par défaut, **100 Mb/s ÷ débit du lien** (avec un minimum de 1). Le chemin retenu est celui dont la **somme des coûts** est la plus faible.

```topologie
titre: OSPF préfère deux liens rapides à un lien lent
R1 routeur 0,0 "R1"
R2 routeur 2,0 "R2"
R3 routeur 1,1 "R3"
N switch 3,0 "10.9.0.0/24"
R1 -- R2 "10 Mb/s : coût 10"
R1 ++ R3 "1 Gb/s : coût 1*"
R3 ++ R2 "1 Gb/s : coût 1*"
R2 -- N
```

Chemin direct R1 → R2 : coût 10. Chemin R1 → R3 → R2 : coût 1 + 1 = 2. OSPF choisit **le chemin par R3**, plus long en sauts mais bien plus rapide.

\* Avec la référence par défaut de 100 Mb/s, tous les liens de 100 Mb/s et plus coûtent 1 : on ne distingue plus 1 Gb/s de 100 Gb/s. En pratique, on **relève la référence** (voir « Approfondir »).

## Les zones

Dans un grand réseau, chaque changement oblige tous les routeurs à recalculer. On découpe donc le réseau en **zones** (*areas*). Toutes les zones se raccrochent à la **zone 0**, l’épine dorsale. Les routeurs d’une zone connaissent le détail de leur zone, et seulement un **résumé** des autres. Dans une PME, une seule zone 0 suffit souvent.

## Les mots à connaître

- **OSPF** — *Open Shortest Path First*, protocole de routage standard à état de liens.
- **État de liens** — Famille de protocoles où chaque routeur connaît la topologie complète ; *link state*.
- **LSA** — *Link State Advertisement*, description d’un lien ou d’un réseau diffusée par un routeur OSPF.
- **Coût** — Métrique OSPF d’un lien, d’autant plus faible que le lien est rapide.
- **Zone** — Partie d’un réseau OSPF ; la zone 0 est l’épine dorsale à laquelle les autres se raccrochent.
- **Voisin / adjacence** — Relation établie entre deux routeurs OSPF compatibles qui échangent leurs bases.

## Teste-toi

**1.** Deux routeurs reliés par un câble n’arrivent pas à devenir voisins OSPF. L’un est configuré dans la zone 0, l’autre dans la zone 1 sur ce lien. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Les deux extrémités d’un lien doivent être **dans la même zone**. Le numéro de zone est inscrit dans les messages Hello : s’il diffère, les routeurs ignorent les Hello de l’autre.

</details>

**2.** Pourquoi OSPF converge-t-il beaucoup plus vite que RIP ?

<details><summary>Voir le corrigé</summary>

Parce qu’un changement est **diffusé immédiatement** à tous les routeurs, et que chacun **recalcule** seul sur une carte complète, sans attendre que l’information se propage de voisin en voisin toutes les 30 secondes.

</details>

<!-- approfondir -->

## La formation d’une adjacence

```sequence
titre: États d’une adjacence OSPF
R1 | R2
R1 -> R2 : Hello (router-id 1.1.1.1, zone 0, temporisateurs) — état Init chez R2
R2 -> R1 : Hello qui cite 1.1.1.1 comme voisin vu — état 2-Way
note R1, R2 : sur un réseau multi-accès, élection DR/BDR
R1 -> R2 : DBD : négociation maître / esclave — état ExStart (MTU comparée ici)
R2 -> R1 : DBD : résumé de la base — état Exchange
R1 -> R2 : LSR : « envoie-moi ces LSA » — état Loading
R2 --> R1 : LSU contenant les LSA demandées
R1 --> R2 : LSAck — état Full
```

Les conditions pour devenir voisins :

| Paramètre | Doit être identique |
|---|---|
| Zone et type de zone (stub…) | oui |
| Sous-réseau et masque de l’interface | oui (sauf liens point à point non numérotés) |
| Hello / Dead interval | oui (10 / 40 s par défaut sur Ethernet) |
| Authentification | oui |
| MTU | oui, sinon blocage en **ExStart/Exchange** |
| Router-ID | doit être **différent** |

## DR et BDR

Sur un segment multi-accès (Ethernet partagé avec plusieurs routeurs), chaque routeur ne forme une adjacence complète qu’avec un **routeur désigné** (DR) et un secours (BDR), pour éviter un maillage complet. L’élection se fait sur la **priorité** d’interface (1 par défaut, 0 = jamais DR) puis le **router-ID**. Elle n’est **pas préemptive** : un routeur à priorité plus haute qui arrive plus tard ne prend pas la place.

Sur un lien entre **deux** routeurs seulement, l’élection est inutile : on configure `ip ospf network point-to-point`, qui accélère aussi la formation de l’adjacence.

## Types de LSA principaux

| Type | Nom | Émis par | Contenu |
|---|---|---|---|
| 1 | Router | chaque routeur | ses liens dans la zone |
| 2 | Network | le DR | les routeurs d’un segment multi-accès |
| 3 | Summary | les ABR (routeurs de bordure de zone) | les réseaux des autres zones |
| 5 | External | les ASBR | les routes importées (statiques, autre protocole) |
| 7 | NSSA External | ASBR d’une zone NSSA | routes externes dans une zone « not so stubby » |

Les **zones stub** refusent les LSA 5 (et les remplacent par une route par défaut) ; les **totally stubby** refusent aussi les LSA 3. Cela réduit la taille des bases dans les sites distants.

## Configuration (Cisco IOS)

```cisco
router ospf 1
 router-id 10.255.255.1
 auto-cost reference-bandwidth 100000     ! 100 Gb/s : 1 Gb/s coûte 100, 10 Gb/s coûte 10
 passive-interface default                ! pas de Hello vers les LAN utilisateurs
 no passive-interface GigabitEthernet0/0/1
 default-information originate            ! propager la route par défaut
!
interface GigabitEthernet0/0/1
 ip address 10.255.0.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 Un-Secret
!
interface Vlan10
 ip ospf 1 area 0                         ! le réseau est annoncé, sans Hello (passive)
```

- `reference-bandwidth` doit être **la même sur tous les routeurs**, sinon les coûts sont incohérents.
- `passive-interface default` empêche un poste malveillant de se faire passer pour un routeur sur un VLAN d’utilisateurs.
- Les versions récentes privilégient l’authentification par **trousseau de clés en SHA** (`ip ospf authentication key-chain`).

## Vérification

```cisco
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.255.255.2      0   FULL/  -        00:00:36    10.255.0.2      Gi0/0/1
10.255.255.3      1   FULL/BDR        00:00:33    10.10.0.3       Vl10

R1# show ip ospf interface brief
Interface    PID   Area   IP Address/Mask    Cost  State Nbrs F/C
Gi0/0/1      1     0      10.255.0.1/30      100   P2P   1/1
Vl10         1     0      10.10.0.1/24       100   DR    0/0

R1# show ip route ospf
O     10.9.0.0/24 [110/200] via 10.255.0.2, 01:12:44, GigabitEthernet0/0/1
O IA  10.40.0.0/16 [110/300] via 10.255.0.2, 01:12:44, GigabitEthernet0/0/1
O E2  0.0.0.0/0 [110/1] via 10.255.0.2, 01:12:44, GigabitEthernet0/0/1
```

`O IA` : route d’une autre zone (*inter-area*). `O E2` : route externe, importée par un ASBR (son coût ne tient pas compte du chemin interne).

## Dépannage par symptôme

| Symptôme | Cause probable | Vérifier |
|---|---|---|
| Aucun voisin | interface passive, zone, sous-réseau, Hello/Dead, ACL bloquant le protocole 89, authentification | `show ip ospf interface`, `debug ip ospf adj` |
| Voisin bloqué en **ExStart/Exchange** | **MTU différente** | `show interfaces`, `ip mtu` |
| Voisin bloqué en **2-Way** | normal entre deux DROTHER sur un segment multi-accès | rien à corriger |
| Voisin FULL mais route absente | réseau non annoncé, filtrage, type de zone | `show ip ospf database`, `network` / `ip ospf area` |
| Chemin inattendu | coûts par défaut (référence de 100 Mb/s) | `show ip ospf interface brief` |
| Router-ID dupliqué | deux routeurs avec le même ID | journal `%OSPF-4-DUP_RTRID` |

## Exercices

**1.** Avec `auto-cost reference-bandwidth 100000`, quel est le coût d’un lien à 1 Gb/s, à 10 Gb/s et à 40 Gb/s ?

<details><summary>Voir le corrigé</summary>

Référence 100 000 Mb/s. 1 Gb/s : 100 000 / 1 000 = **100**. 10 Gb/s : **10**. 40 Gb/s : 100 000 / 40 000 = 2,5, arrondi à **2**.

</details>

**2.** Deux routeurs restent indéfiniment en état EXSTART. L’un a une interface en MTU 1500, l’autre en 9000. Explique et propose deux corrections.

<details><summary>Voir le corrigé</summary>

Pendant l’échange des descriptions de base (DBD), chaque routeur annonce sa MTU ; un routeur rejette les DBD dont la MTU annoncée dépasse la sienne. L’échange ne progresse pas. Corriger en **alignant la MTU** des deux côtés (solution propre), ou, en dernier recours, avec `ip ospf mtu-ignore`, qui masque le problème mais peut provoquer des pertes de gros paquets OSPF.

</details>

**3.** Après l’ajout d’un routeur, `show ip ospf neighbor` affiche des voisins qui apparaissent et disparaissent, et le journal mentionne un router-ID dupliqué. Que s’est-il passé ?

<details><summary>Voir le corrigé</summary>

Le nouveau routeur a été configuré (souvent par copie d’une configuration existante) avec le **même router-ID** qu’un autre. Les LSA des deux routeurs s’écrasent mutuellement : la base est instable. Corriger le router-ID (`router-id`), puis `clear ip ospf process` sur le routeur modifié.

</details>
