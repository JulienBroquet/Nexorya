---
titre: Ethernet
nom: La trame Ethernet (IEEE 802.3)
idee: Ethernet définit la trame, l’enveloppe qui transporte les données sur un réseau local, avec l’adresse du destinataire, celle de l’expéditeur et un code pour détecter les erreurs.
osi: "1 et 2"
duree: [8, 18]
prerequis: [osi]
retenir:
  - "Une trame contient — **MAC destination**, **MAC source**, **type** du contenu, **données** (46 à 1 500 octets) et **FCS**."
  - Le **FCS** permet au récepteur de détecter une trame abîmée ; elle est alors jetée (compteur **CRC**).
  - Aujourd’hui, Ethernet fonctionne en **full duplex** sur des liens point à point — les collisions ont disparu.
---

## Le problème : envoyer un message au bon voisin

Sur un réseau local, des dizaines d’appareils partagent les mêmes switches. Pour qu’un message arrive à la bonne machine et qu’on puisse savoir s’il a été abîmé en route, il faut un **format commun** : une enveloppe standard. Ethernet définit cette enveloppe, appelée **trame**, et la façon de la transmettre.

> [!IMPORTANT] L’idée en une phrase
> Ethernet est le protocole des réseaux locaux filaires : il emballe les données dans une **trame** qui porte l’adresse MAC du destinataire, celle de l’expéditeur et un code de contrôle.

## Les parties d’une trame

| Champ | Taille | À quoi il sert |
|---|---|---|
| **MAC destination** | 6 octets | Qui doit recevoir la trame. |
| **MAC source** | 6 octets | Qui l’a envoyée (pour pouvoir répondre). |
| **Type** | 2 octets | Ce que contient la trame : un paquet IPv4, IPv6, ARP… |
| **Données** | 46 à 1 500 octets | Le contenu transporté, souvent un paquet IP. |
| **FCS** | 4 octets | Un code calculé sur toute la trame, pour détecter les erreurs. |

> [!TIP] L’analogie de l’enveloppe scellée
> Le FCS fonctionne comme un sceau. L’expéditeur calcule un nombre à partir de tout le contenu et l’inscrit à la fin. Le destinataire refait le calcul : si le résultat diffère, la trame a été abîmée en route et elle est **jetée**. Ethernet ne la redemande pas : ce sont les couches supérieures (TCP par exemple) qui s’apercevront du manque.

## De l’Ethernet partagé à l’Ethernet commuté

Aux débuts d’Ethernet, toutes les machines étaient branchées sur **un même câble** (ou un hub). Une seule pouvait parler à la fois : si deux parlaient ensemble, il y avait **collision**, et chacune attendait un délai aléatoire avant de réessayer (c’est la méthode CSMA/CD).

Aujourd’hui, chaque appareil a **son propre câble vers un switch**, en full duplex. Il n’y a plus de support partagé, donc **plus de collisions**. CSMA/CD n’existe plus que dans les livres d’histoire… et dans les pannes de duplex.

## Exemple : des erreurs CRC après un déménagement

Après le déplacement d’un bureau, un port du switch affiche un compteur **CRC** qui augmente régulièrement, et l’utilisateur se plaint de lenteurs. Chaque CRC est une trame dont le FCS ne correspondait pas : abîmée pendant le transport. Les causes classiques sont physiques : prise mal sertie, câble écrasé, passage près d’un moteur ou de néons. On change d’abord le cordon.

## Les mots à connaître

- **Ethernet** — Famille de normes IEEE 802.3 qui définit les réseaux locaux filaires : câbles, signaux et format des trames.
- **Trame** — Unité de données de la couche 2, qui contient adresses MAC, type, données et FCS.
- **FCS** — *Frame Check Sequence*, code de contrôle calculé sur la trame pour détecter les erreurs.
- **CRC** — Méthode de calcul du FCS ; par extension, compteur des trames reçues abîmées.
- **Hub** — Ancien équipement qui recopiait chaque signal sur tous ses ports, sans rien comprendre aux trames.

## Teste-toi

**1.** Une trame arrive avec un FCS incorrect. Que fait le switch ?

<details><summary>Voir le corrigé</summary>

Il la **jette** et incrémente son compteur d’erreurs CRC. Ethernet ne demande pas de renvoi : si les données comptaient, c’est le protocole de transport (TCP) des machines qui constatera le manque et renverra.

</details>

**2.** Quelle est la taille maximale des données dans une trame Ethernet standard ?

<details><summary>Voir le corrigé</summary>

**1 500 octets**. C’est la **MTU** standard d’Ethernet. Avec les en-têtes et le FCS, la trame complète fait au maximum 1 518 octets (1 522 avec une étiquette VLAN).

</details>

<!-- approfondir -->

## Format exact d’une trame Ethernet II

