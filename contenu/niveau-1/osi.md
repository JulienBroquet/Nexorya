---
titre: Les modèles OSI et TCP/IP
nom: Une carte en couches pour tout le réseau
idee: Le modèle OSI découpe une communication en sept couches, chacune avec un rôle précis ; il sert de carte pour situer une technologie et localiser une panne.
osi: "1 à 7"
duree: [10, 20]
cle: true
retenir:
  - Sept couches OSI — **physique, liaison, réseau, transport, session, présentation, application**.
  - "Chaque couche a son unité et son adresse : **bit** (1), **trame** et adresse MAC (2), **paquet** et adresse IP (3), **segment** et port (4)."
  - Le modèle **TCP/IP** regroupe ces couches en quatre ; c’est lui qui décrit Internet tel qu’il fonctionne.
  - Dépanner **de bas en haut** — une couche ne peut pas fonctionner si celle du dessous est en panne.
---

## Le problème : trop de choses à la fois

Envoyer un message sur un réseau mélange des questions très différentes : comment transformer des 0 et des 1 en signal électrique ? À quel appareil voisin remettre le message ? Par quel chemin traverser la planète ? Comment s’assurer que tout est arrivé ? Comment le navigateur comprend-il la réponse ?

Si un seul protocole devait tout gérer, il serait énorme et impossible à faire évoluer. Les ingénieurs ont donc **découpé le problème en couches**. Chaque couche s’occupe d’une seule question et rend service à la couche du dessus.

> [!IMPORTANT] L’idée en une phrase
> Le modèle OSI est une **carte** : il découpe une communication en sept couches, de la plus concrète (le câble) à la plus abstraite (l’application). Il sert à situer chaque technologie et à localiser une panne.

## Les sept couches, de bas en haut

| N° | Couche | Question à laquelle elle répond | Exemples | Unité |
|---|---|---|---|---|
| 1 | **Physique** | Comment transformer des bits en signal ? | câble, fibre, ondes Wi-Fi, connecteurs | bit |
| 2 | **Liaison** | À quel appareil **voisin** remettre le message ? | Ethernet, Wi-Fi, adresses MAC, switch | trame |
| 3 | **Réseau** | Par quel **chemin** atteindre un autre réseau ? | IP, routeur, adresses IP | paquet |
| 4 | **Transport** | À quel **service** remettre, et faut-il garantir l’arrivée ? | TCP, UDP, numéros de port | segment |
| 5 | Session | Comment ouvrir et maintenir un dialogue ? | (rarement isolée en pratique) | — |
| 6 | Présentation | Sous quelle forme coder les données ? | encodage, compression, chiffrement | — |
| 7 | **Application** | Que signifie le message pour l’application ? | HTTP, DNS, SMTP | données |

> [!TIP] Un moyen mnémotechnique
> De bas en haut : « **P**our **L**e **R**éseau, **T**out **S**e **P**asse **A**utomatiquement » — Physique, Liaison, Réseau, Transport, Session, Présentation, Application.

En entreprise, on parle constamment des couches 1 à 4 et de la couche 7. Les couches 5 et 6 existent surtout dans la théorie : en pratique, leur rôle est assuré par l’application ou par TLS.

## Le voyage d’un message à travers les couches

Au départ, chaque couche **ajoute son en-tête** au message reçu de la couche du dessus : c’est l’**encapsulation**. À l’arrivée, chaque couche **retire** l’en-tête qui la concerne.

```sequence
titre: Encapsulation au départ, désencapsulation à l’arrivée
Application | Transport | Réseau | Liaison | Physique
Application -> Transport : données « GET /index.html »
Transport -> Réseau : segment = en-tête TCP (port 443) + données
Réseau -> Liaison : paquet = en-tête IP (adresses IP) + segment
Liaison -> Physique : trame = en-tête Ethernet (adresses MAC) + paquet + contrôle
note Physique : la trame devient une suite de bits, puis un signal électrique, lumineux ou radio
```

## Qui travaille à quelle couche ?

Chaque équipement ne lit que les couches dont il a besoin :

| Équipement | Couche la plus haute qu’il lit | Ce qu’il regarde |
|---|---|---|
| Câble, répéteur | 1 | rien, il transporte le signal |
| Switch | 2 | l’adresse MAC de destination |
| Routeur | 3 | l’adresse IP de destination |
| Pare-feu | 4 à 7 | adresses, ports, parfois l’application |
| Ordinateur, serveur | 7 | tout, jusqu’au contenu |

C’est pour cela qu’on parle de « switch de niveau 2 », de « routage de niveau 3 » ou de « pare-feu de niveau 7 ».

