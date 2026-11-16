---
titre: MLD
nom: Multicast Listener Discovery (IPv6)
idee: MLD est l’équivalent d’IGMP en IPv6 — les postes s’abonnent aux groupes multicast auprès de leur routeur ; il sert aussi au fonctionnement normal d’IPv6.
osi: "3 (ICMPv6)"
duree: [5, 10]
prerequis: [igmp, ipv6]
retenir:
  - "**MLDv1** ≈ IGMPv2, **MLDv2** ≈ IGMPv3 (choix des sources, SSM)."
  - MLD est transporté dans **ICMPv6** — bloquer ICMPv6 casse aussi le multicast IPv6.
  - IPv6 utilise le multicast en permanence (NDP) — **MLD Snooping** mal réglé peut gêner IPv6 lui-même.
---

## Le problème

IPv6 a remplacé le broadcast par le **multicast**, y compris pour son fonctionnement de base (découverte des voisins avec [NDP](ndp.md)). Il lui faut donc, comme IPv4, un protocole d’abonnement aux groupes.

> [!IMPORTANT] L’idée en une phrase
> MLD fait en IPv6 ce qu’IGMP fait en IPv4 : les postes annoncent à leur routeur les groupes multicast qu’ils veulent recevoir.

## Correspondances

| IPv4 | IPv6 |
|---|---|
| IGMPv2 | MLDv1 |
| IGMPv3 | MLDv2 |
| IGMP Snooping | MLD Snooping |
| 224.0.0.0/4 | ff00::/8 |

Une particularité : chaque machine IPv6 s’abonne automatiquement à ses groupes de **nœud sollicité** pour que NDP fonctionne. Les messages MLD circulent donc même sans aucune application multicast.

## Les mots à connaître

- **MLD** — *Multicast Listener Discovery*, protocole d’abonnement multicast en IPv6.
- **MLD Snooping** — Écoute des messages MLD par un switch pour limiter le multicast IPv6 aux ports abonnés.

## Teste-toi

**Pourquoi un pare-feu qui bloque tout ICMPv6 gêne-t-il le multicast IPv6 ?**

<details><summary>Voir le corrigé</summary>

Parce que les messages MLD sont des messages **ICMPv6** (types 130, 131, 132 et 143). Les bloquer empêche les abonnements, et peut aussi gêner la résolution de voisins.

</details>

<!-- approfondir -->

## Configuration et vérification (Cisco IOS)

```cisco
ipv6 multicast-routing
ipv6 mld snooping
!
interface Vlan30
 ipv6 mld version 2
!
R1# show ipv6 mld groups
MLD Connected Group Membership
Group Address                           Interface      Uptime    Expires
FF3E::8000:1                            Vlan30         00:12:40  00:03:51
FF02::1:FF00:25                         Vlan30         02:15:03  00:04:02
```

`FF3E::/32` correspond à la plage SSM en IPv6 ; `FF02::1:FF…` est un groupe de nœud sollicité créé par NDP.

## Exercice

**Après l’activation de MLD Snooping sur un switch qui ne voit aucun querier, certains postes IPv6 ne se résolvent plus entre eux. Quelle explication ?**

<details><summary>Voir le corrigé</summary>

Sans querier, les abonnements aux groupes de **nœud sollicité** peuvent expirer dans la table du switch, qui cesse alors de transmettre les sollicitations de voisin (NS) vers ces ports. Activer un querier MLD, ou vérifier que le switch traite correctement les groupes de lien local (beaucoup de plateformes les inondent toujours, justement pour éviter ce problème).

</details>