```text
 octets :  7          1     6           6          2        46-1500        4
        ┌──────────┬─────┬──────────┬──────────┬────────┬──────────────┬──────┐
        │Préambule │ SFD │ MAC dest │ MAC src  │EtherType│  Données     │ FCS  │
        └──────────┴─────┴──────────┴──────────┴────────┴──────────────┴──────┘
          synchronisation                                          CRC-32
          (non compté dans la taille de trame)
        + écart inter-trames de 12 octets minimum entre deux trames
```

- **Préambule et SFD** : 8 octets de motif 1010… qui permettent au récepteur de se synchroniser. Ils ne figurent pas dans les captures Wireshark.
- **EtherType** : `0x0800` IPv4, `0x86DD` IPv6, `0x0806` ARP, `0x8100` étiquette VLAN 802.1Q, `0x88CC` LLDP. Si la valeur est **inférieure ou égale à 1 500**, il s’agit d’une **longueur** (format 802.3 avec en-tête LLC), comme pour les BPDU STP.
- **Taille minimale** : 64 octets de l’adresse destination au FCS. Si les données font moins de 46 octets, la carte ajoute du **bourrage** (*padding*).
- **FCS** : CRC-32 calculé sur les adresses, le type et les données.

Une trame de moins de 64 octets est un **runt** ; une trame de plus de 1 518 octets (sans VLAN ni jumbo configuré) est un **giant**. Les deux sont jetées et comptées.

## Pourquoi 64 octets minimum ?

C’est un héritage de CSMA/CD : en half duplex, l’émetteur devait encore être en train d’émettre quand une éventuelle collision revenait de l’extrémité du réseau, pour la détecter. 64 octets à 10 Mb/s correspondent à 51,2 µs, le temps d’aller-retour du signal sur le plus grand réseau autorisé. La règle est restée pour la compatibilité.

## Débit réel sur Ethernet

Chaque trame coûte, en plus des données : 8 octets de préambule, 14 d’en-tête, 4 de FCS et 12 d’écart inter-trames, soit **38 octets**. Avec des trames pleines :

```text
efficacité = 1500 / (1500 + 38) ≈ 97,5 %   → environ 975 Mb/s de paquets IP sur un lien à 1 Gb/s
avec des trames minimales : 46 / (46 + 38) ≈ 55 %
```

C’est pour cela qu’on exprime aussi la capacité d’un switch en **paquets par seconde** : un lien à 1 Gb/s peut transporter jusqu’à 1 488 095 trames de 64 octets par seconde.

## Lire les compteurs d’une interface (Cisco IOS)

```cisco
SW1# show interfaces GigabitEthernet1/0/7
GigabitEthernet1/0/7 is up, line protocol is up (connected)
  Hardware is Gigabit Ethernet, address is 7c21.0e4a.1b07 (bia 7c21.0e4a.1b07)
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
  Full-duplex, 1000Mb/s, media type is 10/100/1000BaseTX
  …
     1734 input errors, 1734 CRC, 0 frame, 0 overrun, 0 ignored
     0 runts, 0 giants, 0 throttles
     0 output errors, 0 collisions, 2 interface resets
```

| Compteur | Signification | Cause typique |
|---|---|---|
| `CRC` | trames reçues avec un FCS faux | câble, connecteur, interférences, duplex |
| `runts` / `giants` | trames trop courtes / trop longues | duplex, MTU incohérente |
| `collisions`, `late collision` | collisions (half duplex) | désaccord de duplex |
| `interface resets` | réinitialisations du port | lien instable, problème physique |
| `output drops` (ailleurs dans la sortie) | trames rejetées faute de place | congestion |

Pour savoir si un compteur **augmente**, on le remet à zéro (`clear counters GigabitEthernet1/0/7`) puis on relance la commande quelques minutes plus tard. Un compteur élevé mais figé raconte un incident passé.

## Exercices

**1.** Une capture montre une trame dont le champ type vaut `0x0026`. Qu’est-ce que cela signifie ?

<details><summary>Voir le corrigé</summary>

`0x0026` = 38, une valeur inférieure à 1 500 : ce n’est pas un EtherType mais une **longueur**. C’est une trame au format **802.3 avec en-tête LLC**, comme celles qui transportent les BPDU STP.

</details>

**2.** Pourquoi un switch rapporte-t-il un nombre de CRC sur un port, alors que le PC branché dessus n’en voit aucun ?

<details><summary>Voir le corrigé</summary>

Chaque côté ne compte que les erreurs **qu’il reçoit**. Le switch voit des trames abîmées **dans le sens PC → switch** : défaut sur les paires d’émission du PC, sur le connecteur, ou interférences sur ce sens. L’autre sens peut être parfaitement sain. Dans un désaccord de duplex, c’est le côté full duplex qui compte des CRC.

</details>

**3.** Combien de trames de 1 518 octets un lien à 10 Gb/s peut-il transporter par seconde ?

<details><summary>Voir le corrigé</summary>

Chaque trame occupe 1 518 + 8 (préambule) + 12 (écart) = 1 538 octets = 12 304 bits. 10 × 10⁹ / 12 304 ≈ **812 744 trames par seconde**.

</details>
