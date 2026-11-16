---
titre: MACsec
nom: Chiffrement des liens Ethernet (IEEE 802.1AE)
idee: MACsec chiffre chaque trame Ethernet entre deux équipements directement reliés, à la vitesse du lien ; il protège les câbles et les fibres contre l’écoute et l’insertion.
osi: "2"
duree: [5, 12]
prerequis: [ethernet, 802-1x]
retenir:
  - MACsec chiffre **lien par lien** — chaque équipement déchiffre, traite et rechiffre.
  - Il est réalisé **en matériel**, à la vitesse du lien, sans réduire le débit.
  - Les clés sont gérées par **MKA** (avec une clé pré-partagée ou 802.1X).
  - "Usages — fibres entre bâtiments ou datacenters, liens sur des infrastructures louées, ports d’accès sensibles."
---

## Le problème

Une fibre relie deux bâtiments en passant par des fourreaux partagés, ou deux datacenters par une liaison louée à un opérateur. Quiconque a un accès physique à cette fibre peut, avec un coupleur, **écouter** ou **injecter** du trafic. IPsec protégerait les paquets routés, mais pas les protocoles de niveau 2, et il est coûteux à très haut débit.

> [!IMPORTANT] L’idée en une phrase
> MACsec chiffre et authentifie chaque trame directement sur le lien Ethernet, en matériel : ce qui circule sur le câble devient illisible et infalsifiable.

## MACsec ou IPsec ?

| | MACsec | IPsec |
|---|---|---|
| Portée | **un lien** (entre deux équipements voisins) | de bout en bout entre deux routeurs, à travers des réseaux |
| Couche | 2 | 3 |
| Débit | vitesse du lien (10, 40, 100 Gb/s…) | limité par le matériel de chiffrement |
| Protège | tout le trafic du lien, y compris les protocoles de niveau 2 | les paquets IP sélectionnés |

```topologie
titre: MACsec chiffre chaque lien, d’un équipement au suivant
PC pc 0,0 "Poste"
ACC switch 1.5,0 "Switch d’accès"
COEUR l3 3,0 "Cœur"
DC switch 4.5,0 "Datacenter"
PC ++ ACC "chiffré"
ACC ++ COEUR "chiffré"
COEUR ++ DC "chiffré"
```

## Les mots à connaître

- **MACsec** — Chiffrement et authentification des trames Ethernet entre deux équipements voisins.
- **MKA** — *MACsec Key Agreement*, protocole d’échange des clés MACsec.
- **CAK / CKN** — Clé et nom de clé de connectivité, à partir desquels MKA dérive les clés de chiffrement.

## Teste-toi

**Pourquoi MACsec ne protège-t-il pas le trafic à l’intérieur d’un switch ?**

<details><summary>Voir le corrigé</summary>

Parce que chaque équipement **déchiffre** les trames reçues pour les traiter (consulter la table MAC, appliquer les VLAN), puis les **rechiffre** sur le lien suivant. Le trafic est en clair à l’intérieur de chaque équipement : MACsec protège les **liens**, pas les nœuds.

</details>

<!-- approfondir -->

## Configuration entre deux switches (Cisco IOS-XE, clé pré-partagée)

```cisco
key chain MACSEC-INTERBAT macsec
 key 01
  cryptographic-algorithm aes-256-cmac
  key-string 0 <64 caractères hexadécimaux>
  lifetime local 00:00:00 Jan 1 2026 infinite
!
mka policy MKA-256
 key-server priority 200
 macsec-cipher-suite gcm-aes-256
 confidentiality-offset 0
!
interface TenGigabitEthernet1/1/1
 macsec network-link
 mka policy MKA-256
 mka pre-shared-key key-chain MACSEC-INTERBAT
```

```cisco
SW1# show macsec summary
Interface                     Transmit SC          Receive SC
Te1/1/1                            1                    1
SW1# show mka sessions
Interface      Local-TxSCI         Policy-Name      Inherited         Key-Server
Te1/1/1        7c21.0e4a.1b81/0013 MKA-256          NO                YES
Port-ID   Peer-RxSCI       MACsec-Peers     Status       CKN
19        00aa.0b00.0081/0013    1          Secured      01
```

`Status: Secured` : le lien est chiffré. Si MKA ne s’établit pas, le lien peut rester **bloqué** (comportement *must-secure*) ou passer **en clair** (*should-secure*) selon la politique choisie.

## Points d’attention

- Les deux équipements **et leurs ports** (ou modules) doivent supporter MACsec à la vitesse voulue.
- L’en-tête MACsec ajoute 24 à 32 octets : vérifier la **MTU** des liens.
- Sur une liaison opérateur, le service doit transporter les trames MACsec (EtherType `0x88E5`) de façon transparente.

## Exercice

**Après l’activation de MACsec sur une fibre inter-bâtiments, les petits pings passent mais les transferts de fichiers échouent. Hypothèse ?**

<details><summary>Voir le corrigé</summary>

Un problème de **MTU** : l’en-tête MACsec ajoute plusieurs dizaines d’octets, et les trames pleines dépassent la taille acceptée sur le chemin (par exemple par l’équipement de l’opérateur). Augmenter la MTU des interfaces concernées ou vérifier ce que l’opérateur accepte.

</details>
