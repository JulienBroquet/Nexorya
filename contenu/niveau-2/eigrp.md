---
titre: EIGRP
nom: Enhanced Interior Gateway Routing Protocol
idee: EIGRP est un protocole de routage d’origine Cisco qui calcule ses chemins avec la bande passante et le délai, et garde en réserve un chemin de secours garanti sans boucle pour basculer instantanément.
osi: "3 (protocole IP 88)"
duree: [7, 16]
prerequis: [passerelle]
retenir:
  - "Métrique composite — par défaut, **bande passante minimale** du chemin et **délai cumulé**."
  - Le **successeur** est le meilleur chemin ; le **successeur possible** (*feasible successor*) est un secours pré-validé, utilisé immédiatement en cas de panne.
  - Distance administrative **90** (interne) ; publié en RFC 7868, mais surtout utilisé dans les réseaux Cisco.
---

## Le problème

Les entreprises équipées uniquement en Cisco ont longtemps voulu un protocole plus simple qu’OSPF à configurer, plus intelligent que RIP, et capable de basculer instantanément sur un chemin de secours. Cisco a créé EIGRP.

> [!IMPORTANT] L’idée en une phrase
> EIGRP choisit le chemin le plus rapide d’après la bande passante et le délai, et **prépare à l’avance** un chemin de secours dont il a prouvé qu’il ne crée pas de boucle.

## Comment ça marche

1. Les routeurs découvrent leurs voisins avec des **Hello** (toutes les 5 s sur un LAN).
2. Ils échangent leurs routes **une fois**, puis seulement les **changements** (pas de mises à jour périodiques comme RIP).
3. Pour chaque réseau, chaque routeur retient :
   - le **successeur** : le voisin par lequel passe le meilleur chemin ;
   - un éventuel **successeur possible** : un voisin de secours dont le chemin est garanti sans boucle.
4. Si le successeur disparaît et qu’un successeur possible existe, la bascule est **immédiate**. Sinon, le routeur interroge ses voisins (*query*) pour trouver un nouveau chemin.

## Les mots à connaître

- **EIGRP** — Protocole de routage hybride d’origine Cisco, fondé sur l’algorithme DUAL.
- **Successeur** — Voisin par lequel passe le meilleur chemin vers un réseau.
- **Successeur possible** — Voisin de secours dont le chemin est garanti sans boucle ; *feasible successor*.
- **Système autonome (AS)** — Numéro qui regroupe les routeurs EIGRP qui doivent échanger leurs routes.

## Teste-toi

**Pourquoi EIGRP peut-il basculer plus vite qu’OSPF dans certains cas ?**

<details><summary>Voir le corrigé</summary>

Parce que le **successeur possible** est calculé **à l’avance** : en cas de panne, le routeur l’installe aussitôt, sans recalcul ni échange. OSPF doit, lui, recevoir la mise à jour et recalculer (très vite aussi sur du matériel moderne).

</details>

<!-- approfondir -->

## La métrique

Avec les coefficients par défaut (K1 = K3 = 1, les autres à 0) :

```text
métrique = 256 × ( 10^7 / bande passante minimale du chemin en kb/s  +  somme des délais en dizaines de µs )

Exemple : chemin dont le lien le plus lent est à 100 Mb/s, 3 liens de 10 µs de délai chacun
  10^7 / 100 000 = 100      délai : 3 × 1 = 3      métrique = 256 × 103 = 26 368
```

Les coefficients K doivent être **identiques** sur tous les voisins, sinon l’adjacence ne se forme pas. Les versions récentes utilisent des **métriques étendues** (*wide metrics*) adaptées aux liens au-delà de 10 Gb/s.

## La condition de faisabilité

- **FD** (*Feasible Distance*) : la meilleure métrique totale connue vers le réseau.
- **RD** (*Reported Distance*) : la métrique annoncée par un voisin, c’est-à-dire sa propre distance vers le réseau.

Un voisin devient successeur possible si **sa RD est strictement inférieure à la FD** du routeur. Cela prouve qu’il est plus proche de la destination que le routeur lui-même : il ne peut donc pas renvoyer le trafic vers lui (pas de boucle).

## Configuration (Cisco IOS, mode nommé)

```cisco
router eigrp ENTREPRISE
 address-family ipv4 unicast autonomous-system 100
  af-interface default
   passive-interface
  exit-af-interface
  af-interface GigabitEthernet0/0/1
   no passive-interface
  exit-af-interface
  network 10.0.0.0
  eigrp router-id 10.255.255.1
```

```cisco
R1# show ip eigrp topology 10.9.0.0/24
P 10.9.0.0/24, 1 successors, FD is 26368
        via 10.255.0.2 (26368/2816), GigabitEthernet0/0/1
        via 10.255.0.6 (28672/26112), GigabitEthernet0/0/2
```

La seconde ligne a une RD de 26 112, **inférieure** à la FD de 26 368 : c’est un **successeur possible**.

## Exercice

**Un voisin annonce une route avec une RD de 30 000 ; la FD du routeur vers ce réseau est 26 368. Ce voisin peut-il être successeur possible ? Pourquoi ?**

<details><summary>Voir le corrigé</summary>

**Non.** Sa RD (30 000) n’est pas inférieure à la FD (26 368) : rien ne garantit que son chemin ne passe pas par le routeur lui-même. EIGRP ne le garde pas en secours immédiat ; si le successeur tombe, il devra interroger ses voisins.

</details>
