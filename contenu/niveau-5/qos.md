---
titre: QoS
nom: Qualité de service
idee: Quand un lien est saturé, la QoS décide quels paquets passent en premier ; la voix et la vidéo passent devant les sauvegardes, et les applications importantes ont une part garantie.
osi: "2 et 3"
duree: [10, 22]
prerequis: [mesures, voip]
retenir:
  - "La QoS n’ajoute pas de débit — elle **répartit** la capacité quand il y a **congestion**."
  - "Les étapes — **classifier**, **marquer** (DSCP), **mettre en file**, **ordonnancer**, éventuellement **lisser** ou **limiter**."
  - "La voix va dans une **file prioritaire** (LLQ), limitée pour ne pas affamer les autres."
  - La QoS doit être **cohérente de bout en bout** — elle n’agit que là où elle est configurée.
---

## Le problème : la file d’attente unique

Sur un lien de 100 Mb/s vers une agence, tout va bien tant que le trafic reste sous 100 Mb/s. Quand la sauvegarde du soir démarre et réclame tout le lien, une **file d’attente** se forme dans le routeur. Les paquets de voix y attendent derrière des milliers de paquets de sauvegarde : la conversation devient hachée, alors que la voix ne représente que 1 % du trafic.

> [!IMPORTANT] L’idée en une phrase
> La QoS crée **plusieurs files d’attente** avec des règles de passage : la voix passe toujours en premier, les applications métier ont une part garantie, et les flux qui peuvent attendre attendent.

> [!TIP] L’analogie du péage
> Sans QoS, toutes les voitures font la queue au même guichet, y compris l’ambulance. Avec QoS, il y a une voie réservée aux véhicules prioritaires (limitée en nombre), des voies pour les abonnés, et une voie pour tout le monde.

## Les étapes

| Étape | Question | Exemple |
|---|---|---|
| **Classifier** | de quel type de trafic s’agit-il ? | voix (RTP), visio, ERP, Web, sauvegarde |
| **Marquer** | comment l’indiquer aux équipements suivants ? | champ **DSCP** de l’en-tête IP : 46 (EF) pour la voix |
| **Mettre en file et ordonnancer** | qui passe en premier ? | file prioritaire pour la voix, parts garanties pour les autres |
| **Lisser / limiter** | comment respecter un débit contractuel ? | lisser à 100 Mb/s sur un lien physique à 1 Gb/s |

```illustration
fichier: qos-files.svg
legende: "Les paquets sont classés selon leur marquage, rangés dans des files séparées, puis l’ordonnanceur sert toujours la file **voix** en premier, dans la limite de son plafond."
alt: "Paquets mélangés classés en trois files (voix prioritaire, métier, sauvegardes) avant le lien WAN ; en sortie, la voix passe en premier"
```

## Où la QoS est-elle utile ?

Partout où un lien peut être **saturé** : principalement les liens **WAN** (bien plus lents que le LAN), les liaisons montantes des switches d’accès, et les liens Wi-Fi. Sur un lien jamais chargé, elle ne fait rien… et ne coûte rien.

## Les mots à connaître

- **QoS** — *Quality of Service*, ensemble de mécanismes qui traitent différemment les flux selon leur importance.
- **Congestion** — Situation où plus de trafic arrive qu’un lien ne peut en écouler.
- **Classification** — Identification du type de trafic d’un paquet.
- **Marquage** — Inscription d’une priorité dans le paquet (DSCP) ou la trame (CoS).
- **LLQ** — *Low Latency Queuing*, file à priorité stricte pour la voix et la vidéo interactive.
- **Lissage** — Mise en attente du trafic pour respecter un débit maximal ; *shaping*.

## Teste-toi

**Un lien n’est jamais chargé à plus de 30 %. La QoS y améliore-t-elle la voix ?**

<details><summary>Voir le corrigé</summary>

**Non**, en principe : sans congestion, il n’y a pas de file d’attente, donc rien à prioriser. Attention toutefois aux **rafales** : une moyenne à 30 % peut cacher des pics à 100 % de quelques secondes, pendant lesquels la QoS est utile.

</details>

<!-- approfondir -->

