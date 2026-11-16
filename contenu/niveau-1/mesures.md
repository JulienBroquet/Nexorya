---
titre: Mesurer une connexion
nom: Débit, latence, gigue et pertes
idee: Une connexion se juge avec quatre mesures — le débit (combien), la latence (en combien de temps), la gigue (avec quelle régularité) et les pertes (avec quelle fiabilité).
osi: "1 à 4"
duree: [8, 15]
cle: true
retenir:
  - Le **débit** se mesure en bits par seconde (Mb/s) ; un octet vaut 8 bits.
  - La **latence** est le temps d’aller-retour (ms) ; la **gigue**, sa variation ; les **pertes**, la part de paquets disparus.
  - Une « connexion à 1 Gb/s » peut être inutilisable pour la voix si la latence, la gigue ou les pertes sont mauvaises.
  - La congestion d’un lien fait monter **en même temps** latence, gigue et pertes.
---

## Le problème : « c’est lent »

« La connexion est lente » ne veut rien dire tant qu’on ne précise pas **ce qui** est lent. Un téléchargement qui avance péniblement, une page qui met du temps à **commencer** à s’afficher, une voix hachée en visioconférence : ce sont trois problèmes différents, avec trois causes différentes. Pour les distinguer, on utilise **quatre mesures**.

> [!TIP] L’analogie de l’autoroute
> Le **débit**, c’est le nombre de voies : combien de voitures peuvent passer par heure. La **latence**, c’est le temps de trajet d’une voiture. La **gigue**, c’est l’irrégularité de ce temps de trajet d’une voiture à l’autre. Les **pertes**, ce sont les voitures qui n’arrivent jamais. Une autoroute à dix voies peut quand même être bouchée.

## Les quatre mesures

| Mesure | Question | Unité | Ce qui est bon pour… |
|---|---|---|---|
| **Débit** | Combien de données par seconde ? | Mb/s, Gb/s | Téléchargements, sauvegardes, vidéo en haute définition |
| **Latence** | Combien de temps pour un aller-retour ? | ms | Jeux, sites Web interactifs, bureau à distance |
| **Gigue** | Le délai est-il régulier ? | ms | Voix et vidéo en direct |
| **Pertes** | Quelle part des paquets disparaît ? | % | Tout, mais surtout la voix et les transferts TCP |

```illustration
fichier: quatre-mesures.svg
legende: "Quatre mesures différentes, quatre problèmes différents : un gros débit ne garantit ni une faible latence, ni une gigue faible."
alt: "Quatre panneaux : débit comme largeur de tuyau, latence comme temps d’aller-retour, gigue comme arrivées irrégulières, pertes comme paquets manquants"
```

### Bits ou octets ?

Les réseaux mesurent en **bits par seconde** (b/s), les logiciels de téléchargement affichent souvent des **octets par seconde** (o/s ou B/s). **Un octet = 8 bits**. Une connexion à 100 Mb/s télécharge donc au mieux environ 12,5 Mo/s — un peu moins en réalité, à cause des en-têtes.

## Exemple : pourquoi la voix hache pendant les sauvegardes

Une agence a un lien de 100 Mb/s vers le siège. Toute la journée, la téléphonie fonctionne bien. Mais tous les soirs à 18 h, les appels deviennent hachés. Que se passe-t-il ?

- À 18 h, la **sauvegarde** démarre et tente d’utiliser tout le lien.
- Les paquets de voix se retrouvent **dans la même file d’attente** que les paquets de la sauvegarde.
- Certains paquets de voix attendent longtemps, d’autres non : la **gigue** explose. Quand la file déborde, des paquets sont **perdus**.

Le débit du lien n’a pas changé. C’est la **congestion** qui dégrade la latence, la gigue et les pertes. La solution n’est pas forcément un lien plus rapide : on peut **donner la priorité à la voix** grâce à la qualité de service (QoS), que tu verras au niveau 5.

## Mesurer avec `ping`

```powershell
C:\> ping -n 10 10.20.0.1
Réponse de 10.20.0.1 : octets=32 temps=18 ms TTL=62
Réponse de 10.20.0.1 : octets=32 temps=21 ms TTL=62
Réponse de 10.20.0.1 : octets=32 temps=95 ms TTL=62
Délai d’attente de la demande dépassé.
Réponse de 10.20.0.1 : octets=32 temps=19 ms TTL=62
…
Paquets : envoyés = 10, reçus = 9, perdus = 1 (perte 10%)
Durée approximative des boucles en millisecondes :
    Minimum = 18ms, Maximum = 95ms, Moyenne = 30ms
```

