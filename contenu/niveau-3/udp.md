---
titre: UDP
nom: User Datagram Protocol
idee: UDP envoie des messages sans connexion ni vérification d’arrivée ; c’est rapide et simple, idéal quand une donnée en retard ne sert plus à rien.
osi: "4"
duree: [6, 12]
prerequis: [tcp]
retenir:
  - "UDP = **ports + longueur + contrôle d’erreur**, rien de plus — pas de connexion, pas de retransmission, pas d’ordre."
  - "Utilisé pour la **voix et la vidéo en direct**, le **DNS**, le **DHCP**, **NTP**, et par **QUIC** (HTTP/3)."
  - "Pour diagnostiquer UDP, pas de poignée de main à observer — un pare-feu peut le jeter **silencieusement**."
---

## Le problème : la fiabilité a un prix

TCP garantit tout, mais au prix d’une ouverture de connexion, d’accusés et de retransmissions. Pour un appel vocal, une syllabe renvoyée une demi-seconde plus tard ne sert à rien : il vaut mieux la perdre et passer à la suivante. Pour une question DNS, ouvrir une connexion juste pour un message de 50 octets serait du gaspillage.

> [!IMPORTANT] L’idée en une phrase
> UDP envoie chaque message tel quel, sans connexion préalable et sans vérifier qu’il arrive : c’est à l’application de décider quoi faire en cas de perte.

> [!TIP] L’analogie de la carte postale
> TCP, c’est le recommandé avec accusé de réception. UDP, c’est la carte postale : on l’écrit, on la poste, et l’on passe à autre chose. Pas de garantie, mais aucune attente.

## TCP ou UDP ?

| | TCP | UDP |
|---|---|---|
| Connexion | oui (SYN, SYN-ACK, ACK) | non |
| Garantie d’arrivée | oui, retransmissions | non |
| Ordre | rétabli | non garanti |
| Contrôle de congestion | oui | non (à la charge de l’application) |
| En-tête | 20 octets minimum | **8 octets** |
| Usages | Web, e-mail, fichiers, SSH | voix, vidéo en direct, DNS, DHCP, NTP, SNMP, jeux, QUIC |

```sequence
titre: Une requête DNS en UDP : pas de connexion, pas d’accusé de réception
Client | Résolveur DNS
Client -> Résolveur DNS : question : adresse de www.exemple.fr ? (UDP, port 53)
Résolveur DNS --> Client : réponse : 93.184.215.14
note Client, Résolveur DNS : 2 messages au total. Si la réponse se perd, c’est le client qui redemande après un délai.
```

## Les mots à connaître

- **UDP** — Protocole de transport simple, sans connexion ni garantie d’arrivée.
- **Datagramme** — Message UDP envoyé indépendamment des autres.
- **Sans connexion** — Fonctionnement où l’on envoie sans établir de session au préalable.

## Teste-toi

**Pourquoi la voix sur IP utilise-t-elle UDP plutôt que TCP ?**

<details><summary>Voir le corrigé</summary>

Une syllabe **retransmise** arriverait trop tard pour être utile, et TCP bloquerait les syllabes suivantes en attendant celle qui manque. Avec UDP, une perte produit un minuscule trou dans le son, que le téléphone masque, et la conversation continue.

</details>

<!-- approfondir -->

## L’en-tête UDP

```text
 0               16              31
+----------------+----------------+
|  Port source   |  Port destin.  |
+----------------+----------------+
|    Longueur    | Somme contrôle |
+----------------+----------------+
|           Données…              |
```

En IPv4, la somme de contrôle est facultative (0 = absente) ; en IPv6, elle est **obligatoire**, puisque l’en-tête IPv6 n’en a plus.

## Diagnostiquer un service UDP

Avec UDP, il n’y a pas de SYN/SYN-ACK pour prouver qu’un port est ouvert :

- si un port UDP est **fermé**, la machine renvoie en principe un **ICMP Port Unreachable** ;
- si un **pare-feu** jette le paquet, on n’obtient **rien** — exactement comme si le service fonctionnait mais ne répondait pas à cette requête-là.

On teste donc avec un **client du protocole lui-même** : `nslookup` ou `dig` pour le DNS, `ntpq -p` ou `w32tm /stripchart` pour NTP, `snmpwalk` pour SNMP. Les outils génériques (`nc -u`) donnent des résultats ambigus.

```bash
$ dig @10.99.0.53 intranet.exemple.test +short     # DNS en UDP 53
10.20.0.15
$ sudo tcpdump -ni eth0 udp port 53                 # voir les questions et réponses
```

## Pare-feu à états et UDP

Un pare-feu suit les « connexions » UDP en associant une réponse à une requête récente (même couple d’adresses et de ports) pendant un délai court (souvent 30 à 120 s). Pour les flux longs mais intermittents (voix, VPN), ce délai peut expirer : les applications envoient des messages de maintien (*keepalive*).

## UDP comme base d’autres protocoles

UDP sert de transport « nu » à des protocoles qui ajoutent leur propre fiabilité ou leur propre logique : **QUIC** (fiabilité, chiffrement, multiplexage, sur UDP 443), **RTP** (numérotation et horodatage des médias), **DTLS** (TLS pour datagrammes), **VXLAN** (UDP 4789), **WireGuard**. Voir [QUIC](quic.md) et [RTP](rtp.md).

## Exercice

**Un pare-feu bloque l’UDP 53 sortant d’un réseau. Les postes utilisent un DNS sur Internet. Que voient les utilisateurs, et comment le prouver ?**

<details><summary>Voir le corrigé</summary>

Les noms ne se résolvent plus (délais d’attente, « serveur introuvable »), alors que la navigation par adresse IP fonctionne. Preuve : `nslookup www.exemple.fr 1.1.1.1` échoue par délai d’attente, et une capture sur le poste montre des requêtes sans réponse. Les journaux du pare-feu montrent les rejets UDP/53.

</details>
