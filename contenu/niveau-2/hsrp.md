---
titre: HSRP
nom: Hot Standby Router Protocol (Cisco)
idee: HSRP fait partager à deux routeurs une passerelle virtuelle — une adresse IP et une adresse MAC que les postes utilisent ; si le routeur actif tombe, l’autre reprend la même adresse en quelques secondes.
osi: "3"
duree: [8, 16]
prerequis: [passerelle, arp]
retenir:
  - Les postes utilisent une **adresse IP virtuelle** comme passerelle ; un routeur est **actif**, l’autre en **veille**.
  - La **priorité** (100 par défaut) choisit l’actif ; la **préemption** permet au routeur prioritaire de reprendre sa place.
  - Le **suivi d’interface** (tracking) baisse la priorité si le lien vers l’extérieur tombe.
  - HSRP est propriétaire Cisco ; l’équivalent standard est **VRRP**.
---

## Le problème : une seule passerelle, un point de panne

Tous les postes d’un VLAN ont **une seule** passerelle configurée : `10.10.0.1`. Si le routeur qui porte cette adresse tombe en panne, tout le VLAN perd l’accès aux autres réseaux, même s’il existe un second routeur parfaitement fonctionnel juste à côté. Changer la passerelle sur des centaines de postes n’est pas une solution.

> [!IMPORTANT] L’idée en une phrase
> Deux routeurs se partagent une **passerelle virtuelle**. Les postes utilisent son adresse sans savoir quel routeur répond. Si le routeur actif tombe, l’autre prend sa place, avec la même adresse IP et la même adresse MAC.

## Comment ça marche

```topologie
titre: Une passerelle virtuelle partagée par deux routeurs
R1 l3 0,0 "R1 — actif" "10.10.0.2, priorité 110"
R2 l3 2,0 "R2 — veille" "10.10.0.3, priorité 100"
V boite 1,0.6 "Passerelle virtuelle" "10.10.0.1"
SW switch 1,1.4 "Switch d’accès"
PC pc 1,2.4 "Postes" "passerelle 10.10.0.1"
R1 -- SW
R2 -- SW
R1 .. V
R2 .. V
SW -- PC
```

1. R1 et R2 ont chacun leur propre adresse (`.2` et `.3`) et partagent l’adresse **virtuelle** `.1`.
2. Ils s’échangent des messages **Hello** toutes les 3 secondes. Le routeur à la priorité la plus haute devient **actif** : c’est lui qui répond aux requêtes ARP pour `.1`, avec une **adresse MAC virtuelle**.
3. Les postes envoient leurs paquets à cette MAC virtuelle : c’est R1 qui les traite.
4. Si R2 n’entend plus R1 pendant 10 secondes, il devient actif, prend l’adresse IP et la MAC virtuelles, et envoie un **ARP gratuit** pour que les switches apprennent où se trouve désormais cette MAC.
5. Les postes ne voient rien : leur passerelle n’a pas changé.

## Les mots à connaître

- **Passerelle virtuelle** — Adresse IP de passerelle partagée par plusieurs routeurs.
- **Routeur actif / en veille** — Le routeur qui assure la passerelle / celui qui attend pour prendre le relais.
- **Priorité** — Valeur qui détermine quel routeur devient actif ; la plus haute gagne.
- **Préemption** — Possibilité pour le routeur le plus prioritaire de reprendre le rôle actif dès son retour.
- **Suivi (tracking)** — Surveillance d’une interface ou d’une sonde qui diminue la priorité en cas de problème.

## Teste-toi

**R1 (priorité 110) tombe, R2 (100) devient actif. R1 redémarre. Qui est actif ensuite ?**

<details><summary>Voir le corrigé</summary>

**Ça dépend de la préemption.** Sans `preempt` sur R1, R2 **reste** actif : HSRP ne change pas d’actif tant que tout fonctionne. Avec `preempt`, R1 reprend le rôle actif dès qu’il est prêt.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
! R1
interface Vlan10
 ip address 10.10.0.2 255.255.255.0
 standby version 2
 standby 10 ip 10.10.0.1
 standby 10 priority 110
 standby 10 preempt delay minimum 60
 standby 10 authentication md5 key-string Un-Secret
 standby 10 track 1 decrement 20
