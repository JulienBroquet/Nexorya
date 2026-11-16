---
titre: "Projet fil rouge — Le réseau de Lumen"
actif: pratique
chapeau: Lumen est une PME qui fabrique des luminaires. Elle grandit, et son réseau doit suivre. À chaque niveau, tu conçois l’étape suivante et tu produis les documents d’un vrai ingénieur réseau.
---

> [!NOTE] Comment l’utiliser
> Chaque étape correspond à un niveau. Lis les fiches du niveau, puis réalise l’étape : rédige les livrables (un document, un schéma, des configurations), construis-la dans un simulateur si tu peux, et compare avec les points de contrôle. Il n’y a pas une seule bonne réponse : ce qui compte, c’est de **justifier** tes choix.

## Étape 0 — Comprendre l’existant

*Après « Je débute ».*

Lumen compte 15 salariés dans un bureau. Il y a une box opérateur, un petit switch de 24 ports, une imprimante, un NAS de fichiers et le Wi-Fi de la box. Tout le monde est dans le même réseau `192.168.1.0/24`.

**Livrables** : un schéma de l’existant ; la liste des équipements avec leur rôle ; trois risques que tu repères.

<details><summary>Points de contrôle</summary>

Le schéma montre la box (routeur, Wi-Fi, DHCP, NAT), le switch, les postes, l’imprimante et le NAS. Risques typiques : les visiteurs utilisent le même Wi-Fi que les salariés et voient le NAS ; une seule box sans secours ; aucune sauvegarde de configuration ni documentation.

</details>

## Étape 1 — Un vrai réseau local

*Après le niveau 1.*

Lumen déménage dans un bâtiment de deux étages : 60 salariés, des téléphones IP, des caméras, un Wi-Fi invités. Il y aura un switch d’accès par étage et un switch central.

**Livrables** : la liste des VLAN (numéro, nom, usage) ; le schéma physique (switches, liens, câblage cuivre ou fibre) ; le choix de la racine STP ; les ports qui ont besoin de PoE et le budget PoE de chaque switch.

<details><summary>Points de contrôle</summary>

VLAN séparés au minimum pour : postes, voix, caméras, imprimantes, Wi-Fi salariés, Wi-Fi invités, administration. Liens montants doublés et agrégés en LACP ; racine STP sur le switch central (priorité forcée) ; PortFast et BPDU Guard sur les ports d’accès. Budget PoE calculé : téléphones (~7 W), bornes Wi-Fi (~15 à 30 W), caméras (~7 à 13 W), avec une marge.

</details>

## Étape 2 — Adresser et router

*Après le niveau 2.*

Lumen ouvre un entrepôt à 20 km, relié au siège par un lien opérateur. Le switch central devient un switch de niveau 3.

**Livrables** : le plan d’adressage IPv4 complet (un sous-réseau par VLAN et par site, de taille justifiée, avec de la marge) ; un plan IPv6 ; le choix du protocole de routage entre les deux sites ; la redondance de la passerelle au siège.

<details><summary>Points de contrôle</summary>

Une plage par site facile à résumer (par exemple `10.10.0.0/16` siège, `10.20.0.0/16` entrepôt), puis un /24 ou un /23 par VLAN selon les effectifs prévus à trois ans. IPv6 : un /64 par VLAN. OSPF en zone unique est un bon choix à cette taille. Passerelle redondante avec VRRP (ou HSRP) si deux switches de cœur.

</details>

## Étape 3 — Les services

*Après le niveau 3.*

**Livrables** : où placer DHCP et DNS (et comment l’entrepôt les joint) ; la configuration NTP ; la stratégie d’accès à Internet (NAT, proxy) ; la supervision (SNMP, Syslog) ; la téléphonie (QoS minimale sur le lien vers l’entrepôt).

<details><summary>Points de contrôle</summary>

DHCP central avec relais sur chaque passerelle (ou un DHCP local à l’entrepôt pour survivre à une coupure du lien). DNS interne pour les noms de l’entreprise, transfert vers des résolveurs externes. Tous les équipements en NTP sur une même source. Syslog et SNMPv3 vers un serveur de supervision. Voix marquée EF et prioritaire sur le lien inter-sites.

</details>

## Étape 4 — Sécuriser

*Après le niveau 4.*

Un audit pointe : Wi-Fi salariés en mot de passe partagé, administration des équipements en Telnet avec le compte « admin », aucun filtrage entre VLAN, télétravail via des outils grand public.

**Livrables** : la matrice de flux (qui a le droit de joindre quoi) ; le choix d’authentification du Wi-Fi et des ports filaires ; la politique d’accès d’administration ; la solution de télétravail ; trois mesures de durcissement prioritaires.

<details><summary>Points de contrôle</summary>

WPA-Entreprise (802.1X) avec RADIUS relié à l’annuaire, idéalement EAP-TLS ; caméras et imprimantes isolées et filtrées ; administration en SSH depuis un réseau d’administration, comptes nominatifs via AAA (TACACS+ ou RADIUS), MFA ; télétravail par VPN avec MFA ; durcissement : services inutiles coupés, ports inutilisés désactivés, DHCP snooping et DAI sur les VLAN utilisateurs.

</details>

## Étape 5 — Passer à l’échelle

*Après le niveau 5.*

Lumen rachète une entreprise à Lyon, ouvre trois boutiques, héberge son ERP dans un petit datacenter et migre la messagerie et la comptabilité dans le cloud.

**Livrables** : l’architecture WAN (MPLS, SD-WAN, Internet) justifiée par les coûts et les besoins ; l’intégration du réseau racheté (chevauchement d’adresses ?) ; le raccordement au cloud ; le tableau de bord de supervision d’un site ; un plan de changement pour la bascule d’un site ; ce que tu automatises en premier.

<details><summary>Points de contrôle</summary>

SD-WAN sur deux accès Internet par site (plus économique et plus souple pour les boutiques), éventuellement MPLS conservé pour le datacenter. Chevauchement d’adresses traité par renumérotation planifiée, ou temporairement par NAT/VRF. VPC dans une plage unique du plan d’adressage, raccordé par VPN IPsec ou lien dédié. Supervision : sondes vers l’ERP et le cloud, flux NetFlow, journaux centralisés. Plan de changement avec fenêtre, vérifications et retour arrière. Automatiser d’abord la sauvegarde des configurations et l’inventaire.

</details>

> [!TIP] Constituer un portfolio
> Rassemble tes livrables dans un dépôt Git : schémas, plan d’adressage, configurations, plans de changement. C’est une excellente pièce à montrer en entretien.
