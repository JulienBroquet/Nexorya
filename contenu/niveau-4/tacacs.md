---
titre: TACACS+
nom: Terminal Access Controller Access-Control System Plus
idee: TACACS+ contrôle qui peut se connecter aux équipements réseau, quelles commandes chacun peut taper, et garde la trace de chaque commande.
osi: "7 (TCP 49)"
duree: [6, 12]
prerequis: [aaa]
retenir:
  - TACACS+ sépare **authentification, autorisation et traçabilité**, et peut autoriser **commande par commande**.
  - Il chiffre **tout le contenu** des messages (pas seulement le mot de passe comme RADIUS).
  - "Il sert surtout à **l’administration des équipements** ; RADIUS sert à l’**accès au réseau**."
---

## Le problème

Vingt personnes administrent les équipements réseau : support, administrateurs, ingénieurs, prestataires. Elles n’ont pas toutes les mêmes droits. Il faut savoir précisément **qui a tapé quelle commande, sur quel équipement, à quelle heure** — et empêcher un technicien de supprimer la configuration de sécurité.

> [!IMPORTANT] L’idée en une phrase
> Avec TACACS+, chaque connexion et **chaque commande** tapée sur un équipement sont validées par un serveur central, qui les enregistre.

## RADIUS ou TACACS+ ?

| | RADIUS | TACACS+ |
|---|---|---|
| Usage principal | accès au réseau (802.1X, Wi-Fi, VPN) | administration des équipements |
| Transport | UDP 1812/1813 | TCP 49 |
| Chiffrement | mot de passe seulement | tout le contenu |
| Autorisation par commande | non | **oui** |
| Norme | ouverte (RFC 2865) | publiée par Cisco (RFC 8907), largement supportée |

## Les mots à connaître

- **TACACS+** — Protocole AAA pour l’administration des équipements réseau.
- **Autorisation par commande** — Vérification auprès du serveur de chaque commande tapée par un administrateur.
- **Niveau de privilège** — Niveau de droits d’une session sur un équipement Cisco, de 0 à 15.

## Teste-toi

**Pourquoi TACACS+ est-il préféré à RADIUS pour l’accès administrateur aux switches ?**

<details><summary>Voir le corrigé</summary>

Parce qu’il permet d’**autoriser et de journaliser chaque commande**, qu’il **chiffre** l’ensemble des échanges, et qu’il sépare clairement authentification, autorisation et traçabilité.

</details>

<!-- approfondir -->

## Ce que voit le serveur

```text
2026-11-15 14:02:11  sw-etage2  bruno  tty1  10.99.0.15  stop  task_id=8812  service=shell
                     cmd=interface GigabitEthernet1/0/4 <cr>
2026-11-15 14:02:19  sw-etage2  bruno  tty1  10.99.0.15  stop  task_id=8813  service=shell
                     cmd=switchport access vlan 30 <cr>
2026-11-15 14:02:47  sw-etage2  bruno  tty1  10.99.0.15  stop  task_id=8815  service=shell
                     cmd=no shutdown <cr>
```

En cas d’incident, on retrouve exactement la séquence de modifications.

## Un jeu de règles typique

| Profil | Commandes autorisées |
|---|---|
| Support | `show *`, `ping`, `traceroute` |
| Administrateur accès | les précédentes + `configure terminal`, `interface *`, `switchport *`, `shutdown`, `description *` |
| Ingénieur réseau | tout sauf `aaa *`, `username *`, `crypto *` |
| Ingénieur sécurité | tout |

## Configuration (rappel)

La configuration Cisco complète (serveurs, groupe, méthodes `login`, `exec`, `commands`, accounting) est détaillée dans la fiche [AAA](aaa.md). La vérification :

```cisco
SW1# show tacacs
Tacacs+ Server - public  :
               Server name: ISE-1
            Server address: 10.99.0.80
               Server port: 49
      Socket opens:       4211
     Socket closes:       4211
     Socket errors:          0
   Socket Timeouts:          0
```

## Exercice

**Un prestataire doit pouvoir changer le VLAN des ports d’accès d’un étage, et rien d’autre. Comment le traduire avec TACACS+ ?**

<details><summary>Voir le corrigé</summary>

Créer un profil qui n’autorise que : `configure terminal`, `interface GigabitEthernet1/0/*` (sur les ports d’accès), `switchport access vlan *`, `description *`, `exit`, `end` et les `show`. Le limiter aux équipements de l’étage (groupe de NAS), activer l’accounting des commandes, et limiter la validité du compte à la durée de la mission.

</details>
