---
titre: RSTP
nom: Rapid Spanning Tree Protocol (IEEE 802.1w)
idee: RSTP fait le même travail que STP, mais remplace les longues attentes par un dialogue entre switches voisins ; un câble de secours reprend le relais en une seconde environ.
osi: "2"
duree: [7, 16]
prerequis: [stp]
retenir:
  - RSTP bascule en **environ une seconde**, contre **30 à 50 secondes** pour le STP classique.
  - Il prépare à l’avance des ports de secours — **alternate** (vers la racine) et **backup**.
  - "Les ports **edge** (PortFast) passent immédiatement en transmission — ils ne doivent mener qu’à des postes."
  - Chez Cisco, on l’active avec **`spanning-tree mode rapid-pvst`**.
---

## Le problème : 40 secondes sans réseau

Avec le [STP classique](stp.md), quand un câble actif tombe, le port de secours doit passer par plusieurs états d’attente avant de transmettre : jusqu’à 50 secondes de coupure. Pour la téléphonie, la vidéo ou une application métier, c’est inacceptable.

> [!IMPORTANT] L’idée en une phrase
> RSTP garde le même principe que STP (une racine, un seul chemin actif), mais les switches **se mettent d’accord directement** entre voisins au lieu d’attendre des minuteries. La bascule prend environ une seconde.

## Ce qui change par rapport à STP

| | STP classique (802.1D) | RSTP (802.1w) |
|---|---|---|
| Après une panne | attend des temporisateurs (écoute 15 s, apprentissage 15 s) | négocie directement avec le voisin |
| Câble de secours | rien n’est préparé | un port **alternate** est déjà prêt à basculer |
| Port vers un PC | 30 s d’attente au branchement (sans PortFast) | port **edge** : transmission immédiate |
| Temps de bascule | 30 à 50 s | ≈ 1 s, parfois moins |

> [!TIP] L’analogie du copilote
> Le STP classique, c’est un conducteur qui, après une route barrée, s’arrête, consulte la carte, attend un peu pour être sûr, puis repart. RSTP, c’est un copilote qui a **déjà** repéré l’itinéraire de déviation : dès que la route est barrée, on bifurque.

## Les rôles de ports

- **Root** : le port qui mène à la racine (comme en STP).
- **Designated** : le port qui transmet vers un segment (comme en STP).
- **Alternate** : un **autre chemin vers la racine**, bloqué mais prêt. Si le port root tombe, l’alternate devient root immédiatement.
- **Backup** : un port de secours vers un segment où le switch a déjà un port désigné (cas rare, avec un hub).

## Exemple

Un switch d’accès a deux uplinks vers deux switches de distribution. Avec RSTP, l’un est **root** (actif), l’autre **alternate** (en attente). Un technicien débranche par erreur l’uplink actif : la bascule vers l’alternate est si rapide qu’un appel téléphonique en cours n’est même pas coupé.

## Les mots à connaître

- **RSTP** — *Rapid Spanning Tree Protocol*, version rapide de STP qui bascule en une seconde environ.
- **Port alternate** — Port bloqué qui offre un autre chemin vers la racine, prêt à prendre le relais.
- **Port edge** — Port d’accès vers un appareil final, qui passe immédiatement en transmission ; équivalent de PortFast.
- **Rapid PVST+** — Version Cisco de RSTP, avec un arbre par VLAN.

## Teste-toi

**1.** Pourquoi le port alternate permet-il une bascule quasi immédiate ?

<details><summary>Voir le corrigé</summary>

Parce que le switch a **déjà calculé** que ce port mène à la racine. Quand le port root disparaît, il n’y a rien à rechercher : l’alternate devient root et passe aussitôt en transmission, sans risque de boucle.

</details>

**2.** Un technicien active PortFast sur un lien entre deux switches « pour accélérer ». Que risque-t-il ?

<details><summary>Voir le corrigé</summary>

Un port edge transmet **immédiatement**, sans vérifier qu’il ne ferme pas une boucle. Entre deux switches, une boucle peut se former et provoquer une tempête de broadcast. (RSTP rétrograde le port s’il reçoit une BPDU, mais quelques trames peuvent tourner entre-temps ; BPDU Guard aurait coupé le port.)

</details>

<!-- approfondir -->

## Les états simplifiés

RSTP fusionne les états de STP :

| STP 802.1D | RSTP 802.1w | Transmet les données ? | Apprend les MAC ? |
|---|---|---|---|
| Disabled, Blocking, Listening | **Discarding** | non | non |
| Learning | **Learning** | non | oui |
| Forwarding | **Forwarding** | oui | oui |

