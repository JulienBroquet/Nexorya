---
titre: Durcir un équipement
nom: Sécuriser un switch ou un routeur sans se couper l’accès
idee: Durcir un équipement réseau, c’est fermer tout ce qui n’est pas nécessaire, protéger les accès d’administration et garder des traces — en préparant toujours un accès de secours avant de modifier.
osi: "plans de gestion et de contrôle"
duree: [10, 20]
cle: true
prerequis: [ssh, aaa]
retenir:
  - "Accès d’administration — **SSH** seulement, depuis le **réseau d’administration**, comptes **nominatifs** via AAA, compte local de secours."
  - Désactiver les **services inutiles** (HTTP en clair, CDP/LLDP vers l’extérieur, Telnet, SNMP v1/v2c).
  - "Protéger le **plan de contrôle** — authentification des protocoles de routage, limitation du trafic vers le processeur (CoPP)."
  - "Avant toute modification à distance — session de secours, **reload in**, sauvegarde."
---

## Le problème

Un switch sorti du carton fonctionne… avec des réglages pensés pour la facilité, pas pour la sécurité : services inutiles actifs, accès d’administration ouverts à tous, pas de journaux centralisés. Or celui qui contrôle un équipement réseau peut **écouter, détourner ou couper** tout le trafic qui le traverse.

> [!IMPORTANT] L’idée en une phrase
> On réduit tout ce qu’un attaquant pourrait utiliser — services, accès, protocoles — et l’on rend visible tout ce qui se passe sur l’équipement.

## Les trois plans d’un équipement

| Plan | Ce qu’il fait | Comment le protéger |
|---|---|---|
| **Gestion** | l’administration : SSH, SNMP, interface Web, NTP, Syslog | accès restreints, chiffrés, authentifiés, journalisés |
| **Contrôle** | les protocoles entre équipements : OSPF, BGP, STP, ARP | authentification des voisins, filtrage, limitation vers le processeur |
| **Données** | le trafic des utilisateurs | ACL, protections des ports, segmentation |

## La liste de contrôle essentielle

1. **Mettre à jour** le système vers une version maintenue et sans vulnérabilité critique connue.
2. **Accès d’administration** : SSH v2 uniquement, ACL sur les lignes VTY, délai d’inactivité, bannière légale.
3. **Comptes** : authentification centralisée (TACACS+), comptes nominatifs, compte local de secours avec un secret fort (`algorithm-type scrypt`).
4. **Services inutiles** : désactiver le serveur HTTP en clair, Telnet, les petits services, CDP/LLDP sur les ports exposés.
5. **SNMP** : v3 en lecture seule, limité au superviseur.
6. **Journaux et heure** : NTP, Syslog centralisé, journalisation des commandes.
7. **Plan de contrôle** : authentifier OSPF/BGP, filtrer les routes, protéger le processeur.
8. **Ports inutilisés** : éteints, dans un VLAN parking.
9. **Sauvegarde** automatique de la configuration.

## Les mots à connaître

- **Durcissement** — Réduction de la surface d’attaque d’un système ; *hardening*.
- **Plan de gestion / de contrôle / de données** — Les trois grandes fonctions d’un équipement réseau.
- **CoPP** — *Control Plane Policing*, limitation du trafic destiné au processeur d’un équipement.
- **Surface d’attaque** — Ensemble des points par lesquels un système peut être attaqué.

## Teste-toi

**Pourquoi programmer un `reload in 10` avant de modifier l’ACL des lignes VTY d’un routeur distant ?**

<details><summary>Voir le corrigé</summary>

Si la modification te **coupe ton propre accès**, le routeur redémarrera dans 10 minutes avec la configuration **sauvegardée** (celle d’avant la modification), et tu retrouveras l’accès. Si tout fonctionne, tu annules avec `reload cancel` puis tu sauvegardes.

</details>

<!-- approfondir -->

