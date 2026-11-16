---
titre: RIP
nom: Routing Information Protocol
idee: RIP est le plus ancien protocole de routage dynamique — chaque routeur envoie régulièrement toute sa table à ses voisins, et choisit le chemin qui traverse le moins de routeurs.
osi: "3 (transporté en UDP 520)"
duree: [6, 12]
prerequis: [passerelle]
retenir:
  - "Métrique = **nombre de sauts** ; **16 = injoignable**, donc 15 routeurs au maximum."
  - Il envoie toute sa table toutes les **30 secondes** et converge **lentement**.
  - On le rencontre encore sur de vieux équipements ; on lui préfère **OSPF** ou EIGRP.
---

## Le problème : des routes qui se mettent à jour toutes seules

Avec des routes statiques, chaque ajout de réseau ou chaque panne demande une intervention humaine. Un **protocole de routage dynamique** fait échanger aux routeurs ce qu’ils savent, pour que chacun construise et mette à jour sa table automatiquement. RIP fut l’un des premiers.

> [!IMPORTANT] L’idée en une phrase
> Chaque routeur RIP dit régulièrement à ses voisins : « voici les réseaux que je connais, et à combien de sauts ils sont de moi ». Chacun garde le chemin le plus court en nombre de sauts.

## Comment ça marche

```topologie
titre: RIP compte les routeurs, pas la vitesse des liens
R1 routeur 0,0 "R1"
R2 routeur 2,0 "R2"
R3 routeur 1,1 "R3"
N switch 3,0 "Réseau 10.9.0.0/24"
R1 -- R2 "lien lent, 2 Mb/s"
R1 -- R3 "10 Gb/s"
R3 -- R2 "10 Gb/s"
R2 -- N
```

R1 peut joindre `10.9.0.0/24` en passant directement par R2 (**2 sauts**) ou par R3 puis R2 (**3 sauts**). RIP choisit le lien à 2 Mb/s, parce qu’il ne compte que les sauts. C’est sa principale faiblesse.

## Les limites de RIP

- **Maximum 15 sauts** : au-delà, le réseau est considéré comme injoignable.
- **Convergence lente** : après une panne, plusieurs minutes peuvent être nécessaires pour que tous les routeurs se mettent d’accord.
- **Il ignore la vitesse des liens.**

## Les mots à connaître

- **Protocole de routage dynamique** — Protocole par lequel les routeurs échangent leurs routes automatiquement.
- **Vecteur de distance** — Famille de protocoles où chaque routeur annonce à ses voisins des réseaux et leur distance, sans connaître toute la topologie.
- **Saut** — Passage par un routeur ; RIP mesure les chemins en nombre de sauts.
- **Convergence** — Moment où tous les routeurs ont une vision cohérente après un changement.

## Teste-toi

**Pourquoi un réseau RIP ne peut-il pas dépasser 15 routeurs de diamètre ?**

<details><summary>Voir le corrigé</summary>

Parce que la métrique **16** signifie « injoignable ». Ce plafond très bas sert à limiter la durée du problème de « comptage à l’infini » dans les boucles de routage.

</details>

<!-- approfondir -->

## Vecteur de distance et comptage à l’infini

Un routeur RIP ne connaît pas la topologie : il fait confiance à ce que disent ses voisins. Si R2 perd un réseau et que R1 lui annonce « je l’atteins en 2 sauts » (en réalité via R2 lui-même), R2 croit pouvoir le joindre via R1 en 3 sauts, et ainsi de suite : la métrique monte jusqu’à 16. Plusieurs mécanismes limitent ce phénomène :

| Mécanisme | Principe |
|---|---|
| **Split horizon** | ne pas réannoncer une route sur l’interface d’où on l’a apprise |
| **Route poisoning** | annoncer immédiatement une route perdue avec la métrique 16 |
| **Hold-down** | ignorer pendant 180 s les annonces moins bonnes d’une route qui vient de tomber |
| **Triggered updates** | envoyer un changement immédiatement, sans attendre les 30 s |

Temporisateurs par défaut : mise à jour **30 s**, invalidité **180 s**, hold-down **180 s**, suppression **240 s**.

## RIPv1, RIPv2, RIPng

| Version | Caractéristiques |
|---|---|
| RIPv1 | **sans masque** dans les annonces (classful), broadcast : à proscrire |
| RIPv2 | masques transportés (VLSM), multicast `224.0.0.9`, authentification MD5 |
| RIPng | version IPv6, `ff02::9`, port UDP 521 |

## Configuration (Cisco IOS)

```cisco
router rip
 version 2
 no auto-summary
 network 10.0.0.0
 network 192.168.20.0
 passive-interface default
 no passive-interface GigabitEthernet0/0/1
!
R1# show ip route rip
R     10.9.0.0/24 [120/2] via 10.255.0.2, 00:00:12, GigabitEthernet0/0/1
R1# debug ip rip
```

`[120/2]` : distance administrative 120, **2 sauts**. Le compteur `00:00:12` indique l’âge de la dernière mise à jour reçue.

## Exercice

**Lors d’une migration, RIP et OSPF tournent en même temps et annoncent tous deux `10.9.0.0/24`. Laquelle des deux routes est installée ?**

<details><summary>Voir le corrigé</summary>

La route **OSPF** : distance administrative 110 contre 120 pour RIP. Cette propriété permet de migrer progressivement : dès qu’OSPF connaît un réseau, il prend le dessus, et l’on retire RIP à la fin.

</details>
