---
titre: SD-WAN
nom: Le WAN piloté par logiciel
idee: Le SD-WAN combine plusieurs accès (fibre, MPLS, 4G) dans un même réseau chiffré, piloté depuis une console centrale, et envoie chaque application sur le lien le plus adapté à cet instant.
osi: "3 à 7"
duree: [8, 16]
prerequis: [wan, ipsec, qos]
retenir:
  - "Le SD-WAN mesure en continu la **qualité** de chaque lien (latence, gigue, pertes)."
  - "Il oriente chaque **application** selon une politique — la voix sur le lien le plus stable, les sauvegardes sur le moins cher."
  - "Configuration **centralisée** — un nouveau site se met en service presque tout seul (*zero touch*)."
  - "Des tunnels **chiffrés** entre sites, au-dessus de n’importe quel transport."
---

## Le problème

Une agence a une fibre Internet et une 4G. Avec un routeur classique, la 4G ne sert que si la fibre tombe complètement. Mais quand la fibre est **dégradée** (pertes, latence), les appels sont hachés alors que la 4G est parfaite. Et configurer 200 agences à la main, avec des tunnels IPsec et des règles de routage, prend des semaines.

> [!IMPORTANT] L’idée en une phrase
> Le SD-WAN mesure en permanence la qualité de tous les liens d’un site et choisit, pour chaque application, le meilleur lien du moment, le tout configuré depuis une console centrale.

## Comment ça marche

```topologie
titre: Une agence SD-WAN à deux accès
AG routeur 0,1 "Équipement SD-WAN agence"
FIB nuage 1.5,0 "Internet fibre"
LTE nuage 1.5,2 "4G"
DC routeur 3,1 "Équipement SD-WAN siège"
CTRL serveur 3,2.2 "Contrôleur" "politiques centrales"
AG ++ FIB "voix : latence 18 ms, 0 % perte"
AG -- LTE "secours, pertes 0,5 %"
FIB .. DC "tunnel"
LTE .. DC "tunnel"
CTRL .. AG
CTRL .. DC
```

1. Les équipements de chaque site établissent des **tunnels chiffrés** sur tous leurs liens.
2. Ils envoient des **sondes** dans chaque tunnel et mesurent latence, gigue et pertes.
3. Le **contrôleur** distribue les politiques : « la voix doit avoir moins de 150 ms et moins de 1 % de pertes », « les sauvegardes passent par le lien le moins cher ».
4. Chaque flux est **classé** par application et envoyé sur le lien qui respecte sa politique. Si la fibre se dégrade, les appels basculent sur la 4G en quelques secondes, sans couper la sauvegarde.

## Les mots à connaître

- **SD-WAN** — *Software-Defined WAN*, réseau étendu piloté par une couche logicielle centrale.
- **Overlay** — Réseau logique (tunnels) construit au-dessus des liens de transport.
- **Underlay / transport** — Les liens physiques ou d’opérateur utilisés par l’overlay (fibre, MPLS, 4G).
- **Zero touch provisioning** — Mise en service automatique d’un équipement dès son branchement.
- **Routage par application** — Choix du lien en fonction de l’application et de la qualité mesurée.

## Teste-toi

**Quelle différence avec une route de secours classique (route flottante ou IP SLA) ?**

<details><summary>Voir le corrigé</summary>

Une route de secours ne bascule qu’en cas de **panne** (ou d’échec d’une sonde), et pour **tout** le trafic. Le SD-WAN réagit à une **dégradation** de la qualité et décide **application par application** : la voix peut basculer pendant que les autres flux restent sur la fibre.

</details>

<!-- approfondir -->

## Les composants

| Composant | Rôle |
|---|---|
| **Équipement de bordure** (edge) | dans chaque site : tunnels, mesures, classification, application des politiques |
| **Contrôleur** | distribue les routes, les clés et les politiques aux équipements |
| **Orchestrateur / console** | interface d’administration, modèles de configuration, supervision |
| **Passerelles cloud** | points de présence pour accéder efficacement aux applications SaaS et au cloud |

## Une politique type

| Classe d’application | Exigence | Lien préféré | Repli |
|---|---|---|---|
| Voix, visioconférence | latence < 150 ms, gigue < 30 ms, pertes < 1 % | le meilleur lien mesuré | tout lien conforme |
| Applications métier | latence < 100 ms | MPLS ou fibre | 4G |
| Navigation Web, SaaS | — | sortie Internet locale (avec sécurité cloud) | — |
| Sauvegardes, mises à jour | — | lien le moins cher | jamais la 4G |

## SD-WAN et sécurité : SASE

Avec la sortie Internet **locale** dans chaque agence, le filtrage ne peut plus se faire uniquement au siège. On associe donc le SD-WAN à des services de sécurité dans le cloud (proxy, CASB, ZTNA, pare-feu) : c’est l’approche **SASE** (*Secure Access Service Edge*).

## Points de vigilance

- La **QoS sur Internet** n’existe que dans votre propre équipement : le SD-WAN choisit le meilleur lien, mais ne garantit rien chez l’opérateur.
- Les tunnels ajoutent un en-tête : surveiller la **MTU**.
- La **visibilité** dépend de la classification des applications, qui doit être tenue à jour.

## Exercice

**Une agence perd 3 % des paquets sur sa fibre depuis une heure, sans coupure. Que fait un SD-WAN correctement configuré pour les appels en cours et pour la sauvegarde ?**

<details><summary>Voir le corrigé</summary>

Les sondes mesurent 3 % de pertes : la fibre ne respecte plus la politique de la **voix** (< 1 %). Les nouveaux appels, et souvent les appels en cours, sont envoyés sur le **lien conforme** (la 4G, par exemple). La **sauvegarde**, qui tolère les pertes et ne doit jamais passer par la 4G, reste sur la fibre.

</details>