## Dépanner avec les couches

Une couche ne peut pas fonctionner si la couche du dessous est en panne. On dépanne donc **de bas en haut** :

1. **Couche 1** — le voyant du port est-il allumé ? le câble est-il branché ?
2. **Couche 2** — le poste est-il dans le bon VLAN ? le switch connaît-il son adresse MAC ?
3. **Couche 3** — le poste a-t-il une adresse IP et une passerelle correctes ? un `ping` passe-t-il ?
4. **Couche 4** — le port du service est-il ouvert, ou bloqué par un pare-feu ?
5. **Couche 7** — le service répond-il correctement ?

> [!WARNING]
> L’erreur la plus fréquente consiste à commencer par le haut — « le site doit être en panne » — alors que le câble est débranché. Partir du bas fait gagner un temps considérable.

## Les mots à connaître

- **Modèle OSI** — Modèle de référence qui découpe une communication réseau en sept couches.
- **Couche** — Niveau du modèle qui assure une fonction précise et rend service à la couche du dessus.
- **Trame** — Unité de données de la couche 2 (liaison), avec adresses MAC et code de contrôle.
- **Segment** — Unité de données de la couche 4 (transport), avec numéros de port.
- **Encapsulation** — Ajout successif des en-têtes de chaque couche au départ du message.
- **Modèle TCP/IP** — Modèle en quatre couches qui décrit le fonctionnement réel d’Internet.

## Teste-toi

**1.** Un switch reçoit une trame. Jusqu’à quelle couche lit-il le message pour décider où l’envoyer ?

<details><summary>Voir le corrigé</summary>

**Couche 2.** Le switch lit l’en-tête Ethernet et l’adresse MAC de destination. Il n’a pas besoin de l’adresse IP ni du contenu pour livrer la trame dans le réseau local. (Un « switch de niveau 3 » sait en plus router, mais c’est alors sa fonction de routeur qui lit l’IP.)

</details>

**2.** Un utilisateur dit : « le site de l’intranet ne s’affiche pas ». Son voyant réseau est éteint. Faut-il vérifier le serveur Web ?

<details><summary>Voir le corrigé</summary>

**Non, pas encore.** Le voyant éteint signale un problème de **couche 1**. Tant qu’elle ne fonctionne pas, aucune couche supérieure ne peut fonctionner. On vérifie le câble, la prise et le port du switch avant tout le reste.

</details>

**3.** Classe ces éléments par couche : adresse IP, port 443, adresse MAC, fibre optique, HTTP.

<details><summary>Voir le corrigé</summary>

Fibre optique : **1**. Adresse MAC : **2**. Adresse IP : **3**. Port 443 : **4**. HTTP : **7**.

</details>

<!-- approfondir -->

## OSI et TCP/IP : deux modèles, une même réalité

Le modèle **OSI** (*Open Systems Interconnection*) a été publié par l’ISO en 1984 comme modèle de référence. Le modèle **TCP/IP**, issu des travaux qui ont donné Internet, décrit les protocoles réellement utilisés, en quatre couches :

| Modèle TCP/IP (RFC 1122) | Couches OSI correspondantes | Protocoles |
|---|---|---|
| Application | 5, 6, 7 | HTTP, DNS, TLS, SSH, SMTP |
| Transport | 4 | TCP, UDP, QUIC (sur UDP) |
| Internet | 3 | IPv4, IPv6, ICMP |
| Accès réseau | 1, 2 | Ethernet, Wi-Fi, PPP |

Dans le métier, on utilise **le vocabulaire OSI** (« un problème de couche 2 ») pour décrire **les protocoles TCP/IP**. Les deux modèles ne s’opposent pas : l’un sert de langage commun, l’autre décrit l’implémentation.

## Ce que contient chaque en-tête

```text
Trame Ethernet (couche 2)
┌──────────────┬─────────────┬───────────┬───────────────────────────────┬─────┐
│ MAC dest. 6o │ MAC src. 6o │ Type 2o   │ Paquet IP (46 à 1500 octets)   │ FCS │
└──────────────┴─────────────┴───────────┴───────────────────────────────┴─────┘
                                          │
              Paquet IPv4 (couche 3)      ▼
              ┌──────────────────────────────────────────┬──────────────────┐
              │ Version, TTL, protocole, IP src, IP dest. │ Segment TCP/UDP  │
              │ (20 octets minimum)                       │                  │
              └──────────────────────────────────────────┴──────────────────┘
                                                            │
                                 Segment TCP (couche 4)     ▼
                                 ┌──────────────────────────┬──────────┐
                                 │ Port src, port dest, n° de │ Données  │
                                 │ séquence… (20 o minimum)  │ (HTTP…)  │
                                 └──────────────────────────┴──────────┘
```