- **Latence** : environ 20 ms en temps normal.
- **Gigue** : forte, puisque le délai varie de 18 à 95 ms.
- **Pertes** : 10 %, c’est beaucoup.

## Les mots à connaître

- **Débit** — Quantité de données transmises par seconde, mesurée en bits par seconde (Mb/s, Gb/s).
- **Latence** — Temps nécessaire à un message pour faire l’aller-retour, en millisecondes (ms).
- **Gigue** — Variation de la latence d’un paquet à l’autre ; en anglais, *jitter*.
- **Perte de paquets** — Part des paquets envoyés qui n’arrivent jamais.
- **Congestion** — Situation où plus de données arrivent sur un lien qu’il ne peut en transmettre : une file d’attente se forme.

## Teste-toi

**1.** Un fichier de 500 Mo se télécharge sur une connexion de 100 Mb/s. Combien de temps faut-il au minimum ?

<details><summary>Voir le corrigé</summary>

500 Mo = 500 × 8 = **4 000 Mb**. À 100 Mb/s, il faut au moins **40 secondes**, et un peu plus en réalité à cause des en-têtes et des échanges de contrôle.

</details>

**2.** Un lien satellite offre 50 Mb/s avec 600 ms de latence. Est-il adapté à un bureau à distance interactif ?

<details><summary>Voir le corrigé</summary>

**Mal adapté.** Le débit est suffisant, mais chaque clic met plus d’une demi-seconde à produire un effet visible. Pour l’interactivité, c’est la **latence** qui compte, pas le débit.

</details>

<!-- approfondir -->

## D’où vient la latence ?

La latence d’un paquet est la somme de quatre délais, à chaque équipement traversé :

| Délai | Origine | Ordre de grandeur |
|---|---|---|
| **Propagation** | Vitesse du signal dans le support : environ 200 000 km/s dans la fibre, soit **5 µs par kilomètre** | Paris–New York (≈ 6 000 km de câble) : ≈ 30 ms aller, 60 ms aller-retour minimum |
| **Sérialisation** | Temps pour « poser » tous les bits sur le lien = taille / débit | 1 500 octets à 1 Mb/s : 12 ms ; à 1 Gb/s : 12 µs |
| **Traitement** | Décision de commutation ou de routage | quelques microsecondes sur du matériel moderne |
| **File d’attente** | Attente derrière d’autres paquets quand le lien est chargé | de 0 à plusieurs centaines de ms : **c’est la partie variable** |

La propagation est incompressible : aucune optimisation ne fera passer Paris–New York sous 60 ms aller-retour. La file d’attente, elle, dépend de la charge : c’est elle qui crée la gigue.

## Débit nominal, débit utile, produit débit-délai

- **Débit nominal** : la vitesse du lien (1 Gb/s).
- **Débit utile** (*goodput*) : ce qu’une application obtient réellement, après les en-têtes (Ethernet + IP + TCP ≈ 3 à 5 % sur des trames de 1 500 octets) et les retransmissions.

Pour TCP, une contrainte supplémentaire existe : l’émetteur ne peut envoyer qu’une quantité limitée de données sans accusé de réception (la **fenêtre**). Le débit maximal d’un flux TCP est donc :

```text
débit max ≈ taille de fenêtre / latence aller-retour (RTT)

Exemple : fenêtre de 64 Ko, RTT de 100 ms
  64 × 1024 × 8 bits / 0,1 s ≈ 5,2 Mb/s   — même sur un lien de 1 Gb/s
```

C’est le **produit débit-délai** (*bandwidth-delay product*) : pour remplir un lien de 1 Gb/s avec 100 ms de RTT, il faut une fenêtre d’environ 12,5 Mo. Les systèmes modernes agrandissent automatiquement la fenêtre (*window scaling*), mais ce phénomène explique encore bien des transferts lents sur de longues distances.

## Seuils de référence pour la voix et la vidéo

| Mesure | Objectif courant pour la voix sur IP |
|---|---|
| Latence de bout en bout (un sens) | < 150 ms (recommandation UIT-T G.114) |
| Gigue | < 30 ms |
| Pertes | < 1 % |

Au-delà, la qualité perçue chute rapidement. Les téléphones compensent un peu la gigue avec un **tampon de gigue** (*jitter buffer*), au prix d’un délai supplémentaire.

