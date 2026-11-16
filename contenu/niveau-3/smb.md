---
titre: SMB
nom: Server Message Block
idee: SMB est le protocole des partages de fichiers et d’imprimantes Windows — les lecteurs réseau comme `\\serveur\partage` reposent sur lui.
osi: "7 (TCP 445)"
duree: [6, 12]
prerequis: [tcp]
retenir:
  - SMB fonctionne sur **TCP 445**.
  - "Utiliser **SMB 3** (chiffrement, signature) ; **SMB 1** est obsolète et doit être désactivé."
  - Ne **jamais** exposer le port 445 sur Internet.
  - Les droits combinent les **autorisations du partage** et celles du **système de fichiers** (NTFS).
---

## Le problème

Les employés partagent des dossiers d’équipe, des modèles de documents, des imprimantes. Il faut un protocole qui permette d’ouvrir, de modifier et de verrouiller des fichiers sur un serveur comme s’ils étaient sur le disque local, en respectant les droits de chacun.

> [!IMPORTANT] L’idée en une phrase
> SMB permet à un poste d’utiliser les fichiers et les imprimantes d’un serveur à travers le réseau, avec l’identité de l’utilisateur pour contrôler les droits.

## Les versions

| Version | Statut |
|---|---|
| SMB 1 (CIFS) | **à désactiver** : utilisé par le rançongiciel WannaCry en 2017 |
| SMB 2.x | performant, encore courant |
| SMB 3.x | **chiffrement**, signature renforcée, basculement transparent entre serveurs |

```sequence
titre: Ouvrir \\srv-fichiers\compta depuis un poste Windows
Poste | Serveur de fichiers | Contrôleur de domaine
Poste -> Serveur de fichiers : NEGOTIATE : quelle version de SMB ? (TCP 445)
Serveur de fichiers --> Poste : SMB 3.1.1, chiffrement possible
Poste -> Contrôleur de domaine : demande un ticket Kerberos pour srv-fichiers
Contrôleur de domaine --> Poste : ticket de service
Poste -> Serveur de fichiers : SESSION SETUP avec le ticket
Poste -> Serveur de fichiers : TREE CONNECT \\srv-fichiers\compta
Serveur de fichiers --> Poste : accès accordé selon les droits du partage et des fichiers
```

## Les mots à connaître

- **SMB** — Protocole de partage de fichiers et d’imprimantes des environnements Windows.
- **Partage** — Dossier rendu accessible sur le réseau, noté `\\serveur\nom`.
- **UNC** — Notation des chemins réseau Windows : `\\serveur\partage\dossier`.

## Teste-toi

**Pourquoi bloquer le port 445 entre Internet et le réseau de l’entreprise, dans les deux sens ?**

<details><summary>Voir le corrigé</summary>

Vers l’intérieur : pour que personne ne puisse attaquer les partages et les vulnérabilités de SMB depuis Internet. Vers l’extérieur : pour qu’un poste piégé (lien malveillant vers `\\serveur-attaquant\…`) n’envoie pas les **éléments d’authentification** de l’utilisateur à un serveur pirate.

</details>

<!-- approfondir -->

## Diagnostiquer un partage inaccessible

```powershell
PS> Test-NetConnection srv-fichiers -Port 445
PS> Get-SmbConnection                          # connexions SMB actives et version (Dialect)
ServerName    ShareName  UserName          Dialect
srv-fichiers  Equipe     EXEMPLE\alice     3.1.1
PS> Get-SmbServerConfiguration | Select EnableSMB1Protocol, EncryptData, RequireSecuritySignature
PS> net use \\srv-fichiers\Equipe
```

| Symptôme | Piste |
|---|---|
| « Chemin réseau introuvable » | DNS, port 445 filtré, service Serveur arrêté |
| « Accès refusé » | droits de partage ou NTFS, groupe de l’utilisateur |
| Erreur d’authentification sur un nom court mais pas sur l’adresse IP (ou l’inverse) | Kerberos (nom) contre NTLM (adresse IP) ; SPN, heure du poste |
| Lenteurs | latence (SMB est bavard), signature ou chiffrement sur un serveur ancien |

## Bonnes pratiques

- Désactiver SMB 1 partout (`Set-SmbServerConfiguration -EnableSMB1Protocol $false`).
- Exiger la **signature** SMB, activer le **chiffrement** sur les partages sensibles.
- Limiter les flux 445 aux **serveurs de fichiers** : les postes n’ont pas besoin de s’échanger du SMB entre eux. Cela freine fortement la propagation d’un rançongiciel.

## Exercice

**Un rançongiciel se propage de poste en poste par SMB. Quelle règle de segmentation simple aurait limité sa diffusion ?**

<details><summary>Voir le corrigé</summary>

**Interdire le TCP 445 entre postes de travail** (pare-feu Windows et ACL entre VLAN) et ne l’autoriser que vers les serveurs de fichiers. Les postes n’ont pas besoin de partager des fichiers directement entre eux.

</details>
