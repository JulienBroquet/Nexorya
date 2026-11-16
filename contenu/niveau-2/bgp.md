---
titre: BGP
nom: Border Gateway Protocol
idee: BGP est le protocole qui relie les réseaux des organisations entre eux — c’est lui qui fait tenir Internet ; il ne cherche pas le chemin le plus rapide, mais applique les choix politiques de chaque organisation.
osi: "7 (transporté en TCP 179), décide du routage de couche 3"
duree: [10, 25]
prerequis: [ospf]
retenir:
  - Chaque organisation forme un **système autonome** (AS) identifié par un numéro ; BGP échange des routes **entre AS**.
  - "Une route BGP porte des **attributs** — le chemin d’AS traversés (**AS_PATH**), le prochain saut, les préférences locales…"
  - BGP choisit selon des **politiques** (préférence locale, AS_PATH le plus court…), pas selon la vitesse des liens.
  - On **filtre toujours** ce qu’on annonce et ce qu’on accepte — une erreur de BGP peut détourner le trafic d’autres organisations.
---

## Le problème : relier des réseaux qui ne se font pas confiance

OSPF fonctionne très bien **à l’intérieur** d’une organisation, où tous les routeurs se font confiance et partagent une carte complète. Mais Internet relie des dizaines de milliers d’organisations — opérateurs, hébergeurs, entreprises — qui ne veulent ni partager leur topologie, ni laisser les autres décider de leurs chemins. Et la table d’Internet compte plus de **900 000 réseaux IPv4**.

> [!IMPORTANT] L’idée en une phrase
> BGP fait échanger à des organisations indépendantes la liste des réseaux qu’elles savent joindre, en indiquant par quelles organisations il faut passer ; chacune choisit ensuite selon **ses propres règles**.

## Les systèmes autonomes

Un **système autonome** (AS) est un réseau géré par une seule organisation, avec une politique de routage commune : un opérateur, un hébergeur, une grande entreprise. Chacun a un **numéro d’AS** (par exemple AS 64512 dans les exemples, AS 3215 pour Orange, AS 13335 pour Cloudflare).

- **eBGP** (externe) : session entre deux AS différents, par exemple entre une entreprise et son opérateur.
- **iBGP** (interne) : session entre routeurs d’un même AS, pour partager les routes apprises de l’extérieur.

## Comment ça marche

1. Deux routeurs BGP ouvrent une **connexion TCP** (port 179) : ce sont des **pairs** (*peers*), configurés à la main — BGP ne découvre pas ses voisins tout seul.
2. Chacun annonce les réseaux qu’il sait joindre, avec leurs **attributs**.
3. Chacun choisit, pour chaque réseau, la meilleure route selon une liste de critères et ses politiques.
4. Ensuite, seuls les **changements** sont échangés.

```topologie
titre: Une entreprise reliée à deux opérateurs
ENT routeur 2,0 "Entreprise" "AS 64512 — 198.51.100.0/24"
OP1 nuage 0.5,1 "Opérateur A" "AS 65001"
OP2 nuage 3.5,1 "Opérateur B" "AS 65002"
NET nuage 2,2 "Internet"
ENT -- OP1 "eBGP"
ENT -- OP2 "eBGP"
OP1 -- NET
OP2 -- NET
```

L’entreprise annonce son réseau `198.51.100.0/24` à ses deux opérateurs. Si l’un tombe, Internet continue de la joindre par l’autre : c’est le **multihoming**.

## L’AS_PATH : la liste des étapes

Chaque route BGP transporte la liste des AS traversés. Une route vers `198.51.100.0/24` reçue par un AS lointain peut porter `AS_PATH : 65001 64512` : « passe par l’AS 65001, puis tu arrives dans l’AS 64512 ». Cette liste sert à deux choses :

- **éviter les boucles** : un AS qui voit son propre numéro dans l’AS_PATH rejette la route ;
- **choisir** : à critères égaux, BGP préfère le chemin qui traverse le moins d’AS.

## Les mots à connaître

