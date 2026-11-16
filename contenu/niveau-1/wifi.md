---
titre: Le Wi-Fi
nom: Ondes, SSID et canaux (IEEE 802.11)
idee: Le Wi-Fi remplace le câble par des ondes radio partagées ; une seule borne parle à la fois sur un canal, donc le débit réel dépend du nombre d’appareils, de la distance et des voisins.
osi: "1 et 2"
duree: [10, 20]
cle: true
retenir:
  - Le **SSID** est le nom du réseau ; une borne peut en diffuser plusieurs, souvent un par VLAN.
  - Les ondes sont **partagées** — sur un canal, un seul appareil émet à la fois, d’où un débit réel bien inférieur au débit annoncé.
  - "**2,4 GHz** porte loin mais n’offre que **3 canaux** indépendants (1, 6, 11) ; **5 et 6 GHz** offrent beaucoup plus de canaux, mais portent moins loin."
  - La sécurité moderne repose sur **WPA2 ou WPA3**, et sur **802.1X** en entreprise.
---

## Le problème : brancher ce qui ne peut pas l’être

Un téléphone, un ordinateur portable, un lecteur de codes-barres dans un entrepôt : on ne peut pas les relier par câble. Le Wi-Fi transporte les trames **par ondes radio**, entre l’appareil et une **borne** (point d’accès) elle-même reliée au réseau filaire.

> [!IMPORTANT] L’idée en une phrase
> Le Wi-Fi est un câble invisible **partagé** : tous les appareils d’un même canal se partagent l’air, et un seul parle à la fois.

## Les éléments

- **Point d’accès** (AP, borne) : relié au switch par un câble, il émet et reçoit les ondes.
- **SSID** : le nom du réseau affiché sur les appareils (« Entreprise », « Invités »). Une même borne peut diffuser plusieurs SSID, chacun relié à un VLAN différent.
- **Canal** : une portion de fréquence. Deux bornes voisines sur le même canal se gênent, comme deux conversations dans la même pièce.
- **Bandes de fréquence** : 2,4 GHz, 5 GHz et 6 GHz.

## Pourquoi le Wi-Fi est plus lent qu’annoncé

Une borne « Wi-Fi 6 à 2,4 Gb/s » ne donnera jamais 2,4 Gb/s à un téléphone. Plusieurs raisons :

1. **L’air est partagé.** Tous les appareils connectés à la borne, et toutes les bornes voisines sur le même canal, se partagent le temps de parole.
2. **On ne parle pas en même temps qu’on écoute.** Contrairement à un câble full duplex, le Wi-Fi est à l’alternat.
3. **La distance et les murs** affaiblissent le signal ; l’appareil passe alors à une vitesse plus basse, plus robuste.
4. **Les échanges de contrôle** (accusés de réception, attente avant d’émettre) consomment une bonne part du temps.

> [!TIP] L’analogie de la salle de réunion
> Le câble, c’est un téléphone privé entre deux personnes. Le Wi-Fi, c’est une salle de réunion : chacun attend que la salle soit silencieuse pour parler. Plus il y a de monde, plus chacun attend. Et si la salle d’à côté (la borne voisine) a les portes ouvertes sur le même canal, on s’entend mutuellement.

## 2,4 GHz, 5 GHz, 6 GHz

| Bande | Portée | Canaux indépendants | Remarque |
|---|---|---|---|
| **2,4 GHz** | la meilleure, traverse mieux les murs | **3** seulement (1, 6, 11) | très encombrée : micro-ondes, Bluetooth, voisins |
| **5 GHz** | moyenne | une vingtaine (selon les pays) | le choix habituel en entreprise |
| **6 GHz** (Wi-Fi 6E et 7) | plus courte | très nombreux | peu encombrée, réservée aux appareils récents |

```illustration
fichier: wifi-canaux-24ghz.svg
legende: "Chaque émission occupe environ 20 MHz alors que les canaux ne sont espacés que de 5 MHz : deux bornes voisines sur les canaux 3 et 5 se gênent. Seuls **1, 6 et 11** ne se recouvrent pas."
alt: "Treize canaux Wi-Fi 2,4 GHz représentés par des arcs qui se chevauchent ; les canaux 1, 6 et 11 sont mis en évidence et ne se recouvrent pas"
```

## Exemple : la salle de formation saturée