## La négociation proposal / agreement

Sur un lien **point à point** (full duplex), un switch qui veut passer un port désigné en transmission **propose** ; le voisin **synchronise** (il bloque ses propres ports non edge pour éviter toute boucle temporaire) puis **accepte**. La transmission démarre aussitôt.

```sequence
titre: Passage rapide en forwarding sur un lien point à point
DIST (désigné) | ACC
DIST (désigné) -> ACC : BPDU avec drapeau Proposal
note ACC : sync : bloque ses ports désignés non edge
ACC --> DIST (désigné) : BPDU avec drapeau Agreement
note DIST (désigné) : le port passe en forwarding immédiatement
note ACC : propose à son tour vers l’aval, de proche en proche
```

Cette négociation ne fonctionne que sur des liens **point à point**. Un lien half duplex est considéré comme partagé : RSTP y retombe sur les temporisateurs classiques. On peut forcer le type : `spanning-tree link-type point-to-point`.

## Détection des pannes et changements de topologie

- Une BPDU est envoyée toutes les 2 s par **chaque** switch (pas seulement relayée depuis la racine). Après **3 BPDU manquées** (6 s), le voisin est considéré comme perdu. Une panne **physique** (lien down) est détectée instantanément.
- Seuls les ports non edge qui passent en **forwarding** déclenchent un changement de topologie (*TC*). Les switches vident alors les adresses MAC apprises sur les autres ports, pour réapprendre le nouveau chemin. Brancher un PC sur un port edge ne déclenche rien.

## Configuration et vérification (Cisco IOS)

```cisco
spanning-tree mode rapid-pvst
!
interface range GigabitEthernet1/0/1 - 46
 spanning-tree portfast              ! ports edge
 spanning-tree bpduguard enable
!
interface range GigabitEthernet1/0/47 - 48
 spanning-tree link-type point-to-point
```

```cisco
ACC1# show spanning-tree vlan 10 | begin Interface
Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- ------------------------
Gi1/0/1             Desg FWD 4         128.1    P2p Edge
Gi1/0/47            Root FWD 4         128.47   P2p
Gi1/0/48            Altn BLK 4         128.48   P2p

ACC1# show spanning-tree detail | include ieee|occurr|from|is exec
 VLAN0010 is executing the rstp compatible Spanning Tree protocol
  Number of topology changes 3 last change occurred 2d04h ago
          from GigabitEthernet1/0/48
```

Un nombre de changements de topologie qui augmente sans cesse signale un port qui monte et descend (*flapping*) ou un port utilisateur sans PortFast. La ligne `from` désigne le port d’origine.

## Compatibilité avec STP

Si un switch RSTP reçoit des BPDU 802.1D sur un port, il passe **ce port** en mode compatible (lent). Un seul vieux switch dans un coin du réseau dégrade donc la convergence de cette partie. Pour revenir au mode rapide après son retrait : `clear spanning-tree detected-protocols`.

## Exercices

**1.** Un switch d’accès a deux uplinks, Gi1/0/47 (root) et Gi1/0/48 (alternate). Gi1/0/47 tombe physiquement. Combien de temps dure la coupure, et pourquoi ?

<details><summary>Voir le corrigé</summary>

Quasiment **rien** (de l’ordre de quelques dizaines de millisecondes à une seconde) : la perte du lien est détectée immédiatement, et l’alternate Gi1/0/48 devient root et passe en forwarding sans négociation. Les switches vident ensuite les MAC concernées et réapprennent.

</details>

**2.** Après le branchement d’un vieux switch de laboratoire, une partie du réseau met de nouveau 30 secondes à converger. Explique.

<details><summary>Voir le corrigé</summary>

Le vieux switch parle **STP 802.1D**. Les ports RSTP qui reçoivent ses BPDU passent en mode compatible, avec les temporisateurs lents. Retirer le switch (ou le passer en RSTP), puis `clear spanning-tree detected-protocols` sur les ports concernés.

</details>

**3.** Le compteur de changements de topologie augmente toutes les quelques minutes, toujours depuis Gi1/0/22, un port utilisateur. Quelle correction ?

<details><summary>Voir le corrigé</summary>

Le port n’est pas configuré en **edge** : chaque fois que le PC s’allume, se met en veille ou redémarre, le port passe en forwarding et déclenche un changement de topologie, qui vide des tables MAC dans tout le VLAN. Configurer `spanning-tree portfast` (et BPDU Guard) sur ce port.

</details>
