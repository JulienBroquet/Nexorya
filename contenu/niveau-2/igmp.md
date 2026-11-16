---
titre: IGMP
nom: Internet Group Management Protocol
idee: IGMP permet à un poste de dire à son routeur local « je veux recevoir tel groupe multicast » ; les switches l’écoutent pour n’envoyer le flux qu’aux bons ports.
osi: "3"
duree: [6, 14]
prerequis: [multicast]
retenir:
  - Le poste envoie un **Report** pour rejoindre un groupe, un **Leave** pour le quitter (IGMPv2 et v3).
  - Le routeur **interroge** régulièrement le réseau (**Query**) pour savoir s’il reste des abonnés.
  - "**IGMPv3** permet de choisir la **source** (SSM)."
  - "**IGMP Snooping** sur les switches évite d’inonder le multicast dans tout le VLAN — il a besoin d’un **querier**."
---

## Le problème : savoir qui veut quoi

Le routeur d’un étage reçoit un flux vidéo multicast. Doit-il l’envoyer sur le VLAN de l’étage ? Seulement si quelqu’un, dans ce VLAN, le regarde. Il faut un moyen pour les postes de **s’abonner** et de **se désabonner**.

> [!IMPORTANT] L’idée en une phrase
> IGMP est le dialogue entre les postes et leur routeur local : « je veux ce groupe », « je n’en veux plus », « quelqu’un veut-il encore ce groupe ? ».

## Comment ça marche

```sequence
titre: Abonnement et désabonnement IGMP
Poste | Switch (IGMP Snooping) | Routeur
Poste -> Routeur : Membership Report : « je rejoins 239.1.1.1 »
note Switch (IGMP Snooping) : note : ce port veut 239.1.1.1
Routeur -> Poste : le flux 239.1.1.1 arrive, seulement sur ce port
Routeur -> Poste : General Query régulière : « qui veut encore quoi ? »
Poste --> Routeur : Report : « toujours 239.1.1.1 »
Poste -> Routeur : Leave : « je quitte 239.1.1.1 »
Routeur -> Poste : Query spécifique : « quelqu’un d’autre veut 239.1.1.1 ? »
note Routeur : pas de réponse : le flux est arrêté sur ce VLAN
```

## IGMP Snooping : le multicast ciblé dans le VLAN

Sans aide, un switch envoie le multicast **partout** dans le VLAN. Un flux vidéo de 8 Mb/s arrive alors sur chaque PC, chaque imprimante, chaque téléphone. Avec **IGMP Snooping**, le switch **écoute** les Report et les Leave qui le traversent, et n’envoie chaque groupe qu’aux ports abonnés.

## Les mots à connaître

- **IGMP** — Protocole par lequel un poste s’abonne à des groupes multicast auprès de son routeur local.
- **Report / Leave** — Message d’abonnement / de désabonnement à un groupe.
- **Query** — Interrogation régulière du routeur pour vérifier les abonnements.
- **IGMP Snooping** — Écoute des messages IGMP par un switch pour limiter le multicast aux ports abonnés.
- **Querier** — Équipement qui envoie les Query IGMP dans un VLAN.

## Teste-toi

**Dans un VLAN, un flux multicast de 20 Mb/s sature les ports Wi-Fi alors qu’un seul poste regarde la vidéo. Quelle fonction manque probablement sur le switch ?**

<details><summary>Voir le corrigé</summary>

**IGMP Snooping** (ou son fonctionnement correct). Sans lui, le switch inonde le flux sur tous les ports du VLAN, y compris ceux des bornes Wi-Fi, qui le diffusent sur les ondes.

</details>

<!-- approfondir -->

## Les versions

| Version | Apports |
|---|---|
| IGMPv1 | Report et Query ; pas de Leave : le routeur attend l’expiration (plusieurs minutes) |
| IGMPv2 | **Leave** et Query spécifique : arrêt rapide d’un flux ; élection du querier |
| IGMPv3 | listes de **sources** à inclure ou exclure : nécessaire pour **SSM** ; Report envoyés à 224.0.0.22 |

## Le querier : la cause n°1 des pannes de snooping

Les switches suppriment les abonnements qui ne sont pas renouvelés. Or les postes ne renouvellent leur Report **qu’en réponse à une Query**. Dans un VLAN **sans routeur multicast** (pas de PIM), personne n’envoie de Query : au bout de quelques minutes, les abonnements expirent et **le flux s’arrête** chez tout le monde. Symptôme typique : « la vidéo coupe au bout de 4 minutes ».

La solution : activer un **querier** sur un switch du VLAN.

```cisco
ip igmp snooping
ip igmp snooping querier
ip igmp snooping vlan 30 querier address 10.30.0.2
!
SW1# show ip igmp snooping querier
Vlan      IP Address     IGMP Version   Port
-------------------------------------------------------------
30        10.30.0.2      v2             Switch
SW1# show ip igmp snooping groups vlan 30
Vlan      Group                    Type        Version     Port List
-----------------------------------------------------------------------
30        239.1.1.1                igmp        v2          Gi1/0/12, Gi1/0/48
```

`Gi1/0/48` apparaît comme port vers le **mrouter** (routeur multicast ou querier) : les Report y sont toujours relayés.

## Côté routeur

```cisco
ip multicast-routing
interface Vlan30
 ip pim sparse-mode            ! active aussi IGMP sur l'interface
 ip igmp version 3
!
R1# show ip igmp groups
IGMP Connected Group Membership
Group Address    Interface   Uptime    Expires   Last Reporter
239.1.1.1        Vlan30      00:42:11  00:02:31  10.30.0.57
```

## Exercices

**1.** Dans un VLAN de laboratoire sans routeur, une application multicast fonctionne quelques minutes puis s’arrête. Le switch a IGMP Snooping activé. Explique et corrige.

<details><summary>Voir le corrigé</summary>

Aucun **querier** : les abonnements ne sont pas renouvelés et le switch les supprime à expiration. Activer `ip igmp snooping querier` sur un switch du VLAN (ou un routeur avec PIM sur ce VLAN).

</details>

**2.** Pourquoi un téléviseur sur IP qui utilise SSM (groupe 232.x.x.x) a-t-il besoin d’IGMPv3 ?

<details><summary>Voir le corrigé</summary>

En SSM, l’abonnement doit préciser **la source** en plus du groupe (« 232.1.1.1 depuis 198.51.100.20 »). Seul **IGMPv3** transporte cette liste de sources. Avec IGMPv2, le routeur ne saurait pas quelle source joindre.

</details>
