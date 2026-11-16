---
titre: "Labo 3 — Redondance sans boucle"
actif: pratique
chapeau: Tu vas ajouter des liens de secours entre trois switches, voir le spanning tree bloquer un port, choisir toi-même la racine, puis doubler un lien avec LACP.
---

> [!IMPORTANT] Objectif
> Observer l’élection STP, contrôler le choix de la racine, mesurer la reprise après une panne, et agréger deux liens en un seul avec LACP.

**Durée** : 1 heure. **Fiches utiles** : [STP](../niveau-1/stp.md), [RSTP](../niveau-1/rstp.md), [LACP](../niveau-1/lacp.md).

## La topologie

```topologie
titre: Labo 3
D1 switch 0,0 "DIST1" "racine voulue"
D2 switch 2,0 "DIST2" "racine de secours"
A1 switch 1,1.3 "ACC1"
PC pc 1,2.4 "PC"
D1 == D2 "2 liens LACP"
D1 -- A1
D2 -- A1
A1 -- PC
```

## Étape 1 — Observer l’élection

Relie les trois switches en triangle (un seul lien entre DIST1 et DIST2 pour l’instant), sans rien configurer.

```cisco
ACC1# show spanning-tree vlan 1
  Root ID    Priority    32769
             Address     0001.4227.8a01
  ...
Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- -----
Gi0/1            Root FWD 4         128.25   P2p
Gi0/2            Altn BLK 4         128.26   P2p
```

Note quel switch est la racine. C’est celui qui a la **plus petite adresse MAC**, au hasard du matériel — souvent un mauvais choix, comme le switch d’accès.

## Étape 2 — Choisir la racine

```cisco
DIST1(config)# spanning-tree mode rapid-pvst
DIST1(config)# spanning-tree vlan 1-4094 priority 4096
DIST2(config)# spanning-tree mode rapid-pvst
DIST2(config)# spanning-tree vlan 1-4094 priority 8192
ACC1(config)#  spanning-tree mode rapid-pvst
```

Vérifie que DIST1 est racine et repère le port **bloqué** : il doit maintenant se trouver sur ACC1, vers DIST2.

## Étape 3 — Provoquer une panne

Lance un ping continu depuis le PC vers une adresse au-delà de DIST1 (`ping -t`), puis coupe le lien ACC1–DIST1. Compte les pings perdus. Remets le lien.

## Étape 4 — Protéger les ports d’accès

```cisco
ACC1(config)# interface Fa0/1
ACC1(config-if)# spanning-tree portfast
ACC1(config-if)# spanning-tree bpduguard enable
```

## Étape 5 — Agréger DIST1–DIST2

Ajoute un second câble entre DIST1 et DIST2, puis :

```cisco
DIST1(config)# interface range Gi0/1 - 2
DIST1(config-if-range)# channel-group 1 mode active
DIST1(config-if-range)# interface Port-channel1
DIST1(config-if)# switchport mode trunk
```

Même configuration sur DIST2.

```cisco
DIST1# show etherchannel summary
1      Po1(SU)         LACP      Gi0/1(P)    Gi0/2(P)
```

## Questions

**1.** Sans agrégat, pourquoi le second câble entre DIST1 et DIST2 n’apporterait-il pas de débit ?

**2.** Combien de pings as-tu perdus à l’étape 3 ? Qu’attendrais-tu avec l’ancien STP (802.1D) ?

**3.** Que fait BPDU Guard si quelqu’un branche un switch sur Fa0/1 ?

<details><summary>Voir le corrigé</summary>

**1.** Le spanning tree verrait une **boucle** et bloquerait l’un des deux câbles. Avec LACP, les deux liens forment **un seul lien logique** : STP ne voit plus de boucle, et le trafic se répartit sur les deux.

**2.** Avec RSTP, en général 0 à 2 pings perdus (une à quelques secondes). Avec 802.1D, la reprise prend **30 à 50 secondes**, soit une trentaine de pings perdus.

**3.** Le port reçoit des BPDU, alors qu’il ne devrait y avoir qu’un poste : il passe en **err-disabled** (coupé) pour protéger la topologie. Il faut une intervention (`shutdown` / `no shutdown`) ou une reprise automatique configurée.

</details>

**Suite** : [Labo 4 — Plusieurs sites routés](labo-4-routage.md).
