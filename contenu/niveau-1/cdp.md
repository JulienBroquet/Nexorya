---
titre: CDP
nom: Cisco Discovery Protocol
idee: CDP est l’équivalent Cisco de LLDP — chaque équipement Cisco annonce son nom, son modèle, son port et son adresse à ses voisins directs.
osi: "2"
duree: [5, 10]
prerequis: [lldp]
retenir:
  - CDP est **propriétaire Cisco** et **activé par défaut** sur les équipements Cisco.
  - "`show cdp neighbors` indique le voisin de chaque port ; `detail` donne son adresse IP et sa version logicielle."
  - CDP signale aussi des incohérences (VLAN natif, duplex) et configure les téléphones Cisco.
---

## Le problème

Le même que pour [LLDP](lldp.md) : savoir qui est branché en face de chaque port. Cisco a créé CDP avant que LLDP ne soit normalisé, et l’utilise toujours par défaut.

> [!IMPORTANT] L’idée en une phrase
> CDP fait le même travail que LLDP, mais entre équipements Cisco : chacun annonce son identité à ses voisins directs, toutes les 60 secondes.

## À l’usage

```cisco
SW1# show cdp neighbors
Device ID      Local Intrfce   Holdtme  Capability  Platform     Port ID
DIST1          Gig 1/0/48      152      R S I       C9500-24Y4C  Ten 1/0/3
SEP001122AABB  Gig 1/0/5       131      H P M       IP Phone 88  Port 1
```

La colonne **Platform** donne directement le modèle du voisin : C9500 pour un Catalyst 9500, « IP Phone 88xx » pour un téléphone.

| | CDP | LLDP |
|---|---|---|
| Norme | propriétaire Cisco | IEEE 802.1AB, toutes marques |
| Par défaut sur Cisco | activé | souvent désactivé |
| Fréquence | 60 s | 30 s |
| Usage | réseaux 100 % Cisco | réseaux multi-constructeurs |

## Les mots à connaître

- **CDP** — *Cisco Discovery Protocol*, protocole Cisco d’annonce aux voisins directs.
- **Holdtime** — Durée pendant laquelle une annonce reste valide sans être renouvelée.

## Teste-toi

**Un switch Cisco est relié à un switch d’une autre marque. Que verra-t-on avec `show cdp neighbors` ?**

<details><summary>Voir le corrigé</summary>

Probablement **rien** pour ce port, car l’autre marque ne parle pas CDP. Il faut activer **LLDP** des deux côtés et utiliser `show lldp neighbors`.

</details>

<!-- approfondir -->

## Ce que CDP apporte en plus

- **Détection d’incohérences** : CDP compare des paramètres avec le voisin et journalise les écarts.

```text
%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on
GigabitEthernet1/0/48 (999), with DIST1 TenGigabitEthernet1/0/3 (1).
%CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on GigabitEthernet1/0/7 (not full duplex)
```

Ces messages sont précieux : ils désignent directement un trunk au VLAN natif incohérent ([802.1Q](802-1q.md)) ou un désaccord de duplex ([PHY](phy.md)).

- **Téléphones Cisco** : CDP indique au téléphone le VLAN voix à utiliser et négocie la puissance PoE.

## Commandes utiles (Cisco IOS)

```cisco
SW1# show cdp neighbors GigabitEthernet1/0/48 detail
Device ID: DIST1
Entry address(es):
  IP address: 10.99.0.2
Platform: cisco C9500-24Y4C,  Capabilities: Router Switch IGMP
Interface: GigabitEthernet1/0/48,  Port ID (outgoing port): TenGigabitEthernet1/0/3
Version :
Cisco IOS Software [Cupertino], Catalyst L3 Switch Software, Version 17.9.4
Native VLAN: 1
Duplex: full
```

```cisco
! Désactiver CDP sur un port exposé, ou globalement
interface GigabitEthernet0/0/0
 no cdp enable
!
no cdp run
```

> [!WARNING]
> CDP divulgue le modèle, la version logicielle et l’adresse de gestion. Des vulnérabilités ont aussi visé son traitement. Désactive-le sur les ports vers Internet, les opérateurs et les zones non maîtrisées (salles de réunion, invités), en gardant à l’esprit que les téléphones Cisco en ont besoin sur leurs ports.

## Exercice

**Le journal affiche `NATIVE_VLAN_MISMATCH` sur l’uplink Gi1/0/48 (999) avec DIST1 Te1/0/3 (1). Quelle correction, et sur quel équipement ?**

<details><summary>Voir le corrigé</summary>

Aligner le **VLAN natif** aux deux extrémités du trunk. Si la norme de l’entreprise est d’utiliser le VLAN 999 comme natif, configurer `switchport trunk native vlan 999` sur Te1/0/3 de **DIST1**. Faire la modification en fenêtre de maintenance : pendant quelques secondes, les deux côtés seront incohérents.

</details>
