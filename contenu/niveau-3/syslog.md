---
titre: Syslog
nom: Journalisation centralisée
idee: Syslog envoie les messages des équipements (une interface tombe, un utilisateur se connecte, une règle bloque un flux) vers un serveur central, où l’on peut les conserver, les chercher et les corréler.
osi: "7 (UDP 514 ; TCP 514 ou 6514 avec TLS)"
duree: [6, 12]
prerequis: [ntp]
retenir:
  - Chaque message a une **gravité** de 0 (urgence) à 7 (débogage).
  - Centraliser les journaux protège la **preuve** — un équipement compromis ou redémarré peut perdre les siens.
  - Sans **NTP**, les horodatages ne sont pas comparables.
  - "Format Cisco — `%INSTALLATION-GRAVITÉ-MNÉMONIQUE: message`."
---

## Le problème : des journaux éparpillés et éphémères

Chaque switch, routeur et pare-feu produit des messages : un port qui tombe, une boucle détectée, un échec de connexion. Mais ils restent dans une petite mémoire locale, effacée au redémarrage. Lors d’un incident, il faudrait se connecter sur 50 équipements, un par un, pour reconstituer ce qui s’est passé.

> [!IMPORTANT] L’idée en une phrase
> Syslog envoie chaque message, au moment où il est produit, vers un **serveur central** qui les conserve et permet de les rechercher et de les corréler.

## Lire un message

```text
Nov 15 09:12:44.318 CET: %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet1/0/48, changed state to down
```

| Partie | Signification |
|---|---|
| `Nov 15 09:12:44.318 CET` | horodatage (à condition que NTP fonctionne) |
| `LINEPROTO` | la fonction qui parle (*facility* Cisco) |
| `5` | la **gravité** : notification |
| `UPDOWN` | le type de message |
| texte | le détail |

## Les niveaux de gravité

| Niveau | Nom | Exemple |
|---|---|---|
| 0 | emergency | système inutilisable |
| 1 | alert | action immédiate nécessaire |
| 2 | critical | panne matérielle |
| 3 | error | erreur d’interface |
| 4 | warning | VLAN natif incohérent, MAC flapping |
| 5 | notification | interface up/down, changement de configuration |
| 6 | informational | ACL qui journalise un flux |
| 7 | debugging | sortie des commandes `debug` |

> [!TIP] Un moyen mnémotechnique
> « **E**very **A**wesome **C**isco **E**ngineer **W**ill **N**eed **I**ce cream **D**aily » : emergency, alert, critical, error, warning, notification, informational, debugging.

## Les mots à connaître

- **Syslog** — Protocole et format standard d’envoi des messages de journal vers un serveur central.
- **Gravité** — Niveau d’importance d’un message, de 0 (urgence) à 7 (débogage) ; *severity*.
- **SIEM** — Plateforme qui collecte et corrèle les journaux pour détecter les incidents de sécurité.

## Teste-toi

**On configure `logging trap warnings` sur un switch. Les messages « interface up/down » arrivent-ils au serveur ?**

<details><summary>Voir le corrigé</summary>

**Non.** `warnings` (4) n’envoie que les messages de gravité **0 à 4**. Les changements d’état d’interface sont de gravité **5** (notification). Il faut `logging trap notifications` (ou `informational`).

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
service timestamps log datetime msec localtime show-timezone
service sequence-numbers
logging buffered 64000 informational
logging host 10.99.0.60 transport tcp port 6514     ! selon la plateforme, avec profil TLS
logging host 10.99.0.61
logging trap informational
logging source-interface Loopback0
logging origin-id hostname
archive
 log config
  logging enable
  notify syslog contenttype plaintext   ! journaliser chaque commande de configuration
```

- `logging buffered` garde une copie locale (utile si le serveur est injoignable).
- `logging source-interface` : une adresse source stable, que le serveur sait associer à l’équipement.
- `archive log config` : chaque commande saisie en mode configuration est journalisée, avec l’utilisateur.

## Transport et fiabilité

| Transport | Avantage | Limite |
|---|---|---|
| UDP 514 | simple, universel | pertes possibles, pas d’authentification, en clair |
| TCP 514 / 601 | pas de perte silencieuse | en clair |
| TLS (TCP 6514, RFC 5425) | confidentialité et intégrité | configuration plus lourde |

## Côté serveur

Un serveur rsyslog ou syslog-ng reçoit et range les messages ; une plateforme (Graylog, Elastic, Splunk, Wazuh, un SIEM) les indexe pour la recherche, les tableaux de bord et les alertes.

```text
# /etc/rsyslog.d/reseau.conf
module(load="imudp")  input(type="imudp" port="514")
module(load="imtcp")  input(type="imtcp" port="514")
template(name="ParEquipement" type="string" string="/var/log/reseau/%HOSTNAME%/%$YEAR%-%$MONTH%-%$DAY%.log")
if $fromhost-ip startswith "10.99." then { action(type="omfile" dynaFile="ParEquipement") stop }
```

## Messages à surveiller en priorité

| Message | Pourquoi |
|---|---|
| `%SYS-5-CONFIG_I` | configuration modifiée : par qui, quand ? |
| `%SEC_LOGIN-4-LOGIN_FAILED` | échecs de connexion répétés : force brute ? |
| `%SW_MATM-4-MACFLAP_NOTIF` | boucle probable |
| `%PM-4-ERR_DISABLE` | port coupé (BPDU Guard, Port Security…) |
| `%OSPF-5-ADJCHG`, `%BGP-5-ADJCHANGE` | voisins de routage qui tombent |
| `%PLATFORM_ENV-1-…`, `%ILPOWER-…` | alimentation, ventilateurs, température, PoE |

## Exercice

**Après un incident, on veut savoir qui a modifié l’ACL d’un routeur la nuit dernière. Le routeur a redémarré entre-temps. Quelles configurations auraient permis de répondre ?**

<details><summary>Voir le corrigé</summary>

L’envoi des journaux vers un **serveur Syslog central** (le tampon local est perdu au redémarrage), la journalisation des commandes (**`archive log config`**), une authentification **nominative** des administrateurs (TACACS+ avec comptabilité des commandes), et une heure juste (**NTP**) pour situer précisément la modification.

</details>
