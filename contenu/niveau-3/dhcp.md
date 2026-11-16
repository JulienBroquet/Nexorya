---
titre: DHCP
nom: Dynamic Host Configuration Protocol
idee: DHCP donne automatiquement à chaque appareil son adresse IP, son masque, sa passerelle et ses serveurs DNS, pour une durée limitée appelée bail.
osi: "7 (UDP 67 serveur, 68 client)"
duree: [8, 18]
prerequis: [adresses, udp]
retenir:
  - "Échange en quatre messages — **D**iscover, **O**ffer, **R**equest, **A**ck (DORA)."
  - "Le client reçoit au minimum — adresse, masque, **passerelle**, **DNS**, durée du **bail**."
  - "Le DHCP commence par un **broadcast** — il ne traverse pas les routeurs sans **relais** (`ip helper-address`)."
  - "Adresse en **169.254.x.x** = aucun serveur DHCP n’a répondu."
---

## Le problème : configurer 500 postes à la main

Chaque appareil a besoin d’une adresse IP unique, du bon masque, de la bonne passerelle et des bons serveurs DNS. Les saisir à la main sur 500 postes, des téléphones et les ordinateurs des visiteurs, c’est des heures de travail et des erreurs garanties (deux postes avec la même adresse, une faute de frappe dans la passerelle).

> [!IMPORTANT] L’idée en une phrase
> Un serveur DHCP tient un stock d’adresses et **prête** une adresse à chaque appareil qui se connecte, avec toute la configuration réseau, pour une durée limitée.

## Comment ça marche : DORA

```sequence
titre: Un poste obtient son adresse
Poste | Serveur DHCP
Poste -> Serveur DHCP : DISCOVER (broadcast) : « y a-t-il un serveur DHCP ? »
Serveur DHCP --> Poste : OFFER : « je te propose 10.10.0.57 »
Poste -> Serveur DHCP : REQUEST (broadcast) : « j’accepte 10.10.0.57 »
Serveur DHCP --> Poste : ACK : « confirmé : masque /24, passerelle .1, DNS 10.99.0.53, bail 8 h »
```

1. **Discover** : le poste, qui n’a pas encore d’adresse, crie en **broadcast** pour trouver un serveur.
2. **Offer** : un serveur propose une adresse libre.
3. **Request** : le poste accepte (en broadcast, pour prévenir les autres serveurs éventuels qu’il a choisi).
4. **Ack** : le serveur confirme et envoie toute la configuration.

## Le bail

L’adresse est **prêtée**, pas donnée. À **la moitié** du bail, le poste demande à le prolonger. S’il est éteint ou parti, le serveur pourra réattribuer l’adresse à expiration. On choisit des baux courts (1 à 4 heures) pour les réseaux invités où les appareils changent souvent, plus longs (8 heures à quelques jours) pour les postes fixes.

## Le relais DHCP : traverser les routeurs

Le Discover est un broadcast : il **ne traverse pas** les routeurs. Or on n’installe pas un serveur DHCP dans chaque VLAN. On configure donc sur la passerelle de chaque VLAN un **relais** qui transforme le broadcast en message dirigé vers le serveur central.

```topologie
titre: Un serveur DHCP central pour tous les VLAN
P1 pc 0,0 "Poste VLAN 10"
P2 pc 0,1 "Poste VLAN 20"
L3 l3 1.5,0.5 "Switch L3" "relais DHCP sur chaque VLAN"
SRV serveur 3,0.5 "Serveur DHCP" "10.99.0.10"
P1 -- L3 "broadcast"
P2 -- L3 "broadcast"
L3 ++ SRV "unicast"
```

## Les mots à connaître

- **DHCP** — Protocole qui attribue automatiquement la configuration réseau aux appareils.
- **Bail** — Durée pendant laquelle une adresse est prêtée à un appareil.
- **Étendue** — Plage d’adresses qu’un serveur DHCP peut distribuer pour un réseau ; *scope* ou *pool*.
- **Réservation** — Adresse toujours attribuée au même appareil, identifié par son adresse MAC.
- **Relais DHCP** — Fonction d’un routeur qui transmet les demandes DHCP vers un serveur situé dans un autre réseau.

## Teste-toi

**1.** Un nouveau VLAN est créé. Les postes obtiennent une adresse en 169.254.x.x. Le serveur DHCP a bien une étendue pour ce VLAN. Que manque-t-il le plus souvent ?

<details><summary>Voir le corrigé</summary>

Le **relais DHCP** (`ip helper-address`) sur l’interface du nouveau VLAN. Sans lui, le broadcast Discover reste dans le VLAN et n’atteint jamais le serveur.

</details>

**2.** Pourquoi réserver l’adresse d’une imprimante plutôt que la configurer à la main ?

<details><summary>Voir le corrigé</summary>

