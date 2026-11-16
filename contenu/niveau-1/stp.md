---
titre: STP
nom: Spanning Tree Protocol (IEEE 802.1D)
idee: STP garde les câbles de secours branchés mais en met certains en pause, pour qu’il n’existe jamais deux chemins actifs entre deux switches.
osi: "2"
duree: [8, 25]
prerequis: [mac, vlan]
retenir:
  - Une trame Ethernet n’a **pas de TTL** — une boucle entre switches sature tout le VLAN en quelques secondes.
  - STP élit un **pont racine** (plus petit Bridge ID = priorité, puis adresse MAC), garde un seul chemin actif vers lui et **bloque** les autres ports.
  - L’administrateur **choisit la racine** (`root primary`) et protège les ports d’accès avec **PortFast + BPDU Guard**.
  - En production, on utilise **Rapid PVST+** ou **MST** pour basculer en une seconde environ.
---

## Le problème : un câble de secours qui fait tout tomber

Une entreprise relie ses trois switches **en triangle** : si un câble est coupé, les deux autres permettent encore de passer. Bonne idée… sur le papier.

Souviens-toi de ce que fait un switch avec un **broadcast** (une trame destinée à tout le monde, comme une requête ARP) : il la recopie sur **tous ses ports**, sauf celui par lequel elle est arrivée.

```topologie
titre: Sans STP, un broadcast tourne sans fin dans le triangle
SW1 switch 1,0 "SW1"
SW2 switch 0,1 "SW2"
SW3 switch 2,1 "SW3"
PC pc 1,2 "PC"
SW1 -- SW2 "copie 1"
SW1 -- SW3 "copie 2"
SW2 -- SW3 "les copies se croisent"
PC -- SW2
```

1. Le PC envoie un broadcast à SW2.
2. SW2 le recopie vers SW1 **et** vers SW3.
3. SW1 renvoie sa copie vers SW3, SW3 renvoie la sienne vers SW1… et chacun les renvoie encore vers SW2.

La trame tourne **sans fin**, dans les deux sens, et se multiplie à chaque passage. Contrairement à un paquet IP, **une trame Ethernet n’a pas de compteur de durée de vie (TTL)** : rien ne l’arrête. En quelques secondes, les liens sont saturés, les processeurs des switches débordés et **plus rien ne fonctionne dans le VLAN**. On appelle cela une **tempête de broadcast**.

> [!IMPORTANT] L’idée en une phrase
> STP garde les câbles de secours branchés, mais **en met certains en pause** pour qu’il n’existe jamais deux chemins actifs entre deux switches. Si un câble actif tombe, un câble en pause reprend le travail.

## Comment STP décide, étape par étape

Imagine une **randonnée en groupe**. On désigne un point de ralliement, puis chacun prend le chemin le plus court pour le rejoindre. Les sentiers inutiles sont fermés par une barrière, qu’on rouvre si un sentier principal s’effondre.

| Étape | Ce que font les switches | Dans la randonnée |
|---|---|---|
| 1. Se parler | Ils échangent toutes les 2 secondes de petits messages appelés **BPDU**. | Les randonneurs discutent par talkie-walkie. |
| 2. Élire un chef | Ils élisent le **pont racine** : le switch qui a le plus petit identifiant. | On choisit le point de ralliement. |
| 3. Choisir le meilleur chemin | Chaque autre switch garde **un seul** port vers la racine, celui du chemin le moins « coûteux » (un lien rapide coûte moins cher). | Chacun prend le sentier le plus court. |
| 4. Mettre en pause le reste | Les ports qui fermeraient une boucle sont **bloqués** : ils ne transmettent plus de trames, mais continuent d’écouter les BPDU. | Les sentiers en trop sont fermés par une barrière. |
| 5. Réagir aux pannes | Si un lien actif tombe, STP recalcule et **débloque** un port de secours. | On rouvre la barrière. |

### Comment le pont racine est-il choisi ?

Chaque switch possède un **Bridge ID** fait de deux parties : une **priorité** (32768 par défaut, modifiable) et son **adresse MAC**. **Le plus petit Bridge ID gagne** : on compare d’abord la priorité, puis l’adresse MAC en cas d’égalité.

> [!WARNING]
> Si personne ne change les priorités, toutes valent 32768 et c’est la **plus petite adresse MAC** qui l’emporte… souvent celle du switch **le plus ancien**. Un vieux switch au fond d’un bureau peut ainsi devenir le centre de tout le réseau. C’est pourquoi l’administrateur **choisit lui-même** la racine : un switch central et robuste.

## Un exemple concret

