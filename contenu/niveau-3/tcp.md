---
titre: TCP
nom: Transmission Control Protocol
idee: TCP établit une connexion entre deux applications et garantit que toutes les données arrivent, dans l’ordre, en renvoyant ce qui se perd et en ralentissant quand le réseau sature.
osi: "4"
duree: [10, 22]
prerequis: [ipv4, protocoles]
retenir:
  - "Ouverture en **trois temps** — SYN, SYN-ACK, ACK."
  - Chaque octet est **numéroté** ; le destinataire **accuse réception** ; ce qui manque est **retransmis**.
  - La **fenêtre** limite les données envoyées sans accusé ; le **contrôle de congestion** ralentit en cas de pertes.
  - "Une connexion = 4 valeurs — IP source, port source, IP destination, port destination."
---

## Le problème : IP ne garantit rien

IP fait de son mieux pour livrer chaque paquet, mais sans aucune promesse : un paquet peut se perdre, arriver en double ou après le suivant. Pour une page Web, un e-mail ou un fichier, c’est inacceptable : il manquerait des morceaux. Il faut une couche qui **vérifie** et **répare**.

> [!IMPORTANT] L’idée en une phrase
> TCP numérote les données, attend des accusés de réception, renvoie ce qui manque et remet tout dans l’ordre : l’application reçoit un flux complet, comme si le réseau était parfait.

> [!TIP] L’analogie du recommandé
> TCP, c’est un envoi en recommandé avec accusé de réception, page par page. Chaque page est numérotée. Si l’accusé d’une page n’arrive pas, on la renvoie. Le destinataire range les pages dans l’ordre avant de lire.

## Ouvrir une connexion : la poignée de main en trois temps

```sequence
titre: Ouverture d’une connexion TCP
Client | Serveur (port 443)
Client -> Serveur (port 443) : SYN : « je veux me connecter, mon numéro de départ est 1000 »
Serveur (port 443) --> Client : SYN-ACK : « d’accord, le mien est 5000, j’attends ton 1001 »
Client -> Serveur (port 443) : ACK : « bien reçu, j’attends ton 5001 »
note Client, Serveur (port 443) : la connexion est ouverte : les données peuvent circuler
```

Avant d’envoyer la moindre donnée, les deux côtés se mettent d’accord sur leurs **numéros de départ**. C’est ce qui permettra ensuite de repérer les manques et les doublons.

## Envoyer, accuser, renvoyer

1. L’émetteur envoie des segments numérotés.
2. Le destinataire répond par un **accusé de réception** (ACK) qui indique le prochain numéro attendu.
3. Si un accusé n’arrive pas à temps, l’émetteur **renvoie** le segment.
4. Le destinataire remet les données **dans l’ordre** à l’application.

## Ne pas noyer le destinataire ni le réseau

- **La fenêtre** : le destinataire annonce combien de données il peut encore recevoir. L’émetteur n’envoie pas plus.
- **Le contrôle de congestion** : l’émetteur démarre doucement, accélère tant que tout va bien, et **ralentit fortement** dès qu’il constate des pertes. C’est pour cela qu’un lien qui perd un peu de paquets fait chuter le débit des transferts.

## Fermer

La fermeture se fait par des segments **FIN** (fermeture polie, chaque côté termine) ou **RST** (coupure brutale, souvent signe d’un refus : port fermé, pare-feu, application plantée).

## Les mots à connaître

- **TCP** — Protocole de transport fiable, orienté connexion.
- **Segment** — Unité de données de TCP.
- **Poignée de main en trois temps** — Ouverture d’une connexion TCP par SYN, SYN-ACK, ACK.
- **Accusé de réception (ACK)** — Message qui confirme les données reçues en indiquant le prochain numéro attendu.
- **Retransmission** — Nouvel envoi d’un segment dont l’accusé n’est pas arrivé.
- **Fenêtre** — Quantité de données que l’émetteur peut envoyer sans attendre d’accusé.
- **Port** — Numéro qui identifie l’application à chaque extrémité.

## Teste-toi

**1.** Un poste envoie des SYN vers un serveur sur le port 443, mais ne reçoit jamais de SYN-ACK. Où chercher ?

<details><summary>Voir le corrigé</summary>

Le serveur ne répond pas à l’ouverture : il est injoignable, son service n’écoute pas, ou un **pare-feu** jette les SYN (ou les réponses). Si le serveur répondait par un **RST**, ce serait plutôt « port fermé » ou refus explicite.

</details>

**2.** Pourquoi un lien qui perd 2 % des paquets peut-il diviser par dix le débit d’un téléchargement ?

<details><summary>Voir le corrigé</summary>

Parce que TCP interprète chaque perte comme un signe de **congestion** et **réduit fortement** son débit avant de remonter progressivement. Avec des pertes répétées, il passe son temps à ralentir.

</details>

<!-- approfondir -->

## L’en-tête TCP