Une salle de formation de 40 personnes est couverte par une seule borne en 2,4 GHz, sur le canal 3. Les sessions vidéo saccadent. Le diagnostic montre que le canal 3 chevauche les canaux 1 et 6 utilisés par les bornes voisines, et que 40 appareils se partagent une seule borne. Solution : passer les appareils en **5 GHz**, utiliser des canaux **qui ne se chevauchent pas** (1, 6, 11 en 2,4 GHz), et ajouter une deuxième borne avec une puissance réduite.

## Les mots à connaître

- **Wi-Fi** — Nom commercial des réseaux locaux sans fil de la famille IEEE 802.11.
- **Point d’accès** — Borne reliée au réseau filaire qui diffuse le réseau sans fil ; *access point*, AP.
- **SSID** — *Service Set Identifier*, nom du réseau Wi-Fi.
- **Canal** — Plage de fréquences utilisée par une borne ; deux bornes proches doivent utiliser des canaux qui ne se chevauchent pas.
- **WPA2 / WPA3** — Protocoles de sécurité qui chiffrent le Wi-Fi et contrôlent l’accès.

## Teste-toi

**1.** Deux bornes voisines en 2,4 GHz utilisent les canaux 3 et 4. Bonne idée ?

<details><summary>Voir le corrigé</summary>

**Non.** En 2,4 GHz, les canaux se chevauchent fortement : 3 et 4 se perturbent mutuellement. Il faut utiliser des canaux séparés, **1, 6 et 11**.

</details>

**2.** Un ordinateur affiche « 866 Mb/s » de vitesse de connexion Wi-Fi, mais un téléchargement plafonne à 300 Mb/s. Est-ce anormal ?

<details><summary>Voir le corrigé</summary>

**Non.** La vitesse affichée est le **débit physique** sur les ondes. Le débit utile est souvent la moitié, voire moins, à cause du partage de l’air, de l’alternat et des échanges de contrôle.

</details>

<!-- approfondir -->

## Les générations

| Nom commercial | Norme | Bandes | Apports principaux |
|---|---|---|---|
| Wi-Fi 4 | 802.11n | 2,4 / 5 GHz | MIMO (plusieurs antennes), canaux de 40 MHz |
| Wi-Fi 5 | 802.11ac | 5 GHz | canaux de 80/160 MHz, MU-MIMO descendant |
| Wi-Fi 6 / 6E | 802.11ax | 2,4 / 5 / 6 GHz (6E) | **OFDMA** (plusieurs clients par transmission), BSS coloring, Target Wake Time |
| Wi-Fi 7 | 802.11be | 2,4 / 5 / 6 GHz | canaux de 320 MHz, **MLO** (plusieurs bandes à la fois) |

## Comment un appareil rejoint un réseau

```sequence
titre: Connexion d’un client à un réseau WPA2-Personnel
Client | Point d’accès
Point d’accès -> Client : beacon (SSID, sécurité, débits), environ 10 fois par seconde
Client -> Point d’accès : probe request (recherche active)
Point d’accès --> Client : probe response
Client -> Point d’accès : authentication (ouverte, héritage historique)
Point d’accès --> Client : authentication OK
Client -> Point d’accès : association request
Point d’accès --> Client : association response (AID)
== Poignée de main à 4 messages (WPA2/WPA3) ==
Point d’accès -> Client : message 1 : nonce de l’AP
Client -> Point d’accès : message 2 : nonce du client + preuve de connaissance de la clé
Point d’accès -> Client : message 3 : clé de groupe chiffrée
Client -> Point d’accès : message 4 : confirmation, le trafic chiffré commence
```

En **WPA2-Personnel**, la clé dérive d’un mot de passe partagé (PSK). En **WPA2/WPA3-Entreprise**, chaque utilisateur s’authentifie avec 802.1X auprès d’un serveur RADIUS, avant la poignée de main : voir [WPA Entreprise](../niveau-4/wpa-entreprise.md). **WPA3-Personnel** remplace le PSK par SAE, résistant aux attaques par dictionnaire hors ligne.

## L’accès au médium : CSMA/CA

Comme les appareils ne peuvent pas détecter une collision pendant qu’ils émettent, le Wi-Fi les **évite** :

1. l’appareil écoute ; si le canal est libre pendant un délai fixe (DIFS), il attend encore un délai **aléatoire** (*backoff*) ;
2. il émet la trame ;
3. le destinataire renvoie un **accusé de réception** (ACK). Sans ACK, l’émetteur suppose une collision et recommence avec un délai aléatoire plus long.

Chaque trame est donc suivie d’un ACK : c’est l’une des raisons du rendement limité.

## Débit physique : ce qui le détermine

