---
titre: FIDO
nom: L’authentification par clé publique
idee: Avec FIDO, l’appareil de l’utilisateur garde une clé privée qui ne quitte jamais l’appareil ; le site n’enregistre qu’une clé publique, et chaque connexion consiste à signer un défi lié au vrai site.
osi: "7"
duree: [6, 12]
prerequis: [mfa]
retenir:
  - Une **paire de clés par site** — la clé privée reste dans l’appareil, le site ne connaît que la clé publique.
  - La connexion = **signer un défi** envoyé par le site ; aucun secret réutilisable ne circule.
  - La signature est **liée au nom du site** — un faux site ne peut pas l’utiliser, d’où la résistance à l’hameçonnage.
---

## Le problème

Les mots de passe et les codes à usage unique ont un point commun : ce sont des **secrets qu’on peut recopier**. Un faux site bien imité peut donc les obtenir et les rejouer. L’alliance FIDO (*Fast IDentity Online*) a conçu une méthode où il n’y a **rien à recopier**.

> [!IMPORTANT] L’idée en une phrase
> L’appareil de l’utilisateur prouve son identité en **signant** un défi avec une clé privée qui ne sort jamais de l’appareil, et cette signature n’est valable que pour le vrai site.

## Comment ça marche

```sequence
titre: Connexion avec une clé FIDO
Clé de sécurité | Navigateur | Site exemple.fr
Navigateur -> Site exemple.fr : « je veux me connecter en tant qu’alice »
Site exemple.fr --> Navigateur : défi aléatoire
Navigateur -> Clé de sécurité : signe ce défi pour le site « exemple.fr » (l’origine vérifiée par le navigateur)
note Clé de sécurité : l’utilisateur touche la clé (ou saisit son PIN)
Clé de sécurité --> Navigateur : signature avec la clé privée propre à exemple.fr
Navigateur -> Site exemple.fr : signature
note Site exemple.fr : vérifie avec la clé publique enregistrée : accès accordé
```

Si l’utilisateur est sur un faux site `exemple-connexion.fr`, le navigateur indique ce nom-là à la clé : la clé n’a **aucune clé** pour ce site, ou produit une signature que le vrai site refusera.

## Les mots à connaître

- **FIDO** — Ensemble de normes d’authentification par clé publique, résistantes à l’hameçonnage.
- **Défi** — Valeur aléatoire envoyée par le site, que l’appareil doit signer ; *challenge*.
- **Clé de sécurité** — Petit appareil USB, NFC ou Bluetooth qui stocke des clés FIDO.
- **Authentificateur** — Appareil ou composant qui détient les clés FIDO (clé de sécurité, puce du téléphone ou de l’ordinateur).

## Teste-toi

**Pourquoi une fuite de la base de données du site ne permet-elle pas à un attaquant de se connecter avec FIDO ?**

<details><summary>Voir le corrigé</summary>

Parce que le site ne stocke que des **clés publiques**. Elles permettent de **vérifier** une signature, pas d’en **produire** une. La clé privée n’a jamais quitté l’appareil de l’utilisateur.

</details>

<!-- approfondir -->

## Les générations de normes

| Norme | Rôle |
|---|---|
| **UAF** | authentification sans mot de passe sur mobile (historique) |
| **U2F** (CTAP1) | clé de sécurité comme **second facteur** après le mot de passe |
| **FIDO2** = **WebAuthn** + **CTAP2** | authentification sans mot de passe dans les navigateurs, clés résidentes, PIN ; voir [FIDO2](fido2.md) |

## Ce qui rend FIDO résistant à l’hameçonnage

- **Liaison à l’origine** : le navigateur, pas l’utilisateur, indique à l’authentificateur le site réel. L’utilisateur ne peut pas se tromper à sa place.
- **Une clé par site** : pas de réutilisation entre sites, pas de suivi possible d’un site à l’autre.
- **Présence de l’utilisateur** : il faut toucher la clé (ou un geste biométrique), ce qui bloque un logiciel malveillant agissant seul à distance.

## Exercice

**Un utilisateur clique sur un lien d’hameçonnage qui imite parfaitement le portail de l’entreprise et tente de se connecter avec sa clé FIDO. Que se passe-t-il ?**

<details><summary>Voir le corrigé</summary>

Le navigateur transmet à la clé le **nom réel** du faux site. La clé n’a pas de clé enregistrée pour ce nom : l’authentification **échoue**, et rien d’utilisable n’est transmis à l’attaquant. C’est la différence fondamentale avec un mot de passe ou un code OTP.

</details>
