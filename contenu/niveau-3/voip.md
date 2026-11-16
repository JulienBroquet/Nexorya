---
titre: La téléphonie sur IP
nom: Construire un réseau qui transporte bien la voix
idee: Un réseau prêt pour la voix met les téléphones dans un VLAN dédié, les alimente en PoE, leur donne la priorité absolue et surveille latence, gigue et pertes.
osi: "2 à 7"
duree: [9, 18]
cle: true
prerequis: [sip, rtp, vlan]
retenir:
  - "**VLAN voix** dédié, annoncé au téléphone par CDP ou LLDP-MED ; le PC se branche derrière le téléphone."
  - "**PoE** pour alimenter les postes, avec un budget dimensionné."
  - "**QoS** de bout en bout — voix marquée **EF**, file prioritaire, sur tous les liens où elle peut être congestionnée."
  - "Objectifs — latence < 150 ms (un sens), gigue < 30 ms, pertes < 1 %."
---

## Le problème : la voix ne pardonne rien

Un e-mail qui arrive une seconde plus tard, personne ne le remarque. Une voix qui arrive avec 300 ms de retard, des trous ou de l’écho rend la conversation pénible. Le réseau doit donc **traiter la voix à part**.

> [!IMPORTANT] L’idée en une phrase
> La téléphonie sur IP fonctionne bien quand chaque couche du réseau est préparée pour elle : un VLAN dédié, l’alimentation par le câble, et une priorité absolue sur tous les liens.

## Les briques d’un réseau prêt pour la voix

```topologie
titre: Un poste de travail avec téléphone IP
PC pc 0,0 "PC" "VLAN 10, non étiqueté"
TEL telephone 1.2,0 "Téléphone IP" "VLAN 20, étiqueté, PoE"
SW switch 2.5,0 "Switch d’accès" "PoE, QoS, voice vlan 20"
CO l3 3.8,0 "Cœur" "QoS"
PBX serveur 5,0 "IPBX" "signalisation SIP"
PC -- TEL
TEL -- SW "un seul câble"
SW -- CO
CO -- PBX
```

| Brique | Rôle | Fiche |
|---|---|---|
| VLAN voix | séparer les téléphones, appliquer la QoS facilement | [VLAN](../niveau-1/vlan.md) |
| CDP / LLDP-MED | annoncer au téléphone son VLAN et négocier sa puissance | [LLDP](../niveau-1/lldp.md) |
| PoE | alimenter le téléphone par le câble | [PoE](../niveau-1/poe.md) |
| DHCP | adresse, et souvent l’adresse du serveur de configuration (options 66/150) | [DHCP](dhcp.md) |
| QoS | faire passer la voix avant tout le reste | [QoS](../niveau-5/qos.md) |
| SIP / RTP | signalisation et transport de la voix | [SIP](sip.md), [RTP](rtp.md) |

## Les mots à connaître

- **VoIP** — *Voice over IP*, transport de la voix sur un réseau IP.
- **VLAN voix** — VLAN réservé aux téléphones, transporté étiqueté sur le même port que le PC.
- **EF** — *Expedited Forwarding*, marquage DSCP 46 réservé à la voix.
- **MOS** — Note de qualité perçue d’un appel, de 1 à 5.

## Teste-toi

**Les appels sont parfaits le matin, mais hachés tous les soirs pendant les sauvegardes vers le site distant. Qu’est-ce qui manque ?**

<details><summary>Voir le corrigé</summary>

La **qualité de service** sur le lien vers le site distant : quand la sauvegarde sature le lien, les paquets de voix attendent dans la même file que ceux de la sauvegarde. Il faut marquer la voix (EF) et lui réserver une **file prioritaire** sur ce lien.

</details>

<!-- approfondir -->

## Configuration d’un port d’accès (Cisco IOS)

```cisco
interface GigabitEthernet1/0/5
 description Bureau 214 - téléphone + PC
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 trust device cisco-phone          ! faire confiance au marquage seulement si c'est un téléphone (selon la plateforme)
 auto qos voip cisco-phone         ! modèle de QoS Cisco (ou une politique QoS manuelle)
 power inline auto
 spanning-tree portfast
 spanning-tree bpduguard enable
```

## Dimensionner un lien WAN

```text
Site de 40 personnes, au plus 12 appels simultanés vers l’extérieur en G.711
  12 × 87 kb/s ≈ 1,05 Mb/s par sens pour la voix
  + signalisation, marge : réserver ≈ 1,5 Mb/s en file prioritaire
  Ne pas dépasser environ 33 % du lien en file prioritaire (bonne pratique)
```

Si le lien est petit, un codec compressé (G.729, Opus à bas débit) réduit le besoin, au prix d’une légère baisse de qualité.

## Méthode de dépannage par symptôme

| Symptôme | Pistes |
|---|---|
| Le téléphone ne s’allume pas | PoE : budget, classe, câble |
| Il s’allume mais ne s’enregistre pas | VLAN voix, DHCP (options), joignabilité de l’IPBX, SIP 5060/5061 filtré |
| Appel établi, pas de son / son dans un seul sens | RTP filtré, NAT, ALG SIP, routage asymétrique |
| Voix hachée à certaines heures | congestion : QoS absente ou mal appliquée ; vérifier les `output drops` et les files |
| Écho | souvent lié aux terminaux (casques, passerelles analogiques), ou à une latence élevée qui rend un écho existant audible |
| Appels qui coupent au bout de 30 s ou 15 min | délais du pare-feu ou du NAT pour UDP, absence de rafraîchissement SIP |

## Exercices

**1.** Dans un site, les téléphones prennent une adresse dans le VLAN 10 (données) au lieu du VLAN 20. Le port est configuré avec `switchport voice vlan 20`. Que vérifier ?

<details><summary>Voir le corrigé</summary>

Le téléphone doit **apprendre** le VLAN voix par **CDP** (téléphones Cisco) ou **LLDP-MED** (autres marques). Si LLDP est désactivé sur le switch (souvent le cas par défaut sur Cisco) et que le téléphone n’est pas Cisco, il ne connaît pas le VLAN 20 et démarre dans le VLAN natif du port (10). Activer `lldp run`, ou configurer le VLAN sur le téléphone ou par une option DHCP.

</details>

**2.** Calcule le débit nécessaire pour 20 appels simultanés en G.711 sur un lien WAN, à environ 87 kb/s par appel et par sens.

<details><summary>Voir le corrigé</summary>

20 × 87 = **1 740 kb/s ≈ 1,74 Mb/s par sens**. On réserve environ 2 Mb/s en file prioritaire, et l’on vérifie que cela reste raisonnable par rapport à la capacité du lien.

</details>