!
track 1 interface GigabitEthernet0/0/0 line-protocol
!
! R2
interface Vlan10
 ip address 10.10.0.3 255.255.255.0
 standby version 2
 standby 10 ip 10.10.0.1
 standby 10 preempt
 standby 10 authentication md5 key-string Un-Secret
```

- `preempt delay minimum 60` : après un redémarrage, R1 attend 60 s avant de reprendre la main, le temps que son routage soit complet. Sinon, il redeviendrait actif avant de savoir où envoyer le trafic.
- `track 1 decrement 20` : si l’uplink de R1 tombe, sa priorité passe de 110 à 90, sous celle de R2 (100) : R2 devient actif (s’il a `preempt`).

## Le suivi : l’oubli classique

Sans suivi, R1 reste actif même si **son lien vers le reste du réseau** est coupé : les Hello passent toujours sur le VLAN, R2 ne voit aucun problème. Les postes envoient leur trafic à R1, qui ne peut plus le faire sortir. Le suivi d’interface, ou mieux, le suivi d’une **sonde IP SLA** vers une destination lointaine, corrige ce défaut. Voir [IP SLA](ipsla.md).

## Versions, temporisateurs, MAC virtuelle

| | HSRPv1 | HSRPv2 |
|---|---|---|
| Numéros de groupe | 0 à 255 | 0 à 4095 (on peut reprendre le numéro de VLAN) |
| Adresse multicast | 224.0.0.2 | 224.0.0.102 |
| MAC virtuelle | `0000.0c07.acXX` | `0000.0c9f.fXXX` |
| IPv6 | non | oui |

Hello **3 s**, hold **10 s** par défaut. On peut descendre sous la seconde (`standby 10 timers msec 200 msec 750`), mais le couplage avec [BFD](bfd.md) est préférable pour une détection rapide.

## Vérification

```cisco
R1# show standby brief
                     P indicates configured to preempt.
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Vl10        10   110 P Active  local           10.10.0.3       10.10.0.1
```

Si les deux routeurs se déclarent **actifs** en même temps, ils ne s’entendent pas : VLAN non transporté entre eux, numéro de groupe différent, authentification différente, ou ACL qui bloque le multicast. Le journal affiche alors des messages de conflit d’adresse.

## Répartir la charge entre les deux routeurs

HSRP n’utilise qu’un routeur actif **par groupe**. Pour faire travailler les deux, on alterne par VLAN : R1 actif pour les VLAN pairs, R2 pour les VLAN impairs. Idéalement, on aligne ce choix sur la racine [STP](../niveau-1/stp.md) de chaque VLAN, pour que le chemin de niveau 2 et la passerelle soient sur le même switch.

## Exercices

**1.** R1 est actif (priorité 110, `track` de son uplink avec `decrement 5`). Son uplink tombe, mais R2 ne devient pas actif. Pourquoi ?

<details><summary>Voir le corrigé</summary>

La priorité de R1 passe à 110 − 5 = **105**, toujours au-dessus de R2 (100). Il faut un décrément suffisant (au moins 11), et `preempt` sur R2 pour qu’il prenne la main.

</details>

**2.** Après une bascule HSRP, certains postes perdent le réseau pendant une minute, puis tout revient. Quelle hypothèse ?

<details><summary>Voir le corrigé</summary>

Les **switches** n’ont pas mis à jour l’emplacement de la MAC virtuelle (ARP gratuit perdu, ou chemin STP qui change en même temps). Les trames continuent d’être envoyées vers l’ancien routeur jusqu’à l’expiration de l’entrée MAC. Vérifier que les deux routeurs sont bien reliés par le VLAN, et que la racine STP et le routeur actif sont alignés.

</details>
