---
titre: "Labo 1 — Mon premier réseau"
actif: pratique
chapeau: Deux ordinateurs, un switch, deux adresses. Tu vas les faire communiquer, puis observer ce qui se passe vraiment quand un ping part.
---

> [!IMPORTANT] Objectif
> Relier deux PC par un switch, leur donner une adresse IP, vérifier qu’ils se joignent, et comprendre le rôle d’ARP et de la table MAC.

**Durée** : 30 minutes. **Fiches utiles** : [Le réseau](../demarrer/reseau.md), [Les adresses](../demarrer/adresses.md), [Le switch](../niveau-1/switch.md), [ARP](../niveau-2/arp.md).

## La topologie

```topologie
titre: Labo 1
PC1 pc 0,0 "PC1" "192.168.10.11/24"
SW switch 1.5,0 "SW1"
PC2 pc 3,0 "PC2" "192.168.10.12/24"
PC1 -- SW "Fa0/1"
SW -- PC2 "Fa0/2"
```

## Étape 1 — Brancher

Dans Packet Tracer, place un switch 2960 et deux PC. Relie chaque PC au switch avec un câble droit (*Copper Straight-Through*). Attends que les voyants passent au vert : c’est le [spanning tree](../niveau-1/stp.md) qui vérifie qu’il n’y a pas de boucle (une trentaine de secondes).

## Étape 2 — Donner les adresses

Sur PC1 : *Desktop → IP Configuration* → adresse `192.168.10.11`, masque `255.255.255.0`. Sur PC2 : `192.168.10.12`, même masque. Pas besoin de passerelle : les deux PC sont dans le même réseau.

## Étape 3 — Tester

Sur PC1, ouvre *Command Prompt* :

```text
C:\> ping 192.168.10.12

Reply from 192.168.10.12: bytes=32 time<1ms TTL=128
Reply from 192.168.10.12: bytes=32 time<1ms TTL=128
```

> [!NOTE]
> Le premier ping échoue parfois (« Request timed out ») : pendant ce temps, PC1 apprenait l’adresse MAC de PC2 avec ARP.

## Étape 4 — Observer

Sur PC1 :

```text
C:\> arp -a
  Internet Address      Physical Address      Type
  192.168.10.12         0060.2f84.1a03        dynamic
```

Sur le switch (clique dessus → *CLI*) :

```cisco
Switch> enable
Switch# show mac address-table
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    0060.2f84.1a03    DYNAMIC     Fa0/2
   1    00d0.97a1.5b2c    DYNAMIC     Fa0/1
```

Passe ensuite en mode **Simulation** (en bas à droite), filtre sur ARP et ICMP, vide la table ARP de PC1 (`arp -d`) et relance un ping : tu vois la requête ARP partir vers tous les ports, puis la réponse revenir uniquement vers PC1.

## Questions

**1.** Pourquoi le switch connaît-il l’adresse MAC de PC1 sur Fa0/1 ?

**2.** Change le masque de PC2 en `255.255.255.128` et l’adresse en `192.168.10.200`. Le ping fonctionne-t-il encore ? Pourquoi ?

**3.** Que se passe-t-il si tu donnes la même adresse IP aux deux PC ?

<details><summary>Voir le corrigé</summary>

**1.** Le switch **apprend** l’adresse MAC source de chaque trame qu’il reçoit, et note le port d’arrivée. Dès que PC1 a envoyé une trame, son adresse a été associée à Fa0/1.

**2.** Non. Avec un masque /25, PC2 est dans le réseau `192.168.10.128/25`, et il considère que `192.168.10.11` est **hors de son réseau** : il voudrait passer par une passerelle, qu’il n’a pas. Les deux PC doivent être dans le même sous-réseau pour communiquer sans routeur. Voir [Le masque et les sous-réseaux](../niveau-2/subnet.md).

**3.** Un **conflit d’adresses** : les PC le détectent généralement (message d’erreur), et les échanges deviennent imprévisibles. Une adresse IP doit être unique dans un réseau.

</details>

## Pour aller plus loin

Ajoute un troisième PC et un deuxième switch relié au premier. Observe la table MAC du premier switch : sur quel port voit-il le PC du second switch ?

**Suite** : [Labo 2 — Des VLAN qui se parlent](labo-2-vlan.md).
