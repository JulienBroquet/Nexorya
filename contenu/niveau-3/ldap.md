---
titre: LDAP
nom: Lightweight Directory Access Protocol
idee: LDAP permet aux applications d’interroger l’annuaire de l’entreprise — comptes, groupes, ordinateurs — pour authentifier les utilisateurs et vérifier leurs droits.
osi: "7 (TCP 389 ; 636 en LDAPS)"
duree: [7, 14]
prerequis: [tcp, tls]
retenir:
  - "L’annuaire est un **arbre** d’objets, chacun identifié par un **DN** (`CN=Alice,OU=Compta,DC=exemple,DC=fr`)."
  - Une application se **lie** (bind) à l’annuaire, **cherche** un utilisateur, vérifie ses **groupes**.
  - "Toujours chiffrer — **LDAPS** (636) ou **StartTLS** ; un bind simple sur 389 transmet le mot de passe en clair."
  - Active Directory est l’annuaire le plus répandu ; il parle LDAP.
---

## Le problème : un compte, toutes les applications

Sans annuaire, chaque application a sa propre liste d’utilisateurs et de mots de passe : quand un employé part, il faut penser à le supprimer partout. Avec un **annuaire central**, il existe un seul compte par personne, et les applications l’interrogent.

> [!IMPORTANT] L’idée en une phrase
> LDAP est la façon standard de poser des questions à l’annuaire : « ce mot de passe est-il bon pour alice ? », « alice fait-elle partie du groupe Compta ? ».

## L’annuaire est un arbre

```text
DC=exemple,DC=fr
├── OU=Utilisateurs
│   ├── OU=Compta
│   │   └── CN=Alice Martin        (objet utilisateur : mail, téléphone, groupes…)
│   └── OU=Informatique
│       └── CN=Bruno Petit
├── OU=Groupes
│   └── CN=GG-Compta-Lecture
└── OU=Ordinateurs
    └── CN=PC-COMPTA-12
```

Chaque objet a un **nom distinctif** (DN) qui donne son chemin complet, de la feuille vers la racine : `CN=Alice Martin,OU=Compta,OU=Utilisateurs,DC=exemple,DC=fr`.

## Comment une application l’utilise

1. L’application se **connecte** à l’annuaire avec un compte de service (*bind*).
2. Elle **cherche** l’utilisateur à partir de son identifiant (`sAMAccountName=alice`).
3. Elle **vérifie** son mot de passe (nouveau bind avec le DN trouvé et le mot de passe saisi).
4. Elle **lit** ses groupes pour décider de ses droits.

```sequence
titre: Une application vérifie un utilisateur dans l’annuaire
Application | Annuaire LDAP
Application -> Annuaire LDAP : BIND avec le compte de service (LDAPS, port 636)
Annuaire LDAP --> Application : OK
Application -> Annuaire LDAP : SEARCH : uid=alice, quels groupes ?
Annuaire LDAP --> Application : DN de l’utilisateur + groupes (Compta, VPN)
Application -> Annuaire LDAP : BIND avec le DN d’Alice et son mot de passe
Annuaire LDAP --> Application : OK : mot de passe correct
```

## Les mots à connaître

- **LDAP** — Protocole d’interrogation des annuaires.
- **Annuaire** — Base centrale des comptes, groupes et ressources d’une organisation.
- **DN** — *Distinguished Name*, nom complet et unique d’un objet de l’annuaire.
- **OU** — *Organizational Unit*, dossier de l’annuaire qui regroupe des objets.
- **Bind** — Authentification d’un client auprès de l’annuaire.
- **Active Directory** — Annuaire de Microsoft, qui utilise LDAP et Kerberos.

## Teste-toi

**Une application se connecte à l’annuaire en LDAP simple sur le port 389, sans TLS. Quel est le risque ?**

<details><summary>Voir le corrigé</summary>

Lors d’un **bind simple**, le mot de passe circule **en clair** : celui du compte de service, et celui de chaque utilisateur qui se connecte à l’application. Il faut **LDAPS** (636) ou **StartTLS** sur 389.

</details>

<!-- approfondir -->

## Interroger l’annuaire

```bash
$ ldapsearch -H ldaps://dc1.exemple.fr -D "CN=svc-appli,OU=Services,DC=exemple,DC=fr" -W \
    -b "DC=exemple,DC=fr" "(sAMAccountName=alice)" memberOf mail
dn: CN=Alice Martin,OU=Compta,OU=Utilisateurs,DC=exemple,DC=fr
mail: alice.martin@exemple.fr
memberOf: CN=GG-Compta-Lecture,OU=Groupes,DC=exemple,DC=fr
```

```powershell
PS> Get-ADUser alice -Properties MemberOf, LastLogonDate
PS> Test-NetConnection dc1.exemple.fr -Port 636
```

## Les ports d’Active Directory

| Port | Usage |
|---|---|
| 389 TCP/UDP | LDAP (StartTLS possible) |
| 636 TCP | LDAPS |
| 3268 / 3269 TCP | catalogue global (recherche dans toute la forêt) / en TLS |
| 88 TCP/UDP | Kerberos |
| 53 | DNS (indispensable : les clients trouvent les contrôleurs par des enregistrements SRV) |
| 445 | SMB (stratégies de groupe, SYSVOL) |
| 135 + plage dynamique | RPC |

## Bonnes pratiques

- **Chiffrement obligatoire** et **signature LDAP** exigée sur les contrôleurs de domaine.
- Compte de service dédié, **en lecture seule**, avec un mot de passe long, idéalement géré automatiquement.
- Viser **plusieurs contrôleurs de domaine** (ou un nom qui les regroupe) pour la tolérance aux pannes.
- Pour les applications Web modernes, préférer une fédération d’identité (**SAML**, **OpenID Connect**) : l’application ne voit jamais le mot de passe.

## Exercice

**Une application interne refuse soudain toutes les connexions après une mise à jour des contrôleurs de domaine qui exige la signature LDAP. Elle utilisait LDAP simple sur 389. Que faire ?**

<details><summary>Voir le corrigé</summary>

Configurer l’application en **LDAPS (636)** ou **StartTLS**, avec la chaîne de certificats de l’autorité interne approuvée par l’application. Les binds simples non protégés sont désormais refusés : c’était justement le but de la mise à jour.

</details>
