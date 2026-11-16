---
titre: NetFlow
nom: NetFlow, IPFIX et sFlow
idee: NetFlow résume le trafic en « flux » — qui parle à qui, sur quel port, combien et combien de temps — sans copier les paquets ; on sait ainsi ce qui consomme un lien et l’on repère les comportements anormaux.
osi: "3 et 4"
duree: [7, 14]
prerequis: [tcp, udp]
retenir:
  - "Un **flux** = adresses source et destination, ports, protocole, interface ; avec des compteurs d’octets et de paquets."
  - "L’**exportateur** (routeur, switch, pare-feu) envoie les flux à un **collecteur** qui les analyse."
  - "**IPFIX** est la version standard (dérivée de NetFlow v9) ; **sFlow** fonctionne par échantillonnage."
  - "Questions typiques — qui sature ce lien ? ce poste parle-t-il à des destinations inhabituelles ?"
---

## Le problème : savoir qui consomme

La supervision SNMP montre qu’un lien est saturé à 95 %. Mais **par quoi** ? Une sauvegarde, une mise à jour, un utilisateur qui télécharge des vidéos, un poste infecté qui exfiltre des données ? SNMP ne compte que des octets ; une capture complète serait trop lourde à garder.

> [!IMPORTANT] L’idée en une phrase
> NetFlow tient une sorte de **relevé détaillé des communications** : pour chaque conversation, qui, avec qui, sur quel port, combien — sans le contenu.

## Comment ça marche

```topologie
titre: Exportation des flux vers un collecteur
R routeur 0,0 "Routeur WAN" "exportateur"
SW l3 0,1 "Cœur" "exportateur"
COL serveur 2,0.5 "Collecteur" "analyse, tableaux de bord"
R .. COL "IPFIX (UDP)"
SW .. COL "IPFIX (UDP)"
```

1. L’équipement observe le trafic et regroupe les paquets en **flux** (même source, destination, ports, protocole).
2. Quand un flux se termine ou après un délai, il **exporte** un enregistrement vers le collecteur.
3. Le collecteur stocke, agrège et présente : « top 10 des conversations sur le lien WAN », « trafic par application », « historique d’un poste ».

## Un enregistrement de flux

| Champ | Exemple |
|---|---|
| Source → destination | 10.50.0.25:51544 → 10.20.0.40:443 |
| Protocole | TCP |
| Interfaces | entrée Gi0/0/1, sortie Tunnel10 |
| Octets / paquets | 1,8 Go / 1,3 million |
| Début / fin | 18:02:11 → 18:47:56 |
| DSCP | 8 (CS1, arrière-plan) |

## Les mots à connaître

- **NetFlow** — Technologie Cisco d’export des statistiques de flux réseau.
- **IPFIX** — Version standard de l’export de flux (RFC 7011).
- **sFlow** — Méthode d’observation par échantillonnage de paquets, courante sur les switches.
- **Flux** — Ensemble de paquets partageant les mêmes adresses, ports et protocole.
- **Collecteur** — Logiciel qui reçoit, stocke et analyse les flux exportés.

## Teste-toi

**NetFlow permet-il de lire le contenu d’un e-mail ?**

<details><summary>Voir le corrigé</summary>

**Non.** NetFlow ne garde que des **métadonnées** (qui, quand, combien, sur quel port), jamais le contenu des paquets. C’est ce qui le rend léger, et moins intrusif qu’une capture.

</details>

<!-- approfondir -->

## Configuration (Flexible NetFlow, Cisco IOS-XE)

```cisco
flow record FLUX-IPV4
 match ipv4 source address
 match ipv4 destination address
 match transport source-port
 match transport destination-port
 match ipv4 protocol
 match interface input
 collect interface output
 collect counter bytes long
 collect counter packets long
 collect timestamp absolute first
 collect timestamp absolute last
 collect ipv4 dscp
!
flow exporter VERS-COLLECTEUR
 destination 10.99.0.90
 source Loopback0
 transport udp 4739
 export-protocol ipfix
!
flow monitor MON-WAN
 record FLUX-IPV4
 exporter VERS-COLLECTEUR
 cache timeout active 60
!
interface GigabitEthernet0/0/1
 ip flow monitor MON-WAN input
 ip flow monitor MON-WAN output
```

`cache timeout active 60` : un flux long (une sauvegarde d’une heure) est exporté **toutes les 60 s**, pour que les tableaux de bord montrent la charge en temps quasi réel.

## Cas d’usage

| Question | Ce que montre NetFlow |
|---|---|
| Qui sature le lien ? | top des conversations et des applications sur l’interface |
| Ce poste est-il compromis ? | connexions vers des destinations inhabituelles, volumes sortants anormaux, balayages |
| Quels flux pour ma matrice de segmentation ? | inventaire réel de qui parle à qui avant de filtrer |
| La QoS est-elle appliquée ? | valeurs DSCP réelles par flux |
| Faut-il augmenter ce lien ? | tendances de consommation par application |

## Échantillonnage

Sur des liens très rapides, analyser chaque paquet est coûteux. On **échantillonne** (1 paquet sur 1 000, par exemple) : les volumes sont estimés statistiquement. C’est le principe de **sFlow**, et une option de NetFlow. Bien pour les tendances et les gros flux, moins pour repérer un flux minuscule.

## Exercice

**Le lien WAN d’une agence est saturé chaque jour de 12 h à 14 h. Comment NetFlow aide-t-il à décider entre « augmenter le lien » et « corriger un usage » ?**

<details><summary>Voir le corrigé</summary>

Le collecteur montre **quelles conversations et applications** occupent le lien à ces heures. Si c’est un usage légitime en croissance (visioconférence, SaaS), on augmente le lien ou l’on ajuste la QoS. Si c’est une mise à jour mal planifiée, une sauvegarde déclenchée au mauvais moment ou du streaming personnel, on corrige l’usage (planification, politique, filtrage) sans dépense.

</details>
