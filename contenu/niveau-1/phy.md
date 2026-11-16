---
titre: PHY
nom: La couche physique d’un port Ethernet
idee: Le PHY est le composant qui transforme les bits en signal sur le câble, et qui négocie avec le port d’en face la vitesse et le mode de communication.
osi: "1"
duree: [7, 15]
prerequis: [cablage]
retenir:
  - Le **PHY** code les bits en signal électrique ou optique, et inversement.
  - "L’**auto-négociation** choisit avec le voisin la meilleure **vitesse** et le **duplex** communs."
  - Un câble abîmé peut faire redescendre un lien de 1 Gb/s à **100 Mb/s** ; un réglage forcé d’un seul côté provoque un **désaccord de duplex**.
---

## Le problème : parler le même « langage électrique »

Deux cartes réseau reliées par un câble doivent s’entendre sur des détails très concrets : à quelle vitesse envoyer les bits ? peuvent-elles parler et écouter en même temps ? comment représenter un 0 et un 1 par une tension électrique ? Ce travail est confié à un composant de chaque port : le **PHY** (prononcé « faï », pour *physical layer*).

> [!IMPORTANT] L’idée en une phrase
> Le PHY est le « modem » de chaque port Ethernet : il transforme les bits en signal sur le câble, et il **négocie** avec le port d’en face la vitesse et le mode de communication.

## Ce que fait le PHY

1. **Il détecte un partenaire.** Dès qu’un câble est branché, il envoie de petites impulsions pour savoir s’il y a quelqu’un en face.
2. **Il négocie.** Les deux PHY annoncent ce qu’ils savent faire (10, 100, 1000 Mb/s ; half ou full duplex) et retiennent le meilleur mode **commun** : c’est l’**auto-négociation**.
3. **Il code et décode.** Pendant la communication, il transforme les bits en niveaux de tension (ou en impulsions lumineuses sur une fibre), et inversement.
4. **Il allume le voyant.** Le voyant « lien » du port signifie que la négociation a réussi.

## Half duplex ou full duplex ?

- **Half duplex** : chacun parle à son tour, comme avec un talkie-walkie. Si les deux parlent en même temps, il y a **collision**. C’était le cas des anciens réseaux partagés.
- **Full duplex** : les deux parlent et écoutent **en même temps**, comme au téléphone. C’est le cas de tous les liens modernes entre un PC et un switch.

## Exemple : le PC bloqué à 100 Mb/s

Un PC équipé d’une carte 1 Gb/s ne se connecte qu’à 100 Mb/s. Le testeur de câble montre que **deux des quatre paires sont coupées**.

Explication : le Gigabit Ethernet cuivre (1000BASE-T) **utilise les quatre paires** en même temps. Le 100 Mb/s (100BASE-TX) n’en utilise que **deux**. Avec seulement deux paires valides, l’auto-négociation ne peut retenir que 100 Mb/s. Remplacer le cordon ou refaire la prise résout le problème.

## Erreurs fréquentes

- **Forcer la vitesse et le duplex d’un seul côté.** Le côté forcé ne participe plus à la négociation, l’autre côté tombe par défaut en half duplex : c’est le **désaccord de duplex**, détaillé dans « Approfondir ».
- **Oublier que la vitesse affichée dépend du câble.** Une vitesse inférieure à celle attendue est souvent un défaut physique, pas un réglage.

## Les mots à connaître

- **PHY** — Composant d’un port Ethernet qui transforme les bits en signal et négocie le lien avec le port d’en face.
- **Auto-négociation** — Échange automatique entre deux ports pour choisir la meilleure vitesse et le meilleur duplex communs.
- **Full duplex** — Mode où l’on peut émettre et recevoir en même temps.
- **Half duplex** — Mode où l’on émet et reçoit à tour de rôle ; des collisions sont possibles.
- **Collision** — Situation où deux appareils émettent en même temps sur un support partagé : les signaux se mélangent.

## Teste-toi

**1.** Pourquoi un câble dont deux paires sont abîmées peut-il encore fonctionner, mais à 100 Mb/s seulement ?

<details><summary>Voir le corrigé</summary>

Parce que 100BASE-TX n’a besoin que de **deux paires**, alors que 1000BASE-T en utilise **quatre**. L’auto-négociation retient la meilleure vitesse possible avec les paires qui fonctionnent.

</details>

**2.** Sur un lien full duplex entre un PC et un switch, peut-il y avoir des collisions ?

<details><summary>Voir le corrigé</summary>

**Non.** En full duplex, chaque sens a ses propres paires (ou ses propres fréquences) : émettre et recevoir en même temps ne crée aucune collision. Des « collisions » sur un tel lien sont le signe d’un désaccord de duplex.

</details>

<!-- approfondir -->

## Ce qui se cache dans un port Ethernet

Un port Ethernet est composé de deux blocs :

- le **MAC** (contrôleur d’accès au support), qui fabrique et vérifie les trames : adresses, FCS, gestion des files ;
- le **PHY**, qui transforme le flux de bits en symboles puis en signal, et réalise l’opération inverse.

Ils dialoguent par une interface normalisée (MII, GMII, SGMII, XGMII…). Sur un port SFP, le PHY optique est en partie **dans le module** : c’est pour cela qu’on change de module pour changer de type de fibre.

## Codage du signal

Le PHY ne pose pas les bits « tels quels » sur le câble : il les **code** pour garantir assez de transitions (le récepteur doit garder le rythme) et pour tenir dans la bande de fréquences du câble.