L’administrateur a donné la priorité 24576 à SW1, le switch central. SW2 et SW3 ont gardé 32768, et SW2 a une adresse MAC plus petite que SW3. Tous les liens sont à 1 Gb/s.

```topologie
titre: Avec STP, un lien reste branché mais en pause
SW1 switch 1,0 "SW1" "racine, priorité 24576"
SW2 switch 0,1 "SW2"
SW3 switch 2,1 "SW3"
SW1 ++ SW2 "chemin actif"
SW1 ++ SW3 "chemin actif"
SW2 -x- SW3 "en pause"
```

- **La racine** est SW1, car 24576 est plus petit que 32768.
- **SW2** rejoint SW1 directement (un lien) plutôt qu’en passant par SW3 (deux liens). Même raisonnement pour SW3.
- **Le lien SW2–SW3** fermerait la boucle. STP bloque l’extrémité du switch qui a le plus grand Bridge ID : SW3.

Résultat : trois câbles branchés, **deux actifs**, un **en pause**. Si le câble SW1–SW3 est coupé, le port bloqué de SW3 se réactive et SW3 rejoint la racine en passant par SW2.

## Ce que tu verras sur un vrai switch

La commande `show spanning-tree vlan 10` affiche, en fin de sortie, le rôle de chaque port :

```text
Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- ----------
Gi1/0/1             Root FWD 4         128.1    P2p
Gi1/0/2             Altn BLK 4         128.2    P2p
Gi1/0/10            Desg FWD 4         128.10   P2p Edge
```

- **Root FWD** : port racine, il transmet (*forwarding*). C’est le chemin vers le pont racine.
- **Altn BLK** : port alternatif, **bloqué**. C’est le câble de secours en pause.
- **Desg FWD** : port désigné, il transmet. Ici vers un PC (*Edge* signifie port d’accès).

## Erreurs fréquentes

- **Désactiver STP « parce qu’il bloque un port »** : ce port bloqué est justement ce qui empêche la panne totale.
- **Relier deux prises murales avec un câble**, ou brancher un petit switch de bureau sur deux prises : cela crée une boucle. Sur un réseau bien configuré, la protection **BPDU Guard** coupe alors le port.
- **Laisser l’élection au hasard** : sans priorité choisie, la racine peut être le pire switch du réseau.

## Les mots à connaître

- **Boucle de niveau 2** — Situation où deux chemins actifs existent entre des switches : les trames tournent en rond.
- **Tempête de broadcast** — Multiplication incontrôlée des broadcasts dans une boucle, qui sature le réseau.
- **BPDU** — *Bridge Protocol Data Unit*, message de contrôle que les switches s’échangent pour construire l’arbre STP.
- **Pont racine** — Switch de référence élu par STP ; tous les chemins actifs mènent à lui.
- **Bridge ID** — Identifiant d’un switch pour STP : priorité puis adresse MAC. Le plus petit gagne l’élection.
- **Port racine** — Sur un switch qui n’est pas la racine, le port qui y mène par le meilleur chemin.
- **Port bloqué** — Port maintenu en pause pour casser une boucle, prêt à reprendre le relais.

## Teste-toi

**1.** Trois switches ont tous la priorité 32768. Leurs adresses MAC sont A = `0019.aa00.0001`, B = `0004.bb00.0002` et C = `0021.cc00.0003`. Lequel devient pont racine ?

<details><summary>Voir le corrigé</summary>

**B.** Les priorités sont égales, on compare donc les adresses MAC comme des nombres, de gauche à droite : `0004…` est plus petit que `0019…` et que `0021…`. B gagne alors que personne ne l’a choisi — exactement le piège décrit plus haut. Pour imposer la racine, on donnerait une priorité plus petite (par exemple 24576) au switch souhaité.

</details>

**2.** Un collègue voit qu’un port est « BLK » et propose de désactiver STP pour « récupérer ce lien ». Qu’en penses-tu ?

<details><summary>Voir le corrigé</summary>

**C’est une très mauvaise idée.** Ce port est bloqué parce qu’il fermerait une boucle. Sans STP, la boucle deviendrait active et le premier broadcast déclencherait une tempête qui paralyserait tout le VLAN. Le port bloqué n’est pas perdu : c’est le câble de secours. Pour utiliser plusieurs liens **en même temps**, la bonne technologie est l’agrégation de liens, [LACP](lacp.md).

</details>

**3.** Après la panne d’un câble, le réseau est coupé 40 secondes avec le STP classique, mais une seconde avec RSTP. D’où vient la différence ?

<details><summary>Voir le corrigé</summary>

