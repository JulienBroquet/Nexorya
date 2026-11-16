---
titre: ICMP
nom: Internet Control Message Protocol
idee: ICMP est le service de messages d’erreur et de contrôle d’IP ; c’est lui qui fait fonctionner ping et traceroute, et qui prévient quand un paquet ne peut pas être livré.
osi: "3"
duree: [7, 15]
prerequis: [ipv4]
retenir:
  - "**ping** = ICMP Echo Request / Echo Reply."
  - "**traceroute** s’appuie sur les messages **Time Exceeded** renvoyés quand le TTL tombe à 0."
  - "**Destination Unreachable** dit pourquoi un paquet n’a pas pu être livré (réseau, machine, port, fragmentation nécessaire)."
  - "Ne pas bloquer **tout** ICMP — certains messages sont indispensables au bon fonctionnement du réseau."
---

## Le problème : savoir pourquoi ça ne passe pas

IP envoie des paquets sans garantie. Si un paquet ne peut pas être livré — réseau inconnu, machine absente, paquet trop gros —, il faut un moyen de **prévenir l’expéditeur**. Il faut aussi des outils pour **tester** qu’une machine répond. Ce rôle est confié à ICMP.

> [!IMPORTANT] L’idée en une phrase
> ICMP est le « service de messages » d’IP : il transporte les tests (ping) et les avis d’erreur (destination injoignable, durée de vie dépassée).

## Les messages à connaître

| Type | Nom | Quand ? |
|---|---|---|
| 8 | **Echo Request** | envoyé par `ping` |
| 0 | **Echo Reply** | réponse au ping |
| 3 | **Destination Unreachable** | le paquet ne peut pas être livré ; un code précise pourquoi |
| 11 | **Time Exceeded** | le TTL est tombé à 0 en route (boucle, ou traceroute) |
| 5 | Redirect | « il y a un meilleur routeur pour cette destination » |

## Comment marche traceroute

`traceroute` envoie des paquets avec un **TTL volontairement petit**. Chaque routeur décrémente le TTL ; celui qui le fait tomber à 0 jette le paquet et renvoie un **Time Exceeded** : il révèle ainsi son adresse.

```sequence
titre: traceroute découvre le chemin routeur par routeur
PC | R1 | R2 | Serveur
PC -> R1 : paquet avec TTL = 1
R1 --> PC : Time Exceeded (R1 se révèle)
PC -> R2 : paquet avec TTL = 2 (R1 le fait passer, TTL = 1)
R2 --> PC : Time Exceeded (R2 se révèle)
PC -> Serveur : paquet avec TTL = 3
Serveur --> PC : réponse finale (Echo Reply ou Port Unreachable)
```

## Lire un ping qui échoue

| Message | Ce qu’il signifie |
|---|---|
| `Délai d’attente de la demande dépassé` | aucune réponse : machine éteinte, filtrage, ou chemin de retour cassé |
| `Hôte de destination inaccessible` (venant de ta propre machine) | ta machine ne trouve pas le voisin en ARP |
| `Réseau de destination inaccessible` (venant d’un routeur) | ce routeur n’a pas de route vers la destination |
| `TTL expiré lors du transit` | une **boucle de routage** probable |

## Les mots à connaître

- **ICMP** — Protocole de messages de contrôle et d’erreur associé à IP.
- **Echo Request / Echo Reply** — Messages ICMP utilisés par ping.
- **Time Exceeded** — Message envoyé quand le TTL d’un paquet atteint zéro.
- **Destination Unreachable** — Message indiquant qu’un paquet n’a pas pu être livré, avec un code qui précise la raison.

## Teste-toi

**1.** Un ping vers un serveur échoue, mais tu arrives à ouvrir son site Web. Le serveur est-il en panne ?

<details><summary>Voir le corrigé</summary>

**Non.** Le site fonctionne, donc le serveur répond. Le serveur ou un pare-feu **bloque simplement les pings** (ICMP Echo). Un ping qui échoue ne prouve pas qu’une machine est injoignable.

</details>

**2.** Un ping renvoie « TTL expiré lors du transit ». Que soupçonnes-tu ?

<details><summary>Voir le corrigé</summary>

Une **boucle de routage** : le paquet tourne entre des routeurs jusqu’à épuisement de son TTL. Un `traceroute` montrera les mêmes adresses qui se répètent.

</details>

<!-- approfondir -->

## Format

Un message ICMP est transporté dans IP (protocole n° 1) : type (8 bits), code (8 bits), somme de contrôle, puis un contenu qui dépend du type. Les **messages d’erreur** contiennent l’en-tête IP et les 8 premiers octets du paquet fautif : l’expéditeur sait ainsi exactement quel flux (adresses, ports) a échoué.