| Norme | Codage | Principe |
|---|---|---|
| 100BASE-TX | 4B5B + MLT-3 | 4 bits deviennent 5 symboles, sur 3 niveaux de tension |
| 1000BASE-T | PAM-5 sur 4 paires, émission et réception simultanées sur chaque paire | annulation d’écho pour séparer les deux sens |
| 1000BASE-X (fibre) | 8B10B | 8 bits deviennent 10 symboles, d’où un débit de ligne de 1,25 Gbaud |
| 10GBASE-R | 64B66B | surcoût réduit à environ 3 % |

C’est ce codage qui explique qu’on parle de **baud** (symboles par seconde) et de **bits par seconde** : les deux ne sont pas égaux.

## L’auto-négociation en détail (IEEE 802.3 clause 28)

Les PHY cuivre s’échangent des rafales d’impulsions (*Fast Link Pulses*) qui codent leurs capacités. Chacun choisit ensuite le meilleur mode commun, selon un ordre de priorité fixé par la norme (1000 full > 1000 half > 100 full > 100 half > 10 full > 10 half).

Si l’un des deux côtés est **forcé** (auto-négociation désactivée), il n’envoie plus ces rafales. Le côté resté en automatique peut encore deviner la **vitesse** en analysant le signal (*parallel detection*), mais **pas le duplex** : la norme lui impose alors le **half duplex**.

```topologie
titre: Désaccord de duplex
SRV serveur 0,0 "Serveur" "forcé 100 / full"
SW switch 2,0 "Switch" "auto → 100 / half"
SRV -- SW "les deux côtés ne parlent pas la même règle"
```

Conséquences :

- le côté **half** croit voir des collisions dès que l’autre émet pendant qu’il parle : il compte des **late collisions** et retransmet ;
- le côté **full** reçoit des trames tronquées : il compte des **CRC** et des **runts** ;
- les petits échanges passent, les transferts volumineux s’effondrent.

## Configuration et vérification (Cisco IOS)

La règle d’or : **auto des deux côtés** (recommandé), ou **forcé des deux côtés** avec les mêmes valeurs. Jamais un mélange.

```cisco
! Retour à l'auto-négociation (recommandé)
interface GigabitEthernet1/0/12
 speed auto
 duplex auto
end

! Vérifier ce qui a été négocié
SW1# show interfaces GigabitEthernet1/0/12 status
Port      Name      Status       Vlan  Duplex  Speed Type
Gi1/0/12  SRV-SAV   connected    20    a-full  a-100 10/100/1000BaseTX
```

Le préfixe **a-** signifie « auto-négocié ». Ici, la carte annonce 1000 Mb/s mais le lien est à `a-100` : c’est le signe d’un défaut de câblage, d’un cordon Cat5 ou d’un réglage de la carte.

```cisco
SW1# show interfaces GigabitEthernet1/0/12 | include duplex|collisions|CRC
  Full-duplex, 100Mb/s, media type is 10/100/1000BaseTX
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 output errors, 0 collisions, 1 interface resets
     0 late collision, 0 deferred
```

Avec un désaccord de duplex, on verrait `late collision` augmenter d’un côté et `CRC` de l’autre.

## Diagnostiquer le câble depuis le switch

Beaucoup de switches intègrent un réflectomètre (TDR) qui teste chaque paire :

```cisco
SW1# test cable-diagnostics tdr interface GigabitEthernet1/0/12
SW1# show cable-diagnostics tdr interface GigabitEthernet1/0/12
Interface Speed Local pair Pair length        Remote pair Pair status
--------- ----- ---------- ------------------ ----------- -----------
Gi1/0/12  100M  Pair A     41   +/- 5 meters  Pair B      Normal
                Pair B     41   +/- 5 meters  Pair A      Normal
                Pair C     17   +/- 5 meters  Pair D      Open
                Pair D     17   +/- 5 meters  Pair C      Open
```

Les paires C et D sont **ouvertes** (coupées) à 17 m : un connecteur ou une prise murale est à reprendre à cet endroit. Ce test coupe brièvement le lien : à éviter en production sur un port critique.

> [!CAUTION]
> Forcer `speed 100` et `duplex full` « pour stabiliser » un serveur est une vieille habitude qui crée plus de pannes qu’elle n’en résout. Si l’auto-négociation échoue, cherche d’abord un défaut de câble.

## Exercices

**1.** Un switch affiche `a-half a-100` sur le port d’une imprimante, et l’impression est très lente. L’imprimante est configurée en 100 / full. Que se passe-t-il et comment corriger ?

<details><summary>Voir le corrigé</summary>

**Désaccord de duplex.** L’imprimante, forcée, ne négocie plus ; le switch détecte 100 Mb/s mais tombe en half duplex. Remettre l’imprimante en **auto-négociation** (ou forcer le port du switch en 100/full, en dernier recours). Les deux côtés doivent être réglés de la même manière.

</details>

**2.** Pourquoi le 1000BASE-X sur fibre a-t-il un débit de ligne de 1,25 Gbaud pour transporter 1 Gb/s ?

<details><summary>Voir le corrigé</summary>

À cause du codage **8B10B** : chaque octet (8 bits) est transmis sous forme de 10 symboles, soit 25 % de surcoût. 1 Gb/s × 10/8 = 1,25 Gbaud. Ce surcoût garantit des transitions régulières et permet de détecter certaines erreurs.

</details>

**3.** Le test TDR indique toutes les paires « Normal » à 95 m, mais le port affiche des CRC. Quelle piste explores-tu ?

<details><summary>Voir le corrigé</summary>

Le câble est proche de la limite de 100 m et ses paires sont continues. Les CRC peuvent venir d’**interférences** (passage près de câbles électriques ou de néons), d’une **catégorie de câble insuffisante** ou d’un **connecteur de mauvaise qualité** (le TDR ne détecte pas tout). Vérifier aussi le **duplex** des deux côtés, puis essayer un autre cordon de brassage.

</details>
