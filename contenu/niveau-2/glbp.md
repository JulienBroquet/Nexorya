---
titre: GLBP
nom: Gateway Load Balancing Protocol (Cisco)
idee: GLBP partage une passerelle virtuelle entre plusieurs routeurs qui travaillent tous en même temps, en donnant à chaque poste l’adresse MAC de l’un d’eux.
osi: "3"
duree: [5, 10]
prerequis: [hsrp]
retenir:
  - Une seule IP virtuelle, mais **plusieurs MAC virtuelles** — une par routeur.
  - L’**AVG** répond aux requêtes ARP et répartit les postes ; chaque **AVF** traite le trafic de ses postes.
  - Propriétaire Cisco, peu utilisé aujourd’hui — on préfère alterner HSRP/VRRP par VLAN ou utiliser des switches empilés.
---

## Le problème

Avec HSRP ou VRRP, un seul routeur travaille par VLAN ; l’autre attend. Pour faire travailler les deux sur un **même** VLAN, Cisco a créé GLBP.

> [!IMPORTANT] L’idée en une phrase
> Quand un poste demande en ARP l’adresse MAC de la passerelle, GLBP lui répond avec la MAC de l’un des routeurs, à tour de rôle : les postes se répartissent entre les routeurs.

## Comment ça marche

1. Un routeur est élu **AVG** (*Active Virtual Gateway*) : c’est lui qui répond aux requêtes ARP pour l’adresse virtuelle.
2. Chaque routeur du groupe est un **AVF** (*Active Virtual Forwarder*) avec sa propre MAC virtuelle.
3. L’AVG répond à chaque poste avec la MAC d’un AVF différent (par défaut, à tour de rôle).
4. Si un AVF tombe, un autre reprend sa MAC virtuelle : ses postes ne voient rien.

## Les mots à connaître

- **GLBP** — Protocole Cisco de passerelle virtuelle avec partage de charge.
- **AVG** — Routeur qui répond aux requêtes ARP et distribue les MAC virtuelles.
- **AVF** — Routeur qui achemine le trafic des postes qui ont reçu sa MAC virtuelle.

## Teste-toi

**Pourquoi GLBP répartit-il les postes, et non les paquets ?**

<details><summary>Voir le corrigé</summary>

Parce que la répartition se fait au moment de la **réponse ARP** : chaque poste garde la MAC qu’il a reçue dans son cache, et envoie tout son trafic à ce routeur jusqu’à l’expiration du cache. La charge dépend donc du nombre de postes et de leur activité.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
interface Vlan10
 ip address 10.10.0.2 255.255.255.0
 glbp 10 ip 10.10.0.1
 glbp 10 priority 110
 glbp 10 preempt
 glbp 10 load-balancing round-robin
!
R1# show glbp brief
Interface   Grp  Fwd Pri State    Address         Active router   Standby router
Vl10        10   -   110 Active   10.10.0.1       local           10.10.0.3
Vl10        10   1   -   Active   0007.b400.0a01  local           -
Vl10        10   2   -   Listen   0007.b400.0a02  10.10.0.3       -
```

Méthodes de répartition : `round-robin` (à tour de rôle), `weighted` (selon un poids par routeur), `host-dependent` (un poste reçoit toujours la même MAC).

## Pourquoi GLBP est rare aujourd’hui

- Il est propriétaire, et n’est pas disponible sur toutes les plateformes récentes.
- Les architectures actuelles utilisent des switches de cœur **empilés** ou en **vPC/MLAG**, qui présentent une seule passerelle active des deux côtés à la fois.
- Alterner les VLAN entre deux routeurs HSRP/VRRP donne une répartition plus prévisible.

## Exercice

**Dans un VLAN, 90 % du trafic vient de trois serveurs très actifs, qui ont tous reçu la MAC de R1. Que propose GLBP pour corriger ce déséquilibre ?**

<details><summary>Voir le corrigé</summary>

La répartition `weighted` ne corrige pas un déséquilibre déjà installé dans les caches ARP. On peut vider le cache ARP de ces serveurs pour qu’ils redemandent, ou utiliser `host-dependent` combiné à un choix de priorités. Cet exemple montre la limite de GLBP : il répartit des **postes**, pas des volumes de trafic.

</details>
