---
titre: RTP
nom: Real-time Transport Protocol
idee: RTP transporte la voix et la vidéo en temps réel sur UDP ; il numérote et horodate chaque paquet pour que le récepteur détecte les pertes et restitue le son au bon rythme.
osi: "7 (sur UDP, ports dynamiques)"
duree: [6, 12]
prerequis: [udp, sip]
retenir:
  - RTP ajoute un **numéro de séquence** (pertes) et un **horodatage** (rythme) à chaque paquet média.
  - Un paquet de voix toutes les **20 ms** — environ 50 paquets par seconde et par sens.
  - "**RTCP** remonte des statistiques — pertes, gigue, délai."
  - "**SRTP** chiffre le média."
---

## Le problème

La voix est découpée en petits morceaux de 20 ms. Ils doivent être joués **au même rythme** qu’ils ont été enregistrés, même si le réseau les livre irrégulièrement, en désordre, ou en perd quelques-uns. UDP ne fournit aucune de ces informations.

> [!IMPORTANT] L’idée en une phrase
> RTP étiquette chaque paquet de voix avec un **numéro** et une **heure de capture** : le récepteur remet les paquets dans l’ordre, repère les manquants et les joue au bon moment.

## Ce que fait le récepteur

1. Il range les paquets dans un **tampon de gigue** de quelques dizaines de millisecondes.
2. Il les joue dans l’ordre des numéros, au rythme des horodatages.
3. Si un paquet manque au moment de le jouer, il **masque** le trou (répétition, interpolation).
4. Si un paquet arrive trop tard, il est jeté : il ne sert plus à rien.

## Les mots à connaître

- **RTP** — Protocole de transport des flux audio et vidéo en temps réel.
- **RTCP** — Protocole compagnon de RTP qui échange des statistiques de qualité.
- **SRTP** — Version chiffrée et authentifiée de RTP.
- **Codec** — Algorithme qui code et décode la voix ou la vidéo (G.711, G.722, Opus…).
- **Tampon de gigue** — Mémoire qui absorbe les variations de délai avant de jouer les paquets.

## Teste-toi

**Pourquoi un paquet de voix qui arrive avec 300 ms de retard est-il jeté au lieu d’être joué ?**

<details><summary>Voir le corrigé</summary>

Le moment où il devait être joué est **passé** : le tampon de gigue a déjà joué (ou masqué) cet instant. Le jouer plus tard décalerait toute la conversation. En temps réel, une donnée en retard est une donnée perdue.

</details>

<!-- approfondir -->

## L’en-tête RTP (12 octets)

| Champ | Rôle |
|---|---|
| Version, drapeaux | version 2 |
| Payload Type | codec : 0 = G.711 µ-law, 8 = G.711 A-law, 9 = G.722, 96–127 = dynamique (Opus…) |
| **Numéro de séquence** | +1 à chaque paquet : détection des pertes et du désordre |
| **Horodatage** | instant d’échantillonnage : restitution au bon rythme |
| SSRC | identifiant de la source du flux |

## Bande passante d’un appel

```text
G.711 (64 kb/s) avec des paquets de 20 ms
  charge audio : 160 octets
  + RTP 12 + UDP 8 + IP 20 = 200 octets par paquet (couche 3)
  50 paquets/s × 200 octets × 8 = 80 kb/s par sens (sans en-tête Ethernet)
  avec Ethernet (+18 octets) : ≈ 87 kb/s par sens
```

Les en-têtes représentent un quart du débit : c’est pour cela que les codecs compressés à très bas débit ne divisent pas la bande passante réelle autant que leur débit nominal le laisse croire.

## Mesurer la qualité

Le **MOS** (*Mean Opinion Score*, de 1 à 5) estime la qualité perçue. On vise **au-dessus de 4**. Il se dégrade avec la latence (au-delà de 150 ms dans un sens), la gigue (au-delà de 30 ms) et les pertes (au-delà de 1 %). Les téléphones, les IPBX et les sondes IP SLA `udp-jitter` le calculent.

Dans Wireshark : **Téléphonie → RTP → Flux RTP → Analyser** affiche pour chaque flux les pertes, la gigue maximale et moyenne, et les numéros de séquence manquants.

## Exercice

**L’analyse d’un flux RTP montre 0 % de perte mais une gigue qui atteint 120 ms par moments. L’utilisateur entend des coupures. Comment est-ce possible sans perte réseau ?**

<details><summary>Voir le corrigé</summary>

Les paquets arrivent tous, mais certains **trop tard** pour le tampon de gigue (souvent 40 à 60 ms) : le téléphone les jette, ce qui produit des coupures. La cause est la **congestion** (files d’attente) sur le chemin. La solution est la **QoS** : priorité stricte pour la voix, et éventuellement un tampon de gigue adaptatif.

</details>
