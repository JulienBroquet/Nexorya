---
titre: Zero Trust
nom: Ne plus faire confiance par défaut
idee: Le Zero Trust supprime la confiance accordée à un appareil parce qu’il est « dans le réseau » ; chaque accès est vérifié selon l’identité, l’état de l’appareil et le contexte, et limité au strict nécessaire.
osi: "transversal"
duree: [9, 18]
cle: true
prerequis: [segmentation, mfa]
retenir:
  - "Principe — **ne jamais faire confiance, toujours vérifier**, à chaque accès."
  - "Trois piliers — **identité forte**, **état de l’appareil**, **moindre privilège** par application."
  - "La **microsegmentation** limite les échanges entre machines, même dans un même réseau."
  - Le Zero Trust est une **démarche progressive**, pas un produit qu’on achète.
---

## Le problème : le château fort

Le modèle traditionnel ressemble à un château fort : un mur épais (le pare-feu Internet) et, une fois à l’intérieur, on circule librement. Or les attaques modernes passent **par l’intérieur** : un poste piégé par un e-mail, un mot de passe volé utilisé sur le VPN, un prestataire compromis. Une fois dedans, l’attaquant se déplace sans obstacle jusqu’aux serveurs et aux sauvegardes. Et les utilisateurs et applications ne sont plus seulement « dedans » : télétravail, cloud, mobiles.

> [!IMPORTANT] L’idée en une phrase
> Être « dans le réseau » ne donne plus aucun droit : chaque accès à chaque application est vérifié — qui es-tu, depuis quel appareil, dans quel contexte — et n’ouvre que ce qui est nécessaire.

## Les principes

1. **Vérifier explicitement** chaque demande : identité forte (MFA, idéalement FIDO2), appareil connu et en bon état (à jour, chiffré, protégé), contexte (lieu, heure, comportement).
2. **Moindre privilège** : accès à une **application** précise, pas à un réseau entier ; droits limités dans le temps quand c’est possible.
3. **Supposer la compromission** : segmenter finement, chiffrer, journaliser, et concevoir chaque zone comme si sa voisine était déjà compromise.

## Ce que cela change concrètement

| Avant | Avec une démarche Zero Trust |
|---|---|
| VPN qui donne accès à tout le réseau | accès par application (ZTNA), après vérification de l’utilisateur et du poste |
| Tous les postes d’un VLAN se voient | microsegmentation : un poste ne parle qu’aux serveurs dont il a besoin |
| Mot de passe seul en interne | MFA aussi en interne, pour les accès sensibles |
| Administrateurs avec des droits permanents | droits accordés pour une tâche et une durée (PAM, accès juste-à-temps) |

```sequence
titre: Zero trust : chaque accès est vérifié
Utilisateur | Proxy d’accès | Moteur de règles | Application
Utilisateur -> Proxy d’accès : je veux ouvrir l’application RH
Proxy d’accès -> Moteur de règles : qui ? quel poste ? d’où ? MFA faite ?
note Moteur de règles : identité vérifiée, poste à jour et chiffré, groupe RH
Moteur de règles --> Proxy d’accès : autorisé pour l’application RH seulement
Proxy d’accès -> Application : connexion relayée
note Utilisateur, Application : aucune autre application n’est visible depuis ce poste
```

## Les mots à connaître

- **Zero Trust** — Modèle de sécurité qui ne fait confiance à aucun accès par défaut et vérifie chacun.
- **ZTNA** — *Zero Trust Network Access*, accès à des applications précises après vérification, en remplacement du VPN « tout le réseau ».
- **Microsegmentation** — Contrôle des échanges entre machines individuelles ou petits groupes, même dans un même réseau.
- **Conformité de l’appareil** — Vérification qu’un appareil respecte la politique (mises à jour, chiffrement, antivirus).

## Teste-toi

**Un prestataire se connecte au VPN avec un compte valide et MFA. Dans un modèle Zero Trust, à quoi devrait-il avoir accès ?**

<details><summary>Voir le corrigé</summary>

**Uniquement** aux applications ou équipements nécessaires à sa mission (par exemple l’interface d’administration d’un seul serveur), éventuellement pour une durée limitée et avec sa session enregistrée. Pas à tout le réseau interne, même s’il est authentifié.

</details>

<!-- approfondir -->

## Le rôle du réseau dans le Zero Trust

Le Zero Trust est souvent présenté comme une affaire d’identité, mais le réseau en est une pièce maîtresse :

| Brique réseau | Contribution |
|---|---|
| **802.1X / NAC** | identifier chaque appareil qui se branche, et lui attribuer des droits selon son profil |
| **Segmentation et VRF** | séparer les grandes zones, forcer le passage par des points de contrôle |
| **Étiquettes de groupe** (Cisco TrustSec / SGT, groupes de sécurité) | filtrer selon le **rôle** de la source et de la destination plutôt que selon les adresses |
| **Pare-feu internes et microsegmentation** (hôte, hyperviseur, cloud) | limiter les échanges est-ouest |
| **ZTNA / SSE** | accès aux applications sans exposer le réseau |
| **Télémétrie** (NetFlow, journaux) | détecter les comportements anormaux, alimenter les décisions |

## Une démarche progressive

1. **Inventorier** les utilisateurs, appareils, applications et flux réels.
2. **Identité forte** partout : MFA résistante à l’hameçonnage, en priorité pour les administrateurs et les accès distants.
3. **Gérer les appareils** : seuls les appareils connus et conformes accèdent aux ressources sensibles.
4. **Segmenter** à grandes mailles (zones), puis **microsegmenter** les zones critiques (serveurs, administration, sauvegardes).
5. **Remplacer** progressivement le VPN global par des accès par application.
6. **Mesurer** et ajuster en continu, à partir des journaux.

Le référentiel le plus cité est la publication **NIST SP 800-207** ; l’ANSSI publie aussi des recommandations sur le sujet.

## Exercices

**1.** Pourquoi la microsegmentation freine-t-elle un rançongiciel, même quand il a infecté un poste légitime ?

<details><summary>Voir le corrigé</summary>

Le rançongiciel se propage en se connectant à d’autres machines (SMB, RDP, outils d’administration). Si chaque poste n’est autorisé à joindre que quelques serveurs précis, sur quelques ports, il ne peut pas atteindre les autres postes ni les serveurs et sauvegardes hors de sa liste : la propagation est **contenue**.

</details>

**2.** Un dirigeant demande « d’acheter une solution Zero Trust ». Que lui répondre ?

<details><summary>Voir le corrigé</summary>

Le Zero Trust est une **démarche** qui s’appuie sur plusieurs briques (identité, gestion des appareils, segmentation, accès par application, supervision), dont certaines existent souvent déjà. Un produit (ZTNA, NAC, microsegmentation) peut en couvrir une partie, mais le résultat dépend de l’inventaire, des politiques définies et de leur application progressive. Proposer une feuille de route par étapes, en commençant par l’identité forte et la protection des accès d’administration.

</details>
