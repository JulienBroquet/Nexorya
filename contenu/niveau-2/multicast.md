---
titre: Multicast
nom: Envoyer à un groupe de récepteurs
idee: Le multicast envoie un flux une seule fois vers une adresse de groupe ; le réseau le recopie seulement là où se trouvent des récepteurs intéressés.
osi: "3"
duree: [8, 16]
prerequis: [ipv4]
retenir:
  - "Trois modes d’envoi — **unicast** (un vers un), **broadcast** (un vers tous), **multicast** (un vers les abonnés)."
  - "Adresses multicast IPv4 — **224.0.0.0/4** ; en IPv6, **ff00::/8**."
  - Les récepteurs s’abonnent avec **IGMP** (IPv4) ou **MLD** (IPv6) ; les routeurs construisent l’arbre de distribution avec **PIM**.
  - Sans IGMP Snooping, un switch inonde le multicast sur tous les ports du VLAN.
---

## Le problème : 300 écrans, un même flux

Le directeur fait une intervention vidéo diffusée en direct dans 300 bureaux. En **unicast**, le serveur devrait envoyer 300 copies identiques du flux : à 5 Mb/s chacune, cela fait 1,5 Gb/s qui sortent du serveur et traversent les mêmes liens. En **broadcast**, le flux arriverait aussi chez les milliers de machines qui ne le regardent pas, et ne traverserait pas les routeurs.

> [!IMPORTANT] L’idée en une phrase
> En multicast, la source envoie **une seule copie** vers une adresse de groupe ; les routeurs et les switches la **dupliquent** seulement aux embranchements qui mènent à des récepteurs abonnés.

## Trois façons d’envoyer

| Mode | Destinataire | Exemple |
|---|---|---|
| **Unicast** | une seule machine | consulter un site Web |
| **Broadcast** | toutes les machines du réseau local | requête ARP |
| **Multicast** | les machines **abonnées** à un groupe, où qu’elles soient | télévision sur IP, diffusion vidéo interne, cotations boursières, protocoles de routage |

```topologie
titre: Une seule copie par lien, dupliquée aux embranchements
S serveur 2,0 "Source vidéo" "groupe 239.1.1.1"
R1 routeur 2,1 "R1"
R2 routeur 1,2 "R2"
R3 routeur 3,2 "R3"
A pc 0.5,3 "Abonné"
B pc 1.5,3 "Abonné"
C pc 3,3 "Pas abonné"
S ++ R1 "1 copie"
R1 ++ R2 "1 copie"
R1 -- R3 "rien"
R2 ++ A
R2 ++ B
R3 -- C
```

## Comment ça marche, en trois briques

1. **Les adresses de groupe.** Un groupe est une adresse IP spéciale, dans la plage `224.0.0.0` à `239.255.255.255`. La source envoie ses paquets vers cette adresse.
2. **L’abonnement.** Un poste qui veut recevoir le flux le signale à son routeur avec [IGMP](igmp.md) (ou [MLD](mld.md) en IPv6) : « je rejoins le groupe 239.1.1.1 ».
3. **La distribution.** Les routeurs s’échangent ces abonnements avec [PIM](pim.md) et construisent un **arbre** de la source vers les abonnés.

## Les mots à connaître

- **Multicast** — Envoi d’un même flux vers un groupe de récepteurs abonnés.
- **Groupe multicast** — Adresse IP de classe D (224.0.0.0/4) qui désigne les récepteurs d’un flux.
- **Abonnement** — Signalement par un poste qu’il veut recevoir un groupe ; on dit aussi « rejoindre le groupe ».
- **Arbre de distribution** — Chemin construit par les routeurs pour acheminer un flux de la source vers les abonnés.

## Teste-toi

**Pourquoi le multicast économise-t-il de la bande passante sur le lien qui sort du serveur ?**

<details><summary>Voir le corrigé</summary>

Parce que le serveur envoie **une seule copie** du flux, quel que soit le nombre de récepteurs. La duplication est faite plus loin, par les routeurs et les switches, aux embranchements de l’arbre.

</details>

<!-- approfondir -->

## Les plages d’adresses

| Plage | Usage |
|---|---|
| 224.0.0.0/24 | **lien local**, jamais routé : 224.0.0.5/6 OSPF, 224.0.0.9 RIP, 224.0.0.13 PIM, 224.0.0.22 IGMPv3, 224.0.0.102 HSRPv2 |
| 232.0.0.0/8 | **SSM** (*Source-Specific Multicast*) |
| 239.0.0.0/8 | **portée administrative** : l’équivalent des adresses privées, pour les flux internes |
| reste de 224.0.0.0/4 | groupes globaux attribués |

## De l’adresse IP à l’adresse MAC

Une adresse IP multicast correspond à une adresse MAC multicast : préfixe `01:00:5e`, puis les **23 bits de poids faible** de l’adresse IP.

```text
239.1.1.1 → 01:00:5e:01:01:01
224.1.1.1 → 01:00:5e:01:01:01   (même MAC !)
```

Comme 5 bits de l’adresse IP sont perdus, **32 groupes IP** partagent chaque adresse MAC. Une carte réseau peut donc recevoir des flux qu’elle n’a pas demandés ; c’est la pile IP qui les écarte. Choisir ses groupes en évitant les collisions avec 224.0.0.x (souvent traités spécialement par les switches) est une bonne pratique.

En IPv6 : `33:33` + les 32 derniers bits de l’adresse.

## ASM et SSM

- **ASM** (*Any-Source Multicast*) : le récepteur rejoint un groupe, sans préciser la source. Le réseau doit découvrir les sources : on a besoin d’un **point de rendez-vous** (RP). Plus complexe.
- **SSM** (*Source-Specific Multicast*) : le récepteur demande « le groupe G **de la source S** ». Pas de RP, arbre direct, plus simple et plus sûr. Il exige IGMPv3 (ou MLDv2) côté récepteurs. C’est le choix recommandé pour la télévision sur IP et les diffusions internes dont on connaît la source.

## Le multicast dans un VLAN : IGMP Snooping

Un switch traite par défaut une trame multicast comme un broadcast : il l’**inonde** sur tous les ports du VLAN. Avec **IGMP Snooping**, il écoute les abonnements IGMP qui passent et n’envoie chaque groupe qu’aux ports concernés. C’est indispensable dès qu’on transporte de la vidéo. Voir [IGMP](igmp.md).

## Diagnostic : les questions dans l’ordre

1. La **source** émet-elle (capture, compteurs) ? Avec quel **TTL** (un TTL de 1 ne dépassera pas le premier routeur) ?
2. Le **récepteur** s’abonne-t-il (IGMP Report visible) ?
3. Le **routeur du récepteur** a-t-il l’abonnement (`show ip igmp groups`) ?
4. Les **routeurs** ont-ils construit l’arbre (`show ip mroute`) ? Le contrôle **RPF** passe-t-il ?
5. Les **switches** transmettent-ils au bon port (`show ip igmp snooping groups`) ?

## Exercice

**Une source émet vers 239.10.10.10 avec un TTL de 1. Les récepteurs du même VLAN reçoivent le flux, ceux d’un autre site non. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

Le premier routeur décrémente le TTL à 0 et **jette** les paquets : le flux ne quitte jamais le VLAN de la source. Il faut que l’application émette avec un TTL suffisant (par exemple 16 ou 32), en plus du routage multicast (PIM) entre les sites.

</details>
