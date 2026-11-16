---
titre: Les équipements
nom: Switch, routeur, point d’accès, pare-feu
idee: Le switch relie les appareils d’un même lieu, le routeur relie des réseaux entre eux, le point d’accès remplace le câble par des ondes et le pare-feu filtre.
duree: [8]
retenir:
  - Le **switch** relie les appareils d’un **même réseau local**.
  - Le **routeur** relie **des réseaux différents** — c’est la porte de sortie vers Internet.
  - Le **point d’accès** Wi-Fi remplace le câble par des ondes ; le **pare-feu** décide quels échanges sont autorisés.
  - Une box Internet réunit tous ces rôles dans un seul boîtier.
---

## Le problème : relier beaucoup d’appareils

Avec deux ordinateurs, un seul câble suffit à les relier. Avec trente, il faudrait des centaines de câbles pour relier chacun à tous les autres. On utilise donc des **équipements intermédiaires**, chacun avec un rôle précis. Voici les quatre que tu croiseras partout.

```topologie
titre: Les équipements d’un petit réseau d’entreprise
Net nuage 2,0 "Internet"
FW parefeu 2,1 "Pare-feu"
R routeur 2,2 "Routeur"
SW switch 2,3 "Switch"
PC1 pc 0,4 "Poste"
PC2 pc 1,4 "Poste"
AP ap 3,4 "Point d’accès"
Srv serveur 4,4 "Serveur"
Tel portable 3,5 "Portable"
Net -- FW
FW -- R
R -- SW
SW -- PC1
SW -- PC2
SW -- AP
SW -- Srv
AP ~~ Tel "Wi-Fi"
```

## Le switch : le standardiste du réseau local

Un **switch** (commutateur en français) possède de nombreux ports, souvent 24 ou 48. On y branche les ordinateurs, les imprimantes, les téléphones, les points d’accès.

Son travail : **livrer chaque message au bon appareil du réseau local**, et seulement à lui. Pour cela, il apprend quel appareil est branché sur quel port, en regardant l’adresse de chaque message qui arrive. C’est comme un standardiste qui saurait, au bout de quelques minutes, dans quel bureau se trouve chaque employé.

## Le routeur : la douane entre les réseaux

Un **routeur** relie des **réseaux différents** : le réseau de l’entreprise et Internet, ou le réseau du siège et celui d’une agence. Il lit l’adresse de destination de chaque message et choisit par où l’envoyer pour qu’il se rapproche de sa destination.

Pour un ordinateur, le routeur est la **passerelle** : la porte qu’on emprunte dès qu’un message doit sortir du réseau local.

> [!TIP] Switch ou routeur ?
> Pose-toi la question : « est-ce que je reste dans le même réseau local ? » Si oui, c’est le switch qui livre. Si le message doit sortir vers un autre réseau, il passe par le routeur.

## Le point d’accès Wi-Fi : le câble devient une onde

Un **point d’accès** (*access point*, AP) est relié au switch par un câble, et diffuse le réseau par ondes radio. Les ordinateurs portables et les téléphones s’y connectent sans fil. Pour le réseau, c’est un peu comme une prise murale invisible qui couvre toute une pièce.

## Le pare-feu : le vigile

Un **pare-feu** (*firewall*) observe les échanges qui le traversent et **décide** lesquels sont autorisés : « les employés peuvent consulter le Web, mais personne depuis Internet ne peut se connecter directement aux ordinateurs du bureau ». Il se place surtout entre le réseau de l’entreprise et Internet, mais aussi entre des zones internes sensibles.

## Et les serveurs ?

Un **serveur** est un ordinateur qui **rend un service** aux autres : héberger des fichiers, un site Web, la messagerie, les comptes des utilisateurs. Ce n’est pas un équipement réseau à proprement parler, mais c’est souvent la destination des messages.

## Et la box de la maison ?

La box Internet est un **tout-en-un** : un routeur (pour sortir vers Internet), un petit switch (les 4 prises à l’arrière), un point d’accès Wi-Fi et un pare-feu simple. En entreprise, ces rôles sont séparés dans des équipements dédiés, plus puissants et plus faciles à surveiller.

| Équipement | Relie… | Regarde… | Analogie |
|---|---|---|---|
| Switch | les appareils d’un même réseau local | l’adresse matérielle (MAC) | le standardiste |
| Routeur | des réseaux différents | l’adresse IP | la douane, l’aiguilleur |
| Point d’accès | des appareils sans fil au réseau | — | une prise invisible |
| Pare-feu | des zones de confiance différentes | adresses, ports, applications | le vigile |

## Les mots à connaître

- **Switch** — Équipement qui relie les appareils d’un même réseau local et livre chaque message au bon port. En français : commutateur.
- **Routeur** — Équipement qui relie des réseaux différents et choisit le chemin des messages entre eux.
- **Passerelle** — Pour un ordinateur, l’adresse du routeur à qui confier les messages qui sortent du réseau local.
- **Point d’accès** — Équipement qui diffuse le réseau par ondes Wi-Fi.
- **Pare-feu** — Équipement qui autorise ou bloque les échanges selon des règles.
- **Serveur** — Ordinateur qui rend un service aux autres (fichiers, site Web, messagerie…).
- **Port** — Prise physique d’un équipement où l’on branche un câble. Le mot désigne aussi, plus tard, un numéro de service : on le verra dans la fiche [Les protocoles](protocoles.md).

## Teste-toi

**1.** Deux ordinateurs du même bureau, branchés sur le même switch, s’échangent un fichier. Le routeur intervient-il ?

<details><summary>Voir la réponse</summary>

**Non.** Ils sont dans le même réseau local : le switch livre directement les messages de l’un à l’autre. Le routeur n’intervient que lorsqu’un message doit sortir du réseau local.

</details>

**2.** Dans une entreprise, l’accès Internet fonctionne mais personne ne peut imprimer. Quel équipement soupçonnes-tu en premier : le routeur ou le switch ?

<details><summary>Voir la réponse</summary>

Plutôt le **switch** (ou le câble et le port de l’imprimante) : l’impression reste dans le réseau local, alors qu’Internet, qui passe par le routeur, fonctionne. Cette façon de raisonner — « qu’est-ce qui marche, qu’est-ce qui ne marche pas, quel équipement est commun » — est la base du dépannage.

</details>
