---
titre: DTP
nom: Dynamic Trunking Protocol (Cisco)
idee: DTP permet à deux ports Cisco de négocier tout seuls s’ils deviennent un trunk ; pratique en laboratoire, dangereux en production, où on le désactive.
osi: "2"
duree: [5, 10]
prerequis: [802-1q]
retenir:
  - DTP négocie automatiquement le mode **trunk** ou **accès** entre deux ports Cisco.
  - Un attaquant peut l’utiliser pour obtenir un trunk et **accéder à tous les VLAN**.
  - "Bonne pratique — **`switchport mode access`** sur les ports utilisateurs, **`switchport mode trunk`** + **`switchport nonegotiate`** sur les trunks."
---

## Le problème : trunk ou pas trunk ?

Quand on relie deux switches Cisco, il faut que leurs ports passent en trunk. DTP a été créé pour que cela se fasse **automatiquement**. Mais un port qui accepte de devenir trunk sur simple demande est aussi une porte d’entrée.

> [!IMPORTANT] L’idée en une phrase
> DTP fait négocier le mode trunk entre deux ports. En production, on fixe le mode à la main et on coupe la négociation.

## Les modes

| Mode du port | Comportement |
|---|---|
| `dynamic auto` | devient trunk **si l’autre côté le demande** (défaut sur de nombreux switches récents) |
| `dynamic desirable` | **demande** activement à devenir trunk |
| `trunk` | trunk forcé, continue d’envoyer des messages DTP |
| `access` | jamais trunk |
| `nonegotiate` | n’envoie plus de messages DTP |

Deux ports en `dynamic auto` restent… en accès : aucun ne fait la demande.

## Le risque

Un attaquant branche un ordinateur sur une prise murale dont le port est en `dynamic auto` ou `desirable`. Avec un outil, il envoie des messages DTP : le port devient trunk. L’attaquant reçoit alors le trafic de **tous les VLAN** autorisés, et peut en envoyer dans n’importe lequel. C’est l’attaque par **usurpation de switch**.

## Les mots à connaître

- **DTP** — *Dynamic Trunking Protocol*, protocole Cisco de négociation automatique du mode trunk.
- **Usurpation de switch** — Attaque où un poste se fait passer pour un switch pour obtenir un trunk.

## Teste-toi

**Un port utilisateur est en `dynamic auto`. Un employé y branche un PC normal. Le port devient-il trunk ?**

<details><summary>Voir le corrigé</summary>

**Non** : un PC normal n’envoie pas de messages DTP, donc aucune demande n’est faite et le port reste en accès. Le risque vient d’un équipement ou d’un logiciel qui **envoie** des messages DTP. C’est pourquoi on fixe quand même `switchport mode access`.

</details>

<!-- approfondir -->

## Configuration recommandée (Cisco IOS)

```cisco
! Ports utilisateurs
interface range GigabitEthernet1/0/1 - 46
 switchport mode access
 switchport nonegotiate
!
! Trunks entre switches
interface range GigabitEthernet1/0/47 - 48
 switchport mode trunk
 switchport nonegotiate
```

`switchport mode access` suffit à empêcher le port de devenir trunk ; `nonegotiate` supprime en plus l’envoi des messages DTP, inutiles.

## Vérifier l’état réel d’un port

```cisco
SW1# show interfaces GigabitEthernet1/0/12 switchport
Name: Gi1/0/12
Switchport: Enabled
Administrative Mode: dynamic auto
Operational Mode: trunk
Negotiation of Trunking: On
```

**Administrative Mode** est ce qui est configuré, **Operational Mode** ce qui se passe réellement. Ici, un port utilisateur configuré en `dynamic auto` est devenu **trunk** : quelque chose en face a négocié. À investiguer immédiatement (`show cdp neighbors`, `show lldp neighbors`, journal).

## Exercice

**Deux switches sont reliés, l’un en `dynamic desirable`, l’autre en `switchport mode access`. Que se passe-t-il ?**

<details><summary>Voir le corrigé</summary>

Le lien reste en **accès** : le port configuré en `access` refuse de devenir trunk. Seul le VLAN d’accès passe. Si le but était un trunk, il faut configurer `switchport mode trunk` des deux côtés (avec `nonegotiate`).

</details>