Deux champs servent de **lien** entre les couches, pour que le récepteur sache à qui remettre le contenu :

- le champ **Type** (*EtherType*) de la trame : `0x0800` = IPv4, `0x86DD` = IPv6, `0x0806` = ARP ;
- le champ **Protocole** de l’en-tête IP : `6` = TCP, `17` = UDP, `1` = ICMP.

C’est ce qu’on appelle le **démultiplexage** : chaque couche lit un numéro qui désigne la couche suivante.

## Où se situent les technologies « entre deux couches » ?

Le modèle est un outil de raisonnement, pas une loi physique. Plusieurs technologies ne rentrent pas parfaitement dans une case :

| Technologie | Pourquoi elle est ambiguë | Classement courant |
|---|---|---|
| ARP | Utilise des trames Ethernet pour découvrir des adresses IP | « 2,5 » : entre 2 et 3 |
| MPLS | Insère une étiquette entre l’en-tête Ethernet et l’en-tête IP | « 2,5 » |
| TLS | Chiffre au-dessus de TCP, sous l’application | 6 (ou entre 4 et 7) |
| VXLAN | Transporte des trames Ethernet dans de l’UDP | tunnel : une couche 2 au-dessus d’une couche 4 |
| QUIC | Transport fiable construit au-dessus d’UDP | 4, implémenté dans l’application |

Quand une technologie est ambiguë, la bonne question n’est pas « quelle case ? » mais « **quel en-tête ajoute-t-elle, et qui le lit ?** ».

## Une méthode de dépannage par couches

| Couche | Questions | Outils |
|---|---|---|
| 1 | Lien établi ? vitesse et duplex corrects ? erreurs ? | voyant, `show interfaces`, testeur de câble, puissance optique |
| 2 | Bon VLAN ? MAC apprise ? boucle ? | `show mac address-table`, `show vlan`, `show spanning-tree` |
| 3 | Adresse, masque, passerelle ? route ? | `ipconfig`, `ping`, `traceroute`, `show ip route` |
| 4 | Port ouvert ? filtré ? | `Test-NetConnection -Port`, `nc -zv`, journaux du pare-feu |
| 7 | Réponse correcte de l’application ? certificat ? nom ? | navigateur, `curl -v`, `nslookup`, journaux applicatifs |

Deux stratégies complémentaires :

- **de bas en haut** quand le symptôme est flou (« plus rien ne marche ») ;
- **diviser pour régner** quand on a un indice : on teste directement une couche du milieu (un `ping` vers la passerelle, par exemple). S’il réussit, les couches 1 à 3 fonctionnent jusque-là, et l’on cherche plus haut.

## Exercices

**1.** Une capture montre une trame avec EtherType `0x0806`. Quel protocole transporte-t-elle, et y a-t-il un en-tête IP ?

<details><summary>Voir le corrigé</summary>

`0x0806` désigne **ARP**. Il n’y a **pas d’en-tête IP** : ARP est transporté directement dans la trame Ethernet, ce qui explique qu’on le classe « entre » les couches 2 et 3.

</details>

**2.** Un `ping` vers le serveur fonctionne, mais l’application, qui écoute sur TCP 8443, ne répond pas. Quelles couches sont mises hors de cause, et que tester ensuite ?

<details><summary>Voir le corrigé</summary>

Le ping prouve que les couches **1, 2 et 3** fonctionnent jusqu’au serveur. On teste ensuite la **couche 4** : `Test-NetConnection serveur -Port 8443` (Windows) ou `nc -zv serveur 8443` (Linux). Si le port est fermé ou filtré, on regarde le service sur le serveur et les pare-feu. S’il est ouvert, on remonte à la couche 7 (journaux de l’application, certificat).

</details>

**3.** Pourquoi un switch de niveau 2 n’a-t-il pas besoin de modifier l’en-tête IP, alors qu’un routeur doit au moins décrémenter le TTL ?

<details><summary>Voir le corrigé</summary>

Le switch reste **dans le même réseau** : il livre la trame telle quelle, sans toucher aux couches supérieures. Le routeur **fait passer le paquet d’un réseau à un autre** : il décrémente le TTL de l’en-tête IP (pour éviter les boucles de routage), recalcule la somme de contrôle IPv4 et fabrique une **nouvelle trame** avec de nouvelles adresses MAC pour le lien suivant.

</details>