## Un modèle de classes simple

| Classe | Exemples | DSCP | Traitement sur le WAN |
|---|---|---|---|
| Voix | RTP audio | **EF (46)** | file prioritaire stricte, ≤ 10–33 % du lien |
| Visioconférence | RTP vidéo interactive | AF41 (34) | part garantie importante |
| Signalisation | SIP, H.323 | CS3 (24) | petite part garantie |
| Applications métier | ERP, bureau à distance | AF21 (18) | part garantie |
| Défaut | navigation, e-mail | 0 (BE) | ce qui reste |
| Moins que le défaut | sauvegardes, mises à jour | CS1 (8) | petite part, passe après tout le monde |

## Configuration MQC (Cisco IOS)

```cisco
class-map match-any VOIX
 match dscp ef
class-map match-any VISIO
 match dscp af41
class-map match-any METIER
 match dscp af21
class-map match-any ARRIERE-PLAN
 match dscp cs1
!
policy-map WAN-SORTIE
 class VOIX
  priority percent 20                 ! file prioritaire (LLQ), plafonnée à 20 %
 class VISIO
  bandwidth remaining percent 30
 class METIER
  bandwidth remaining percent 30
 class ARRIERE-PLAN
  bandwidth remaining percent 5
 class class-default
  bandwidth remaining percent 35
  fair-queue
!
! Le lien physique est à 1 Gb/s mais le contrat est de 100 Mb/s : lisser d'abord
policy-map WAN-LISSAGE
 class class-default
  shape average 100000000
  service-policy WAN-SORTIE
!
interface GigabitEthernet0/0/0
 service-policy output WAN-LISSAGE
```

> [!WARNING]
> Sans **lissage** au débit du contrat, la congestion n’a pas lieu dans **ton** routeur (qui envoie à 1 Gb/s), mais chez l’opérateur, qui jette les paquets sans tenir compte de tes priorités. La QoS doit s’appliquer là où la file d’attente se forme réellement : on la **déplace** chez soi grâce au lissage.

## Vérifier qu’elle fonctionne

```cisco
R1# show policy-map interface GigabitEthernet0/0/0 output
  Class-map: VOIX (match-any)
    1832940 packets, 366588000 bytes
    5 minute offered rate 1792000 bps, drop rate 0000 bps
    Priority: 20% (20000 kbps), burst bytes 500000, b/w exceed drops: 0
  Class-map: ARRIERE-PLAN (match-any)
    5 minute offered rate 71540000 bps, drop rate 18320000 bps
```

Ici, la voix ne subit **aucun rejet** pendant que la sauvegarde (arrière-plan) en subit beaucoup : la politique fait exactement son travail.

## Faire confiance au marquage ?

Les téléphones marquent leur trafic en EF. Mais un PC pourrait marquer tout son trafic en EF pour passer devant les autres. On définit donc une **frontière de confiance** : on fait confiance au marquage des téléphones (détectés par CDP/LLDP), et l’on **remarque** (ou remet à zéro) celui des PC. Voir [DSCP](dscp.md).

## Exercices

**1.** Pendant les sauvegardes, la voix reste hachée malgré une politique QoS appliquée en sortie du routeur WAN. Le lien physique est à 1 Gb/s, le contrat opérateur à 50 Mb/s, et les compteurs de la politique ne montrent aucun rejet. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Le routeur envoie à 1 Gb/s : **aucune congestion** n’a lieu chez lui, donc ses files ne servent à rien. La congestion se produit chez l’**opérateur**, qui limite à 50 Mb/s sans tenir compte des priorités. Il faut un **lissage** à 50 Mb/s avec la politique de files à l’intérieur.

</details>

**2.** Pourquoi limite-t-on la file prioritaire à une fraction du lien, au lieu de lui laisser tout ce qu’elle demande ?

<details><summary>Voir le corrigé</summary>

Parce qu’une file à priorité **stricte** passe toujours avant les autres : si elle n’était pas plafonnée, un flux mal marqué ou une augmentation imprévue pourrait **affamer** toutes les autres classes. Le plafond protège le reste du trafic, et oblige à dimensionner la voix correctement.

</details>
