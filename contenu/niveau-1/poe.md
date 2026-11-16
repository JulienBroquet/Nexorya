---
titre: PoE
nom: Power over Ethernet (IEEE 802.3af, at, bt)
idee: Le PoE fait passer le courant électrique dans le câble réseau ; un seul câble suffit pour alimenter et connecter un téléphone, une caméra ou une borne Wi-Fi.
osi: "1"
duree: [7, 14]
prerequis: [cablage]
retenir:
  - Le switch (**PSE**) alimente l’appareil (**PD**) par le câble Ethernet, après l’avoir **détecté** et **classé**.
  - Trois générations — **PoE** 15,4 W, **PoE+** 30 W, **PoE++** 60 à 90 W (puissances au port du switch).
  - Le switch a un **budget total** ; quand il est épuisé, les nouveaux appareils ne sont plus alimentés.
---

## Le problème : une prise électrique au plafond ?

Une borne Wi-Fi se pose au plafond, une caméra en haut d’un mur, un téléphone sur un bureau. Faire venir une prise électrique à chacun de ces endroits coûte cher et demande un électricien. Or un câble réseau y arrive déjà.

> [!IMPORTANT] L’idée en une phrase
> Le PoE fait passer **le courant électrique dans le câble réseau** : un seul câble apporte à la fois le réseau et l’alimentation.

## Comment ça marche, étape par étape

1. **Détection.** Avant d’envoyer du courant, le switch vérifie qu’un appareil compatible est branché, en mesurant une résistance caractéristique. Un PC ordinaire ne sera jamais alimenté : pas de risque de griller une carte réseau.
2. **Classement.** L’appareil annonce sa **classe**, c’est-à-dire la puissance dont il a besoin.
3. **Alimentation.** Le switch envoie le courant (environ 50 V continu) si son **budget** le permet.
4. **Surveillance.** Si l’appareil est débranché, le switch coupe immédiatement le courant.

```sequence
titre: Mise sous tension d’une caméra PoE
Switch (PSE) | Caméra (PD)
Switch (PSE) -> Caméra (PD) : détection : « es-tu un appareil PoE ? »
Caméra (PD) --> Switch (PSE) : signature valide
Switch (PSE) -> Caméra (PD) : classement : « de combien as-tu besoin ? »
Caméra (PD) --> Switch (PSE) : classe 4 : jusqu’à 30 W
note Switch (PSE) : budget restant suffisant ? oui : 30 W réservés
Switch (PSE) -> Caméra (PD) : alimentation 50 V
```

## Les générations

| Nom | Norme | Puissance au port du switch | Exemples d’appareils |
|---|---|---|---|
| PoE | 802.3af | 15,4 W | téléphone IP, petite caméra |
| PoE+ | 802.3at | 30 W | borne Wi-Fi, caméra motorisée |
| PoE++ | 802.3bt | 60 W ou 90 W | borne Wi-Fi 6E/7, écran, éclairage |

Une partie de la puissance se perd en chaleur dans le câble : l’appareil reçoit un peu moins (12,95 W pour 15,4 W envoyés).

## Exemple : la treizième caméra qui ne s’allume pas

Un switch PoE+ a un **budget total de 370 W**. Douze caméras de classe 4 sont branchées : le switch leur réserve 12 × 30 = 360 W. Il ne reste que 10 W. Quand on branche une treizième caméra identique, son lien réseau s’allume, mais **elle ne démarre pas** : le switch refuse de l’alimenter.

La commande `show power inline` le montre immédiatement. Solutions : un switch au budget plus élevé, une deuxième alimentation, ou un injecteur PoE pour cette caméra.

## Les mots à connaître

- **PoE** — *Power over Ethernet*, alimentation électrique d’un appareil par son câble réseau.
- **PSE** — *Power Sourcing Equipment*, l’équipement qui fournit le courant (le switch ou un injecteur).
- **PD** — *Powered Device*, l’appareil alimenté (téléphone, caméra, borne Wi-Fi).
- **Budget PoE** — Puissance totale qu’un switch peut distribuer sur l’ensemble de ses ports.
- **Classe PoE** — Niveau de puissance annoncé par l’appareil alimenté.

## Teste-toi

**1.** Un PC portable branché sur un port PoE risque-t-il d’être endommagé ?

<details><summary>Voir le corrigé</summary>

**Non.** Le switch n’envoie du courant qu’après avoir **détecté** la signature d’un appareil PoE. Un PC n’a pas cette signature : il reçoit uniquement le réseau.

</details>

