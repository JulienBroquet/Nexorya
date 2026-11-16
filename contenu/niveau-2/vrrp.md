---
titre: VRRP
nom: Virtual Router Redundancy Protocol (RFC 9568)
idee: VRRP est la version standard de la passerelle virtuelle partagée — même principe que HSRP, mais compatible avec toutes les marques d’équipements.
osi: "3 (protocole IP 112)"
duree: [6, 12]
prerequis: [hsrp]
retenir:
  - "Un routeur **master** porte la passerelle virtuelle ; les **backup** attendent."
  - La **préemption est active par défaut** (contrairement à HSRP).
  - L’adresse virtuelle peut être **l’adresse réelle** d’un des routeurs (il est alors le propriétaire, priorité 255).
  - "MAC virtuelle `0000.5e00.01XX` ; messages toutes les **1 s** par défaut."
---

## Le problème

Le même qu’avec [HSRP](hsrp.md) : rendre la passerelle d’un VLAN tolérante aux pannes. Mais quand les deux routeurs sont de **marques différentes**, ou dans un réseau non Cisco, il faut un protocole standard.

> [!IMPORTANT] L’idée en une phrase
> VRRP fait partager une passerelle virtuelle à plusieurs routeurs de n’importe quelle marque : un **master** répond, les **backup** prennent le relais en cas de panne.

## HSRP et VRRP côte à côte

| | HSRP | VRRP |
|---|---|---|
| Norme | Cisco | standard IETF |
| Rôles | actif / veille | master / backup |
| Préemption par défaut | non | **oui** |
| Annonces | 3 s (hold 10 s) | 1 s (≈ 3,6 s pour basculer) |
| Adresse virtuelle = adresse réelle d’un routeur | non | possible (routeur « propriétaire ») |
| MAC virtuelle | `0000.0c07.acXX` (v1) | `0000.5e00.01XX` |

## Les mots à connaître

- **VRRP** — *Virtual Router Redundancy Protocol*, protocole standard de passerelle virtuelle redondante.
- **Master / backup** — Routeur qui porte la passerelle virtuelle / routeurs prêts à le remplacer.
- **Propriétaire** — Routeur dont l’adresse réelle est l’adresse virtuelle ; il a toujours la priorité 255.

## Teste-toi

**Une entreprise relie ses VLAN à deux switches de cœur de marques différentes. Peut-elle utiliser HSRP ?**

<details><summary>Voir le corrigé</summary>

**Non**, HSRP est propriétaire Cisco. Elle utilisera **VRRP**, standard, supporté par toutes les marques.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS-XE, VRRPv3)

```cisco
fhrp version vrrp v3
!
interface Vlan10
 ip address 10.10.0.2 255.255.255.0
 vrrp 10 address-family ipv4
  address 10.10.0.1 primary
  priority 110
  track 1 decrement 20
  preempt delay minimum 60
```

```cisco
R1# show vrrp brief
  Interface          Grp  A-F Pri  Time Own Pre State   Master addr/Group addr
  Vl10                10 IPv4 110     0  N   Y  MASTER  10.10.0.2(local) 10.10.0.1
```

VRRPv3 (RFC 5798, révisée par la RFC 9568) gère IPv4 et IPv6 et accepte des intervalles en centièmes de seconde. L’authentification a été retirée de la norme : elle n’apportait pas de vraie sécurité. On protège plutôt le VLAN lui-même.

## Le temps de bascule

```text
temps de bascule (Master Down Interval) = 3 × intervalle d’annonce + temps de décalage
temps de décalage (skew)               = ((256 − priorité) × intervalle) / 256

Intervalle 1 s, priorité du backup 100 : 3 + 0,61 ≈ 3,6 s
```

Le décalage fait basculer d’abord le backup de **plus haute** priorité, ce qui évite que plusieurs backups prennent la main en même temps.

## Exercice

**Pourquoi l’usage d’une adresse virtuelle égale à l’adresse réelle d’un routeur (propriétaire) est-il pratique, mais à manier avec prudence ?**

<details><summary>Voir le corrigé</summary>

Pratique : pas besoin d’une adresse supplémentaire, et le propriétaire (priorité 255) est toujours master quand il fonctionne. Prudence : il **reprend immédiatement** la main à son retour, même si son routage n’est pas encore prêt ; et sa priorité 255 ne peut pas être abaissée par le suivi. Dans un design avec suivi d’uplink, on préfère une adresse virtuelle distincte.

</details>
