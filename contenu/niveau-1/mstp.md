---
titre: MSTP
nom: Multiple Spanning Tree Protocol (IEEE 802.1s)
idee: MSTP regroupe de nombreux VLAN dans quelques arbres seulement ; on garde la répartition de charge sans calculer un arbre par VLAN.
osi: "2"
duree: [6, 14]
prerequis: [rstp]
retenir:
  - Rapid PVST+ calcule **un arbre par VLAN** ; MSTP calcule **un arbre par instance**, et chaque instance regroupe plusieurs VLAN.
  - "Une **région** MSTP exige le **même nom**, le **même numéro de révision** et la **même table VLAN → instance** sur tous les switches."
  - On répartit la charge en donnant une racine différente à chaque instance.
---

## Le problème : 200 VLAN, 200 arbres

Avec Rapid PVST+, chaque VLAN a son propre arbre Spanning Tree. Avec 200 VLAN, chaque switch calcule 200 arbres et envoie 200 séries de BPDU toutes les deux secondes sur chaque trunk. Or, dans un campus, il n’existe souvent que **deux chemins** possibles. Calculer 200 fois la même chose gaspille du processeur.

> [!IMPORTANT] L’idée en une phrase
> MSTP range les VLAN dans quelques **instances**, et calcule un arbre par instance. Deux instances suffisent souvent : une qui passe par le switch de distribution A, l’autre par B.

## Comment ça marche

1. L’administrateur crée des **instances** : instance 1 et instance 2.
2. Il y range les VLAN : VLAN 10 à 99 → instance 1, VLAN 100 à 199 → instance 2.
3. Il donne la racine de l’instance 1 au switch DIST-A, et celle de l’instance 2 à DIST-B.
4. Résultat : la moitié des VLAN passe par A, l’autre par B. Les deux uplinks travaillent, chacun sert de secours à l’autre.

```topologie
titre: Deux instances, deux racines, deux uplinks utilisés
DA l3 0,0 "DIST-A" "racine instance 1"
DB l3 2,0 "DIST-B" "racine instance 2"
ACC switch 1,1 "Switch d’accès"
DA -- DB
ACC ++ DA "VLAN 10-99"
ACC ++ DB "VLAN 100-199"
```

## Les mots à connaître

- **MSTP** — *Multiple Spanning Tree Protocol*, version de STP qui calcule un arbre par groupe de VLAN.
- **Instance MST** — Groupe de VLAN qui partagent le même arbre Spanning Tree.
- **Région MST** — Ensemble de switches qui partagent exactement la même configuration MST.

## Teste-toi

**Deux switches MSTP ont le même nom de région, mais le VLAN 50 est rangé dans l’instance 1 sur l’un et dans l’instance 2 sur l’autre. Sont-ils dans la même région ?**

<details><summary>Voir le corrigé</summary>

**Non.** La table VLAN → instance doit être **strictement identique**. Une seule différence suffit pour que les switches se considèrent dans des régions différentes : la topologie devient sous-optimale et difficile à comprendre.

</details>

<!-- approfondir -->

## Instances, IST et régions

- L’**instance 0** (IST, *Internal Spanning Tree*) existe toujours. Elle contient tous les VLAN non affectés, et c’est elle qui dialogue avec l’extérieur de la région.
- Les instances 1 à 4094 (le nombre maximal dépend de la plateforme, souvent 64) sont les **MSTI**.
- Toutes les informations MST d’une région voyagent dans **une seule BPDU** par port, ce qui allège considérablement le plan de contrôle.
- Vue de l’extérieur, une région se comporte comme **un seul gros switch** : c’est le CST (*Common Spanning Tree*) qui relie les régions entre elles et aux switches RSTP/STP.

La région est identifiée par un **résumé** calculé sur le nom, la révision et la table VLAN → instance. Deux switches dont le résumé diffère sont dans deux régions.

## Configuration (Cisco IOS)

```cisco
spanning-tree mode mst
!
spanning-tree mst configuration
 name CAMPUS-NORD
 revision 3
 instance 1 vlan 10-99
 instance 2 vlan 100-199
!
! Sur DIST-A
spanning-tree mst 0-1 priority 4096
spanning-tree mst 2 priority 8192
! Sur DIST-B
spanning-tree mst 0-1 priority 8192
spanning-tree mst 2 priority 4096
```

> [!CAUTION]
> Modifier la configuration MST (ajouter un VLAN à une instance) change le résumé de région : le switch sort temporairement de la région jusqu’à ce que tous les switches soient modifiés. Prépare la table VLAN → instance **à l’avance**, y compris pour les VLAN futurs, et applique les changements en fenêtre de maintenance, partout à la fois (automatisation recommandée).

## Vérification

```cisco
DIST-A# show spanning-tree mst configuration
Name      [CAMPUS-NORD]
Revision  3     Instances configured 3
Instance  Vlans mapped
--------  ---------------------------------------------------------------------
0         1-9,200-4094
1         10-99
2         100-199

ACC1# show spanning-tree mst 2
##### MST2    vlans mapped:   100-199
Bridge        address 7c21.0e4a.1b00  priority 32770 (32768 sysid 2)
Root          address 00aa.0b00.0002  priority 4098  (4096 sysid 2)
              port    Gi1/0/48        cost 20000     rem hops 19
Gi1/0/47         Altn BLK 20000     128.47   P2p
Gi1/0/48         Root FWD 20000     128.48   P2p
```

MST utilise les **coûts longs** (20 000 pour 1 Gb/s). Un port qui apparaît comme `Bound(RSTP)` ou `Bound(PVST)` marque la **frontière** avec un switch hors région.

## Exercices

**1.** Un switch est ajouté avec `name CAMPUS-NORD`, `revision 3`, mais sans les lignes `instance`. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

Tous ses VLAN sont dans l’instance 0 : sa table diffère des autres, il forme **sa propre région**. Ses ports vers les autres switches deviennent des ports de frontière, et la répartition de charge par instance ne s’applique plus à travers lui.

</details>

**2.** Pourquoi recommande-t-on d’affecter dès le départ à une instance des plages de VLAN qui n’existent pas encore ?

<details><summary>Voir le corrigé</summary>

Pour ne **jamais modifier** la configuration MST plus tard. Créer un VLAN ne change pas le résumé de région ; modifier la table VLAN → instance, si. Préparer des plages (par exemple 10-99 et 100-199) évite des perturbations à chaque nouveau VLAN.

</details>