Le STP classique est prudent : avant de débloquer un port, il attend la fin de plusieurs temporisateurs (15 s d’écoute, 15 s d’apprentissage, parfois 20 s de plus pour constater la panne). [RSTP](rstp.md) remplace ces attentes par un dialogue direct entre switches voisins et prépare à l’avance un port de secours qui bascule aussitôt.

</details>

<!-- approfondir -->

## Pourquoi une boucle est si grave

Au niveau 2, deux chemins actifs entre deux switches provoquent trois effets immédiats :

| Effet | Mécanisme | Ce qu’on observe |
|---|---|---|
| Tempête de broadcast | Chaque broadcast est réinondé à chaque tour, sans fin : l’en-tête Ethernet n’a pas de TTL. | Liens saturés, processeur des switches à 100 %, plus aucune réponse. |
| Instabilité de la table MAC | La même adresse MAC source arrive alternativement par deux ports. | Journaux `%SW_MATM-4-MACFLAP_NOTIF`. |
| Trames dupliquées | Un unicast inondé arrive plusieurs fois au destinataire. | Retransmissions, applications erratiques. |

STP, inventé par Radia Perlman en 1985 et normalisé en 802.1D, construit un **arbre** qui **couvre** (*spans*) tous les switches sans aucune boucle.

## Le vocabulaire précis

- **BPDU** : trame de contrôle envoyée toutes les 2 secondes (*hello time*) vers l’adresse multicast `01:80:C2:00:00:00` (PVST+ de Cisco utilise `01:00:0C:CC:CC:CD`). Elle contient l’identifiant de la racine, le coût pour l’atteindre et l’identifiant de l’émetteur.
- **Bridge ID** : 8 octets, une **priorité** sur 2 octets puis l’**adresse MAC** sur 6 octets. Chez Cisco, la priorité inclut le numéro de VLAN (*extended system ID*) : la priorité affichée vaut priorité configurée + numéro de VLAN, par exemple 32768 + 10 = 32778. Elle se règle donc **par pas de 4096**.
- **Coût de chemin** : coût de chaque lien selon sa vitesse. Le **coût racine** d’un switch est la somme des coûts jusqu’à la racine.
- **Port ID** : priorité de port (128 par défaut) suivie du numéro de port, utilisé en dernier recours pour départager.

| Vitesse | Coût « court » (802.1D-1998, défaut Cisco) | Coût « long » (802.1D-2004) |
|---|---|---|
| 10 Mb/s | 100 | 2 000 000 |
| 100 Mb/s | 19 | 200 000 |
| 1 Gb/s | 4 | 20 000 |
| 10 Gb/s | 2 | 2 000 |

## L’algorithme en quatre étapes

**Étape 1 — Élire le pont racine.** Au démarrage, chaque switch se croit racine et l’annonce. Dès qu’il reçoit une BPDU annonçant un Bridge ID plus petit, il reconnaît cette racine et relaie son annonce. Il ne reste qu’**une** racine par instance STP. Tous ses ports sont **désignés**.

**Étape 2 — Un port racine sur chaque autre switch.** Chaque switch retient le port qui offre le **plus petit coût racine**. En cas d’égalité, il départage dans cet ordre :

1. le plus petit **Bridge ID de l’émetteur** de la BPDU (le voisin) ;
2. la plus petite **priorité de port** de l’émetteur ;
3. le plus petit **numéro de port** de l’émetteur.

**Étape 3 — Un port désigné sur chaque segment.** Sur chaque lien, une seule extrémité transmet : celle qui annonce le plus petit coût racine, puis, à égalité, le plus petit Bridge ID, puis le plus petit Port ID.

**Étape 4 — Bloquer le reste.** Un port ni racine ni désigné devient **bloqué** (802.1D) ou **alternate** (RSTP). Il ne transmet aucune donnée mais continue d’écouter les BPDU.

```sequence
titre: Élection de la racine entre deux switches
SW1 | SW2
SW1 -> SW2 : BPDU « racine = moi (24576), coût 0 »
SW2 -> SW1 : BPDU « racine = moi (32768), coût 0 »
note SW2 : 24576 est plus petit que 32768 : SW2 reconnaît SW1 comme racine
SW2 --> SW1 : SW2 cesse de se déclarer racine
SW1 -> SW2 : toutes les 2 s : « racine SW1, coût 0 »
```

## Un exemple déroulé à la main

| Switch | Priorité | Adresse MAC |
|---|---|---|
| DIST1 | 24576 (configurée) | `0011.2233.4455` |
| ACC1 | 32768 | `0022.0000.0001` |
| ACC2 | 32768 | `0033.0000.0002` |

