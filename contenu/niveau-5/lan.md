---
titre: LAN
nom: Le réseau local d’entreprise
idee: Le LAN relie les équipements d’un même site ; en entreprise, on le construit en couches — accès, distribution, cœur — pour qu’il soit robuste et facile à faire grandir.
osi: "1 à 3"
duree: [8, 16]
retenir:
  - "Un LAN de campus s’organise en **accès** (postes), **distribution** (agrégation, passerelles) et **cœur** (transport rapide)."
  - Dans les petits sites, distribution et cœur sont **fusionnés** (cœur replié).
  - "Tendance actuelle — **routage dès la distribution** (ou l’accès), pour limiter l’étendue des VLAN et de STP."
---

## Le problème : un réseau qui grandit

Une entreprise commence avec un switch dans un placard. Puis un deuxième, puis un étage entier, un second bâtiment… Si chaque switch est simplement branché sur le précédent, on obtient une guirlande fragile : une panne au milieu coupe tout ce qui suit, et personne ne sait plus où passe le trafic.

> [!IMPORTANT] L’idée en une phrase
> On construit le LAN en **couches** qui ont chacune un rôle, avec des liens doublés entre elles : on sait où passe le trafic, et une panne n’isole personne.


```photo
fichier: baie-reseau.jpg
legende: "Une baie de distribution : switches, panneaux de brassage cuivre et fibre, jarretières rangées dans des guide-câbles. Un réseau bien conçu se reconnaît aussi à une baie lisible."
alt: "Baie réseau avec switches, panneaux de brassage et câbles rangés"
```

## Le modèle en trois couches

```topologie
titre: Un campus en trois couches
C1 l3 1,0 "Cœur 1"
C2 l3 3,0 "Cœur 2"
D1 l3 0.5,1 "Distribution A"
D2 l3 1.5,1 "Distribution A’"
D3 l3 2.5,1 "Distribution B"
D4 l3 3.5,1 "Distribution B’"
A1 switch 0.5,2 "Accès étage 1"
A2 switch 1.5,2 "Accès étage 2"
A3 switch 3,2 "Accès bâtiment B"
C1 == C2
C1 -- D1
C1 -- D2
C2 -- D1
C2 -- D2
C1 -- D3
C2 -- D4
C1 -- D4
C2 -- D3
D1 -- A1
D2 -- A1
D1 -- A2
D2 -- A2
D3 -- A3
D4 -- A3
```

| Couche | Rôle | Fonctions typiques |
|---|---|---|
| **Accès** | brancher les utilisateurs et les appareils | ports PoE, VLAN, 802.1X, protections des ports |
| **Distribution** | agréger les switches d’accès d’une zone | passerelles des VLAN (SVI, HSRP), routage, filtrage, QoS |
| **Cœur** | transporter très vite entre les zones | routage rapide, redondance, aucune fonction lourde |

Dans un site de taille moyenne, on fusionne distribution et cœur : c’est le **cœur replié** (*collapsed core*).

## Les mots à connaître

- **LAN** — *Local Area Network*, réseau d’un même site (bureau, bâtiment, campus).
- **Couche d’accès / de distribution / de cœur** — Les trois niveaux d’une architecture de campus.
- **Cœur replié** — Architecture où les rôles de distribution et de cœur sont assurés par les mêmes équipements.
- **Campus** — Réseau qui relie plusieurs bâtiments proches d’un même site.

## Teste-toi

**Pourquoi chaque switch d’accès est-il relié à deux switches de distribution ?**

<details><summary>Voir le corrigé</summary>

Pour qu’une **panne** d’un switch de distribution ou d’un câble n’isole pas l’étage : le second chemin prend le relais. Les deux liens peuvent aussi être utilisés ensemble (agrégation multichâssis, voir [Redondance de switches](redondance-switches.md)).

</details>

<!-- approfondir -->

## Où placer la frontière entre niveau 2 et niveau 3 ?

| Design | Principe | Avantages | Inconvénients |
|---|---|---|---|
| **Accès L2, distribution L3** (classique) | VLAN entre accès et distribution ; passerelles HSRP sur la distribution | simple, VLAN étendus sur quelques switches | STP actif sur les liens accès–distribution |
| **Distribution en paire virtuelle** (StackWise Virtual, vPC, MLAG) | les deux switches de distribution forment un seul partenaire LACP | plus de port bloqué par STP, bascule rapide | dépendance au mécanisme de couplage |
| **Accès routé** (L3 jusqu’à l’accès) | chaque switch d’accès route ; liens routés vers la distribution | plus de STP entre switches, convergence par le routage (ECMP) | un VLAN ne s’étend plus entre étages |
| **Fabric de campus** (SD-Access, EVPN) | réseau routé + overlay pour étendre des segments si besoin | segmentation par rôle, mobilité | complexité, outillage |

La tendance est claire : **limiter les domaines de niveau 2** et confier la redondance au **routage**, qui converge vite et utilise tous les liens.

## Règles de conception

- **Redondance** à chaque niveau : deux équipements, deux liens, deux alimentations.
- **Surdimensionnement** contrôlé des liens montants : rapport accès/uplink de l’ordre de 20:1 dans l’accès, 4:1 vers le cœur.
- **Plan d’adressage** résumable par zone (un bloc par bâtiment), pour simplifier le routage.
- **Racine STP** et **passerelle active** sur le même switch de distribution pour chaque VLAN.
- **Gestion hors bande** (réseau ou VRF d’administration) pour garder la main pendant une panne.

## Exercice

**Un site de 3 étages (150 postes) a deux switches de cœur et un switch d’accès par étage. Faut-il une couche de distribution séparée ?**

<details><summary>Voir le corrigé</summary>

**Non** : à cette taille, un **cœur replié** suffit. Les deux switches de cœur portent les passerelles et le routage ; chaque switch d’accès y est relié par deux liens (idéalement un agrégat multichâssis). Une couche de distribution séparée devient utile quand le nombre de switches d’accès ou de bâtiments augmente.

</details>
