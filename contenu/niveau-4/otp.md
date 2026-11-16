---
titre: OTP
nom: Mots de passe à usage unique (TOTP, HOTP)
idee: Un OTP est un code valable une seule fois, calculé à partir d’un secret partagé et de l’heure (TOTP) ou d’un compteur (HOTP) ; il sert de second facteur.
osi: "7"
duree: [5, 10]
prerequis: [mfa]
retenir:
  - "**TOTP** — un code de 6 chiffres qui change toutes les **30 secondes** (heure + secret)."
  - Le secret est partagé une fois (souvent par **QR code**) ; il doit être protégé comme un mot de passe.
  - L’heure du téléphone et celle du serveur doivent concorder.
  - Un OTP **ne résiste pas** à l’hameçonnage en temps réel.
---

## Le problème

On veut un second facteur simple, qui fonctionne sans réseau sur le téléphone, avec n’importe quelle application d’authentification, et qui ne dépende pas du SMS.

> [!IMPORTANT] L’idée en une phrase
> Le téléphone et le serveur connaissent le **même secret** ; chacun calcule, à partir de ce secret et de l’heure, le même code à 6 chiffres, valable 30 secondes.

## Comment ça marche (TOTP)

1. **Inscription** : le serveur génère un secret et l’affiche sous forme de **QR code** ; l’application du téléphone le mémorise.
2. **Connexion** : l’application calcule `code = HMAC(secret, heure ÷ 30 s)`, tronqué à 6 chiffres.
3. Le serveur fait le même calcul et compare. Il accepte généralement aussi le code de la période précédente et de la suivante, pour tolérer un petit décalage.

```sequence
titre: Un code TOTP : calculé des deux côtés, jamais transmis à l’avance
Application | Serveur
note Application, Serveur : à l’enrôlement, ils partagent un secret (QR code)
note Application : code = calcul(secret, heure actuelle) → 482 913
Application -> Serveur : l’utilisateur saisit 482 913
note Serveur : fait le même calcul avec la même heure
Serveur --> Application : codes identiques : accès accordé
```

## Les mots à connaître

- **OTP** — *One-Time Password*, code valable une seule fois.
- **TOTP** — OTP calculé à partir de l’heure (RFC 6238).
- **HOTP** — OTP calculé à partir d’un compteur incrémenté à chaque usage (RFC 4226).

## Teste-toi

**Les codes TOTP d’un utilisateur sont toujours refusés, alors qu’ils sont bien recopiés. Quelle vérification simple ?**

<details><summary>Voir le corrigé</summary>

L’**heure du téléphone** (ou celle du serveur) : si l’écart dépasse une à deux périodes de 30 s, les codes ne correspondent plus. Activer l’heure automatique sur le téléphone et vérifier NTP sur le serveur.

</details>

<!-- approfondir -->

## Limites et bonnes pratiques

- Un OTP se **recopie** : un faux site peut le demander et l’utiliser dans les 30 secondes. Il protège contre le vol de mot de passe, pas contre l’hameçonnage en temps réel.
- Le **secret** doit être stocké chiffré côté serveur ; s’il fuit, tous les codes futurs sont calculables.
- Prévoir des **codes de secours** à usage unique et une procédure de réinscription sécurisée (le changement de téléphone est la première source d’appels au support).
- Pour les accès sensibles, préférer [FIDO2](fido2.md).

## Exercice

**Pourquoi le serveur accepte-t-il souvent le code de la période précédente, et quel risque cela ajoute-t-il ?**

<details><summary>Voir le corrigé</summary>

Pour tolérer un léger **décalage d’horloge** et le temps de saisie. Le risque est minime : la fenêtre d’utilisation d’un code intercepté s’allonge de 30 s. Le serveur doit aussi refuser la **réutilisation** d’un code déjà accepté.

</details>