## Les codes de Destination Unreachable (type 3)

| Code | Signification | Émis par |
|---|---|---|
| 0 | Net unreachable | un routeur sans route |
| 1 | Host unreachable | le dernier routeur, si la machine ne répond pas en ARP |
| 3 | **Port unreachable** | la machine destination, si aucun service n’écoute sur ce port UDP |
| 4 | **Fragmentation needed and DF set** | un routeur, quand le paquet dépasse la MTU : essentiel à la PMTUD |
| 13 | Communication administratively prohibited | un routeur ou un pare-feu qui filtre (ACL) |

En IPv6, ICMPv6 (type 58) joue le même rôle et porte en plus [NDP](ndp.md) et la découverte de MTU (*Packet Too Big*, type 2).

## traceroute : Windows et Linux ne font pas pareil

| Outil | Paquets envoyés | Fin du parcours |
|---|---|---|
| `tracert` (Windows) | ICMP Echo Request | Echo Reply de la destination |
| `traceroute` (Linux, par défaut) | UDP vers des ports élevés (33434 et suivants) | Port Unreachable de la destination |
| `traceroute -T -p 443` | TCP SYN vers un port choisi | traverse mieux les pare-feu |

Un pare-feu qui laisse passer l’un et bloque l’autre donne deux résultats différents : la différence est elle-même une information.

```bash
$ traceroute -n 203.0.113.10
 1  192.168.1.1     0.9 ms  0.8 ms  0.8 ms
 2  10.142.0.1      5.6 ms  5.1 ms  5.9 ms
 3  * * *
 4  198.51.100.33   9.2 ms  9.0 ms  9.4 ms
 5  203.0.113.10   10.1 ms  9.8 ms 10.0 ms
```

La ligne `* * *` au saut 3 : ce routeur ne renvoie pas de Time Exceeded (filtrage ou limitation), mais il **fait passer** le trafic, puisque les sauts suivants répondent.

## Filtrer ICMP intelligemment

| À autoriser | Pourquoi |
|---|---|
| Type 3 (Destination Unreachable), surtout code 4 | découverte de la MTU du chemin ; diagnostic |
| Type 11 (Time Exceeded) | traceroute, diagnostic des boucles |
| Type 0 et 8 (Echo) **depuis les réseaux d’administration** | supervision |
| ICMPv6 : 1, 2, 3, 4, 133 à 137 | IPv6 ne fonctionne pas sans |

| À limiter ou bloquer | Pourquoi |
|---|---|
| Redirect (type 5) depuis Internet | peut détourner du trafic |
| Echo depuis Internet vers l’interne | réduit la cartographie par des tiers |

Les routeurs limitent eux-mêmes leur production de messages ICMP (*rate limiting*) pour se protéger : c’est pour cela que certains sauts de traceroute affichent des pertes sans qu’il y ait de problème.

```cisco
! Limiter la génération de messages Unreachable (Cisco IOS)
ip icmp rate-limit unreachable 500
! Ne pas envoyer d'Unreachable sur l'interface Internet
interface GigabitEthernet0/0/0
 no ip unreachables
 no ip redirects
```

> [!WARNING]
> `no ip unreachables` sur une interface empêche aussi l’envoi des messages « fragmentation nécessaire » depuis cette interface. Sur un routeur qui porte un tunnel, cela peut créer des trous noirs de MTU : utilise-le en connaissance de cause et complète avec `ip tcp adjust-mss`.

## Exercices

**1.** Un `traceroute` Linux vers un serveur s’arrête à la dernière ligne avec `* * *`, alors que `tracert` sous Windows atteint bien le serveur. Explique.

<details><summary>Voir le corrigé</summary>

Le `traceroute` Linux envoie de l’**UDP** vers des ports élevés : le pare-feu du serveur (ou devant lui) bloque cet UDP ou bloque l’émission des **Port Unreachable**. `tracert` envoie de l’**ICMP Echo**, autorisé. Le serveur est joignable ; ce sont les types de sondes qui diffèrent. `traceroute -I` (ICMP) ou `-T` (TCP) le confirmerait.

</details>

**2.** Un ping vers `10.30.0.50` renvoie « Réponse de 10.0.0.2 : réseau de destination inaccessible ». Que t’apprend ce message ?

<details><summary>Voir le corrigé</summary>

C’est le routeur **10.0.0.2** qui répond : il a reçu le paquet mais **n’a pas de route** vers `10.30.0.0`. Le problème se situe dans sa table de routage (route manquante, protocole de routage qui n’a pas appris le réseau). Tous les routeurs avant lui ont fait leur travail.

</details>
