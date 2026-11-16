---
titre: DAC
nom: Direct Attach Copper
idee: Un DAC est un câble court dont les deux extrémités sont déjà des modules SFP+ ou QSFP ; il relie deux équipements d’une même baie sans optique.
osi: "1"
duree: [5, 8]
prerequis: [sfp-plus]
retenir:
  - Le **DAC** intègre les connecteurs aux deux bouts d’un câble cuivre twinax — pas de module optique à acheter.
  - Il est fait pour les **courtes distances** (quelques mètres, dans une baie) ; au-delà, on utilise un **AOC** ou de la fibre.
  - Moins cher, moins gourmand en énergie et à faible latence, c’est le choix par défaut entre serveurs et switch de baie.
---

## Le problème : deux mètres de câble, deux modules optiques ?

Dans une baie de datacenter, un serveur est souvent à un ou deux mètres de son switch. Acheter deux modules optiques et une fibre pour une si courte distance coûte cher et consomme de l’énergie pour rien.

> [!IMPORTANT] L’idée en une phrase
> Le DAC est un câble cuivre spécial **avec les modules déjà soudés aux deux bouts** : on le branche directement dans les cages SFP+, SFP28 ou QSFP des deux équipements.

## Comment ça marche

Le câble contient des paires de cuivre **twinax** (deux conducteurs blindés) qui transportent directement le signal électrique d’un port à l’autre, sans conversion en lumière. Les « modules » aux extrémités ne contiennent presque rien : juste une petite mémoire qui annonce le type de câble.


```photo
fichier: cable-dac.jpg
legende: "Un câble DAC : un câble noir épais avec, à chaque bout, une tête qui a la forme d’un module SFP+. On ne branche aucune fibre : la tête entre directement dans la cage du switch ou de la carte réseau. On le retire en tirant sur la boucle noire."
alt: "Câble noir enroulé, terminé à chaque extrémité par une tête métallique au format SFP avec une tirette noire"
```

```topologie
titre: DAC dans une baie, fibre entre les baies
SRV1 serveur 0,1 "Serveur 1"
SRV2 serveur 1,1 "Serveur 2"
TOR switch 0.5,0 "Switch de baie" "top of rack"
SPINE switch 3,0 "Switch d’agrégation" "autre rangée"
SRV1 -- TOR "DAC 2 m"
SRV2 -- TOR "DAC 1 m"
TOR -- SPINE "fibre + modules SR"
```

## DAC, AOC ou fibre ?

| Solution | Distance | Avantages | Limites |
|---|---|---|---|
| **DAC passif** | jusqu’à 5 m environ | très bon marché, aucune consommation | rigide, longueur fixe |
| **DAC actif** | jusqu’à 7–10 m | un peu plus long | consomme un peu |
| **AOC** (câble optique actif) | jusqu’à 30–100 m | fin, léger | modules fixés au câble, plus cher |
| **Modules + fibre** | de 100 m à des km | souple, réparable, longues distances | le plus cher |

## Les mots à connaître

- **DAC** — *Direct Attach Copper*, câble cuivre à connecteurs SFP+ ou QSFP intégrés, pour les très courtes distances.
- **Twinax** — Câble cuivre à deux conducteurs blindés, utilisé dans les DAC.
- **AOC** — *Active Optical Cable*, câble optique à modules intégrés, pour des distances moyennes.
- **ToR** — *Top of Rack*, switch placé en haut d’une baie pour relier les serveurs de cette baie.

## Teste-toi

**Il faut relier un serveur à un switch situé dans une autre rangée, à 25 m. Un DAC convient-il ?**

<details><summary>Voir le corrigé</summary>

**Non**, un DAC est limité à quelques mètres. À 25 m, on choisit un **AOC** ou des **modules optiques avec une fibre**.

</details>

<!-- approfondir -->

## Compatibilité

Un DAC annonce dans sa mémoire le constructeur et le type de câble. Les équipements de certaines marques n’acceptent que des DAC « codés » pour eux. Entre deux équipements de marques différentes, on utilise un DAC dont chaque extrémité est codée pour l’équipement correspondant, ou l’on vérifie les listes de compatibilité.

À 25 Gb/s, les DAC sont classés selon leur perte (CA-N, CA-S, CA-L) et imposent un **mode FEC** : un DAC « CA-L » exige généralement RS-FEC des deux côtés. Un lien DAC qui ne monte pas est souvent un problème de FEC ou d’auto-négociation, pas un câble défectueux.

```cisco
SW1# show interfaces Ethernet1/5 transceiver
Ethernet1/5
    transceiver is present
    type is SFP-H25G-CU2M
    name is CISCO-LEONI
    cable length is 2 m
```

## Exercice

**Pourquoi un DAC a-t-il une latence légèrement plus faible et consomme-t-il moins qu’un lien optique de même longueur ?**

<details><summary>Voir le corrigé</summary>

Parce qu’il n’y a **aucune conversion électrique-optique** : pas de laser à alimenter ni de photodiode, et moins de traitement du signal. Le signal électrique du port est transporté tel quel sur le cuivre twinax.

</details>
