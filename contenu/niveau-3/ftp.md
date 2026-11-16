---
titre: FTP
nom: File Transfer Protocol
idee: FTP transfère des fichiers avec deux connexions — une pour les commandes, une pour les données ; ancien et non chiffré, il est remplacé par SFTP ou HTTPS.
osi: "7 (TCP 21 pour les commandes)"
duree: [6, 12]
prerequis: [tcp, nat]
retenir:
  - "**Deux connexions** — contrôle (TCP 21) et données (port négocié)."
  - "Mode **actif** — le serveur se connecte au client (gêné par le NAT et les pare-feu) ; mode **passif** — le client se connecte au serveur."
  - Tout circule **en clair**, mot de passe compris — préférer **SFTP** ou FTPS.
---

## Le problème

Pendant des décennies, FTP a été le moyen standard d’échanger des fichiers entre machines. On le rencontre encore : vieux automates, imprimantes multifonctions qui déposent des numérisations, échanges avec des partenaires. Il pose deux problèmes : il est **en clair**, et il **traverse mal** les pare-feu.

> [!IMPORTANT] L’idée en une phrase
> FTP ouvre une connexion pour les **commandes** (« donne-moi tel fichier ») et une autre pour les **données** (le fichier lui-même) ; cette seconde connexion est la source de la plupart des difficultés.

## Actif ou passif

| Mode | Qui ouvre la connexion de données ? | Problème |
|---|---|---|
| **Actif** | le **serveur** se connecte au client, sur un port annoncé par le client | le pare-feu ou le NAT du client bloque la connexion entrante |
| **Passif** | le **client** se connecte au serveur, sur un port annoncé par le serveur | le pare-feu du serveur doit autoriser une plage de ports |

Le mode **passif** est le choix par défaut aujourd’hui.

## Les mots à connaître

- **FTP** — Protocole historique de transfert de fichiers, sans chiffrement.
- **Canal de contrôle / de données** — Les deux connexions de FTP : commandes et transfert.
- **Mode passif** — Mode où c’est le client qui ouvre la connexion de données.
- **FTPS** — FTP protégé par TLS (à ne pas confondre avec SFTP).

## Teste-toi

**Un transfert FTP réussit dans le réseau local mais échoue à travers le pare-feu : la connexion et la liste des dossiers fonctionnent… sauf qu’elle reste vide et que les téléchargements se figent. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

Le **canal de contrôle** (TCP 21) passe, mais pas le **canal de données**, ouvert sur un autre port. Il faut le mode **passif** et, côté serveur, une plage de ports passifs autorisée au pare-feu (ou un pare-feu qui comprend FTP).

</details>

<!-- approfondir -->

## Ce qui se passe sur le réseau

```sequence
titre: Connexion FTP en mode passif
Client | Serveur FTP
Client -> Serveur FTP : TCP 21 : USER, PASS (en clair)
Client -> Serveur FTP : PASV
Serveur FTP --> Client : 227 Entering Passive Mode (203,0,113,20,195,80)
note Client : port de données = 195 × 256 + 80 = 50 000
Client -> Serveur FTP : nouvelle connexion TCP vers le port 50 000
Client -> Serveur FTP : RETR rapport.pdf (sur le canal de contrôle)
Serveur FTP --> Client : contenu du fichier sur la connexion de données
```

Le serveur **écrit son adresse IP** dans la réponse PASV. Derrière un NAT, s’il annonce son adresse **privée**, le client tente de se connecter à une adresse injoignable : il faut configurer le serveur pour annoncer son adresse publique (`pasv_address` sous vsftpd).

## Pare-feu et FTP

- **Côté serveur** : ouvrir TCP 21 et une **plage** de ports passifs déclarée dans le serveur (`pasv_min_port`, `pasv_max_port`).
- **Inspection FTP** (*ALG*) : de nombreux pare-feu lisent le canal de contrôle et ouvrent dynamiquement le bon port. Avec **FTPS**, le contrôle est chiffré : l’ALG ne peut plus lire les ports, d’où la nécessité de la plage fixe.

## Remplacer FTP

| Besoin | Alternative |
|---|---|
| Échange de fichiers avec authentification | **SFTP** (sur SSH, un seul port 22) |
| Dépôt par une application ou un partenaire | HTTPS avec une API, ou SFTP |
| Mise à disposition publique de fichiers | HTTPS |
| Équipement ancien qui ne sait faire que FTP | FTP limité à un réseau isolé, compte dédié, serveur qui ne sert qu’à cela |

## Exercice

**Un serveur FTP derrière un NAT répond `227 Entering Passive Mode (10,20,0,30,195,80)`. Un client sur Internet n’arrive pas à télécharger. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

Le serveur annonce son adresse **privée** `10.20.0.30` : le client tente de se connecter à cette adresse, injoignable depuis Internet. Il faut configurer l’adresse annoncée en mode passif (adresse publique), ou utiliser un pare-feu dont l’inspection FTP réécrit l’adresse.

</details>
