---
titre: Un message en paquets
nom: Découper, emballer, déballer
idee: Un message est découpé en petits morceaux, et chaque morceau est emballé dans plusieurs enveloppes successives, chacune lue par un équipement différent.
duree: [9]
retenir:
  - Un gros message est **découpé en paquets** de 1 500 octets environ, qui voyagent indépendamment.
  - Chaque paquet est **emballé dans plusieurs enveloppes** (les en-têtes) — c’est l’**encapsulation**.
  - Chaque équipement ne lit **que l’enveloppe qui le concerne** — le switch lit l’adresse MAC, le routeur l’adresse IP.
---

## Pourquoi découper ?

Une photo de 3 Mo, une page Web, un fichier de 2 Go : on ne les envoie pas d’un seul bloc. Le message est **découpé en petits morceaux**, en général d’environ 1 500 octets au maximum, qu’on appelle des **paquets**.

Trois bonnes raisons :

- **Partager la route.** Si ton téléchargement de 2 Go occupait le câble d’un seul bloc, plus personne ne pourrait rien envoyer pendant ce temps. Avec des paquets, les messages de chacun s’intercalent.
- **Réparer à moindre coût.** Si un morceau est abîmé en route, on ne renvoie que ce morceau, pas tout le fichier.
- **Passer par plusieurs chemins.** Des paquets d’un même message peuvent emprunter des routes différentes et être remis dans l’ordre à l’arrivée.

## L’encapsulation : des enveloppes dans des enveloppes

Chaque morceau est emballé **dans plusieurs enveloppes successives**. Chaque enveloppe porte les informations utiles à une étape du voyage. On appelle ces enveloppes des **en-têtes**, et le fait d’emballer, l’**encapsulation**.

| Enveloppe (de l’intérieur vers l’extérieur) | Ce qu’elle contient | Qui la lit |
|---|---|---|
| Les **données** | Le morceau de page Web, de photo, de message… | L’application à l’arrivée (navigateur, messagerie). |
| L’enveloppe **transport** | Le numéro du service visé (le Web, la messagerie…) et un numéro d’ordre pour remettre les morceaux dans l’ordre. | Les deux ordinateurs aux extrémités. |
| L’enveloppe **réseau (IP)** | L’adresse IP de l’expéditeur et celle du destinataire final. | Les **routeurs**, à chaque étape. |
| L’enveloppe **locale (Ethernet ou Wi-Fi)** | L’adresse MAC de l’appareil suivant sur le chemin, et un code de contrôle pour détecter les erreurs. | Le **switch** et la carte réseau voisine. |

```illustration
fichier: encapsulation.svg
legende: "De haut en bas, les données reçoivent un en-tête à chaque étape. Le nom change avec l’enveloppe extérieure : **segment**, puis **paquet**, puis **trame**."
alt: "Quatre lignes : données seules, puis TCP et données, puis IP, TCP et données, puis Ethernet, IP, TCP, données et FCS"
```

```sequence
titre: Emballer au départ, déballer à l’arrivée
Navigateur | Ordinateur | Réseau | Serveur Web
Navigateur -> Ordinateur : demande « donne-moi la page d’accueil »
note Ordinateur : ajoute l’enveloppe transport, puis IP, puis Ethernet
Ordinateur -> Réseau : paquet emballé : Ethernet [ IP [ transport [ données ] ] ]
note Réseau : switches et routeurs lisent seulement l’enveloppe qui les concerne
Réseau -> Serveur Web : le paquet arrive
note Serveur Web : retire chaque enveloppe et lit enfin la demande
```

> [!TIP] L’analogie du colis
> Tu glisses ta lettre dans une enveloppe portant le nom du service (« Service comptabilité »), elle-même dans un colis avec l’adresse de l’entreprise, lui-même dans le sac du transporteur avec le numéro du prochain entrepôt. À chaque entrepôt, on change le sac, mais le colis et la lettre ne bougent pas. C’est exactement ce qui se passe sur un réseau : **l’enveloppe Ethernet change à chaque étape, l’enveloppe IP reste la même de bout en bout**.

## Pourquoi c’est utile de le savoir

Quand quelque chose ne fonctionne pas, la question devient : **quelle enveloppe pose problème ?**

- Le câble est débranché : rien ne peut circuler, aucune enveloppe ne passe.
- L’adresse IP est mauvaise : l’enveloppe locale passe, mais les routeurs ne savent pas où envoyer le paquet.
- Le serveur Web est arrêté : tout le voyage se passe bien, mais personne ne répond à l’arrivée.

Les professionnels décrivent ces enveloppes avec un modèle en **couches**, le modèle OSI. Tu le découvriras au début du [niveau 1](../niveau-1/osi.md). Pour l’instant, retiens l’image des enveloppes successives.

## Les mots à connaître

- **Paquet** — Petit morceau d’un message, emballé avec les adresses nécessaires à son voyage.
- **En-tête** — Informations ajoutées devant les données pour une étape du voyage : adresses, numéros, contrôles.
- **Encapsulation** — Fait d’emballer les données dans des en-têtes successifs avant l’envoi.
- **Octet** — Groupe de 8 bits ; l’unité de base pour mesurer la taille des données.
- **Bit** — La plus petite information possible : 0 ou 1.

## Teste-toi

**1.** Un paquet traverse trois routeurs entre ton ordinateur et un serveur. L’adresse IP de destination change-t-elle en route ?

<details><summary>Voir la réponse</summary>

**Non.** L’enveloppe IP porte l’adresse du destinataire **final** et reste la même de bout en bout. C’est l’enveloppe locale (Ethernet) qui est refaite à chaque étape, avec l’adresse de l’équipement suivant. (Il existe une exception, la traduction d’adresses ou NAT, que tu verras au niveau 3.)

</details>

**2.** Pourquoi ne pas envoyer un fichier de 2 Go en un seul bloc ?

<details><summary>Voir la réponse</summary>

Il monopoliserait la liaison pendant tout son transfert, et la moindre erreur obligerait à tout renvoyer. Découpé en paquets, il partage la liaison avec les autres échanges, et seul un paquet abîmé doit être renvoyé.

</details>
