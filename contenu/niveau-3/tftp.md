---
titre: TFTP
nom: Trivial File Transfer Protocol
idee: TFTP est un transfert de fichiers minimal, sans authentification, sur UDP ; il sert à démarrer des équipements par le réseau et à charger des configurations ou des micrologiciels.
osi: "7 (UDP 69)"
duree: [4, 8]
prerequis: [udp]
retenir:
  - "**Aucune authentification**, aucun chiffrement — à réserver à des réseaux maîtrisés."
  - "Usages — **démarrage réseau** (PXE), téléphones IP, sauvegarde et chargement de configurations et d’images."
  - Le transfert continue sur un **port différent** du port 69 — les pare-feu sans inspection le bloquent.
---

## Le problème

Un téléphone IP qui démarre, un PC qui s’installe par le réseau (PXE), un switch qu’on restaure : ces équipements ont très peu de mémoire et de logiciel au démarrage. Il leur faut un protocole de transfert **minuscule**, simple à programmer.

> [!IMPORTANT] L’idée en une phrase
> TFTP demande un fichier par son nom et le reçoit en blocs numérotés, sur UDP, sans aucune authentification.

## Où on le rencontre

- **PXE** : un PC sans système démarre, obtient une adresse par DHCP (options 66/67), puis télécharge son programme de démarrage en TFTP.
- **Téléphones IP** : ils récupèrent leur configuration et leur micrologiciel au démarrage (option DHCP 150 chez Cisco).
- **Équipements réseau** : sauvegarde et restauration de configurations, chargement d’images logicielles en laboratoire.

```sequence
titre: Télécharger un fichier en TFTP, bloc par bloc
Switch | Serveur TFTP
Switch -> Serveur TFTP : RRQ : je veux le fichier image.bin (UDP 69)
Serveur TFTP --> Switch : DATA bloc 1 (512 octets)
Switch -> Serveur TFTP : ACK 1
Serveur TFTP --> Switch : DATA bloc 2
Switch -> Serveur TFTP : ACK 2
Serveur TFTP -x Switch : DATA bloc 3 (perdu)
note Serveur TFTP : pas d’ACK 3 reçu : il renvoie le bloc après un délai
Serveur TFTP --> Switch : DATA bloc 3 (renvoyé)
```

## Les mots à connaître

- **TFTP** — Protocole de transfert de fichiers très simple, sur UDP, sans authentification.
- **PXE** — *Preboot Execution Environment*, démarrage d’un ordinateur par le réseau.

## Teste-toi

**Pourquoi ne faut-il pas laisser un serveur TFTP accessible depuis tout le réseau ?**

<details><summary>Voir le corrigé</summary>

Parce que n’importe qui peut y **lire** (et parfois **écrire**) des fichiers sans s’authentifier. Il contient souvent des **configurations** d’équipements, avec des secrets. On le limite aux réseaux et aux équipements qui en ont besoin, et l’on préfère SCP ou SFTP pour les sauvegardes.

</details>

<!-- approfondir -->

## Fonctionnement

Le client envoie une requête de lecture (**RRQ**) ou d’écriture (**WRQ**) vers le **port 69** du serveur. Le serveur répond **depuis un autre port**, choisi pour ce transfert : c’est là que les pare-feu sans inspection TFTP échouent. Le fichier est envoyé en blocs de 512 octets (davantage avec l’option *blksize*), chacun acquitté avant le suivant : TFTP est lent sur un lien à forte latence.

## Commandes utiles

```cisco
SW1# copy running-config tftp://10.99.0.70/sw1-2026-11-15.cfg
SW1# copy tftp://10.99.0.70/c9300-17.09.04.bin flash:
! Plus sûr pour les sauvegardes :
SW1# copy running-config scp://sauvegarde@10.99.0.70/sw1.cfg
```

```bash
$ tftp 10.99.0.70 -c get phone-config.xml
```

## Exercice

**L’installation PXE d’un PC s’arrête après « TFTP… » avec un délai d’attente, alors que le DHCP fonctionne. Que vérifier ?**

<details><summary>Voir le corrigé</summary>

Les options DHCP **66/67** (serveur et nom de fichier), la joignabilité du serveur TFTP depuis le VLAN du PC, et le **filtrage** : le pare-feu doit laisser passer l’UDP 69 **et** les réponses depuis les ports dynamiques du serveur (inspection TFTP ou règle adaptée).

</details>
