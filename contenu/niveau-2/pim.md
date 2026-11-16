---
titre: PIM
nom: Protocol Independent Multicast
idee: PIM fait construire aux routeurs l’arbre de distribution d’un flux multicast, depuis la source jusqu’aux réseaux qui ont des abonnés, en s’appuyant sur la table de routage existante.
osi: "3 (protocole IP 103)"
duree: [7, 18]
prerequis: [igmp]
retenir:
  - PIM est « indépendant du protocole » — il réutilise la **table de routage unicast** (OSPF, statique…).
  - "**PIM Sparse Mode** — le flux n’est envoyé que là où il a été **demandé** (Join)."
  - "Le contrôle **RPF** n’accepte un paquet multicast que s’il arrive par l’interface qui mène **vers la source**."
  - En ASM, un **RP** (point de rendez-vous) met en relation sources et récepteurs ; en **SSM**, pas besoin de RP.
---

## Le problème : relier les abonnés à la source à travers plusieurs routeurs

IGMP fonctionne entre un poste et **son** routeur. Mais la source vidéo est au datacenter, et les abonnés sont dans dix bâtiments. Il faut que les routeurs entre les deux construisent un chemin — un arbre — sans boucle et sans envoyer le flux là où personne ne le veut.

> [!IMPORTANT] L’idée en une phrase
> Chaque routeur qui a des abonnés envoie un **Join** vers la source ; de proche en proche, ces Join tracent l’arbre que le flux suivra en sens inverse.

## Comment ça marche (PIM Sparse Mode, SSM)

```sequence
titre: Construction de l’arbre en SSM
Poste | R-étage | R-cœur | R-datacenter | Source
Poste -> R-étage : IGMPv3 : « groupe 232.1.1.1 depuis la source S »
R-étage -> R-cœur : PIM Join (S, G) vers la source
R-cœur -> R-datacenter : PIM Join (S, G)
Source -> R-datacenter : flux 232.1.1.1
R-datacenter -> R-cœur : flux
R-cœur -> R-étage : flux
R-étage -> Poste : flux
```

1. Le poste s’abonne avec IGMP.
2. Son routeur envoie un **Join** au voisin situé **en direction de la source** (selon la table de routage unicast).
3. Chaque routeur fait de même jusqu’à la source.
4. Le flux descend le long des Join. Chaque routeur sait sur quelles interfaces le recopier.
5. Quand plus personne n’est abonné, les routeurs envoient des **Prune** et l’arbre se défait.

## Le contrôle RPF

Pour éviter les boucles, un routeur n’accepte un paquet multicast que s’il arrive par **l’interface qu’il utiliserait pour joindre la source** en unicast. C’est le contrôle **RPF** (*Reverse Path Forwarding*). Un paquet arrivé « par le mauvais côté » est jeté.

## Les mots à connaître

- **PIM** — *Protocol Independent Multicast*, protocole de routage multicast entre routeurs.
- **Join / Prune** — Message PIM qui ajoute / retire une branche de l’arbre de distribution.
- **RPF** — *Reverse Path Forwarding*, vérification qu’un paquet multicast arrive par l’interface qui mène vers sa source.
- **RP** — *Rendezvous Point*, routeur qui met en relation sources et récepteurs en ASM.

## Teste-toi

**Un flux multicast arrive sur un routeur par l’interface Gi0/1, mais sa route vers la source passe par Gi0/2. Que fait le routeur ?**

<details><summary>Voir le corrigé</summary>

Il **jette** le flux : le contrôle **RPF** échoue. Le paquet n’arrive pas par l’interface qui mène vers la source. Il faut corriger le routage unicast (ou ajouter une route statique multicast) pour que le chemin vers la source passe par Gi0/1, ou faire arriver le flux par Gi0/2.

</details>

<!-- approfondir -->

## ASM : le point de rendez-vous

En ASM, les récepteurs demandent seulement le groupe (*, G). Le routeur ne sait pas où est la source : il envoie son Join vers le **RP**.

