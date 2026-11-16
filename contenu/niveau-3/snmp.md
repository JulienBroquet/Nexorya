---
titre: SNMP
nom: Simple Network Management Protocol
idee: SNMP permet à un outil de supervision d’interroger les équipements réseau (débit des interfaces, état, température…) et de recevoir leurs alertes.
osi: "7 (UDP 161 ; alertes UDP 162)"
duree: [7, 15]
prerequis: [udp]
retenir:
  - Le **superviseur** interroge les **agents** (UDP 161) ; les agents envoient des **traps** (UDP 162).
  - Chaque valeur a une adresse, l’**OID**, rangée dans une **MIB**.
  - Utiliser **SNMPv3** (authentification et chiffrement) ; v1/v2c reposent sur une « communauté » en clair.
  - Le débit d’une interface se calcule à partir de **compteurs** qui augmentent — deux mesures et une soustraction.
---

## Le problème : savoir avant les utilisateurs

Un lien sature tous les matins, un switch chauffe, une alimentation est en panne : l’équipe réseau veut le savoir **avant** que les utilisateurs appellent. Il faut un moyen standard d’interroger des centaines d’équipements de marques différentes et de recevoir leurs alertes.

> [!IMPORTANT] L’idée en une phrase
> Chaque équipement fait tourner un **agent** SNMP qui répond aux questions d’un **superviseur** (« combien d’octets sur l’interface 48 ? ») et envoie des **alertes** quand un événement se produit.

## Comment ça marche

```sequence
titre: Interrogation régulière et alerte
Superviseur | Switch (agent SNMP)
Superviseur -> Switch (agent SNMP) : GET ifHCInOctets.48 (toutes les 5 min)
Switch (agent SNMP) --> Superviseur : 8 431 290 113 422
note Switch (agent SNMP) : l’interface 48 tombe
Switch (agent SNMP) -> Superviseur : TRAP linkDown, interface 48
```

- Le superviseur **interroge** périodiquement (UDP 161) et dessine des courbes.
- L’agent **prévient** spontanément d’un événement grave par un **trap** (UDP 162).

## Les mots à connaître

- **SNMP** — Protocole de supervision des équipements réseau.
- **Agent** — Logiciel de l’équipement qui répond aux requêtes SNMP.
- **Superviseur** — Outil qui interroge les agents et reçoit les alertes (Zabbix, LibreNMS, PRTG, Centreon…).
- **OID** — Identifiant numérique d’une valeur supervisée, par exemple 1.3.6.1.2.1.1.3.0.
- **MIB** — Catalogue qui décrit les OID et leur signification.
- **Trap** — Alerte envoyée spontanément par un agent.

## Teste-toi

**Pourquoi SNMPv2c est-il déconseillé ?**

<details><summary>Voir le corrigé</summary>

Il s’appuie sur une **communauté**, un simple mot de passe envoyé **en clair** à chaque requête. N’importe qui sur le chemin peut la lire et, si elle autorise l’écriture, modifier la configuration. **SNMPv3** apporte authentification et chiffrement.

</details>

<!-- approfondir -->

## Calculer un débit à partir des compteurs

Les compteurs d’octets (`ifHCInOctets`, `ifHCOutOctets`, sur 64 bits) ne font qu’augmenter. On interroge deux fois et l’on calcule :

```text
débit (b/s) = (valeur2 − valeur1) × 8 / (temps2 − temps1)

Exemple : 8 431 290 113 422 puis 8 431 327 613 422, à 300 s d’intervalle
          (37 500 000 octets × 8) / 300 = 1 000 000 b/s = 1 Mb/s en moyenne sur 5 minutes
```

Une moyenne sur 5 minutes **lisse** les pics : un lien peut saturer par rafales de quelques secondes sans que la courbe dépasse 60 %. Pour les pics, on raccourcit l’intervalle ou l’on utilise la **télémétrie** (voir [NETCONF et télémétrie](../niveau-5/netconf.md)).

## OID utiles

| OID | Nom | Contenu |
|---|---|---|
| 1.3.6.1.2.1.1.3.0 | sysUpTime | durée depuis le dernier démarrage |
| 1.3.6.1.2.1.1.5.0 | sysName | nom de l’équipement |
| 1.3.6.1.2.1.2.2.1.8 | ifOperStatus | état de chaque interface (1 = up, 2 = down) |
| 1.3.6.1.2.1.31.1.1.1.6 | ifHCInOctets | octets reçus (64 bits) |
| 1.3.6.1.2.1.2.2.1.14 | ifInErrors | erreurs en réception |

```bash
$ snmpwalk -v3 -l authPriv -u supervision -a SHA -A 'Secret-Auth' -x AES -X 'Secret-Priv' 10.99.0.21 1.3.6.1.2.1.31.1.1.1.1
IF-MIB::ifName.48 = STRING: Gi1/0/48
$ snmpget -v3 … 10.99.0.21 IF-MIB::ifHCInOctets.48
```

## SNMPv3 sur un équipement Cisco

```cisco
ip access-list standard SUPERVISION
 permit 10.99.0.50
snmp-server view LECTURE iso included
snmp-server group SUPERVISION v3 priv read LECTURE access SUPERVISION
snmp-server user supervision SUPERVISION v3 auth sha Secret-Auth priv aes 128 Secret-Priv
snmp-server host 10.99.0.50 version 3 priv supervision
snmp-server enable traps snmp linkdown linkup
snmp-server enable traps envmon
```

- Niveau **priv** : authentification et chiffrement.
- Accès en **lecture seule**, limité à l’adresse du superviseur.
- Supprimer les anciennes communautés `public` et `private`.

## Exercices

**1.** Une courbe de supervision montre un lien à 1 Gb/s chargé à 45 % en moyenne, mais la téléphonie hache toutes les quelques minutes. Comment l’expliquer ?

<details><summary>Voir le corrigé</summary>

La moyenne sur 5 minutes **masque les rafales** : le lien peut atteindre 100 % pendant quelques secondes (sauvegarde, synchronisation), ce qui remplit les files et dégrade la voix. Regarder les **rejets en sortie** (`output drops`) sur l’interface, raccourcir l’intervalle de mesure, et appliquer de la QoS.

</details>

**2.** Le superviseur ne reçoit plus aucune donnée d’un switch depuis le passage à SNMPv3, alors que le ping fonctionne. Quelles pistes ?

<details><summary>Voir le corrigé</summary>

Paramètres v3 incohérents (nom d’utilisateur, algorithmes d’authentification ou de chiffrement, mots de passe), **ACL** du groupe qui n’autorise pas l’adresse du superviseur, ou UDP 161 filtré. `snmpget -v3` depuis le superviseur avec des options explicites, et `debug snmp packets` (avec précaution), permettent de trancher.

</details>
