---
titre: EAP-TLS
nom: Authentification par certificats
idee: Avec EAP-TLS, le poste et le serveur se présentent chacun un certificat ; il n’y a plus de mot de passe à voler, et l’on peut retirer l’accès d’un appareil en révoquant son certificat.
osi: "2 (dans EAP)"
duree: [7, 15]
prerequis: [eap, pki]
retenir:
  - Authentification **mutuelle** par certificats — aucun mot de passe ne circule.
  - Il faut une **PKI** pour délivrer, renouveler et révoquer les certificats des postes (souvent automatiquement).
  - "Causes d’échec courantes — autorité non approuvée, certificat expiré, mauvais usage (EKU), **horloge**, révocation injoignable."
---

## Le problème

Les méthodes par mot de passe ont des faiblesses : mots de passe faibles ou réutilisés, hameçonnage, faux serveurs. Et lorsqu’un ordinateur portable est volé, comment être sûr qu’il ne pourra plus jamais se connecter au réseau ?

> [!IMPORTANT] L’idée en une phrase
> Chaque poste reçoit un **certificat** personnel, qu’il présente au serveur ; le serveur présente le sien au poste. Personne ne tape de mot de passe, et un certificat révoqué ne passe plus.

## Comment ça marche

1. Le poste reçoit automatiquement un **certificat machine** (et éventuellement utilisateur) délivré par l’autorité de certification de l’entreprise.
2. À la connexion (filaire 802.1X ou Wi-Fi), le serveur RADIUS présente **son** certificat ; le poste le vérifie.
3. Le poste présente **son** certificat ; le serveur vérifie qu’il est signé par l’autorité de l’entreprise, valide, non révoqué, et prévu pour l’authentification client.
4. Le serveur applique la politique (VLAN, ACL) selon les informations du certificat ou de l’annuaire.

## Les mots à connaître

- **EAP-TLS** — Méthode EAP d’authentification mutuelle par certificats.
- **Certificat machine** — Certificat qui identifie un ordinateur, utilisé avant l’ouverture de session.
- **Révocation** — Annulation d’un certificat avant sa date d’expiration.

## Teste-toi

**Un portable de l’entreprise est volé. Comment l’empêcher de se connecter au réseau avec EAP-TLS ?**

<details><summary>Voir le corrigé</summary>

**Révoquer** son certificat dans la PKI (et désactiver le compte machine dans l’annuaire). Le serveur RADIUS, qui vérifie la révocation (liste CRL ou OCSP), refusera ensuite la connexion.

</details>

<!-- approfondir -->

## Ce que vérifie le serveur

| Vérification | Échec typique |
|---|---|
| Chaîne de confiance | l’autorité qui a signé le certificat du poste n’est pas déclarée sur le serveur |
| Dates de validité | certificat expiré (renouvellement automatique en panne) ou horloge fausse |
| Usage étendu (EKU) | le certificat n’a pas l’usage « Authentification client » |
| Révocation | CRL ou OCSP injoignable depuis le serveur, ou certificat révoqué |
| Correspondance avec l’annuaire | le nom du certificat ne correspond à aucun compte machine actif |

## Ce que vérifie le poste

- le certificat du serveur RADIUS est signé par une autorité **explicitement approuvée** dans le profil ;
- son nom correspond au nom attendu ;
- il a l’usage « Authentification serveur ».

## Déploiement à grande échelle

- **Windows / Active Directory** : inscription automatique des certificats machine et utilisateur (*autoenrollment*) par GPO ; profil filaire et Wi-Fi par GPO.
- **Postes et mobiles gérés** : SCEP ou ACME via l’outil de gestion (Intune, Jamf…).
- **Supervision** : alertes sur les certificats bientôt expirés et sur les taux d’échec EAP-TLS.

## Exemple de diagnostic

Après le déploiement d’une **nouvelle autorité de certification**, les postes échouent en masse. Le journal RADIUS indique « unknown CA ». Le serveur RADIUS n’a pas encore la **nouvelle autorité** dans sa liste de confiance : on l’ajoute (en gardant l’ancienne pendant la transition). Si l’erreur était « certificate expired » sur tous les postes au même moment, on vérifierait l’**heure du serveur RADIUS**.

## Exercice

**Les postes Windows passent bien en EAP-TLS, mais les Mac gérés échouent avec « certificat client sans usage d’authentification ». Que corriger ?**

<details><summary>Voir le corrigé</summary>

Le **modèle de certificat** utilisé pour les Mac (via SCEP) ne contient pas l’usage étendu **Client Authentication** (EKU 1.3.6.1.5.5.7.3.2). Corriger le modèle, puis redélivrer les certificats.

</details>