## Outils de mesure

| Outil | Ce qu’il mesure | Exemple |
|---|---|---|
| `ping` | latence, pertes, gigue approximative | `ping -n 100 10.0.0.1` |
| `mtr` / `pathping` | latence et pertes **par saut** | `mtr -rwc 100 1.1.1.1` |
| `iperf3` | débit TCP ou UDP entre deux machines, gigue et pertes en UDP | `iperf3 -c serveur -u -b 50M` |
| IP SLA (Cisco) | sondes permanentes depuis un routeur | voir [IP SLA](../niveau-2/ipsla.md) |
| Compteurs d’interface | erreurs, rejets en sortie (*output drops*) | `show interfaces` |

```bash
# Sur le serveur
iperf3 -s
# Sur le client : 30 secondes de test UDP à 50 Mb/s
iperf3 -c 10.20.0.10 -u -b 50M -t 30
# Dernière ligne utile :
# [ 5] 0.00-30.00 sec 179 MBytes 50.0 Mbits/sec 0.412 ms 12/129310 (0.0093%)
#                                     débit        gigue    pertes
```

> [!WARNING]
> Un `ping` qui perd des paquets vers un routeur intermédiaire n’indique pas forcément un problème : beaucoup de routeurs **limitent volontairement** leurs réponses ICMP. Ce qui compte, ce sont les pertes **jusqu’à la destination finale**. Si un saut intermédiaire perd 30 % mais que la destination en perd 0 %, le chemin va bien.

## Méthode : qualifier un « c’est lent »

1. **Lent pour quoi ?** Démarrage d’une page (latence), téléchargement (débit), voix (gigue, pertes).
2. **Depuis où et vers où ?** Un seul poste, un étage, un site, tout le monde ?
3. **Quand ?** En permanence ou à certaines heures (sauvegardes, début de journée) ?
4. **Mesurer** : `ping` longue durée, `mtr` pour localiser le saut, `iperf3` pour le débit.
5. **Regarder les compteurs** des interfaces sur le chemin : `output drops` qui augmentent = congestion ; `CRC` qui augmentent = problème physique.

```cisco
SW1# show interfaces GigabitEthernet1/0/48 | include rate|drops|CRC
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 184332
  5 minute input rate 912000000 bits/sec, 81000 packets/sec
  5 minute output rate 987000000 bits/sec, 85000 packets/sec
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
```

Ici, le lien de 1 Gb/s est saturé en sortie (987 Mb/s) et les rejets augmentent : c’est de la **congestion**, pas un défaut de câble (CRC à 0).

## Exercices

**1.** Calcule le temps de sérialisation d’une trame de 1 500 octets sur un lien à 2 Mb/s, puis sur un lien à 10 Gb/s.

<details><summary>Voir le corrigé</summary>

1 500 octets = 12 000 bits. À 2 Mb/s : 12 000 / 2 000 000 = **6 ms**. À 10 Gb/s : 12 000 / 10¹⁰ = **1,2 µs**. Sur les liens lents (anciens accès WAN), la sérialisation pèse lourd ; c’est pourquoi on y fragmentait les gros paquets pour ne pas retarder la voix.

</details>

**2.** Un transfert entre Lyon et Montréal (RTT de 95 ms) plafonne à 5 Mb/s sur une liaison de 1 Gb/s. Les compteurs ne montrent ni pertes ni congestion. Quelle hypothèse ?

<details><summary>Voir le corrigé</summary>

Une **fenêtre TCP trop petite**. 5 Mb/s × 0,095 s ≈ 475 kbit ≈ 60 Ko : cela correspond à une fenêtre de 64 Ko sans *window scaling*. Vérifier que les deux systèmes activent l’agrandissement de fenêtre et qu’aucun équipement intermédiaire ne le désactive ; ou paralléliser le transfert en plusieurs flux.

</details>

**3.** `mtr` vers un serveur montre 40 % de pertes au saut 5, puis 0 % aux sauts 6, 7 et à la destination. Le chemin a-t-il un problème ?

<details><summary>Voir le corrigé</summary>

**Non.** Si les sauts suivants et la destination ne perdent rien, le trafic traverse bien le routeur du saut 5. Celui-ci limite simplement ses **réponses** ICMP. Les pertes ne sont significatives que lorsqu’elles **persistent jusqu’à la destination**.

</details>
