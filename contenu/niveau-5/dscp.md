---
titre: DSCP
nom: Differentiated Services Code Point
idee: Le DSCP est une étiquette de 6 bits dans l’en-tête IP qui indique la classe de service d’un paquet ; chaque équipement sur le chemin la lit pour savoir comment le traiter.
osi: "3"
duree: [6, 12]
prerequis: [qos]
retenir:
  - "Valeurs à connaître — **EF (46)** voix ; **AF41 (34)** visio ; **CS3 (24)** signalisation ; **AF21 (18)** métier ; **0** défaut ; **CS1 (8)** arrière-plan."
  - "On marque **au plus près de la source**, et l’on définit une **frontière de confiance**."
  - "Au niveau 2, l’équivalent est le **CoS** (3 bits de l’étiquette 802.1Q)."
  - Le DSCP n’est respecté que par les équipements **configurés pour** — sur Internet, il est souvent ignoré ou effacé.
---

## Le problème

Le routeur du WAN doit savoir quels paquets sont de la voix. Il pourrait analyser chaque paquet en détail, mais c’est coûteux, et chaque équipement sur le chemin devrait refaire ce travail. Il est plus simple de **coller une étiquette** sur le paquet une fois pour toutes.

> [!IMPORTANT] L’idée en une phrase
> Le DSCP est une étiquette de priorité inscrite dans chaque paquet IP : on la pose une fois à l’entrée du réseau, et tous les équipements suivants s’en servent pour trier.

## Où se trouve-t-il ?

Dans l’octet **Traffic Class** (IPv6) ou **ToS** (IPv4) de l’en-tête IP : les 6 premiers bits sont le **DSCP**, les 2 derniers servent à la notification de congestion (ECN).

## Les valeurs courantes

| Nom | Valeur | Usage habituel |
|---|---|---|
| **EF** | 46 | voix |
| **AF41** | 34 | visioconférence |
| **CS3** | 24 | signalisation (SIP) |
| **AF21** | 18 | applications métier |
| **CS6** | 48 | protocoles de routage (marqués par les routeurs eux-mêmes) |
| **0 (BE)** | 0 | tout le reste |
| **CS1** | 8 | arrière-plan (sauvegardes) |

## Les mots à connaître

- **DSCP** — Champ de 6 bits de l’en-tête IP qui indique la classe de service.
- **EF** — *Expedited Forwarding*, valeur 46, réservée à la voix.
- **AF** — *Assured Forwarding*, familles de classes avec une priorité de rejet (AF11 à AF43).
- **CoS** — *Class of Service*, priorité sur 3 bits dans l’étiquette 802.1Q, au niveau 2.
- **Frontière de confiance** — Point du réseau à partir duquel on fait confiance au marquage reçu.

## Teste-toi

**Un utilisateur configure son PC pour marquer tout son trafic en EF. Que doit faire le réseau ?**

<details><summary>Voir le corrigé</summary>

Ne **pas faire confiance** au marquage venant d’un PC : sur le port d’accès, le switch **remarque** ce trafic (en 0, ou selon une classification qu’il réalise lui-même). On ne fait confiance qu’aux équipements maîtrisés, comme les téléphones IP.

</details>

<!-- approfondir -->

## Lire les AF

`AFxy` : **x** = classe (1 à 4, plus elle est élevée, plus la classe est importante), **y** = priorité de rejet (1 à 3, plus elle est élevée, plus le paquet est jeté tôt en cas de congestion). Valeur décimale = 8x + 2y. Exemple : AF41 = 32 + 2 = 34.

## Marquer et faire confiance (Cisco IOS-XE)

```cisco
! Remarquer le trafic d'un PC selon des critères
class-map match-any ERP
 match access-group name ERP-TRAFIC
policy-map ACCES-ENTREE
 class ERP
  set dscp af21
 class class-default
  set dscp default
!
interface GigabitEthernet1/0/5
 trust device cisco-phone
 service-policy input ACCES-ENTREE
```

## Vérifier le marquage

Dans Wireshark, la colonne **DSCP** (champ `ip.dsfield.dscp`) montre la valeur de chaque paquet. Filtrer `ip.dsfield.dscp == 46` isole la voix. En capturant à deux endroits du chemin, on voit si un équipement **efface** le marquage (souvent un opérateur ou un pare-feu).

## Exercice

**Les paquets de voix partent du téléphone marqués EF, mais arrivent au site distant marqués 0. La QoS du site distant ne les reconnaît plus. Que vérifier ?**

<details><summary>Voir le corrigé</summary>

Un équipement sur le chemin **remarque** ou efface le DSCP : un switch d’accès qui ne fait pas confiance au téléphone, une politique de remarquage sur le routeur WAN, un pare-feu, ou l’opérateur (sur Internet, le DSCP est souvent remis à zéro ; sur un VPN MPLS, il doit correspondre aux classes du contrat). Capturer à chaque étape pour trouver l’endroit.

</details>