1. Les Join des récepteurs construisent un **arbre partagé** enraciné au RP.
2. Le premier routeur de la source **enregistre** la source auprès du RP (messages *Register*).
3. Le RP fait descendre le flux sur l’arbre partagé.
4. Ensuite, le routeur des récepteurs bascule en général sur l’**arbre de la source** (SPT), plus direct.

Le RP est défini statiquement, ou découvert dynamiquement (**BSR**, ou Auto-RP chez Cisco). On le rend redondant avec **Anycast RP** (plusieurs RP qui partagent la même adresse et se synchronisent avec MSDP).

## Configuration (Cisco IOS)

```cisco
ip multicast-routing
!
interface range GigabitEthernet0/0/0 - 1
 ip pim sparse-mode
interface Vlan30
 ip pim sparse-mode
!
! SSM : plage par défaut 232.0.0.0/8
ip pim ssm default
!
! ASM : RP statique pour les groupes internes
ip access-list standard GROUPES-ASM
 permit 239.0.0.0 0.255.255.255
ip pim rp-address 10.255.255.10 GROUPES-ASM
```

## Vérification

```cisco
R1# show ip pim neighbor
Neighbor          Interface                Uptime/Expires    Ver   DR
Address                                                            Prio/Mode
10.255.0.2        GigabitEthernet0/0/1     2d03h/00:01:34    v2    1 / S P G

R1# show ip mroute 232.1.1.1
(198.51.100.20, 232.1.1.1), 00:14:22/00:03:01, flags: sTI
  Incoming interface: GigabitEthernet0/0/1, RPF nbr 10.255.0.2
  Outgoing interface list:
    Vlan30, Forward/Sparse, 00:14:22/00:02:41

R1# show ip rpf 198.51.100.20
RPF information for ? (198.51.100.20)
  RPF interface: GigabitEthernet0/0/1
  RPF neighbor: ? (10.255.0.2)
  RPF route/mask: 198.51.100.0/24
  RPF type: unicast (ospf 1)
```

Lecture de `show ip mroute` : l’entrée (S, G) existe, le flux **entre** par Gi0/0/1 (vers la source) et **sort** vers le Vlan30 où se trouvent les abonnés. Une liste de sortie vide (`Null`) signifie qu’aucun abonné n’a été signalé sur ce routeur.

## Dépannage

| Symptôme | Piste |
|---|---|
| Pas de voisin PIM | PIM non activé sur l’interface, ACL bloquant le protocole 103 |
| Entrée (S, G) absente | la source n’émet pas, ou son TTL est trop petit |
| Entrée présente, liste de sortie vide | pas d’abonnement IGMP reçu sur ce routeur |
| Flux reçu puis jeté (compteur RPF failed) | le chemin unicast vers la source ne passe pas par l’interface d’arrivée |
| ASM : rien ne passe | RP non défini, incohérent entre routeurs, ou injoignable |

## Exercices

**1.** Pourquoi recommande-t-on SSM plutôt qu’ASM pour une diffusion vidéo interne dont la source est connue ?

<details><summary>Voir le corrigé</summary>

SSM supprime le **RP** et la découverte des sources : la configuration est plus simple, l’arbre est direct dès le début, et un appareil quelconque ne peut pas injecter un flux parasite dans le groupe (le récepteur ne reçoit que la source demandée). Il faut seulement que les récepteurs supportent IGMPv3.

</details>

**2.** `show ip mroute` montre un flux en entrée sur un routeur, mais le compteur « RPF failed » augmente et rien ne sort. Après vérification, la route vers la source a été modifiée la veille pour passer par un autre lien. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

Le flux continue d’arriver par l’**ancien** chemin, alors que la table unicast désigne désormais **un autre** lien vers la source : le contrôle RPF échoue et les paquets sont jetés. Il faut que le flux arrive par l’interface RPF (en général, les Join PIM se réorientent d’eux-mêmes ; sinon, vérifier PIM sur le nouveau lien) ou ajouter une route statique multicast (`ip mroute`) si le chemin multicast doit volontairement différer.

</details>
