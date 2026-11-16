---
titre: NTP
nom: Network Time Protocol
idee: NTP garde toutes les horloges du réseau à l’heure, à quelques millisecondes près, en les synchronisant sur des sources de temps fiables.
osi: "7 (UDP 123)"
duree: [6, 12]
prerequis: [udp]
retenir:
  - "Une heure fausse casse — les **certificats** (TLS), **Kerberos** (ouverture de session Windows, tolérance de 5 minutes), la **corrélation des journaux**."
  - Les sources sont organisées en **strates** — strate 1 = directement reliée à une horloge de référence.
  - En entreprise, quelques **serveurs NTP internes** synchronisés sur plusieurs sources ; tous les équipements se synchronisent sur eux.
---

## Le problème : chaque horloge dérive

L’horloge interne d’un ordinateur ou d’un switch dérive de quelques secondes par jour. Au bout de quelques semaines, les équipements ne sont plus d’accord sur l’heure. Les conséquences sont concrètes :

- un poste dont l’horloge a 10 minutes d’écart **ne peut plus ouvrir de session** dans un domaine Windows (Kerberos tolère 5 minutes) ;
- un navigateur à la mauvaise date juge les **certificats** expirés ;
- lors d’un incident, impossible de **reconstituer la chronologie** : les journaux du pare-feu disent 14 h 02, ceux du serveur 13 h 57.

> [!IMPORTANT] L’idée en une phrase
> NTP fait régulièrement comparer à chaque machine son horloge à celle d’un serveur de référence, et la corrige en douceur, en tenant compte du temps de trajet sur le réseau.

## Comment ça marche

```sequence
titre: Un client mesure l’écart et le délai
Client | Serveur NTP
Client -> Serveur NTP : requête, partie à T1 (heure du client)
note Serveur NTP : reçue à T2, réponse partie à T3 (heure du serveur)
Serveur NTP --> Client : réponse avec T2 et T3, arrivée à T4
note Client : délai = (T4 − T1) − (T3 − T2) ; écart = ((T2 − T1) + (T3 − T4)) / 2
```

Le client calcule le **délai** du réseau et son **écart** avec le serveur. Il interroge plusieurs serveurs, écarte les valeurs aberrantes, et ajuste progressivement son horloge.

## Les strates

| Strate | Source |
|---|---|
| 0 | horloge de référence : GPS, horloge atomique (n’est pas sur le réseau) |
| 1 | serveur directement relié à une strate 0 |
| 2 | serveur synchronisé sur une strate 1 |
| … | jusqu’à 15 ; 16 = non synchronisé |

## Les mots à connaître

- **NTP** — *Network Time Protocol*, protocole de synchronisation des horloges.
- **Strate** — Distance d’un serveur NTP à une horloge de référence.
- **Décalage (offset)** — Écart entre l’horloge locale et celle de la référence.

## Teste-toi

**Un utilisateur ne peut plus ouvrir de session sur son poste Windows (« l’heure du poste est différente de celle du domaine »). Quel service est en cause ?**

<details><summary>Voir le corrigé</summary>

La **synchronisation de l’heure** (NTP, via le service W32Time). Kerberos refuse l’authentification au-delà de **5 minutes** d’écart. Resynchroniser le poste sur un contrôleur de domaine résout le problème.

</details>

<!-- approfondir -->

## Architecture recommandée

- Deux à quatre **serveurs NTP internes**, chacun synchronisé sur **plusieurs** sources externes indépendantes (au moins 3 pour pouvoir écarter une source fausse), ou sur un récepteur GPS.
- Tous les équipements réseau, serveurs et contrôleurs de domaine se synchronisent sur ces serveurs internes ; les postes Windows suivent la hiérarchie du domaine.
- Les pare-feu n’autorisent l’UDP 123 sortant que depuis les serveurs NTP internes.

## Configuration et vérification (Cisco IOS)

```cisco
ntp server 10.99.0.123 prefer
ntp server 10.99.0.124
ntp source Loopback0
clock timezone CET 1 0
clock summer-time CEST recurring last Sun Mar 2:00 last Sun Oct 3:00
service timestamps log datetime msec localtime show-timezone
!
SW1# show ntp status
Clock is synchronized, stratum 3, reference is 10.99.0.123
SW1# show ntp associations
  address         ref clock       st   when   poll reach  delay  offset   disp
*~10.99.0.123     192.0.2.53       2     41     64   377  1.234   0.215  0.512
+~10.99.0.124     198.51.100.5     2     12     64   377  1.410  -0.330  0.701
```

- `*` : source retenue ; `+` : candidate valable.
- `reach 377` (octal) : les 8 dernières interrogations ont réussi.

## Côté systèmes

```powershell
PS> w32tm /query /status
PS> w32tm /query /source
PS> w32tm /resync
```

```bash
$ chronyc tracking
Reference ID    : 0A63007B (10.99.0.123)
Stratum         : 3
System time     : 0.000124 seconds fast of NTP time
$ chronyc sources -v
```

## Sécurité et précision

- **NTS** (*Network Time Security*) ajoute l’authentification des serveurs NTP, avec TLS pour l’échange des clés.
- Un serveur NTP exposé sur Internet et mal configuré peut être utilisé pour des attaques par **amplification** : désactiver les requêtes de supervision (`monlist`) et limiter qui peut l’interroger.
- Pour une précision de la microseconde (télécoms, finance, industrie, audio-vidéo professionnel), on utilise **PTP** (IEEE 1588), avec des switches qui prennent en charge l’horodatage matériel.

## Exercice

**Pendant l’analyse d’un incident, les journaux du pare-feu montrent une connexion suspecte à 14 h 02 min 10 s, et ceux du serveur une ouverture de session à 13 h 58 min 40 s. L’un des deux équipements a `Clock is unsynchronized`. Que conclure ?**

<details><summary>Voir le corrigé</summary>

Les horodatages **ne sont pas comparables** : un des équipements a dérivé. On ne peut pas affirmer l’ordre des événements. Il faut corriger NTP, puis estimer l’écart (en le mesurant au moment de la correction) pour réaligner les journaux. Cet exemple montre pourquoi NTP fait partie des **prérequis de sécurité**.

</details>