```topologie
titre: Rôles des ports après convergence (liens à 1 Gb/s, coût 4)
DIST1 l3 1,0 "DIST1" "racine"
ACC1 switch 0,1 "ACC1"
ACC2 switch 2,1 "ACC2"
DIST1 ++ ACC1 "" "désigné" "racine"
DIST1 ++ ACC2 "" "désigné" "racine"
ACC1 -x- ACC2 "" "désigné" "alternate"
```

1. **Racine** : DIST1, qui a la plus petite priorité.
2. **Port racine d’ACC1** : direct vers DIST1, coût 4 ; par ACC2, coût 4 + 4 = 8. Il choisit le lien direct. Même chose pour ACC2.
3. **Segment ACC1–ACC2** : les deux annoncent un coût racine de 4. À égalité, le plus petit Bridge ID gagne : ACC1 (`0022…` < `0033…`). Le port d’ACC1 est désigné.
4. **Port d’ACC2 vers ACC1** : ni racine ni désigné, il devient **alternate** et bloque.

**Panne** : si le lien DIST1–ACC2 est coupé, le port alternate d’ACC2 devient port racine (coût 8) et passe en transmission — en une seconde environ avec RSTP, en 30 secondes avec 802.1D.

## États des ports et temporisateurs : pourquoi 802.1D est lent

| État | Transmet les données ? | Apprend les MAC ? | Durée |
|---|---|---|---|
| Blocking | Non | Non | jusqu’à 20 s (*max age*) pour constater la perte d’une racine distante |
| Listening | Non | Non | 15 s (*forward delay*) |
| Learning | Non | Oui | 15 s (*forward delay*) |
| Forwarding | Oui | Oui | — |

D’où une coupure de **30 à 50 secondes** après une panne. [RSTP (802.1w)](rstp.md) supprime ces attentes grâce à un échange *proposal/agreement* entre voisins, des ports alternate pré-calculés et des ports *edge* qui transmettent immédiatement. [MSTP (802.1s)](mstp.md) regroupe plusieurs VLAN dans une même instance.

Chez Cisco : **PVST+** (un arbre 802.1D par VLAN), **Rapid PVST+** (un arbre RSTP par VLAN, le choix courant en campus) et **MST** (802.1s).

**Encapsulation** : les BPDU sont des trames Ethernet LLC (DSAP/SSAP `0x42`). Il n’y a **ni en-tête IP ni port TCP/UDP** : une ACL IP ne les filtre pas.

## Configurer la racine et les protections (Cisco IOS / IOS-XE)

Scénario : campus avec les VLAN 10 et 20. DIST1 doit être la racine, DIST2 la racine de secours, et les ports utilisateurs Gi1/0/1 à 24 doivent être protégés.

```cisco
! Sur DIST1 : mode rapide et racine principale
configure terminal
 spanning-tree mode rapid-pvst
 spanning-tree vlan 10,20 root primary
end

! Sur DIST2 : racine de secours
configure terminal
 spanning-tree mode rapid-pvst
 spanning-tree vlan 10,20 root secondary
end

! Sur chaque switch d'accès : ports utilisateurs
configure terminal
 spanning-tree mode rapid-pvst
 interface range GigabitEthernet1/0/1 - 24
  spanning-tree portfast
  spanning-tree bpduguard enable
end
```

- `root primary` fixe la priorité à **24576**, ou plus bas si une racine existante a déjà une priorité plus petite. On peut aussi écrire `spanning-tree vlan 10 priority 4096`.
- `root secondary` fixe **28672** : DIST2 prendra le relais si DIST1 disparaît.
- `portfast` fait passer le port immédiatement en transmission. **Uniquement** vers un poste, un téléphone ou une imprimante.
- `bpduguard enable` met le port en **err-disabled** si une BPDU y arrive, c’est-à-dire si quelqu’un y branche un switch.

| Protection | Où l’appliquer | Effet |
|---|---|---|
| BPDU Guard | Ports d’accès (PortFast) | Coupe le port s’il reçoit une BPDU. |
| Root Guard | Ports de distribution vers l’accès | Refuse qu’un switch en aval devienne racine (port *root-inconsistent*). |
| Loop Guard | Ports non désignés entre switches | Empêche un port bloqué de transmettre si les BPDU cessent d’arriver (lien unidirectionnel). |
| BPDU Filter | Rarement, avec précaution | Supprime l’envoi et la réception de BPDU : peut **masquer** une boucle. |

