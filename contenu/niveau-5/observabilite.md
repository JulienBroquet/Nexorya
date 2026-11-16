---
titre: Observabilité
nom: Métriques, journaux, flux et traces
idee: L’observabilité réunit toutes les sources d’information sur le réseau — mesures, journaux, flux, captures, tests synthétiques — pour comprendre vite ce qui se passe, et le prouver.
osi: "transversal"
duree: [8, 16]
cle: true
prerequis: [snmp, syslog, netflow]
retenir:
  - "Quatre sources complémentaires — **métriques** (combien), **journaux** (quoi), **flux** (qui avec qui), **captures** (le détail)."
  - "La **corrélation dans le temps** est la clé — d’où l’importance de NTP et d’un stockage central."
  - "Les **tests synthétiques** (sondes) mesurent l’expérience des utilisateurs avant qu’ils se plaignent."
  - "La **télémétrie** en flux continu (streaming) remplace progressivement l’interrogation SNMP."
---

## Le problème : « le réseau est lent » à 9 h 12

Un incident survient. Les utilisateurs disent « le réseau est lent ». La supervision montre un lien chargé, les journaux une interface qui a oscillé, l’équipe applicative affirme que tout va bien chez elle. Sans une vue **réunie et datée** de tous ces signaux, chacun défend sa version et l’incident s’éternise.

> [!IMPORTANT] L’idée en une phrase
> L’observabilité, c’est pouvoir répondre à n’importe quelle question sur le réseau en croisant, sur une même ligne de temps, les mesures, les événements, les flux et, si besoin, les paquets.

## Les sources et leurs questions

| Source | Répond à… | Outils |
|---|---|---|
| **Métriques** | combien ? (débit, erreurs, CPU, latence) | SNMP, télémétrie, Prometheus |
| **Journaux** | que s’est-il passé ? (interface down, voisin perdu, configuration modifiée) | Syslog, SIEM |
| **Flux** | qui parle à qui, combien ? | NetFlow, IPFIX, sFlow |
| **Captures** | que contiennent exactement les échanges ? | SPAN, TAP, Wireshark |
| **Tests synthétiques** | l’utilisateur obtient-il un bon service ? | IP SLA, sondes HTTP/DNS, ThousandEyes… |

## La méthode d’enquête

1. **Délimiter** : depuis quand, pour qui, pour quoi ? (une application, un site, tout le monde)
2. **Métriques** : quelque chose a-t-il changé à ce moment ? (charge, erreurs, latence des sondes)
3. **Journaux** : quels événements à la même minute ? (oscillation, changement de configuration, bascule)
4. **Flux** : quel trafic a augmenté ou est apparu ?
5. **Capture** ciblée si nécessaire, pour le détail d’un échange.
6. **Conclure** avec des preuves datées, puis corriger.

## Les mots à connaître

- **Observabilité** — Capacité à comprendre l’état d’un système à partir des signaux qu’il produit.
- **Métrique** — Valeur numérique mesurée dans le temps.
- **Test synthétique** — Transaction simulée exécutée régulièrement pour mesurer le service rendu.
- **Télémétrie en streaming** — Envoi continu, à l’initiative de l’équipement, de ses mesures vers un collecteur.

## Teste-toi

**Pourquoi des équipements dont les horloges ne sont pas synchronisées rendent-ils l’enquête presque impossible ?**

<details><summary>Voir le corrigé</summary>

Parce que toute la méthode repose sur la **corrélation dans le temps** : savoir que l’oscillation de l’interface, la hausse de latence et l’apparition d’un flux ont eu lieu **à la même minute**. Avec des horloges décalées, on ne peut plus ordonner les événements. NTP est un prérequis.

</details>

<!-- approfondir -->

## Télémétrie en streaming

Avec SNMP, le superviseur **interroge** toutes les 5 minutes : les pics courts sont invisibles, et l’interrogation charge les équipements. Avec la **télémétrie**, l’équipement **pousse** ses mesures (toutes les quelques secondes, ou à chaque changement) vers un collecteur, dans un format structuré (gNMI, NETCONF/YANG, gRPC).

```text
! Exemple Cisco IOS-XE : pousser les compteurs d'interfaces toutes les 10 s
telemetry ietf subscription 101
 encoding encode-kvgpb
 filter xpath /interfaces-ois:interfaces-state/interface/statistics
 source-address 10.99.0.21
 stream yang-push
 update-policy periodic 1000
 receiver ip address 10.99.0.95 57500 protocol grpc-tcp
```

La chaîne typique : équipements → collecteur (Telegraf, gNMIc) → base de séries temporelles (Prometheus, InfluxDB) → tableaux de bord et alertes (Grafana). Voir [NETCONF et télémétrie](netconf.md).

## Alerter sur ce qui compte

- Alerter sur des **symptômes vus par les utilisateurs** (latence d’une sonde vers l’ERP, taux d’échec DNS) plutôt que sur chaque compteur.
- Définir des **seuils** et des **durées** (latence > 100 ms pendant 5 minutes) pour éviter les fausses alertes.
- Relier chaque alerte à une **procédure** : que vérifier en premier ?
- Mesurer la qualité du service par des **objectifs** (« 99,9 % des requêtes DNS en moins de 50 ms »).

## Un tableau de bord utile pour un site

1. État des liens WAN et latence, gigue, pertes des sondes vers le siège et le cloud.
2. Charge des liens et top des applications (flux).
3. Erreurs d’interfaces (CRC, rejets) sur les équipements du site.
4. Derniers événements importants (journaux) et derniers changements de configuration.

## Exercice

**À 9 h 12, les utilisateurs d’un site se plaignent. Les sondes montrent la latence vers l’ERP passée de 15 à 220 ms. Les flux montrent une sauvegarde démarrée à 9 h 10 vers un autre site. Les journaux ne montrent rien. Quelle conclusion et quelle action ?**

<details><summary>Voir le corrigé</summary>

La **sauvegarde**, lancée à un mauvais moment, sature le lien WAN et la latence grimpe pour tout le monde (pas de panne, donc rien dans les journaux). Action immédiate : suspendre ou limiter la sauvegarde. Action durable : la replanifier, et appliquer une **QoS** qui la place en arrière-plan (CS1) pour qu’elle ne gêne plus jamais les applications.

</details>
