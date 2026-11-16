---
titre: LLDP
nom: Link Layer Discovery Protocol (IEEE 802.1AB)
idee: Avec LLDP, chaque équipement annonce son nom, son modèle et son port à ses voisins directs ; on sait ainsi qui est branché en face de chaque port.
osi: "2"
duree: [6, 12]
prerequis: [ethernet]
retenir:
  - LLDP est **standard** (toutes marques) ; CDP est son équivalent propriétaire Cisco.
  - "`show lldp neighbors` répond à la question — **qui est branché en face de ce port ?**"
  - "**LLDP-MED** permet aux téléphones d’apprendre leur VLAN voix et de négocier leur puissance PoE."
  - On le désactive sur les ports exposés (Internet, invités), car il divulgue des informations.
---

## Le problème : la baie mal documentée

Tu ouvres une baie réseau : des dizaines de câbles, peu ou pas d’étiquettes, un schéma vieux de trois ans. À quel switch mène le port 48 ? Sur quel port de ce switch arrive-t-il ? Suivre le câble à la main est long et risqué.

> [!IMPORTANT] L’idée en une phrase
> Avec LLDP, chaque équipement **se présente** à ses voisins directs, toutes les 30 secondes : « je suis SW-ETAGE2, un switch de telle marque, et tu es branché sur mon port Gi1/0/24 ».

## Comment ça marche

1. Chaque équipement envoie régulièrement un petit message LLDP sur chacun de ses ports.
2. Ce message contient son nom, son type, son adresse de gestion, et le nom du port d’où il part.
3. Le voisin direct le reçoit et le stocke dans une table. Il ne le retransmet **pas** plus loin : LLDP ne voit que les voisins immédiats.
4. L’administrateur consulte cette table avec une simple commande.

```cisco
SW1# show lldp neighbors
Device ID        Local Intf     Hold-time  Capability      Port ID
DIST1            Gi1/0/48       120        B,R             Te1/0/3
AP-ETG2-04       Gi1/0/12       120        B,W             Gi0
SEP0011223344    Gi1/0/5        180        B,T             0011223344:P1
```

Lecture : le port **Gi1/0/48** mène au switch **DIST1**, sur son port **Te1/0/3**. Le port Gi1/0/12 mène à une borne Wi-Fi (`W`), le port Gi1/0/5 à un téléphone (`T`).

```topologie
titre: Les équipements s’annoncent à leurs voisins directs
COEUR l3 0,0 "Cœur"
SW switch 2.2,0 "SW-ETAGE2" "Gi1/0/14"
AP ap 4.4,0 "Borne Wi-Fi"
TEL telephone 2.2,1.3 "Téléphone IP"
PC pc 2.2,2.5 "Poste"
COEUR .. SW "nom, port"
SW .. AP "modèle, PoE"
SW .. TEL "nom, port, VLAN voix"
TEL -- PC
```

## Les mots à connaître

- **LLDP** — Protocole standard par lequel un équipement annonce son identité à ses voisins directs.
- **Voisin** — Équipement relié directement à un port, sans intermédiaire.
- **LLDP-MED** — Extension de LLDP pour les téléphones et terminaux : VLAN voix, PoE, localisation.

## Teste-toi

**Le port Gi1/0/20 d’un switch est relié à un petit switch non administrable, lui-même relié à trois PC. Que montre `show lldp neighbors` sur ce port ?**

<details><summary>Voir le corrigé</summary>

Probablement **rien** : un switch non administrable n’envoie pas de LLDP, et il ne transmet pas non plus les LLDP des PC (ils sont destinés à une adresse multicast que les switches ne relaient pas). LLDP ne voit que les voisins directs qui le parlent.

</details>

<!-- approfondir -->

## Ce que contient une trame LLDP

LLDP est transporté directement dans Ethernet (EtherType `0x88CC`), vers l’adresse multicast `01:80:C2:00:00:0E`, que les switches **ne relaient pas**. Le message est une suite de champs **TLV** (type, longueur, valeur) :

| TLV obligatoires | TLV facultatifs courants |
|---|---|
| Chassis ID (souvent la MAC) | System Name, System Description |
| Port ID | Management Address |
| Time To Live (durée de validité, 120 s par défaut) | Port VLAN ID, capacités (bridge, router, phone, WLAN AP) |
| | Extensions 802.3 : vitesse, duplex, MTU, puissance PoE |
| | LLDP-MED : politique réseau (VLAN voix, priorité), inventaire, localisation |

## Configuration (Cisco IOS)

Sur la plupart des switches Cisco, LLDP est **désactivé par défaut** (CDP est actif).

```cisco
lldp run
!
! Ne pas annoncer vers Internet ou une zone non maîtrisée
interface GigabitEthernet0/0/0
 description Lien opérateur Internet
 no lldp transmit
 no lldp receive
```

```cisco
SW1# show lldp neighbors GigabitEthernet1/0/48 detail
Chassis id: 00aa.0b00.0001
Port id: Te1/0/3
Port Description: Uplink ACC1
System Name: DIST1
System Description:
Cisco IOS XE Software, Version 17.9.4 …
Management Addresses:
    IP: 10.99.0.2
Auto Negotiation - supported, enabled
```

La sortie détaillée donne l’**adresse de gestion** et la **version logicielle** du voisin : très utile pour l’inventaire… et pour un attaquant, d’où la désactivation sur les ports exposés.

## LLDP-MED et les téléphones

Un téléphone IP compatible LLDP-MED reçoit du switch sa **politique réseau** : « utilise le VLAN 20 avec la priorité 5 ». Il négocie aussi sa puissance PoE exacte. C’est l’équivalent standard de ce que CDP fait avec les téléphones Cisco. Sur un switch Cisco, la commande `switchport voice vlan 20` alimente automatiquement cette annonce.

## Exercices

**1.** Comment cartographier rapidement les liens entre 30 switches ?

<details><summary>Voir le corrigé</summary>

Activer LLDP (ou utiliser CDP) partout, puis collecter `show lldp neighbors` sur chaque switch — à la main, avec un script, ou via la base LLDP-MIB en SNMP. Chaque ligne donne un lien « port local → voisin, port distant ». De nombreux outils de supervision construisent ainsi une carte automatique.

</details>

**2.** Pourquoi désactiver LLDP sur le port relié au routeur de l’opérateur Internet ?

<details><summary>Voir le corrigé</summary>

Parce que LLDP annonce le **nom**, le **modèle**, la **version logicielle** et l’**adresse de gestion** de l’équipement : autant d’informations utiles à un attaquant, et inutiles à l’opérateur.

</details>
