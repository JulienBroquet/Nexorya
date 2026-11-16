---
titre: FIDO2 et passkeys
nom: WebAuthn, CTAP2 et la connexion sans mot de passe
idee: FIDO2 permet de se connecter sans mot de passe, avec une clé de sécurité ou une passkey enregistrée dans son téléphone ou son ordinateur, déverrouillée par un PIN ou la biométrie.
osi: "7"
duree: [6, 14]
prerequis: [fido]
retenir:
  - "**WebAuthn** — l’interface entre le site et le navigateur ; **CTAP2** — le dialogue entre le navigateur et l’authentificateur."
  - "Une **passkey** est un identifiant FIDO2 ; elle peut être **liée à un appareil** ou **synchronisée** entre les appareils d’un utilisateur."
  - FIDO2 est le facteur le plus robuste face à l’hameçonnage — à privilégier pour les administrateurs et les accès distants.
---

## Le problème

FIDO a d’abord servi de **second facteur** après le mot de passe. Mais tant qu’il y a un mot de passe, il peut être volé, oublié ou réutilisé. FIDO2 va plus loin : **se passer complètement du mot de passe**, sans sacrifier la sécurité.

> [!IMPORTANT] L’idée en une phrase
> Avec FIDO2, l’utilisateur se connecte en déverrouillant son authentificateur (empreinte, visage ou PIN) : le site reçoit une preuve cryptographique liée à son nom, et aucun mot de passe n’existe plus.

## Les briques

| Brique | Rôle |
|---|---|
| **WebAuthn** | API du navigateur que le site utilise pour inscrire et vérifier un authentificateur |
| **CTAP2** | protocole entre le navigateur (ou le système) et l’authentificateur : USB, NFC, Bluetooth, ou intégré |
| **Authentificateur** | clé de sécurité, puce sécurisée de l’ordinateur (TPM) ou du téléphone |
| **Passkey** | identifiant FIDO2 « découvrable », utilisable sans saisir de nom d’utilisateur |

## Passkey liée ou synchronisée

| Type | Où vit la clé privée | Avantage | Contrepartie |
|---|---|---|---|
| **Liée à l’appareil** | une clé de sécurité, ou un appareil précis | contrôle maximal, aucune copie | perte de l’appareil = réinscription |
| **Synchronisée** | le gestionnaire de clés du système (iCloud, Google, gestionnaire de mots de passe) | pratique, récupérable | dépend de la sécurité du compte de synchronisation |

En entreprise, on réserve souvent les passkeys **liées à l’appareil** (clés de sécurité) aux administrateurs, et l’on autorise les passkeys synchronisées pour les autres utilisateurs selon la politique.

## Les mots à connaître

- **FIDO2** — Norme d’authentification sans mot de passe composée de WebAuthn et CTAP2.
- **WebAuthn** — Interface Web standard d’authentification par clé publique.
- **Passkey** — Identifiant FIDO2 qui remplace le mot de passe.
- **TPM** — Puce de sécurité d’un ordinateur qui peut servir d’authentificateur.

## Teste-toi

**Pourquoi une clé de sécurité FIDO2 demande-t-elle souvent un PIN, alors qu’on voulait se passer des mots de passe ?**

<details><summary>Voir le corrigé</summary>

Le PIN est **local** : il ne déverrouille que la clé, ne circule jamais sur le réseau et n’est utile qu’avec la clé physique. On combine ainsi **possession** (la clé) et **connaissance** (le PIN), sans aucun secret réutilisable côté serveur.

</details>

<!-- approfondir -->

## Inscription et connexion

```sequence
titre: Inscription d’une passkey
Authentificateur | Navigateur | Site
Site -> Navigateur : options d’inscription : identifiant du site (RP ID), défi, utilisateur
Navigateur -> Authentificateur : créer une paire de clés pour ce RP ID
note Authentificateur : vérification de l’utilisateur (PIN, biométrie)
Authentificateur --> Navigateur : clé publique + attestation signée
Navigateur -> Site : clé publique, identifiant de la clé, attestation
note Site : enregistre la clé publique pour cet utilisateur
```

L’**attestation** permet au site de vérifier le **modèle** d’authentificateur (par exemple, n’accepter que des clés d’un fabricant validé). Elle est optionnelle et souvent utilisée en entreprise.

## Déployer en entreprise

- Le **fournisseur d’identité** (Entra ID, Okta, Keycloak…) gère l’inscription et la politique (types d’authentificateurs, attestation).
- Les accès au **VPN**, au **bastion** et aux consoles cloud passent par ce fournisseur (SAML, OIDC) : FIDO2 protège alors aussi l’administration réseau.
- Prévoir **deux** authentificateurs par administrateur (un principal, un de secours dans un coffre) et une procédure de récupération stricte.
- Pour les sessions Windows, FIDO2 et Windows Hello for Business permettent l’ouverture de session sans mot de passe.

## Exercice

**Pourquoi exiger des passkeys liées à l’appareil (clés de sécurité) plutôt que synchronisées pour les administrateurs du domaine ?**

<details><summary>Voir le corrigé</summary>

Une passkey **synchronisée** est aussi sûre que le compte qui la synchronise (compte cloud personnel ou gestionnaire de mots de passe) et peut exister sur plusieurs appareils. Une clé **liée à l’appareil** ne peut pas être copiée : un attaquant doit voler l’objet physique **et** connaître le PIN. Pour les comptes les plus sensibles, on veut ce niveau de garantie et la possibilité de vérifier le modèle (attestation).

</details>
