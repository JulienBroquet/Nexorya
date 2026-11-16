---
titre: BFD
nom: Bidirectional Forwarding Detection
idee: BFD fait échanger à deux routeurs des messages très fréquents et très légers ; si ces messages s’arrêtent, la panne est détectée en moins d’une seconde et signalée aux protocoles de routage.
osi: "3 (UDP 3784)"
duree: [6, 12]
prerequis: [ospf]
retenir:
  - BFD détecte une panne en **quelques centaines de millisecondes**, contre 40 s pour OSPF par défaut.
  - Il **ne route rien** — il prévient OSPF, BGP, HSRP ou les routes statiques, qui réagissent.
  - "Réglage typique — **300 ms × 3** (panne déclarée après 900 ms)."
---

## Le problème : une panne invisible pendant 40 secondes

Deux routeurs sont reliés **à travers** un équipement intermédiaire : un switch, un convertisseur fibre, le réseau d’un opérateur. Si le lien tombe au milieu, **les interfaces des routeurs restent actives** : elles ne voient pas la panne. OSPF attendra la fin de son délai (40 s par défaut sans Hello) pour réagir, BGP jusqu’à 180 s. Pendant tout ce temps, le trafic part dans le vide.

> [!IMPORTANT] L’idée en une phrase
> BFD est un « battement de cœur » ultra-rapide entre deux routeurs. S’il s’arrête, la panne est connue en moins d’une seconde, et les protocoles de routage basculent immédiatement.

## Comment ça marche

```sequence
titre: BFD détecte la panne, OSPF réagit
R1 | Opérateur | R2
R1 -> R2 : BFD toutes les 300 ms
R2 -> R1 : BFD toutes les 300 ms
note Opérateur : coupure au milieu : les interfaces de R1 et R2 restent « up »
R1 -x Opérateur : BFD perdus (1, 2, 3)
note R1 : 3 × 300 ms sans réponse : session BFD down, OSPF prévenu
note R1 : OSPF retire le voisin et bascule sur le chemin de secours
```

BFD est **léger** : il peut tourner très vite sans charger le routeur, souvent pris en charge directement par le matériel. Il est **générique** : un seul mécanisme sert à tous les protocoles.

## Les mots à connaître

- **BFD** — *Bidirectional Forwarding Detection*, protocole de détection rapide de panne entre deux équipements.
- **Multiplicateur** — Nombre de messages BFD manqués avant de déclarer la panne.
- **Client BFD** — Protocole qui s’abonne à BFD pour être prévenu d’une panne (OSPF, BGP, HSRP…).

## Teste-toi

**Pourquoi ne pas simplement régler les Hello OSPF toutes les 100 ms ?**

<details><summary>Voir le corrigé</summary>

Les Hello OSPF sont plus lourds et traités par le **processeur** ; à cadence très élevée sur de nombreuses interfaces, ils chargent le routeur et peuvent provoquer de fausses pannes. BFD est conçu pour être rapide et léger, souvent traité en matériel, et sert à tous les protocoles à la fois.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
interface GigabitEthernet0/0/1
 bfd interval 300 min_rx 300 multiplier 3
!
router ospf 1
 bfd all-interfaces
!
router bgp 64512
 neighbor 203.0.113.1 fall-over bfd
!
! Route statique surveillée par BFD
ip route static bfd GigabitEthernet0/0/1 10.255.0.2
ip route 10.50.0.0 255.255.0.0 GigabitEthernet0/0/1 10.255.0.2
```

```cisco
R1# show bfd neighbors details
IPv4 Sessions
NeighAddr       LD/RD     RH/RS     State     Int
10.255.0.2      1/4       Up        Up        Gi0/0/1
Session state is UP and using echo function with 300 ms interval.
Registered protocols: OSPF CEF
Rx Count: 128344, Tx Count: 128341
```

## Modes et réglages

- **Mode asynchrone** : chaque côté envoie ses paquets de contrôle ; le temps de détection = intervalle négocié × multiplicateur.
- **Mode écho** : un routeur envoie des paquets que le voisin **renvoie sans les traiter** (en matériel), ce qui teste réellement le chemin de transmission. On réduit alors la fréquence des paquets de contrôle.
- **BFD multihop** : entre des routeurs qui ne sont pas directement connectés (sessions BGP entre loopbacks).

> [!CAUTION]
> Des temporisateurs trop agressifs (50 ms × 3) sur des liens chargés ou des équipements dont BFD est traité par le processeur provoquent des **fausses pannes** et des oscillations de routage. Commence par 300 ms × 3, mesure, puis affine. Pense aussi à l’**amortissement** des oscillations (*dampening*).

## Exercice

**Un lien opérateur relie R1 et R2. Un convertisseur fibre tombe en panne au milieu ; les interfaces restent up. Avec OSPF par défaut puis avec BFD 300 ms × 3, combien de temps dure la coupure avant bascule ?**

<details><summary>Voir le corrigé</summary>

OSPF seul : jusqu’au **Dead interval, 40 s**, plus le temps de recalcul. Avec BFD : **900 ms** de détection, puis OSPF retire immédiatement le voisin et recalcule (quelques dizaines de millisecondes) : environ **une seconde** au total.

</details>
