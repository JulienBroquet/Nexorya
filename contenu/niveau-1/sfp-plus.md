---
titre: SFP+ et au-delà
nom: Modules 10, 25, 40 et 100 Gb/s
idee: Le SFP+ reprend la forme du SFP pour monter à 10 Gb/s ; ses successeurs (SFP28, QSFP+, QSFP28) poussent jusqu’à 25, 40 et 100 Gb/s dans les datacenters.
osi: "1"
duree: [6, 12]
prerequis: [sfp]
retenir:
  - "**SFP+** = 10 Gb/s, **SFP28** = 25 Gb/s, **QSFP+** = 40 Gb/s, **QSFP28** = 100 Gb/s."
  - Une cage SFP+ accepte souvent un module SFP à 1 Gb/s ; l’inverse est impossible.
  - Pour les liaisons de quelques mètres dans une baie, un câble **DAC** remplace avantageusement deux modules et une fibre.
---

## Le problème : les serveurs vont plus vite

Un serveur de virtualisation ou de stockage échange des volumes considérables. Un lien à 1 Gb/s devient vite le goulet d’étranglement. Les datacenters utilisent donc des liens à 10, 25, 40 ou 100 Gb/s, avec des modules plus rapides que le SFP d’origine.

> [!IMPORTANT] L’idée en une phrase
> Même principe que le SFP — un module enfichable qui décide du type de liaison — mais pour des débits de 10 Gb/s et plus.

## La famille des modules

| Format | Débit | Usage typique |
|---|---|---|
| SFP | 1 Gb/s | accès, liens entre étages |
| **SFP+** | 10 Gb/s | serveurs, liens entre switches de campus |
| SFP28 | 25 Gb/s | serveurs de datacenter récents |
| QSFP+ | 40 Gb/s (4 × 10) | liens entre switches de datacenter |
| QSFP28 | 100 Gb/s (4 × 25) | cœur de datacenter |

Le « Q » de QSFP signifie *quad* : le module regroupe **quatre voies** en parallèle. Un port QSFP+ peut d’ailleurs être éclaté en quatre liens à 10 Gb/s avec un câble adapté (*breakout*).

## Exemple : passer une baie de serveurs à 10 Gb/s

Une PME virtualise ses serveurs. On remplace les modules SFP 1 Gb/s par des **SFP+ 10GBASE-SR** sur fibre multimode OM4, et les cartes réseau des serveurs par des cartes 10 Gb/s. Pour les serveurs situés dans la même baie que le switch, on utilise plutôt des câbles [DAC](dac.md), moins chers.

## Les mots à connaître

- **SFP+** — Module enfichable au format SFP pour les liens à 10 Gb/s.
- **QSFP** — *Quad SFP*, module à quatre voies parallèles pour 40 ou 100 Gb/s.
- **Breakout** — Câble qui éclate un port QSFP en quatre liens indépendants.

## Teste-toi

**Peut-on insérer un module SFP+ 10 Gb/s dans une cage SFP prévue pour 1 Gb/s ?**

<details><summary>Voir le corrigé</summary>

**Non** : la cage SFP et l’électronique du port ne savent pas fonctionner à 10 Gb/s. L’inverse — un SFP 1 Gb/s dans une cage SFP+ — fonctionne sur la plupart des switches, le port fonctionnant alors à 1 Gb/s.

</details>

<!-- approfondir -->

## Les modules 10 Gb/s courants

| Module | Fibre | Longueur d’onde | Portée |
|---|---|---|---|
| 10GBASE-SR | multimode | 850 nm | 300 m (OM3), 400 m (OM4) |
| 10GBASE-LRM | multimode ancienne | 1310 nm | 220 m |
| 10GBASE-LR | monomode | 1310 nm | 10 km |
| 10GBASE-ER | monomode | 1550 nm | 40 km |
| 10GBASE-T (SFP+) | cuivre Cat6A | — | 30 m en général (consommation élevée) |

## Vitesse du port et module

Un port ne fonctionne qu’à une vitesse que **le port, le module et le partenaire** supportent tous les trois. Sur de nombreux switches, une cage SFP28 accepte un SFP+ (10 Gb/s) ; un port QSFP28 accepte un QSFP+ (40 Gb/s). Il faut parfois configurer la vitesse ou le mode d’éclatement explicitement :

```cisco
! Exemple NX-OS : éclater un port 100 Gb/s en 4 x 25 Gb/s
interface breakout module 1 port 49 map 25g-4x
! Les interfaces Ethernet1/49/1 à 1/49/4 apparaissent
```

Les noms d’interface varient selon les plateformes (`TenGigabitEthernet`, `TwentyFiveGigE`, `Ethernet1/49/1`…). Vérifie toujours la matrice de compatibilité des modules du constructeur.

## Correction d’erreurs (FEC)

À partir de 25 Gb/s, les liens utilisent souvent une **correction d’erreurs directe** (*FEC*, *Forward Error Correction*) : des bits supplémentaires permettent au récepteur de corriger certaines erreurs sans retransmission. Les deux extrémités doivent utiliser **le même mode FEC** (RS-FEC, FC-FEC ou aucun). Un désaccord de FEC donne un lien qui ne monte pas alors que la lumière est bien reçue — une panne déroutante si l’on ne connaît pas ce réglage.

## Exercices

**1.** Un lien 25 Gb/s entre un switch et un serveur ne monte pas. La puissance optique reçue est correcte des deux côtés. Quelle piste vérifier ?

<details><summary>Voir le corrigé</summary>

Le **mode FEC** (et la vitesse configurée) : si le switch attend RS-FEC et que la carte du serveur n’utilise pas de FEC, le lien reste *down* malgré une lumière correcte. Aligner le mode FEC des deux côtés.

</details>

**2.** On veut relier quatre serveurs à 10 Gb/s, mais il ne reste qu’un port QSFP+ libre sur le switch. Solution ?

<details><summary>Voir le corrigé</summary>

Utiliser un **câble breakout** QSFP+ vers 4 × SFP+ (DAC ou optique) et configurer le port en mode **4 × 10 Gb/s**. Le port devient quatre interfaces indépendantes.

</details>
