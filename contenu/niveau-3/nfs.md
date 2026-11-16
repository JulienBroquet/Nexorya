---
titre: NFS
nom: Network File System
idee: NFS permet à des machines Linux et Unix de monter un dossier distant comme s’il était local ; c’est le partage de fichiers des serveurs et du stockage.
osi: "7 (TCP 2049)"
duree: [5, 10]
prerequis: [tcp]
retenir:
  - "**NFSv4** n’utilise qu’un port, **TCP 2049** ; les versions anciennes en utilisaient plusieurs, dynamiques."
  - Les droits reposent sur les **identifiants numériques** (UID/GID) — ils doivent correspondre entre client et serveur.
  - Sans **Kerberos**, NFS fait confiance à l’adresse du client — on le limite à des réseaux dédiés.
---

## Le problème

Plusieurs serveurs Linux doivent partager un même volume : des fichiers d’application, des sauvegardes, des répertoires personnels. Ou une ferme de virtualisation doit stocker ses machines virtuelles sur une baie de stockage.

> [!IMPORTANT] L’idée en une phrase
> NFS « monte » un dossier d’un serveur de fichiers dans l’arborescence d’une machine Linux : les applications l’utilisent comme un disque local.

## SMB ou NFS ?

| | SMB | NFS |
|---|---|---|
| Monde d’origine | Windows | Unix / Linux |
| Identité | utilisateur Windows (Kerberos/NTLM) | identifiants numériques UID/GID (ou Kerberos) |
| Usage typique | partages d’utilisateurs | serveurs, virtualisation, stockage |

## Les mots à connaître

- **NFS** — Protocole de partage de fichiers des systèmes Unix et Linux.
- **Montage** — Rattachement d’un dossier distant à un emplacement de l’arborescence locale.
- **Export** — Dossier qu’un serveur NFS met à disposition, avec la liste des clients autorisés.

## Teste-toi

**Un utilisateur crée un fichier sur un partage NFS ; sur un autre serveur, le fichier appartient à un utilisateur différent. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

NFS transporte les **identifiants numériques** (UID/GID), pas les noms. Si l’utilisateur `alice` a l’UID 1001 sur un serveur et 1003 sur l’autre, le même fichier semble appartenir à des personnes différentes. Il faut un annuaire commun (LDAP) ou le mappage d’identités de NFSv4.

</details>

<!-- approfondir -->

## Configurer et monter

```text
# Serveur : /etc/exports
/srv/applis   10.40.0.0/24(rw,sync,root_squash,sec=sys)
/srv/archives 10.40.0.0/24(ro,sync,sec=krb5p)
```

```bash
$ sudo exportfs -ra && exportfs -v
$ showmount -e srv-nfs                # (v3) liste des exports
$ sudo mount -t nfs4 srv-nfs:/srv/applis /mnt/applis
$ nfsstat -m                          # options de montage effectives
```

- `root_squash` : l’utilisateur `root` d’un client est traité comme un utilisateur sans privilèges sur le serveur.
- `sec=krb5p` : authentification Kerberos **et** chiffrement des échanges.

## Réseau et NFS

- Placer le trafic NFS (surtout pour la virtualisation) dans un **VLAN de stockage** dédié, non routé vers les utilisateurs.
- Utiliser des **jumbo frames** de bout en bout si le stockage le demande, en vérifiant la MTU sur tout le chemin.
- Un délai d’attente NFS fige les applications (montage « hard ») : la qualité du lien est critique.

## Exercice

**Un montage NFS fonctionne pour les petits fichiers, mais la copie de gros fichiers se bloque. Le VLAN de stockage a été passé en MTU 9000 sur les serveurs. Que vérifier ?**

<details><summary>Voir le corrigé</summary>

La **MTU de tout le chemin** : si un switch ou une interface intermédiaire est resté à 1 500, les grosses trames sont perdues (petits échanges OK, gros transferts bloqués). Tester avec `ping -M do -s 8972 <serveur>` et aligner la MTU partout.

</details>
