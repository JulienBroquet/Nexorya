---
titre: Wi-Fi d’entreprise
nom: Contrôleur, VLAN et itinérance
idee: En entreprise, des dizaines de bornes sont pilotées par un contrôleur ; chaque SSID est relié à un VLAN, et les appareils passent d’une borne à l’autre sans couper leurs appels grâce à l’itinérance rapide.
osi: "1 à 3"
duree: [9, 18]
cle: true
prerequis: [wifi, vlan]
retenir:
  - "Un **contrôleur** (physique ou dans le cloud) configure toutes les bornes, gère les canaux et les puissances."
  - "Chaque **SSID** correspond à un **VLAN** (employés, invités, objets connectés)."
  - "C’est le **client** qui décide de changer de borne ; **802.11k/v** l’aident à choisir, **802.11r** accélère le passage."
  - "Objectif de couverture pour la voix — **-67 dBm** minimum partout, avec recouvrement entre bornes."
---

## Le problème : 80 bornes, des centaines d’appareils qui bougent

Un bâtiment de bureaux compte 80 bornes Wi-Fi. Les configurer une à une est impossible. Et un employé en ligne sur son téléphone traverse trois étages : sa conversation ne doit pas couper chaque fois qu’il change de borne.

> [!IMPORTANT] L’idée en une phrase
> Un **contrôleur** pilote toutes les bornes comme un seul système, relie chaque nom de réseau (SSID) à un VLAN, et aide les appareils à passer d’une borne à l’autre en quelques millisecondes.

## L’architecture

```topologie
titre: Bornes pilotées par un contrôleur
WLC serveur 2,0 "Contrôleur Wi-Fi"
CO l3 2,1 "Cœur" "VLAN 10, 30, 50"
SW1 switch 1,2 "Switch étage 1"
SW2 switch 3,2 "Switch étage 2"
AP1 ap 0.5,3 "Borne 1"
AP2 ap 1.5,3 "Borne 2"
AP3 ap 3,3 "Borne 3"
TEL portable 1,4 "Téléphone en mouvement"
WLC -- CO
CO -- SW1
CO -- SW2
SW1 -- AP1
SW1 -- AP2
SW2 -- AP3
AP1 ~~ TEL
AP2 ~~ TEL "itinérance"
```

| SSID | VLAN | Sécurité | Accès |
|---|---|---|---|
| Entreprise | 10 | WPA2/WPA3-Entreprise (802.1X) | réseau interne selon le profil |
| Invités | 30 | portail ou WPA3-Personnel, isolation des clients | Internet seulement |
| Objets | 50 | WPA2-Personnel avec clé par appareil, ou 802.1X | serveurs nécessaires seulement |

## L’itinérance : qui décide ?

Ce n’est **pas** la borne qui décide de transférer un appareil, c’est **l’appareil lui-même**. Il reste souvent accroché à sa borne bien trop longtemps (« client collant »), même quand une autre est plus proche. Les normes suivantes l’aident :

- **802.11k** : la borne fournit la liste des bornes voisines, pour que l’appareil cherche vite.
- **802.11v** : la borne peut **suggérer** à l’appareil de partir vers une meilleure borne.
- **802.11r** (*Fast Transition*) : l’appareil se réauthentifie auprès de la nouvelle borne en quelques millisecondes, sans refaire toute la procédure 802.1X.

## Les mots à connaître

- **Contrôleur Wi-Fi** — Équipement ou service qui configure et supervise les bornes d’un réseau ; *WLC*.
- **Itinérance** — Passage d’un appareil d’une borne à une autre ; *roaming*.
- **802.11r** — Transition rapide entre bornes, qui évite de refaire l’authentification complète.
- **Client collant** — Appareil qui reste connecté à une borne lointaine au lieu de passer à une plus proche.

## Teste-toi

**Les appels Wi-Fi coupent quand on passe du 2ᵉ au 3ᵉ étage, mais pas à l’intérieur d’un étage. Quelles hypothèses ?**

<details><summary>Voir le corrigé</summary>

Une **zone sans couverture suffisante** dans l’escalier (pas de recouvrement entre bornes), ou un **changement de VLAN** entre les étages (le téléphone doit changer d’adresse IP, ce qui coupe l’appel). Le même SSID doit utiliser le même VLAN (ou un groupe de VLAN géré par le contrôleur) dans toute la zone d’itinérance.

</details>

<!-- approfondir -->

## Modes de déploiement

| Mode | Le trafic des clients passe… | Avantages |
|---|---|---|
| **Centralisé** (tunnel CAPWAP vers le contrôleur) | par le contrôleur | politique centrale, itinérance entre étages facile |
| **Local** (*FlexConnect*, commutation locale) | directement sur le switch de la borne | moins de trafic vers le contrôleur, adapté aux agences |
| **Géré dans le cloud** | localement, contrôle par Internet | déploiement rapide, multi-sites |

Les bornes découvrent leur contrôleur par l’option **DHCP 43**, par le DNS (`CISCO-CAPWAP-CONTROLLER.<domaine>`) ou par une configuration de démarrage.

## Ce que le contrôleur automatise

- **Gestion radio** : choix des canaux et des puissances, adaptation aux interférences (RRM chez Cisco).
- **Orientation des clients** : pousser les appareils bi-bande vers le 5 ou 6 GHz (*band steering*).
- **Équilibrage** entre bornes chargées.
- **Détection** des bornes pirates et des attaques radio.

## Diagnostic d’itinérance

```text
(WLC) > show client detail 3c:22:fb:1a:09:7e
Client State..................................... Associated
AP Name.......................................... AP-ETG3-02
Channel.......................................... 44
Radio Signal Strength Indicator.................. -71 dBm
Signal to Noise Ratio............................ 22 dB
Fast Transition (802.11r)........................ Enabled
Mobility Move Count.............................. 14
```

Un client à **-71 dBm** et 22 dB de SNR est en limite pour la voix : il aurait dû changer de borne. On vérifie la couverture (étude sur site), on active 802.11k/v/r si les terminaux les supportent, et l’on réduit éventuellement la puissance des bornes trop « attirantes ».

> [!WARNING]
> Certains terminaux anciens se connectent mal à un SSID où 802.11r est **obligatoire**. On utilise alors le mode **adaptatif** (FT activé pour les clients compatibles seulement) ou un SSID dédié aux appareils anciens.

## Exercices

**1.** Dans un entrepôt, des terminaux restent connectés à une borne lointaine à -80 dBm alors qu’une autre borne, à 10 mètres, offre -55 dBm. Que proposer ?

<details><summary>Voir le corrigé</summary>

Activer **802.11k et 802.11v** pour informer et inciter les clients à changer, régler un **seuil RSSI minimal** (au-delà duquel la borne refuse ou déconnecte poliment), réduire la puissance des bornes trop puissantes, et vérifier la configuration d’itinérance des terminaux (beaucoup de terminaux industriels ont un seuil réglable).

</details>

**2.** Pourquoi tunneliser le trafic des invités jusqu’au contrôleur placé en zone isolée (DMZ) ?

<details><summary>Voir le corrigé</summary>

Le trafic invité ne touche **jamais** les VLAN internes : il traverse les switches de l’entreprise dans un tunnel et n’en sort qu’en DMZ, d’où il ne peut aller que vers Internet. On n’a pas à étendre le VLAN invités sur tous les switches, et l’isolation est plus facile à garantir.

</details>
