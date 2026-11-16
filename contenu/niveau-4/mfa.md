---
titre: MFA
nom: Authentification multifacteur
idee: L’authentification multifacteur exige deux preuves de natures différentes — ce que tu sais, ce que tu possèdes, ce que tu es — ; un mot de passe volé ne suffit plus.
osi: "7"
duree: [6, 12]
retenir:
  - "Trois familles de facteurs — **connaissance** (mot de passe), **possession** (téléphone, clé), **inhérence** (biométrie)."
  - Deux preuves de la **même** famille (deux mots de passe) ne font pas une MFA.
  - "Les facteurs ne se valent pas — **clé FIDO2 / passkey** > application avec confirmation et numéro > code TOTP > SMS."
  - "Priorité absolue — **accès distants** (VPN, messagerie, cloud) et **comptes d’administration**."
---

## Le problème : le mot de passe volé

Les mots de passe se volent facilement : hameçonnage, fuite d’un autre site où l’utilisateur a réutilisé le même, logiciel espion. Avec un mot de passe seul, l’attaquant entre comme s’il était l’utilisateur.

> [!IMPORTANT] L’idée en une phrase
> La MFA demande une **deuxième preuve d’une autre nature** que le mot de passe : un objet que l’on possède, ou une caractéristique de soi. Voler l’une ne suffit pas.

## Les trois familles de facteurs

| Famille | Exemples |
|---|---|
| **Ce que je sais** | mot de passe, code PIN |
| **Ce que je possède** | téléphone (application, SMS), clé de sécurité, carte à puce |
| **Ce que je suis** | empreinte digitale, reconnaissance faciale |

## Tous les facteurs ne se valent pas

| Second facteur | Résiste à l’hameçonnage ? | Remarque |
|---|---|---|
| **Clé FIDO2 / passkey** | **oui** | lié au vrai site, rien à recopier ; voir [FIDO2](fido2.md) |
| Notification avec **numéro à recopier** | partiellement | limite la fatigue MFA |
| Code TOTP (application) | non | un faux site peut demander le code et l’utiliser aussitôt ; voir [OTP](otp.md) |
| Simple notification « Approuver » | non | vulnérable au **bombardement** de notifications |
| SMS | non | détournement de carte SIM, interception |

## Les mots à connaître

- **MFA** — Authentification qui combine au moins deux facteurs de familles différentes.
- **Facteur** — Type de preuve d’identité : connaissance, possession ou inhérence.
- **Fatigue MFA** — Attaque qui envoie des demandes d’approbation en rafale jusqu’à ce que la victime accepte.

## Teste-toi

**Un utilisateur se connecte avec son mot de passe puis répond à une question secrète. Est-ce une MFA ?**

<details><summary>Voir le corrigé</summary>

**Non.** Le mot de passe et la question secrète sont tous deux des facteurs de **connaissance** : un attaquant qui a hameçonné l’un peut hameçonner l’autre. Il faut un facteur d’une autre famille (possession, inhérence).

</details>

<!-- approfondir -->

## Où l’exiger en priorité

1. **Accès distants** : VPN, bureau à distance, messagerie et applications cloud.
2. **Comptes à privilèges** : administrateurs du domaine, des équipements réseau (via le bastion et TACACS+), du cloud.
3. **Actions sensibles** : changement de coordonnées bancaires, réinitialisation de mot de passe.
4. Puis **tous les utilisateurs**, idéalement avec des facteurs résistants à l’hameçonnage.

## MFA et équipements réseau

Les équipements ne gèrent pas directement la MFA. On l’applique :

- sur le **bastion** par lequel passent les administrateurs ;
- dans le **serveur RADIUS / TACACS+**, qui interroge un service MFA avant de répondre (un *Access-Challenge* demande le code, ou une notification est envoyée) ;
- sur le **VPN** (portail SAML vers le fournisseur d’identité).

## Les attaques qui contournent une MFA faible

| Attaque | Principe | Parade |
|---|---|---|
| Proxy d’hameçonnage (AitM) | faux site qui relaie en temps réel mot de passe, code et cookie de session | FIDO2 / passkeys, accès conditionnel sur l’appareil |
| Bombardement de notifications | l’attaquant déclenche des dizaines de demandes | correspondance de numéro, limitation, alerte |
| Détournement de SIM | l’attaquant obtient une nouvelle SIM au nom de la victime | ne pas utiliser le SMS pour les comptes sensibles |
| Vol de cookie de session | le jeton est volé après la connexion | durée de session courte, liaison du jeton à l’appareil |

## Exercice

**Un administrateur a reçu 30 notifications d’approbation en pleine nuit, et a fini par en accepter une. Que s’est-il passé, et quelles mesures prendre ?**

<details><summary>Voir le corrigé</summary>

Une attaque par **fatigue MFA** : l’attaquant connaît le mot de passe et déclenche des demandes jusqu’à l’acceptation. Mesures : révoquer les sessions, changer le mot de passe, enquêter ; puis passer à la **correspondance de numéro** ou à **FIDO2**, limiter les tentatives et alerter sur les rafales de refus.

</details>
