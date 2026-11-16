---
titre: Le voyage d’un clic
actif: pratique
chapeau: Tu tapes www.exemple.fr et la page s’affiche en une fraction de seconde. Entre les deux, une dizaine de protocoles ont travaillé. On les suit dans l’ordre.
---

> [!NOTE] Comment lire cette page
> Chaque étape renvoie vers la fiche qui l’explique. Si tu débutes, lis seulement les phrases en gras de chaque étape ; tu reviendras sur les détails plus tard.

## Le décor

```topologie
titre: Le chemin entre ton ordinateur et le site
PC pc 0,0 "Ton PC" "192.168.1.20"
BOX routeur 1.5,0 "Box" "192.168.1.1"
FAI nuage 3,0 "Opérateur et Internet"
DNS serveur 3,1.2 "Résolveur DNS"
WEB serveur 4.5,0 "Serveur Web" "93.184.215.14"
PC -- BOX "Wi-Fi"
BOX -- FAI "fibre"
FAI -- WEB
FAI .. DNS
```

## Étape 0 — Avoir une adresse

**En se connectant au Wi-Fi, ton PC a reçu une adresse IP, un masque, une passerelle (la box) et l’adresse d’un serveur DNS**, grâce au [DHCP](../niveau-3/dhcp.md). Sans ces quatre informations, rien de ce qui suit n’est possible.

Pour arriver jusqu’à la box, la trame voyage par [Wi-Fi](../niveau-1/wifi.md) et utilise les [adresses MAC](../niveau-1/mac.md).

## Étape 1 — Trouver l’adresse du site

**Ton PC ne sait pas où se trouve www.exemple.fr : il demande au [DNS](../niveau-3/dns.md).** Le résolveur interroge si besoin les serveurs racine, puis ceux de `.fr`, puis ceux d’`exemple.fr`, et renvoie l’adresse (et la garde en cache pour la suite).

## Étape 2 — Savoir à qui remettre le paquet

**L’adresse du site n’est pas dans ton réseau local** (le PC le sait grâce au [masque](../niveau-2/subnet.md)) : **il faut passer par la [passerelle](../niveau-2/passerelle.md).** Pour lui envoyer une trame, le PC doit connaître son adresse MAC : il la demande avec [ARP](../niveau-2/arp.md).

## Étape 3 — Ouvrir la connexion

**Le navigateur ouvre une connexion [TCP](../niveau-3/tcp.md) vers le port 443 du serveur** (ou utilise [QUIC](../niveau-3/quic.md) sur UDP). En sortant, la box remplace ton adresse privée par son adresse publique : c’est le [NAT](../niveau-3/nat.md).

Entre la box et le serveur, chaque [routeur](../niveau-2/routage-statique.md) lit l’adresse de destination et choisit la direction suivante, grâce à des tables construites par [OSPF](../niveau-2/ospf.md) chez chaque opérateur et [BGP](../niveau-2/bgp.md) entre les opérateurs.

## Étape 4 — Sécuriser l’échange

**Le navigateur et le serveur négocient une session [TLS](../niveau-3/tls.md)** : le serveur prouve son identité avec un certificat signé par une autorité reconnue ([PKI](../niveau-4/pki.md)), et les deux côtés établissent des clés de chiffrement. Plus personne sur le chemin ne peut lire ni modifier l’échange.

## Étape 5 — Demander la page

**Le navigateur envoie une requête [HTTP](../niveau-3/http.md) `GET /`** ; le serveur répond `200 OK` avec le code HTML de la page. Le navigateur découvre alors qu’il lui faut aussi des images, des feuilles de style, des scripts… et les demande, souvent sur la même connexion.

```sequence
titre: Le résumé de l’échange
PC | Box | DNS | Serveur
PC -> DNS : Quelle adresse pour www.exemple.fr ?
DNS --> PC : 93.184.215.14
PC -> Box : ARP : quelle MAC pour 192.168.1.1 ?
Box --> PC : c’est moi
PC -> Serveur : TCP SYN (port 443)
Serveur --> PC : SYN-ACK
PC -> Serveur : ACK, puis négociation TLS
PC -> Serveur : GET / (chiffré)
Serveur --> PC : 200 OK et la page
```

## Ce qui peut casser, étape par étape

| Symptôme | Étape en cause | Premier réflexe |
|---|---|---|
| adresse en 169.254.x.x | 0 — DHCP | câble, Wi-Fi, serveur DHCP |
| « Impossible de trouver l’adresse du serveur » | 1 — DNS | `nslookup www.exemple.fr` |
| le ping de la passerelle échoue | 2 — réseau local | configuration IP, ARP, câble |
| le ping d’une adresse Internet échoue | 3 — routage, NAT | passerelle, box, opérateur ; `tracert` |
| alerte de certificat | 4 — TLS | date du PC, certificat du site, proxy |
| erreur 404 ou 500 | 5 — application | le réseau fonctionne : c’est le serveur |

C’est la méthode des [commandes de base](../demarrer/commandes.md), appliquée dans l’ordre : on remonte les étapes jusqu’à trouver la première qui échoue.

## Pour aller plus loin

Fais l’expérience avec [Wireshark](../niveau-5/span.md) : lance une capture, ouvre un site, puis filtre successivement `dns`, `arp`, `tcp.flags.syn == 1`, `tls.handshake`. Tu verras chaque étape de cette page, avec ses vrais paquets.