La **réservation** garantit que l’imprimante reçoit toujours la même adresse, tout en gardant une **gestion centralisée** : changement de DNS, de passerelle ou de plan d’adressage au même endroit, et aucun risque de conflit avec une adresse distribuée.

</details>

<!-- approfondir -->

## Les options DHCP courantes

| Option | Contenu |
|---|---|
| 1 | masque de sous-réseau |
| 3 | passerelle (routeur) |
| 6 | serveurs DNS |
| 15 | suffixe DNS (domaine) |
| 42 | serveurs NTP |
| 43 | informations propres au fabricant (souvent l’adresse du contrôleur Wi-Fi pour les bornes) |
| 51 | durée du bail |
| 66 / 67 | serveur et fichier de démarrage réseau (PXE, téléphones) |
| 82 | informations du relais (switch, port) |
| 150 | serveur TFTP (téléphones Cisco) |

## Configuration (Cisco IOS)

```cisco
! Relais sur la passerelle de chaque VLAN
interface Vlan10
 ip address 10.10.0.1 255.255.255.0
 ip helper-address 10.99.0.10
 ip helper-address 10.99.0.11        ! second serveur, pour la redondance
!
! Petit serveur DHCP sur un routeur d'agence
ip dhcp excluded-address 10.30.0.1 10.30.0.20
ip dhcp pool INVITES
 network 10.30.0.0 255.255.255.0
 default-router 10.30.0.1
 dns-server 10.99.0.53 10.99.0.54
 lease 0 2                           ! 2 heures
```

> [!NOTE]
> `ip helper-address` relaie aussi, par défaut, d’autres broadcasts UDP (TFTP, DNS, NetBIOS, TACACS…). On peut restreindre avec `no ip forward-protocol udp <port>`.

## Vérification et dépannage

```cisco
R1# show ip dhcp binding
IP address      Client-ID/Hardware address   Lease expiration        Type
10.30.0.21      0100.1a2b.3c4d.5e            Nov 15 2026 11:42 AM    Automatic
R1# show ip dhcp pool INVITES
 Total addresses                : 254
 Leased addresses               : 233
 Excluded addresses             : 20
R1# show ip dhcp conflict
R1# debug ip dhcp server packet
```

```powershell
C:\> ipconfig /release
C:\> ipconfig /renew
C:\> ipconfig /all | findstr /i "DHCP Bail Serveur"
```

```bash
$ sudo dhclient -v eth0          # ou : nmcli connection up "Ethernet"
$ journalctl -u NetworkManager | grep -i dhcp
```

| Symptôme | Causes probables |
|---|---|
| 169.254.x.x | pas de réponse : câble, VLAN, relais absent, serveur arrêté, DHCP Snooping qui bloque (uplink non « trusted », option 82) |
| Adresse d’un mauvais réseau (192.168.0.x) | **serveur DHCP pirate** (box, routeur domestique) : voir [DHCP Snooping](../niveau-1/dhcp-snooping.md) |
| Plus d’adresses pour les nouveaux venus | étendue **épuisée** : baux trop longs pour un réseau invités, étendue trop petite |
| Conflit d’adresse signalé | une adresse de l’étendue est utilisée par un équipement configuré à la main : l’exclure |

## Redondance du service

- **Deux serveurs avec basculement** (*DHCP failover*, ISC Kea, Windows Server) : ils partagent l’état des baux.
- Méthode ancienne, encore courante : **découper l’étendue** entre deux serveurs (80/20) sans synchronisation.
- Dans tous les cas : déclarer **deux** `ip helper-address`.

## DHCPv6 en bref

En IPv6, la passerelle vient toujours des **annonces de routeur** ; DHCPv6 fournit les adresses (mode avec état) ou seulement les options comme le DNS (mode sans état). Ports UDP 546 (client) et 547 (serveur), messages SOLICIT, ADVERTISE, REQUEST, REPLY. Voir [IPv6 en pratique](../niveau-2/ipv6-pratique.md).

## Exercices

**1.** Le réseau invités (/24, bail de 8 jours) refuse de nouveaux appareils chaque vendredi après-midi. Pourquoi, et que corriger ?

<details><summary>Voir le corrigé</summary>

Des centaines de visiteurs passent dans la semaine ; chacun garde son adresse **8 jours**, même parti. L’étendue de 254 adresses est **épuisée**. Réduire le bail (1 à 2 heures) et, si besoin, agrandir le réseau (/23 ou /22).

</details>

**2.** Après l’activation du DHCP Snooping, les postes ne reçoivent plus d’adresse, alors que l’uplink est bien « trusted ». Le relais est un routeur Cisco. Quelle piste ?

<details><summary>Voir le corrigé</summary>

L’**option 82** insérée par le switch. Le relais reçoit une requête avec l’option 82 et une adresse `giaddr` nulle, et la **rejette** par défaut. Solutions : `no ip dhcp snooping information option` sur le switch, ou `ip dhcp relay information trusted` sur l’interface du relais.

</details>
