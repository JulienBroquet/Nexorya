---
titre: Qu’est-ce qu’un réseau ?
nom: Des machines qui échangent des messages
idee: Un réseau, ce sont des appareils reliés entre eux et des règles communes pour s’échanger des messages.
duree: [8]
retenir:
  - Un réseau = des **appareils**, des **liaisons** (câble, fibre, ondes) et des **règles** communes (les protocoles).
  - Un **réseau local** (LAN) couvre une maison ou un bâtiment ; **Internet** relie des millions de réseaux entre eux.
  - Chaque échange suit le même principe — un **émetteur**, un **destinataire**, un **message** avec une adresse.
---

## Un réseau, tu en utilises déjà dix

Quand ton téléphone se connecte au Wi-Fi de la maison, quand tu imprimes depuis ton ordinateur, quand tu regardes une vidéo, quand tu paies par carte dans un magasin : à chaque fois, des appareils **s’échangent des messages**. L’ensemble des appareils et des liaisons qui permettent ces échanges, c’est un **réseau**.

Un réseau informatique a toujours trois ingrédients :

| Ingrédient | Exemples | Rôle |
|---|---|---|
| **Des appareils** | ordinateur, téléphone, imprimante, serveur, box, switch | Ils envoient, reçoivent ou relaient les messages. |
| **Des liaisons** | câble Ethernet, fibre optique, ondes Wi-Fi | Elles transportent physiquement les messages. |
| **Des règles communes** | Wi-Fi, Ethernet, IP, HTTP… | Elles permettent aux appareils de se comprendre. On les appelle des **protocoles**. |

> [!TIP] L’analogie de la poste
> Envoyer un message sur un réseau ressemble à envoyer une lettre. Il faut l’**adresse** du destinataire, la tienne pour la réponse, un **format** que la poste comprend (enveloppe, timbre), et des **centres de tri** qui font avancer la lettre vers sa destination. Sur un réseau, les centres de tri s’appellent des **switches** et des **routeurs**.

## Petit réseau, grand réseau

```topologie
titre: Le réseau d’une maison
Net nuage 1,0 "Internet"
Box routeur 1,1 "Box Internet" "routeur + Wi-Fi"
PC pc 0,2 "Ordinateur"
Tel portable 1,2 "Portable"
Imp imprimante 2,2 "Imprimante"
Net -- Box "fibre ou ADSL"
Box -- PC "câble"
Box ~~ Tel "Wi-Fi"
Box ~~ Imp "Wi-Fi"
```

- Le **réseau local**, ou **LAN** (*Local Area Network*), relie les appareils d’un même lieu : une maison, un bureau, une école. Ici, l’ordinateur, le portable et l’imprimante.
- La **box** relie ce réseau local à **Internet**. Internet n’est pas un réseau unique : c’est un **réseau de réseaux**, des millions de réseaux reliés entre eux par des opérateurs.

Dans une entreprise, c’est le même principe en plus grand : des centaines de postes, des switches dans chaque étage, des serveurs dans une salle dédiée, plusieurs bâtiments, plusieurs sites dans plusieurs villes. Tout ce parcours Nexorya consiste à comprendre comment ce grand réseau fonctionne.

## Comment un message voyage

Prenons un cas simple : ton ordinateur imprime un document sur l’imprimante du bureau.

```sequence
titre: Un échange réseau, vu de très haut
Ordinateur | Switch | Imprimante
Ordinateur -> Switch : message « à l’imprimante, de la part de l’ordinateur »
Switch -> Imprimante : le switch relaie le message au bon destinataire
Imprimante --> Switch : réponse « bien reçu »
Switch --> Ordinateur : le switch relaie la réponse
```

Dans cet échange, on retrouve trois idées qui reviendront partout :

1. **Chaque appareil a une adresse**, comme une maison a une adresse postale. Sans adresse, impossible de savoir à qui livrer un message.
2. **Le message est découpé et emballé** avant de partir : on verra pourquoi dans la fiche [Un message en paquets](paquet.md).
3. **Des équipements intermédiaires relaient le message** sans le lire en entier : ils regardent seulement l’adresse, comme un facteur regarde l’enveloppe.

## Pourquoi c’est souvent invisible

Quand tout fonctionne, on ne voit rien : la page s’affiche, le document s’imprime. Le réseau devient visible **quand il tombe en panne** — « Internet ne marche pas », « l’imprimante est hors ligne ». Le métier de l’administrateur réseau consiste justement à faire en sorte que tout reste invisible, et à trouver vite la cause quand ce n’est plus le cas.

> [!NOTE]
> « Internet ne marche pas » peut cacher des dizaines de causes différentes : un câble débranché, un Wi-Fi saturé, une adresse mal configurée, un nom de site mal traduit, un serveur en panne à l’autre bout du monde. Tout l’intérêt de comprendre le réseau, c’est de pouvoir **localiser** le problème au lieu de redémarrer au hasard.

## Les mots à connaître

- **LAN** — *Local Area Network*, réseau local d’un même lieu (maison, bureau, bâtiment).
- **Internet** — Réseau mondial formé de millions de réseaux interconnectés par des opérateurs.
- **Liaison** — Support physique qui transporte les messages : câble en cuivre, fibre optique ou ondes radio.
- **Émetteur / destinataire** — L’appareil qui envoie un message et celui à qui il est destiné.

## Teste-toi

**1.** Ton téléphone est connecté au Wi-Fi de la maison et regarde une vidéo hébergée aux États-Unis. Combien de réseaux le message traverse-t-il, au minimum ?

<details><summary>Voir la réponse</summary>

**Au moins deux, et en réalité bien plus.** Ton réseau local (le Wi-Fi de la box), puis le réseau de ton fournisseur d’accès, puis souvent ceux d’un ou plusieurs autres opérateurs, puis le réseau de l’hébergeur de la vidéo. C’est pour cela qu’on dit qu’Internet est un **réseau de réseaux**.

</details>

**2.** Cite les trois ingrédients de tout réseau.

<details><summary>Voir la réponse</summary>

Des **appareils** (qui envoient, reçoivent ou relaient), des **liaisons** (câble, fibre, ondes) et des **règles communes**, les protocoles, pour que les appareils se comprennent.

</details>
