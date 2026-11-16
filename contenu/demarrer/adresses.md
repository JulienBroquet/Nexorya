---
titre: Les trois adresses
nom: Nom, adresse IP, adresse MAC
idee: Un appareil se désigne de trois façons — un nom pour les humains, une adresse IP pour trouver son réseau dans le monde, une adresse MAC pour le livrer sur le réseau local.
duree: [10]
retenir:
  - Le **nom** (`www.exemple.fr`) est pour les humains ; le **DNS** le traduit en adresse IP.
  - L’**adresse IP** (`192.168.1.20`) indique **le réseau et la machine** ; les routeurs l’utilisent pour acheminer le paquet.
  - L’**adresse MAC** (`3c:22:fb:1a:09:7e`) identifie la **carte réseau** ; le switch l’utilise pour livrer sur le réseau local.
---

## Le problème : retrouver une machine parmi des milliards

Quand tu tapes `www.wikipedia.org`, ton ordinateur doit retrouver **une machine précise** parmi des milliards. Pour y arriver, le réseau utilise trois sortes d’adresses, chacune à un moment différent du voyage.

> [!TIP] L’analogie de l’employé
> Pour joindre Marie Dupont, tu peux utiliser son **nom** (facile à retenir), l’**adresse de son entreprise** (pour que la poste trouve la ville, la rue, le bâtiment) et son **numéro de bureau** (pour que l’accueil lui remette le courrier). Sur un réseau : le **nom DNS**, l’**adresse IP** et l’**adresse MAC**.

## 1. Le nom : pour les humains

`www.wikipedia.org`, `intranet.monentreprise.fr`, `imprimante-etage2` : les noms sont faciles à retenir, mais les équipements réseau ne savent pas les utiliser. Avant tout échange, l’ordinateur demande à un serveur spécial, le **DNS** (*Domain Name System*), de traduire le nom en adresse IP. C’est l’annuaire du réseau.

## 2. L’adresse IP : pour trouver le réseau

Une adresse IP ressemble à `192.168.1.20` : quatre nombres de 0 à 255, séparés par des points (c’est l’**IPv4** ; il existe aussi l’IPv6, plus longue, comme `2001:db8::20`).

Elle contient **deux informations** :

- **le réseau** auquel la machine appartient (comme la ville et la rue) ;
- **la machine** dans ce réseau (comme le numéro de la maison).

Avec `192.168.1.20` dans un réseau `192.168.1.x`, le réseau est `192.168.1` et la machine est la numéro `20`. Les **routeurs** utilisent cette adresse pour faire avancer le paquet de réseau en réseau jusqu’à la bonne destination.

L’adresse IP est **attribuée** à une machine selon l’endroit où elle est branchée : ton portable n’a pas la même adresse IP chez toi et au bureau. Le plus souvent, elle est donnée automatiquement par un service appelé **DHCP**.

## 3. L’adresse MAC : pour livrer sur le réseau local

Une adresse MAC ressemble à `3c:22:fb:1a:09:7e` : six paires de caractères hexadécimaux (chiffres de 0 à 9 et lettres de A à F). Elle est **gravée dans la carte réseau** par le fabricant et ne change pas quand on déplace l’appareil.

Elle sert à la **dernière étape** : livrer le message à la bonne carte réseau sur le réseau local. C’est l’adresse que lit le **switch**.

## Les trois ensemble

```sequence
titre: Ce qui se passe quand tu tapes un nom de site
Ordinateur | Serveur DNS | Box (passerelle) | Serveur Web
Ordinateur -> Serveur DNS : « quelle est l’adresse IP de www.exemple.fr ? »
Serveur DNS --> Ordinateur : « c’est 203.0.113.10 »
note Ordinateur : 203.0.113.10 n’est pas dans mon réseau : je passe par la passerelle
Ordinateur -> Box (passerelle) : paquet pour l’IP 203.0.113.10, remis à l’adresse MAC de la box
Box (passerelle) -> Serveur Web : la box fait suivre vers Internet
Serveur Web --> Ordinateur : la page revient par le même principe
```

Remarque l’étape 4 : le paquet est destiné à l’**IP du serveur**, mais il est remis à l’**adresse MAC de la box**. L’adresse IP indique la destination finale, l’adresse MAC indique la **prochaine étape**. C’est l’une des idées les plus importantes de tout le parcours.

| | Nom | Adresse IP | Adresse MAC |
|---|---|---|---|
| Exemple | `www.exemple.fr` | `192.168.1.20` | `3c:22:fb:1a:09:7e` |
| Pour qui ? | Les humains | Les routeurs | Les switches et cartes réseau |
| Portée | Monde entier | Monde entier (ou réseau privé) | Réseau local seulement |
| Change si on déplace l’appareil ? | Non | Oui | Non |
| Qui la fournit ? | Le DNS | Le DHCP ou l’administrateur | Le fabricant |

## Les mots à connaître

- **Adresse IP** — Adresse logique d’un appareil, qui indique son réseau et son numéro dans ce réseau.
- **Adresse MAC** — Adresse physique gravée dans une carte réseau, utilisée pour livrer les trames sur le réseau local.
- **DNS** — *Domain Name System*, service qui traduit un nom (www.exemple.fr) en adresse IP.
- **DHCP** — *Dynamic Host Configuration Protocol*, service qui donne automatiquement une adresse IP aux appareils.
- **Hexadécimal** — Façon d’écrire les nombres avec 16 symboles : 0 à 9 puis A à F.

## Teste-toi

**1.** Tu emportes ton portable du bureau à la maison. Laquelle de ses adresses change ?

<details><summary>Voir la réponse</summary>

**Son adresse IP**, parce qu’elle dépend du réseau où il est connecté. Son adresse MAC reste la même : elle est gravée dans la carte réseau. (Certains systèmes récents utilisent une adresse MAC aléatoire par réseau Wi-Fi pour protéger la vie privée, mais le principe reste vrai.)

</details>

**2.** Un collègue peut ouvrir `http://10.1.1.50` mais pas `http://intranet.monentreprise.fr`, qui désigne le même serveur. Quel service soupçonnes-tu ?

<details><summary>Voir la réponse</summary>

**Le DNS.** L’accès par adresse IP fonctionne, donc le réseau et le serveur vont bien. Ce qui échoue, c’est la traduction du nom en adresse IP.

</details>