- **BGP** — *Border Gateway Protocol*, protocole de routage entre systèmes autonomes, base d’Internet.
- **Système autonome (AS)** — Réseau géré par une organisation, identifié par un numéro d’AS.
- **Pair BGP** — Routeur avec lequel une session BGP est établie ; *peer* ou *neighbor*.
- **eBGP / iBGP** — Session BGP entre deux AS différents / au sein d’un même AS.
- **AS_PATH** — Attribut qui liste les AS traversés par une route.
- **Multihoming** — Raccordement d’une organisation à plusieurs opérateurs.

## Teste-toi

**1.** Pourquoi BGP n’utilise-t-il pas la vitesse des liens pour choisir ses chemins, comme OSPF ?

<details><summary>Voir le corrigé</summary>

Parce que les AS ne partagent pas leur topologie interne : un AS ne connaît pas la vitesse des liens des autres. Et surtout, entre organisations, les choix sont d’abord **commerciaux et politiques** (coût d’un opérateur, accords d’échange) : BGP est conçu pour appliquer ces politiques.

</details>

**2.** Un routeur de l’AS 64512 reçoit une route dont l’AS_PATH contient 64512. Que fait-il ?

<details><summary>Voir le corrigé</summary>

Il la **rejette** : la route est déjà passée par son propre AS, l’accepter créerait une boucle.

</details>

<!-- approfondir -->

## Les états d’une session

| État | Signification |
|---|---|
| Idle | session arrêtée ou en attente avant réessai |
| Connect / **Active** | tentative d’ouverture TCP ; « Active » qui persiste = le TCP n’aboutit pas (adresse, filtrage, route) |
| OpenSent / OpenConfirm | messages OPEN échangés : numéros d’AS, router-ID, capacités, temporisateurs |
| **Established** | session ouverte, les routes sont échangées |

Messages : **OPEN**, **UPDATE** (annonces et retraits), **KEEPALIVE** (toutes les 60 s ; *hold time* 180 s), **NOTIFICATION** (erreur, puis fermeture).

## La sélection du meilleur chemin (Cisco)

Pour un même préfixe, BGP compare les routes dans cet ordre, et s’arrête au premier critère qui départage :

1. le prochain saut doit être **joignable** ;
2. **Weight** le plus élevé (propre à Cisco, local au routeur) ;
3. **LOCAL_PREF** le plus élevé (partagé dans l’AS : choisit la **sortie** de l’AS) ;
4. route **originée localement** ;
5. **AS_PATH** le plus court ;
6. **ORIGIN** (IGP < EGP < incomplete) ;
7. **MED** le plus bas (suggestion faite par l’AS voisin pour l’**entrée** dans son réseau) ;
8. **eBGP** préféré à iBGP ;
9. métrique IGP la plus faible vers le prochain saut ;
10. puis critères de départage (route la plus ancienne, router-ID le plus bas…).

> [!TIP] Retenir l’essentiel
> Pour contrôler le trafic **sortant**, on joue sur **LOCAL_PREF** (sur les routes reçues). Pour influencer le trafic **entrant**, on agit sur ce qu’on annonce : **AS_PATH prepend** (rallonger artificiellement le chemin) ou des annonces plus précises. Le trafic entrant est toujours plus difficile à maîtriser, car la décision appartient aux autres.

## Configuration d’un multihoming simple (Cisco IOS)

```cisco
router bgp 64512
 bgp router-id 198.51.100.1
 bgp log-neighbor-changes
 neighbor 203.0.113.1 remote-as 65001
 neighbor 203.0.113.1 description Opérateur A
 neighbor 192.0.2.1 remote-as 65002
 neighbor 192.0.2.1 description Opérateur B
 !
 address-family ipv4
  network 198.51.100.0 mask 255.255.255.0
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 prefix-list ANNONCES out
  neighbor 203.0.113.1 route-map PREF-A in
  neighbor 192.0.2.1 activate
  neighbor 192.0.2.1 prefix-list ANNONCES out
 exit-address-family
!
! N'annoncer que notre propre réseau
ip prefix-list ANNONCES seq 10 permit 198.51.100.0/24
! Le préfixe annoncé doit exister dans la table (ex. route vers Null0)
ip route 198.51.100.0 255.255.255.0 Null0
!
! Préférer l'opérateur A en sortie
route-map PREF-A permit 10
 set local-preference 200
```

