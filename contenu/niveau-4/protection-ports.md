---
titre: Protéger les ports d’accès
nom: Port Security, Storm Control, RA Guard et IP Source Guard
idee: Les ports où se branchent les utilisateurs sont la première porte d’entrée ; on les protège avec une série de fonctions qui limitent les adresses, les débits de broadcast et les annonces usurpées.
osi: "2 et 3"
duree: [9, 18]
cle: true
prerequis: [dhcp-snooping, ndp]
retenir:
  - "**Port Security** — limiter le nombre d’adresses MAC par port."
  - "**Storm Control** — limiter le broadcast et le multicast, pour qu’une boucle ou un appareil fou ne sature pas le VLAN."
  - "**RA Guard** — bloquer les fausses annonces de routeur IPv6 sur les ports d’accès (même dans un réseau « sans IPv6 »)."
  - "**IP Source Guard** — n’accepter que l’adresse IP attribuée au port."
  - Ensemble avec **DHCP Snooping**, **DAI**, **BPDU Guard** et **802.1X**, elles forment une défense en profondeur.
---

## Le problème : tout ce qui peut arriver sur une prise

Un port d’accès reçoit normalement le trafic d’un PC et parfois d’un téléphone. Mais on peut aussi y trouver : un petit switch de bureau (boucle possible), une box (faux DHCP), un outil qui génère des milliers d’adresses MAC, une machine qui se déclare routeur IPv6, ou un appareil défaillant qui inonde le VLAN de broadcasts.

> [!IMPORTANT] L’idée en une phrase
> Chaque fonction de protection répond à une menace précise ; activées ensemble sur tous les ports d’accès, elles empêchent un seul appareil de perturber ou d’espionner tout le VLAN.

## La boîte à outils

| Menace | Protection | Fiche |
|---|---|---|
| Switch branché, boucle | **BPDU Guard** | [STP](../niveau-1/stp.md) |
| Saturation de la table MAC, appareils non prévus | **Port Security** | ci-dessous |
| Tempête de broadcast | **Storm Control** | ci-dessous |
| Faux serveur DHCP | **DHCP Snooping** | [DHCP Snooping](../niveau-1/dhcp-snooping.md) |
| Usurpation ARP | **DAI** | [DAI](dai.md) |
| Fausse passerelle IPv6 | **RA Guard** | ci-dessous |
| Usurpation d’adresse IP source | **IP Source Guard** | ci-dessous |
| Appareil non autorisé | **802.1X** | [802.1X](802-1x.md) |

## RA Guard : le piège de l’IPv6 « inexistant »

Beaucoup de réseaux n’utilisent pas IPv6… mais tous les systèmes récents l’activent par défaut. Un attaquant (ou un logiciel de partage de connexion) qui envoie une **annonce de routeur** IPv6 devient la passerelle IPv6 de tous les postes du VLAN, qui préfèrent alors IPv6 pour joindre les sites qui le proposent. **RA Guard** bloque les annonces de routeur reçues sur les ports d’accès.

```topologie
titre: Ce que les protections de port empêchent
SW switch 1.5,0 "Switch d’accès"
PC pc 0,1.2 "Poste" "1 adresse MAC : OK"
MINI switch 1.5,1.2 "Switch personnel" "BPDU reçue : port coupé"
DHCP serveur 3,1.2 "Serveur DHCP pirate" "port non fiable : offres jetées"
SW -- PC
SW -x- MINI
SW -x- DHCP
```

## Les mots à connaître

- **Port Security** — Limitation et contrôle des adresses MAC autorisées sur un port.
- **Storm Control** — Limitation du débit de broadcast, multicast ou unicast inconnu sur un port.
- **RA Guard** — Filtrage des annonces de routeur IPv6 sur les ports où aucun routeur ne doit se trouver.
- **IP Source Guard** — Filtrage du trafic dont l’adresse IP source ne correspond pas à celle attribuée au port.
- **Défense en profondeur** — Superposition de protections indépendantes.