> [!CAUTION]
> Changer la racine recalcule l’arbre de tout le VLAN : brève coupure possible et chemins déplacés. Fais ce changement en fenêtre de maintenance, après avoir relevé l’état existant avec `show spanning-tree root`.

## Lire `show spanning-tree`

```text
ACC2# show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     0011.2233.4455
             Cost        4
             Port        25 (GigabitEthernet1/0/25)
  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     0033.0000.0002

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- ----------
Gi1/0/1             Desg FWD 4         128.1    P2p Edge
Gi1/0/25            Root FWD 4         128.25   P2p
Gi1/0/26            Altn BLK 4         128.26   P2p
```

| Ligne | Ce qu’elle t’apprend |
|---|---|
| `protocol rstp` | Rapid PVST+ est actif ; `ieee` signifierait 802.1D classique. |
| `Root ID … Priority 24586` | 24576 + VLAN 10 : la racine est bien celle configurée. |
| `Cost 4` et `Port 25` | ACC2 atteint la racine par Gi1/0/25, pour un coût de 4. |
| `Altn BLK` sur Gi1/0/26 | Le lien vers ACC1 est en secours : c’est normal. |
| `P2p Edge` sur Gi1/0/1 | Port PortFast vers un poste. |

Sur la racine elle-même, la sortie affiche `This bridge is the root`.

## Méthode de dépannage

**Symptôme A — tout le VLAN est lent ou injoignable, processeur élevé.** Suspecte une boucle.

1. `show processes cpu sorted` : le processeur est-il anormalement chargé ?
2. `show logging | include MACFLAP` : une MAC qui « flappe » entre deux ports désigne les ports de la boucle.
3. `show interfaces | include line|broadcasts` : les compteurs de broadcasts explosent-ils ?
4. Coupe un lien de la boucle (`shutdown`) pour rétablir le service, **puis** cherche pourquoi STP ne l’a pas bloqué : BPDU Filter, câble ajouté sur un port non protégé, lien unidirectionnel.

**Symptôme B — le trafic suit un chemin inattendu.** Suspecte une racine mal placée : `show spanning-tree root` sur plusieurs switches. Si la racine est un switch d’accès, applique `root primary` sur la distribution et Root Guard vers l’accès.

**Symptôme C — un poste n’a pas de réseau pendant 30 secondes après branchement** et son DHCP échoue. Le port n’est pas en PortFast : il passe par listening et learning avant de transmettre.

**Symptôme D — un port utilisateur est err-disabled.** `show interfaces status err-disabled` puis `show logging`. Si la cause est `bpduguard`, un switch a été branché sur la prise : retire-le, puis `shutdown` et `no shutdown` (ou configure `errdisable recovery cause bpduguard`).

> [!WARNING]
> N’active jamais PortFast sur un port qui relie deux switches : le port transmettrait sans attendre et une boucle pourrait se former avant que STP réagisse.

## Exercices

**1. Élection.** SW-A : priorité 32768, MAC `00d0.0000.000a`. SW-B : priorité 28672, MAC `00ff.0000.000b`. SW-C : priorité 32768, MAC `0001.0000.000c`. Qui est racine ?

<details><summary>Voir le corrigé</summary>

**SW-B.** On compare **d’abord la priorité** : 28672 < 32768. L’adresse MAC ne sert qu’en cas d’égalité. SW-C a la plus petite MAC, mais cela ne compte pas ici. L’erreur classique consiste à comparer directement les MAC.

</details>

**2. Coûts.** ACC3 peut atteindre la racine par un lien direct à 100 Mb/s, ou par un voisin via deux liens à 1 Gb/s. Quel port devient port racine ?

<details><summary>Voir le corrigé</summary>

Lien direct à 100 Mb/s : coût **19**. Passage par le voisin : 4 + 4 = **8**. Le chemin par le voisin gagne malgré un saut de plus : STP compare le **coût total**, pas le nombre de sauts. Le port à 100 Mb/s devient alternate.

</details>

**3. Diagnostic.** Lundi matin, tout le VLAN 20 d’un étage est inaccessible. Les journaux montrent des milliers de `MACFLAP` entre Gi1/0/5 et Gi1/0/6, deux ports utilisateurs. Que s’est-il passé, et quelle protection l’aurait évité ?

<details><summary>Voir le corrigé</summary>

Un câble relie probablement **deux prises murales**, ou un petit switch de bureau est branché sur les deux : une boucle s’est formée entre Gi1/0/5 et Gi1/0/6. **BPDU Guard** sur ces ports d’accès les aurait mis en err-disabled dès la première BPDU. Action immédiate : `shutdown` d’un des deux ports, puis visite du bureau.

</details>