| Champ | Rôle |
|---|---|
| Port source / destination | identifient les applications |
| Numéro de séquence | position du premier octet du segment dans le flux |
| Numéro d’acquittement | prochain octet attendu de l’autre côté |
| Longueur d’en-tête | 20 octets sans options, jusqu’à 60 |
| Drapeaux | **SYN**, **ACK**, **FIN**, **RST**, PSH, URG, ECE, CWR |
| Fenêtre | espace disponible en réception (multiplié par le facteur d’échelle négocié) |
| Somme de contrôle | sur l’en-tête, les données et un pseudo-en-tête IP |
| Options | **MSS**, **window scale**, **SACK** (accusés sélectifs), horodatages |

## Le cycle de vie d’une connexion

| État | Signification |
|---|---|
| LISTEN | serveur en attente de connexions |
| SYN-SENT / SYN-RECEIVED | poignée de main en cours |
| ESTABLISHED | connexion ouverte |
| FIN-WAIT-1/2, CLOSE-WAIT, LAST-ACK | fermeture en cours |
| TIME-WAIT | côté qui a fermé en premier : attend 2 × MSL avant de libérer le couple de ports |

```bash
$ ss -tan state established '( dport = :443 )'
Recv-Q Send-Q  Local Address:Port    Peer Address:Port
0      0       10.10.0.57:51544      203.0.113.10:443
$ ss -tln            # ports TCP en écoute
```

```powershell
PS> Get-NetTCPConnection -State Listen | Sort LocalPort | Select LocalAddress, LocalPort, OwningProcess
PS> Test-NetConnection srv-erp -Port 443        # TcpTestSucceeded : True / False
```

Un grand nombre de connexions en **CLOSE-WAIT** côté serveur désigne une application qui ne ferme pas ses connexions ; une accumulation de **SYN-RECEIVED** peut signaler une attaque par inondation de SYN.

## Fiabilité : retransmissions rapides et SACK

- Le délai de retransmission (**RTO**) s’adapte à la latence mesurée.
- **Retransmission rapide** : après **trois ACK dupliqués** (le destinataire redemande toujours le même octet), l’émetteur renvoie le segment manquant sans attendre le RTO.
- **SACK** : le destinataire précise quels blocs il a reçus après le trou ; seul le manque est renvoyé.

## Contrôle de congestion

L’émetteur tient une **fenêtre de congestion** (cwnd), distincte de la fenêtre annoncée par le destinataire ; il envoie au plus le minimum des deux.

| Phase | Comportement |
|---|---|
| Démarrage lent (*slow start*) | cwnd double à chaque aller-retour |
| Évitement de congestion | cwnd augmente d’environ un segment par aller-retour |
| Perte détectée | cwnd est fortement réduite (divisée par deux, ou plus selon l’algorithme) |

Les algorithmes modernes (**CUBIC**, défaut sous Linux et Windows ; **BBR**, qui estime le débit et la latence plutôt que de réagir aux pertes) se comportent mieux sur les liens rapides et lointains.

## Ce que montre une capture

Dans Wireshark, les filtres suivants vont droit au problème :

| Filtre | Ce qu’il révèle |
|---|---|
| `tcp.flags.syn==1 && tcp.flags.ack==0` | tentatives de connexion |
| `tcp.flags.reset==1` | connexions refusées ou coupées |
| `tcp.analysis.retransmission` | pertes sur le chemin |
| `tcp.analysis.zero_window` | le récepteur est saturé (problème applicatif, pas réseau) |
| `tcp.analysis.duplicate_ack` | trous dans le flux |

> [!TIP]
> Une **fenêtre nulle** (*zero window*) signifie que l’application réceptrice ne lit pas assez vite : le réseau n’y est pour rien. Des **retransmissions**, au contraire, désignent des pertes sur le chemin. Savoir les distinguer évite des semaines d’accusations mutuelles entre équipes.

## Exercices

**1.** Une capture montre : SYN du client, puis RST-ACK immédiat du serveur. Que signifie-t-il ?

<details><summary>Voir le corrigé</summary>

Le serveur est **joignable** mais **aucune application n’écoute** sur ce port (ou un équipement répond à sa place pour refuser). Le problème n’est pas le réseau : vérifier le service sur le serveur et le numéro de port.

</details>

**2.** Un transfert vers un serveur de sauvegarde ralentit ; la capture montre beaucoup de « TCP ZeroWindow » envoyés par le serveur, et aucune retransmission. Qui doit enquêter ?

<details><summary>Voir le corrigé</summary>

L’équipe **système ou applicative** du serveur de sauvegarde : il annonce qu’il ne peut plus rien recevoir parce que son application (ou son disque) ne suit pas. Le réseau ne perd rien.

</details>

**3.** Calcule le débit maximal d’une connexion TCP avec une fenêtre de 256 Ko et une latence aller-retour de 40 ms.

<details><summary>Voir le corrigé</summary>

256 × 1 024 × 8 = 2 097 152 bits par aller-retour. 2 097 152 / 0,04 ≈ **52 Mb/s**, quelle que soit la vitesse du lien.

</details>