**2.** Une borne Wi-Fi exige du PoE+ et son switch ne fournit que du PoE (802.3af). Que risque-t-il de se passer ?

<details><summary>Voir le corrigé</summary>

La borne ne reçoit que 15,4 W au lieu des 30 W prévus. Selon le modèle, elle **ne démarre pas** ou démarre en **mode dégradé** (certaines radios ou certains ports désactivés).

</details>

<!-- approfondir -->

## Les classes et les paires utilisées

| Classe | Puissance au PSE | Puissance au PD | Norme | Paires alimentées |
|---|---|---|---|---|
| 0 | 15,4 W | 12,95 W | af (classe par défaut) | 2 |
| 1 | 4 W | 3,84 W | af | 2 |
| 2 | 7 W | 6,49 W | af | 2 |
| 3 | 15,4 W | 12,95 W | af | 2 |
| 4 | 30 W | 25,5 W | at | 2 |
| 5–6 | 45 / 60 W | 40 / 51 W | bt type 3 | 4 |
| 7–8 | 75 / 90 W | 62 / 71,3 W | bt type 4 | 4 |

En 802.3af/at, le courant passe sur deux paires (mode A : paires de données ; mode B : paires libres en 100BASE-TX). En 802.3bt, il passe sur **les quatre paires** pour limiter l’échauffement.

**LLDP-MED** permet à l’appareil de renégocier finement sa puissance après le démarrage, au lieu de réserver le maximum de sa classe. C’est ainsi qu’un switch peut alimenter plus d’appareils que ne le laisserait un calcul « classe maximale × nombre de ports ».

## Configurer et vérifier (Cisco IOS)

```cisco
SW1# show power inline
Module   Available     Used     Remaining
          (Watts)     (Watts)    (Watts)
------   ---------   --------   ---------
1           370.0      360.0        10.0
Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Gi1/0/1   auto   on         30.0    IP Camera           4     30.0
Gi1/0/13  auto   off        0.0     n/a                 n/a   30.0
```

`Oper off` sur Gi1/0/13 alors que `Admin auto` : le port pourrait alimenter, mais le budget restant (10 W) est insuffisant. Le journal contient alors un message `%ILPOWER-5-ILPOWER_POWER_DENY`.

```cisco
! Désactiver le PoE sur un port (par exemple vers un équipement tiers sensible)
interface GigabitEthernet1/0/20
 power inline never
! Limiter la puissance maximale d'un port à 15,4 W
interface GigabitEthernet1/0/21
 power inline auto max 15400
! Donner la priorité à un port en cas de manque de budget (plateformes compatibles)
interface GigabitEthernet1/0/1
 power inline port priority high
```

> [!CAUTION]
> Le budget PoE dépend des **alimentations** installées. Si un switch à deux alimentations en perd une, son budget peut être divisé par deux : des appareils s’éteignent. Prévoir les priorités par port **avant** l’incident, en commençant par les équipements de sécurité (caméras, contrôle d’accès).

## Dimensionner un switch PoE

1. Lister les appareils et leur classe (ou leur consommation réelle annoncée par LLDP).
2. Additionner, puis ajouter **20 à 30 % de marge** pour les évolutions.
3. Vérifier le budget **par alimentation** et en cas de panne d’une alimentation.
4. Tenir compte de la chaleur : 90 W par port sur des faisceaux de câbles serrés fait monter la température ; les normes de câblage recommandent des précautions au-delà de 60 W.

## Exercices

**1.** Un switch de 48 ports a un budget de 740 W. On veut y brancher 24 bornes Wi-Fi de classe 4 et 20 téléphones de classe 2. Le budget suffit-il au pire cas ?

<details><summary>Voir le corrigé</summary>

Bornes : 24 × 30 = 720 W. Téléphones : 20 × 7 = 140 W. Total : **860 W**, supérieur à 740 W. Au pire cas (réservation par classe), **non**. Avec LLDP-MED, la consommation réelle peut être plus faible, mais il est prudent de prévoir une alimentation supplémentaire ou de répartir les bornes sur deux switches.

</details>

**2.** Après une coupure d’une des deux alimentations d’un switch, les caméras d’un parking s’éteignent mais pas les téléphones. Pourquoi, et que configurer ?

<details><summary>Voir le corrigé</summary>

Le budget a diminué et le switch a coupé des ports selon son ordre de priorité par défaut (souvent les numéros de port les plus élevés en premier). Il faut configurer une **priorité haute** sur les ports des équipements critiques (`power inline port priority high`) et, idéalement, dimensionner le budget pour qu’une seule alimentation suffise aux appareils prioritaires.

</details>
