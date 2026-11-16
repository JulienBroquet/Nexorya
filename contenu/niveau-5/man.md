---
titre: MAN
nom: Le réseau métropolitain
idee: Un MAN relie des sites d’une même ville ou agglomération — campus universitaire, hôpitaux, mairie et ses bâtiments — souvent par des fibres louées ou un service Ethernet d’opérateur.
osi: "1 à 3"
duree: [5, 10]
prerequis: [lan]
retenir:
  - Un MAN couvre une **ville** ou une **agglomération** (quelques km à quelques dizaines de km).
  - "Supports — **fibre noire** louée, **longueurs d’onde** (WDM), ou **service Ethernet** d’opérateur (point à point, multipoint)."
  - On y retrouve QinQ, MPLS, MACsec pour transporter et protéger le trafic.
---

## Le problème

Une collectivité a une mairie, dix écoles, une médiathèque et un centre technique répartis dans la ville. Une université a plusieurs campus. Ces sites ont besoin de liaisons rapides et fiables, bien au-delà des 100 m du câble cuivre et des quelques kilomètres d’une fibre interne.

> [!IMPORTANT] L’idée en une phrase
> Le MAN relie des sites d’une même ville avec des fibres ou des services d’opérateur, de façon que l’ensemble se comporte comme un grand réseau d’entreprise.

## Les options de raccordement

| Option | Ce que l’on loue | On maîtrise… | Débit |
|---|---|---|---|
| **Fibre noire** | une fibre « nue » entre deux sites | tout : les modules optiques, le débit, le chiffrement | selon les équipements (10 à 400 Gb/s) |
| **Longueur d’onde** (WDM) | une « couleur » sur la fibre de l’opérateur | le trafic dans cette longueur d’onde | 10 à 400 Gb/s |
| **Service Ethernet** (point à point, multipoint) | un service de niveau 2 | les VLAN transportés | de 100 Mb/s à 100 Gb/s |
| **Service IP / MPLS VPN** | un service de niveau 3 | le routage avec l’opérateur | variable |

## Les mots à connaître

- **MAN** — *Metropolitan Area Network*, réseau à l’échelle d’une ville.
- **Fibre noire** — Fibre optique louée sans équipement actif, que le client allume avec ses propres modules.
- **WDM** — *Wavelength Division Multiplexing*, transport de plusieurs longueurs d’onde sur une même fibre.

## Teste-toi

**Quel est l’intérêt principal de la fibre noire par rapport à un service Ethernet d’opérateur ?**

<details><summary>Voir le corrigé</summary>

On **maîtrise tout** : on choisit le débit (en changeant simplement les modules optiques), on peut multiplexer plusieurs liens, et l’opérateur ne voit jamais le trafic. En contrepartie, on gère soi-même les équipements et le dépannage optique.

</details>

<!-- approfondir -->

## Architecture type

```topologie
titre: Un réseau métropolitain en anneau
MAI l3 2,0 "Mairie" "cœur"
E1 switch 0.5,1 "École A"
E2 switch 3.5,1 "École B"
MED switch 1,2 "Médiathèque"
CT switch 3,2 "Centre technique"
MAI -- E1 "fibre"
MAI -- E2 "fibre"
E1 -- MED
E2 -- CT
MED -- CT
```

- Un **anneau** (ou un double raccordement) évite qu’une coupure de fibre, fréquente lors de travaux de voirie, isole un site.
- Le routage (OSPF, IS-IS) ou des protocoles d’anneau rapides assurent la bascule.
- Chiffrement des liens : **MACsec** sur fibre noire ou longueur d’onde, **IPsec** sur un service partagé.

## Points d’attention

- **Budget optique** de chaque lien (longueur, connecteurs, épissures, marge), voir [Câbles cuivre et fibres](../niveau-1/cablage.md).
- **MTU** du service de l’opérateur, si l’on transporte des étiquettes (QinQ) ou des tunnels.
- **Contrat de service** (délai de rétablissement, chemins physiquement distincts pour la redondance : deux fibres dans la même tranchée tombent ensemble).

## Exercice

**Une ville a doublé tous ses liens MAN pour la redondance, mais une seule pelleteuse a coupé les deux liens d’une école. Que fallait-il vérifier ?**

<details><summary>Voir le corrigé</summary>

La **diversité physique** des chemins : les deux fibres empruntaient le même fourreau ou la même tranchée. Une vraie redondance exige des **parcours distincts**, à exiger contractuellement (et à vérifier sur plan) auprès de l’opérateur.

</details>
