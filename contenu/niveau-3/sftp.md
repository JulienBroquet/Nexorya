---
titre: SFTP
nom: SSH File Transfer Protocol
idee: SFTP transfère des fichiers à l’intérieur d’une session SSH — tout est chiffré, et un seul port (22) suffit.
osi: "7 (TCP 22)"
duree: [4, 8]
prerequis: [ssh, ftp]
retenir:
  - SFTP n’a **rien à voir** avec FTP — c’est un sous-système de **SSH**.
  - Un **seul port** (22), tout est **chiffré**, authentification par mot de passe ou par **clé**.
  - Le bon remplaçant de FTP pour les échanges de fichiers entre systèmes ou avec des partenaires.
---

## Le problème

FTP est en clair et traverse mal les pare-feu ; TFTP n’a pas d’authentification. Pour échanger des fichiers de façon sûre — sauvegardes, échanges de factures avec un partenaire, dépôt de journaux —, il faut un protocole chiffré, authentifié et simple à filtrer.

> [!IMPORTANT] L’idée en une phrase
> SFTP utilise une session SSH ordinaire pour transférer des fichiers : mêmes garanties que SSH, même port 22.

## SFTP, FTPS, SCP : ne pas confondre

| Nom | Ce que c’est | Port |
|---|---|---|
| **SFTP** | transfert de fichiers dans SSH | 22 |
| **FTPS** | FTP classique protégé par TLS (garde les deux connexions) | 21 (+ plage de données), ou 990 |
| **SCP** | copie simple via SSH, sans navigation dans les dossiers | 22 |

## Les mots à connaître

- **SFTP** — Protocole de transfert de fichiers chiffré, intégré à SSH.
- **SCP** — Copie de fichiers via SSH.
- **Chroot** — Enfermement d’un utilisateur dans un dossier, dont il ne peut pas sortir.

## Teste-toi

**Un partenaire demande « un accès SFTP ». Quels ports faut-il ouvrir sur le pare-feu ?**

<details><summary>Voir le corrigé</summary>

Uniquement le **TCP 22** vers le serveur SFTP (idéalement limité à l’adresse du partenaire). Pas de plage de ports supplémentaire, contrairement à FTP.

</details>

<!-- approfondir -->

## Un serveur SFTP cloisonné (OpenSSH)

```text
# /etc/ssh/sshd_config
Match Group partenaires
    ChrootDirectory /srv/sftp/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication no
```

Les comptes du groupe `partenaires` ne peuvent faire **que** du SFTP, enfermés dans leur dossier, avec authentification par **clé**. Le dossier racine du chroot doit appartenir à `root` et ne pas être modifiable par l’utilisateur.

```bash
$ sftp -i ~/.ssh/cle_partenaire facture@sftp.exemple.fr
sftp> put factures-2026-11.zip
$ scp -i ~/.ssh/cle_partenaire rapport.pdf facture@sftp.exemple.fr:/depot/
```

## Exercice

**Pourquoi l’authentification par clé est-elle recommandée pour un échange automatique quotidien avec un partenaire ?**

<details><summary>Voir le corrigé</summary>

Elle évite de stocker un **mot de passe** en clair dans un script, résiste à la force brute, et permet de **révoquer** l’accès en retirant la clé publique sans changer de mot de passe partagé. On peut aussi restreindre ce que la clé autorise (commande forcée, adresse source).

</details>
