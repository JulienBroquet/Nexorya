---
titre: SPAN
nom: Port miroir
idee: Le SPAN copie le trafic d’un ou plusieurs ports d’un switch vers un port d’analyse, où l’on branche un ordinateur avec Wireshark ou une sonde de sécurité.
osi: "2"
duree: [6, 12]
prerequis: [switch]
retenir:
  - Un switch n’envoie à un port que le trafic qui lui est destiné — pour **observer** un autre port, il faut un **miroir**.
  - "Source — un ou plusieurs ports ou VLAN, en entrée, en sortie ou les deux ; destination — le port de l’analyseur."
  - "Si la source dépasse la capacité du port destination, des paquets sont **perdus** dans la capture."
  - Pour une observation permanente et fiable, on préfère un **TAP** réseau.
---

## Le problème : voir ce qui passe

Pour comprendre une panne applicative, il faut souvent **voir les paquets** échangés entre un poste et un serveur. Mais si l’on branche un PC d’analyse sur un port libre du switch, il ne voit rien : le switch ne lui envoie que ce qui lui est destiné (et les broadcasts).

> [!IMPORTANT] L’idée en une phrase
> Le SPAN demande au switch de **recopier** le trafic d’un port choisi vers le port où est branché l’analyseur.

## Comment ça marche

```topologie
titre: Observer le trafic d’un serveur
SRV serveur 0,0 "Serveur" "Gi1/0/10 (source)"
SW switch 1.5,0 "Switch"
NET nuage 3,0 "Reste du réseau"
PC portable 1.5,1.2 "PC d’analyse" "Gi1/0/48 (destination)"
SRV -- SW
SW -- NET
SW .. PC "copie"
```

```cisco
monitor session 1 source interface GigabitEthernet1/0/10 both
monitor session 1 destination interface GigabitEthernet1/0/48
```

Le PC d’analyse, avec Wireshark, voit alors tout ce que le serveur envoie et reçoit.

## Les mots à connaître

- **SPAN** — *Switched Port Analyzer*, recopie du trafic d’un port vers un port d’analyse ; on dit aussi port miroir.
- **TAP** — Boîtier passif inséré sur un lien, qui en fournit une copie complète.
- **Wireshark** — Logiciel de capture et d’analyse de paquets.

## Teste-toi

**On copie un port à 10 Gb/s, chargé à 6 Gb/s dans chaque sens, vers un port destination à 10 Gb/s. La capture est-elle complète ?**

<details><summary>Voir le corrigé</summary>

**Non.** La source « both » produit 6 + 6 = 12 Gb/s de trafic à recopier, plus que les 10 Gb/s du port destination : le switch **perd** une partie des copies. La capture semblera montrer des pertes ou des retransmissions qui n’existent pas dans la réalité.

</details>

<!-- approfondir -->

## Variantes et précautions

| Variante | Principe |
|---|---|
| SPAN local | source et destination sur le même switch |
| **RSPAN** | la copie est transportée dans un VLAN dédié vers un autre switch |
| **ERSPAN** | la copie est encapsulée dans GRE et routée vers n’importe quelle destination IP ; voir [ERSPAN](erspan.md) |
| SPAN de VLAN | copie de tout le trafic d’un VLAN (attention au volume) |

Précautions :

- Le port destination ne sert **qu’à** recevoir la copie : il ne transmet plus de trafic normal.
- Le SPAN est **moins prioritaire** que le trafic réel : en cas de charge, ce sont les copies qui sont sacrifiées.
- Certaines trames (en erreur, trop courtes) ne sont pas recopiées : pour diagnostiquer un problème physique, il faut un TAP.
- Retirer la session après usage : `no monitor session 1`.

## SPAN ou TAP ?

| | SPAN | TAP |
|---|---|---|
| Coût | gratuit (fonction du switch) | boîtier à acheter et insérer |
| Fidélité | perte possible en charge, trames en erreur absentes | copie complète, y compris les erreurs |
| Mise en place | par configuration, à distance | coupure du lien pour l’insérer |
| Usage | dépannage ponctuel | sondes de sécurité permanentes, analyse exigeante |

## Vérifier

```cisco
SW1# show monitor session 1
Session 1
---------
Type                     : Local Session
Source Ports             :
    Both                 : Gi1/0/10
Destination Ports        : Gi1/0/48
    Encapsulation        : Native
          Ingress        : Disabled
```

## Exercice

**Une capture faite par SPAN montre de nombreuses retransmissions TCP entre un poste et un serveur, mais les deux machines n’en voient aucune dans leurs propres captures. Explication ?**

<details><summary>Voir le corrigé</summary>

La session SPAN **perd des copies** (port destination saturé ou SPAN de faible priorité) : l’analyseur voit des « trous » qui n’existent pas en réalité, et Wireshark les interprète comme des pertes. Il faut réduire la source (un seul sens, filtrer), utiliser un port destination plus rapide, ou un TAP.

</details>