Le débit annoncé dépend du **MCS** (modulation et taux de codage), de la **largeur de canal** et du nombre de **flux spatiaux** :

| Paramètre | Effet | Contrepartie |
|---|---|---|
| Modulation plus dense (256-QAM, 1024-QAM, 4096-QAM) | plus de bits par symbole | exige un excellent signal (proche de la borne) |
| Canal plus large (40, 80, 160, 320 MHz) | débit multiplié | moins de canaux disponibles, plus de risque d’interférence |
| Plus de flux spatiaux (MIMO) | débit multiplié | il faut autant d’antennes côté client (souvent 2) |

En entreprise dense, on choisit souvent des **canaux de 20 ou 40 MHz** en 5 GHz : chaque borne a un peu moins de débit, mais on peut placer plus de bornes sans qu’elles se gênent. La capacité totale est meilleure.

## Mesurer la qualité du signal

- **RSSI** : puissance reçue, en dBm (valeurs négatives). -50 dBm est excellent ; **-67 dBm** est le seuil courant visé pour la voix et la vidéo ; en dessous de -75 dBm, la connexion devient médiocre.
- **SNR** : écart entre le signal et le bruit, en dB. On vise au moins 25 dB pour des débits élevés.

```powershell
C:\> netsh wlan show interfaces
    SSID                   : Entreprise
    BSSID                  : 70:7d:b9:4a:12:3f
    Type de radio          : 802.11ax
    Canal                  : 44
    Vitesse de réception (Mbits/s) : 573.5
    Signal                 : 82%
```

```bash
$ iw dev wlan0 link
Connected to 70:7d:b9:4a:12:3f (on wlan0)
        SSID: Entreprise
        freq: 5220
        signal: -58 dBm
        rx bitrate: 573.5 MBit/s 80MHz HE-MCS 11 HE-NSS 2
```

## Concevoir une couverture d’entreprise

1. **Étude de couverture** (*site survey*) avec un logiciel de prédiction, puis des mesures sur place.
2. Viser **-67 dBm** partout où la voix et la vidéo sont utilisées, avec un recouvrement suffisant entre bornes pour l’itinérance.
3. Préférer **plus de bornes à puissance modérée** plutôt que peu de bornes à pleine puissance : les clients, eux, émettent faiblement, et une borne trop puissante attire des clients qu’elle n’entend pas bien.
4. Plan de canaux sans recouvrement ; en 2,4 GHz, désactiver une partie des radios si les bornes sont denses.
5. Un SSID par usage (employés, invités, IoT), relié à un VLAN, en limitant le nombre de SSID (chacun ajoute des *beacons* qui consomment du temps d’antenne).

La gestion centralisée (contrôleur), l’itinérance rapide et les SSID d’entreprise sont détaillés dans [Wi-Fi d’entreprise](../niveau-3/wifi-entreprise.md).

## Exercices

**1.** Un entrepôt est couvert par quatre bornes en 2,4 GHz, toutes réglées sur le canal 6 à pleine puissance. Les scanners de codes-barres se déconnectent souvent. Que proposes-tu ?

<details><summary>Voir le corrigé</summary>

Les quatre bornes se perturbent : un seul canal pour tout l’entrepôt. Répartir les bornes sur **1, 6 et 11**, **réduire la puissance** pour limiter les chevauchements, et vérifier la couverture (-67 dBm) aux points d’usage. Si les scanners le supportent, ajouter le 5 GHz.

</details>

**2.** Pourquoi un client proche de la borne obtient-il un bien meilleur débit qu’un client au fond du couloir, sur le même réseau ?

<details><summary>Voir le corrigé</summary>

Proche de la borne, le signal est fort : le client utilise un **MCS élevé** (modulation dense). Loin, il redescend à un MCS bas, plus robuste mais plus lent. De plus, comme le temps d’antenne est partagé, un client lent occupe longtemps le canal pour transmettre peu de données, ce qui ralentit **tout le monde**.

</details>

**3.** Calcule le nombre de canaux de 80 MHz disponibles si la bande 5 GHz offre 500 MHz utilisables, et explique pourquoi on choisit parfois 40 MHz.

<details><summary>Voir le corrigé</summary>

500 / 80 ≈ **6 canaux** de 80 MHz, contre 12 de 40 MHz ou 25 de 20 MHz. Dans un bâtiment dense, 6 canaux ne suffisent pas pour éviter que des bornes voisines partagent le même canal. Des canaux plus étroits donnent moins de débit par borne, mais **plus de bornes indépendantes**, donc une meilleure capacité globale.

</details>