- La commande `network` annonce un préfixe **seulement s’il existe exactement dans la table de routage** : d’où la route vers `Null0`.
- La `prefix-list` en sortie est **indispensable** : sans elle, l’entreprise risquerait d’annoncer à l’opérateur B les routes apprises de l’opérateur A, et de devenir un lien de transit entre deux opérateurs. Voir [Filtrer les routes BGP](bgp-filtrage.md).

## Vérification

```cisco
R1# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent  Up/Down  State/PfxRcd
192.0.2.1       4 65002  128034    1204 2d03h        943211
203.0.113.1     4 65001  131772    1207 2d03h        943187

R1# show ip bgp 8.8.8.0/24
BGP routing table entry for 8.8.8.0/24
Paths: (2 available, best #1, table default)
  65001 15169
    203.0.113.1 from 203.0.113.1
      Origin IGP, localpref 200, valid, external, best
  65002 3356 15169
    192.0.2.1 from 192.0.2.1
      Origin IGP, localpref 100, valid, external
```

- `State/PfxRcd` contient un **nombre** : la session est *Established* et l’on reçoit ce nombre de préfixes (ici la table Internet complète). Un mot (`Active`, `Idle`) signifie que la session n’est pas établie.
- La meilleure route vers `8.8.8.0/24` passe par l’opérateur A grâce à la **LOCAL_PREF 200**, même si l’AS_PATH par B n’est pas plus long.

## Dépannage

| Symptôme | Causes probables |
|---|---|
| Session bloquée en **Active** | adresse du voisin erronée, pas de route vers lui, TCP 179 filtré, mauvaise source (iBGP entre loopbacks sans `update-source`) |
| Session qui monte puis tombe (NOTIFICATION) | numéro d’AS incorrect, authentification, trop de préfixes reçus (`maximum-prefix`) |
| Session Established, 0 préfixe reçu | filtre entrant trop strict, voisin qui n’annonce rien |
| Préfixe reçu mais pas installé | prochain saut injoignable (fréquent en iBGP : `next-hop-self`), meilleure route par une autre source |
| Notre réseau n’est pas vu sur Internet | `network` sans route exacte dans la table, filtre sortant, opérateur qui filtre (objet ROA/IRR manquant) |

## Exercices

**1.** Une session eBGP reste en état Active. Le ping vers l’adresse du voisin fonctionne. Que vérifier ?

<details><summary>Voir le corrigé</summary>

Le **TCP 179** : une ACL ou un pare-feu peut le bloquer ; le voisin peut attendre une **autre adresse source** ou un autre numéro d’AS ; une **authentification MD5** configurée d’un seul côté empêche aussi l’ouverture TCP. Vérifier la configuration `neighbor` des deux côtés et `debug ip bgp` (avec précaution).

</details>

**2.** Pour que le trafic **entrant** arrive de préférence par l’opérateur A, que peut faire l’entreprise ?

<details><summary>Voir le corrigé</summary>

Rendre la route annoncée par B **moins attirante** : *AS_PATH prepend* (annoncer `64512 64512 64512` à B), ou utiliser les **communautés** proposées par l’opérateur B pour baisser la préférence de la route chez lui. Elle ne peut que suggérer : la décision finale appartient aux autres AS.

</details>

**3.** Pourquoi une entreprise multihomée doit-elle filtrer ce qu’elle annonce à ses opérateurs, même si elle « n’a rien d’autre à annoncer » ?

<details><summary>Voir le corrigé</summary>

Parce qu’un routeur BGP réannonce par défaut à ses voisins eBGP les meilleures routes qu’il a apprises. Sans filtre, l’entreprise annoncerait à l’opérateur B toutes les routes d’Internet apprises par A : elle deviendrait un **chemin de transit**, attirant le trafic d’autres organisations. C’est l’origine de plusieurs incidents majeurs d’Internet.

</details>
