---
titre: WPA Entreprise
nom: WPA2 et WPA3-Enterprise
idee: Le Wi-Fi des salariés n’utilise pas un mot de passe partagé, mais une authentification individuelle 802.1X ; chaque utilisateur ou appareil a ses propres clés, et un départ se gère en désactivant un seul compte.
osi: "2"
duree: [7, 15]
prerequis: [802-1x, wifi]
retenir:
  - "**WPA-Personnel** — un mot de passe partagé par tous ; **WPA-Entreprise** — une identité par utilisateur ou appareil (802.1X + RADIUS)."
  - Chaque client obtient des **clés de chiffrement uniques**.
  - "**WPA3** renforce la sécurité — SAE en Personnel, mode 192 bits et protection des trames de gestion (PMF) en Entreprise."
  - Les **invités** et les **objets connectés** vont sur des SSID séparés.
---

## Le problème : le mot de passe Wi-Fi que tout le monde connaît

Un mot de passe Wi-Fi partagé finit toujours par circuler : affiché en salle de pause, donné à un prestataire, gardé par un ancien salarié. Le changer oblige à reconfigurer tous les appareils. Et tous ceux qui le connaissent peuvent, en théorie, déchiffrer le trafic des autres.

> [!IMPORTANT] L’idée en une phrase
> En WPA-Entreprise, chaque personne (ou appareil) se connecte avec **sa propre identité**, vérifiée par le serveur RADIUS : pas de secret partagé, et des clés de chiffrement différentes pour chacun.

## Personnel ou Entreprise ?

| | WPA2/WPA3-Personnel | WPA2/WPA3-Entreprise |
|---|---|---|
| Authentification | mot de passe partagé | 802.1X : identifiants ou certificat par personne |
| Départ d’un salarié | changer le mot de passe pour tous | désactiver un compte |
| Attribution de droits | identique pour tous | VLAN et ACL selon l’identité |
| Usage | domicile, petites structures, objets connectés | salariés |

## Les mots à connaître

- **WPA2 / WPA3** — Protocoles de sécurité du Wi-Fi.
- **WPA-Entreprise** — Mode où chaque client s’authentifie individuellement via 802.1X et RADIUS.
- **SAE** — *Simultaneous Authentication of Equals*, échange de WPA3-Personnel qui résiste aux attaques par dictionnaire hors ligne.
- **PMF** — *Protected Management Frames*, protection des trames de gestion (empêche les déconnexions forcées).

## Teste-toi

**Pourquoi le départ d’un salarié est-il plus simple à gérer en WPA-Entreprise ?**

<details><summary>Voir le corrigé</summary>

Il suffit de **désactiver son compte** (ou de révoquer son certificat) : il ne peut plus se connecter, sans rien changer pour les autres. Avec un mot de passe partagé, il faudrait le changer et reconfigurer tous les appareils.

</details>

<!-- approfondir -->

## D’où viennent les clés

1. L’authentification 802.1X/EAP aboutit : le serveur RADIUS et le client ont dérivé une clé maîtresse (**PMK**), propre à cette session.
2. Le serveur transmet la PMK à la borne (dans l’Access-Accept, protégée par le secret RADIUS).
3. La borne et le client font la **poignée de main à 4 messages** pour dériver les clés de chiffrement du trafic.

En WPA-Personnel, la PMK dérive du mot de passe et du SSID : tous ceux qui connaissent le mot de passe connaissent la PMK.

## Les apports de WPA3

| Mode | Apport |
|---|---|
| WPA3-Personnel | **SAE** remplace le PSK : capturer une connexion ne permet plus de tester des mots de passe hors ligne ; PMF obligatoire |
| WPA3-Entreprise | PMF obligatoire, validation du certificat serveur renforcée ; mode **192 bits** (CNSA) pour les environnements sensibles |
| Wi-Fi 6E / 7 (6 GHz) | WPA3 **obligatoire** |
| OWE (*Enhanced Open*) | chiffrement sans mot de passe pour les réseaux ouverts (invités) |

## Un design de SSID type

| SSID | Sécurité | VLAN | Accès |
|---|---|---|---|
| Entreprise | WPA3-Entreprise (transition WPA2/3), EAP-TLS | attribué par RADIUS | selon le profil |
| Invités | OWE ou portail, isolation des clients | 30 | Internet, débit limité |
| Objets | WPA2/3-Personnel avec **clé par appareil** (iPSK, DPSK) | 50 | serveurs nécessaires seulement |

> [!WARNING]
> Le mode de **transition** (WPA2 et WPA3 sur le même SSID) est pratique pour la compatibilité, mais un attaquant peut forcer un client à utiliser WPA2. Planifie le passage au WPA3 seul dès que le parc le permet.

## Exercice

**Des objets connectés ne gèrent que WPA2-Personnel. Comment éviter qu’ils partagent tous le même mot de passe ?**

<details><summary>Voir le corrigé</summary>

Utiliser une **clé par appareil** (identity PSK, DPSK, MPSK selon les constructeurs) : le serveur RADIUS associe une clé différente à chaque adresse MAC ou groupe d’appareils, et peut attribuer le VLAN correspondant. Une clé compromise ne concerne qu’un appareil.

</details>