## Teste-toi

**Un réseau n’a jamais déployé IPv6. Pourquoi activer quand même RA Guard ?**

<details><summary>Voir le corrigé</summary>

Parce que les postes ont **IPv6 activé par défaut** : une fausse annonce de routeur suffit à leur donner une passerelle IPv6 contrôlée par l’attaquant, sans que l’IPv4 soit touché. Le réseau « sans IPv6 » est en réalité un réseau IPv6 **non surveillé**.

</details>

<!-- approfondir -->

## Un port d’accès durci (Cisco IOS-XE)

```cisco
! Politique RA Guard pour les ports d'accès
ipv6 nd raguard policy HOTES
 device-role host
!
interface range GigabitEthernet1/0/1 - 46
 switchport mode access
 switchport nonegotiate
 switchport access vlan 10
 switchport voice vlan 20
 ! Boucles
 spanning-tree portfast
 spanning-tree bpduguard enable
 ! Adresses MAC : PC + téléphone (+ marge)
 switchport port-security
 switchport port-security maximum 3
 switchport port-security violation restrict
 switchport port-security aging time 10
 switchport port-security aging type inactivity
 ! Tempêtes
 storm-control broadcast level 1.00
 storm-control multicast level 5.00
 storm-control action trap
 ! IPv6
 ipv6 nd raguard attach-policy HOTES
 ! DHCP et ARP
 ip dhcp snooping limit rate 15
 ip arp inspection limit rate 15
 ! Usurpation d'IP source
 ip verify source
```

## Les modes de violation de Port Security

| Mode | Trames des adresses en trop | Journal | Port |
|---|---|---|---|
| `protect` | jetées | non | reste actif |
| `restrict` | jetées | **oui** | reste actif |
| `shutdown` (défaut) | — | oui | **err-disabled** |

`restrict` est souvent le meilleur compromis sur les ports utilisateurs : on bloque l’intrus sans couper l’utilisateur légitime, et l’on est prévenu.

## Storm Control : choisir les seuils

Les seuils s’expriment en pourcentage du débit du port (ou en paquets par seconde). Un poste normal envoie très peu de broadcast : 1 % d’un lien à 1 Gb/s (10 Mb/s de broadcast) est déjà énorme pour un poste. On mesure d’abord le trafic réel, puis on fixe un seuil confortable. L’action `trap` journalise ; `shutdown` coupe le port.

## Vérifier

```cisco
SW1# show port-security interface Gi1/0/5
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Maximum MAC Addresses      : 3
Total MAC Addresses        : 2
Security Violation Count   : 0
SW1# show storm-control Gi1/0/5
Interface  Type       Filter State   Upper        Lower        Current
---------  ---------  -------------  -----------  -----------  ----------
Gi1/0/5    Bcast      Forwarding       1.00%        1.00%        0.02%
SW1# show ipv6 nd raguard policy HOTES
SW1# show ip verify source interface Gi1/0/5
```

## Exercices

**1.** Après l’activation de Port Security (`maximum 1`, `violation shutdown`), les ports des postes équipés d’un téléphone passent en err-disabled. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Le port voit **deux** adresses MAC : celle du téléphone et celle du PC branché derrière. Avec un maximum de 1, la deuxième déclenche la violation et coupe le port. Il faut au moins `maximum 2` (souvent 3 pour la marge), et de préférence le mode `restrict`.

</details>

**2.** Un logiciel de partage de connexion sur un ordinateur portable a rendu les sites Web très lents pour tout un étage, sans toucher l’IPv4. Quelle protection aurait évité l’incident ?

<details><summary>Voir le corrigé</summary>

**RA Guard** : le portable a émis des **annonces de routeur IPv6** ; les postes du VLAN l’ont pris pour passerelle IPv6 et tentaient de joindre les sites en IPv6 à travers lui, sans succès ou très lentement. RA Guard sur les ports d’accès aurait bloqué ces annonces.

</details>
