---
titre: EEE
nom: Energy Efficient Ethernet (IEEE 802.3az)
idee: EEE met un lien Ethernet en veille pendant les silences pour économiser de l’énergie ; certains équipements anciens gèrent mal le réveil et perdent des trames.
osi: "1"
duree: [4, 8]
prerequis: [phy]
retenir:
  - EEE place le lien en **veille basse consommation** quand aucune trame ne circule.
  - Le réveil prend quelques **microsecondes** ; la plupart des appareils ne le remarquent pas.
  - "Symptôme typique d’un problème EEE — **pertes uniquement quand le lien est peu chargé**, sur un équipement ancien ou industriel."
---

## Le problème : un lien qui consomme pour rien

Un port Ethernet consomme presque autant d’énergie quand il ne transmet rien que quand il transmet à pleine vitesse : il envoie en permanence un signal d’« attente ». Sur des milliers de ports qui passent la majorité du temps à ne rien faire, c’est une dépense inutile.

> [!IMPORTANT] L’idée en une phrase
> EEE met le lien **en veille** pendant les silences et le **réveille** dès qu’une trame doit passer.

## Ce qui peut mal tourner

La plupart des appareils gèrent parfaitement cette veille. Mais certains équipements **anciens ou industriels** (automates, appareils médicaux, vieux serveurs) se réveillent mal : les premières trames après un silence sont perdues.

**Exemple** : un automate industriel perd des paquets **uniquement quand le réseau est calme**, la nuit. Sous forte charge, le lien ne passe jamais en veille et tout fonctionne. Le problème disparaît après avoir désactivé EEE sur le port du switch.

## Les mots à connaître

- **EEE** — *Energy Efficient Ethernet*, mise en veille des liens Ethernet pendant les silences.
- **LPI** — *Low Power Idle*, état de veille d’un lien EEE.

## Teste-toi

**Pourquoi un problème lié à EEE disparaît-il souvent quand on lance un test de débit ?**

<details><summary>Voir le corrigé</summary>

Parce que le lien, constamment chargé, **ne passe jamais en veille** pendant le test. Le symptôme n’apparaît que lorsque le trafic est faible et intermittent.

</details>

<!-- approfondir -->

## Fonctionnement

Les deux extrémités annoncent leur support d’EEE pendant l’auto-négociation. Ensuite, lorsqu’aucune trame n’est à émettre, l’émetteur envoie un signal **LPI** et coupe l’essentiel de son électronique d’émission, en se réveillant périodiquement pour maintenir la synchronisation. Pour transmettre, il sort de veille en quelques microsecondes (environ 16,5 µs en 1000BASE-T). Les trames arrivées pendant le réveil sont mises en attente, ce qui ajoute une petite latence.

EEE ne concerne que les liens **cuivre** compatibles (100BASE-TX, 1000BASE-T, 10GBASE-T) ; il fonctionne indépendamment du PoE.

## Configuration et vérification (Cisco IOS)

```cisco
SW1# show eee status interface GigabitEthernet1/0/30
Gi1/0/30 is up
        EEE(efficient-ethernet):  operational
        Rx LPI Status          :  Low Power
        Tx LPI Status          :  Low Power

! Désactiver EEE sur un port vers un équipement sensible
interface GigabitEthernet1/0/30
 no power efficient-ethernet
```

Les ports où l’on désactive EEE sont typiquement : automates et équipements industriels, équipements temps réel (synchronisation PTP, audio professionnel), et tout appareil dont le constructeur le recommande.

## Exercice

**Une console de supervision perd ses premiers paquets après chaque pause de quelques minutes, sans erreur CRC sur le port. Quelle vérification ajoutes-tu à ta méthode ?**

<details><summary>Voir le corrigé</summary>

Vérifier si **EEE** est actif sur le port (`show eee status`) et, s’il l’est, le désactiver à titre de test (`no power efficient-ethernet`). L’absence de CRC écarte un défaut de câble ; le lien entre les pertes et les **périodes de silence** oriente vers la mise en veille.

</details>
