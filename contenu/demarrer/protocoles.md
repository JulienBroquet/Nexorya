---
titre: Les protocoles
nom: Des règles communes et des numéros de port
idee: Un protocole est un ensemble de règles que deux appareils suivent pour se comprendre ; le numéro de port indique à quel service un message est destiné.
duree: [8]
retenir:
  - Un **protocole** fixe le format des messages et l’ordre des échanges.
  - Les protocoles s’empilent — **Ethernet** pour le local, **IP** pour le chemin, **TCP ou UDP** pour le transport, puis le protocole de l’application (HTTP, DNS…).
  - Le **numéro de port** désigne le service visé sur la machine — 443 pour un site Web sécurisé, 53 pour le DNS.
---

## Le problème : se comprendre sans se connaître

Ton téléphone, fabriqué en Corée, affiche un site hébergé sur un serveur américain, à travers des équipements chinois, européens et américains. Pour que cela marche, tous doivent suivre **exactement les mêmes règles**. Ces règles s’appellent des **protocoles**.

Un protocole précise :

- **le format des messages** : quelles informations, dans quel ordre, sur combien d’octets ;
- **l’ordre des échanges** : qui parle en premier, comment on répond, que faire en cas d’erreur.

> [!TIP] L’analogie du coup de téléphone
> Quand tu appelles quelqu’un, il y a un protocole implicite : il décroche et dit « allô », tu te présentes, vous parlez chacun votre tour, vous vous dites au revoir avant de raccrocher. Si l’un des deux ne suit pas ces règles, la conversation devient confuse.

## Des protocoles qui s’empilent

Aucun protocole ne fait tout. Chacun s’occupe d’une partie du travail, et ils s’empilent comme les enveloppes de la fiche [Un message en paquets](paquet.md).

| Rôle | Protocoles typiques | Question qu’il résout |
|---|---|---|
| Application | HTTP (Web), DNS (noms), SMTP (e-mails) | Que veut dire ce message pour l’application ? |
| Transport | **TCP** (fiable) ou **UDP** (rapide) | À quel service le remettre, et faut-il garantir l’arrivée ? |
| Réseau | **IP** | Par quel chemin l’envoyer à travers les réseaux ? |
| Liaison locale | **Ethernet**, **Wi-Fi** | Comment le transmettre à l’appareil voisin ? |

**TCP** et **UDP** méritent un mot dès maintenant :

- **TCP** fonctionne comme un recommandé avec accusé de réception : il vérifie que tout est arrivé, dans l’ordre, et renvoie ce qui manque. On l’utilise pour le Web, les e-mails, les fichiers.
- **UDP** fonctionne comme une carte postale : envoyée sans vérification, mais sans perte de temps. On l’utilise pour la voix, la vidéo en direct, le DNS.

## Le numéro de port : quel service ?

Un serveur peut faire plusieurs choses à la fois : héberger un site Web, recevoir des e-mails, permettre la connexion à distance. Comment savoir à quel service un message est destiné ? Grâce au **numéro de port**, inscrit dans l’enveloppe transport.

Si l’adresse IP est l’adresse de l’immeuble, le port est le **numéro de l’appartement**.

| Port | Protocole | Service |
|---|---|---|
| 53 | DNS | Traduire un nom en adresse IP |
| 80 | HTTP | Site Web non chiffré |
| 443 | HTTPS | Site Web chiffré (le cadenas du navigateur) |
| 22 | SSH | Administrer un serveur ou un équipement à distance |
| 25 / 587 | SMTP | Envoyer des e-mails |
| 3389 | RDP | Bureau à distance Windows |

```sequence
titre: Un message adressé à un service précis
Ordinateur | Serveur (IP 203.0.113.10)
Ordinateur -> Serveur (IP 203.0.113.10) : vers 203.0.113.10, port 443 (HTTPS)
note Serveur (IP 203.0.113.10) : le système remet le message au service qui écoute sur le port 443 : le serveur Web
Serveur (IP 203.0.113.10) --> Ordinateur : réponse depuis le port 443
```

> [!NOTE]
> Le mot « port » a deux sens en réseau. Le **port physique** est une prise d’un switch ou d’un routeur. Le **port logique** est un numéro de service (443, 53…). Le contexte permet toujours de savoir lequel est utilisé.

## Qui écrit ces règles ?

Les protocoles d’Internet sont décrits dans des documents publics appelés **RFC** (*Request for Comments*), publiés par l’IETF. Ethernet et le Wi-Fi sont normalisés par l’**IEEE** (d’où des noms comme 802.3 ou 802.11). Ces normes ouvertes expliquent pourquoi un équipement de n’importe quelle marque peut dialoguer avec n’importe quel autre.

## Les mots à connaître

- **Protocole** — Ensemble de règles qui fixent le format des messages et l’ordre des échanges entre appareils.
- **TCP** — *Transmission Control Protocol*, transport fiable : il vérifie l’arrivée des données et renvoie ce qui manque.
- **UDP** — *User Datagram Protocol*, transport rapide et simple, sans vérification d’arrivée.
- **Numéro de port** — Numéro qui désigne le service visé sur une machine (443 pour HTTPS, 53 pour le DNS…).
- **RFC** — Document public qui décrit un protocole d’Internet.

## Teste-toi

**1.** Un serveur héberge à la fois un site Web sécurisé et le service de connexion à distance SSH. Comment le serveur sait-il à quel service remettre un message entrant ?

<details><summary>Voir la réponse</summary>

Grâce au **numéro de port de destination** : 443 pour le site Web sécurisé (HTTPS), 22 pour SSH. L’adresse IP désigne la machine, le port désigne le service sur cette machine.

</details>

**2.** Pour un appel vidéo en direct, vaut-il mieux renvoyer une image perdue ou passer à la suivante ? Quel transport convient ?

<details><summary>Voir la réponse</summary>

Mieux vaut **passer à la suivante** : une image qui arrive une seconde trop tard ne sert plus à rien. On utilise donc plutôt **UDP**, plus rapide, quitte à perdre de temps en temps un petit morceau.

</details>