## Un socle de configuration (Cisco IOS-XE)

```cisco
! --- Comptes et chiffrement des secrets
service password-encryption
enable algorithm-type scrypt secret <secret-fort>
username secours privilege 15 algorithm-type scrypt secret <secret-coffre>
login block-for 120 attempts 5 within 60
login on-failure log
login on-success log
!
! --- Accès d'administration
ip ssh version 2
ip access-list standard VTY-ADMIN
 permit 10.99.0.0 0.0.0.255
 deny any log
line vty 0 15
 transport input ssh
 access-class VTY-ADMIN in
 exec-timeout 10 0
line con 0
 exec-timeout 10 0
banner login ^Accès réservé aux personnes autorisées. Toute connexion est journalisée.^
!
! --- Services inutiles
no ip http server
ip http secure-server              ! seulement si l'interface Web est nécessaire, avec ACL
no service pad
no ip source-route
no ip bootp server
!
! --- Interfaces vers l'extérieur
interface GigabitEthernet0/0/0
 no cdp enable
 no lldp transmit
 no ip redirects
 no ip proxy-arp
!
! --- Heure, journaux, traces des commandes
ntp server 10.99.0.123
logging host 10.99.0.60
archive
 log config
  logging enable
  notify syslog
```

## Protéger le plan de contrôle (CoPP)

Le processeur d’un équipement traite les protocoles de contrôle et l’administration. Un flot de paquets vers lui (attaque, boucle, balayage) peut le saturer : l’équipement perd ses voisins OSPF, ne répond plus en SSH. **CoPP** limite le débit de chaque catégorie de trafic destiné au processeur. Les plateformes récentes ont une politique CoPP **par défaut** ; on la vérifie et on l’ajuste plutôt que de la désactiver.

```cisco
SW1# show policy-map control-plane | include Class|conformed|exceeded
```

## Modifier sans se couper : la méthode

1. **Sauvegarder** la configuration (`copy running-config` vers le serveur de sauvegarde).
2. Ouvrir **deux sessions** (ou garder un accès console).
3. `reload in 10` (ou `configure replace` avec retour automatique sur les plateformes qui le permettent).
4. Appliquer la modification.
5. **Tester** une nouvelle connexion depuis le réseau d’administration.
6. `reload cancel`, puis `write memory`.

> [!CAUTION]
> `reload in` redémarre réellement l’équipement s’il n’est pas annulé : sur un équipement de cœur, cela coupe le réseau. Réserve-le aux modifications de l’accès d’administration, en fenêtre de maintenance, et note l’heure prévue.

## Vérifier l’état de durcissement

```cisco
SW1# show running-config | include transport input|access-class|ip http|snmp-server community|username
SW1# show ip ssh
SW1# show users
SW1# show login
```

Des outils d’audit automatisés comparent la configuration de chaque équipement à un référentiel (guides de l’ANSSI, CIS Benchmarks) : c’est le moyen de garder un parc homogène dans la durée.

## Exercices

**1.** Un audit trouve `snmp-server community public RO` sur 40 switches. Quel risque, et quelle correction ?

<details><summary>Voir le corrigé</summary>

N’importe qui sur le réseau peut lire l’état et la configuration détaillée des switches (interfaces, voisins, tables), car la communauté `public` est connue de tous et circule en clair. Supprimer la communauté, passer en **SNMPv3** en lecture seule, limité à l’adresse du superviseur.

</details>

**2.** Pendant une attaque par balayage interne, un switch de cœur perd ses voisins OSPF. Le processeur est à 100 %. Quelle protection aurait limité l’impact ?

<details><summary>Voir le corrigé</summary>

**CoPP** : en limitant le trafic du balayage destiné au processeur (ICMP, ARP, paquets à TTL expiré…), le processeur garde de la capacité pour traiter les Hello OSPF, prioritaires. Il faut aussi bloquer la source du balayage (ACL, isolement du poste).

</details>
