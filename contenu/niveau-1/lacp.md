---
titre: LACP
nom: Link Aggregation Control Protocol (IEEE 802.3ad / 802.1AX)
idee: LACP regroupe plusieurs câbles en un seul lien logique — plus de capacité et une tolérance aux pannes, sans que STP bloque les câbles en trop.
osi: "2"
duree: [8, 16]
prerequis: [stp]
retenir:
  - Un **agrégat** (port-channel, EtherChannel) additionne plusieurs liens en un seul lien logique ; STP le voit comme **un seul port**.
  - Chaque **flux** utilise un seul lien membre (hachage) — un transfert unique ne dépasse pas la vitesse d’un câble.
  - "Modes LACP — **active/active** ou **active/passive**. Jamais **active/on**."
  - Tous les membres doivent avoir la **même configuration** (vitesse, duplex, VLAN, mode).
---

## Le problème : deux câbles, mais un seul utilisé

On relie un switch d’accès à la distribution avec **deux câbles**, pour avoir plus de débit et un secours. Mais [STP](stp.md) voit une boucle et bloque l’un des deux. On paie deux câbles et deux ports, et un seul travaille.

> [!IMPORTANT] L’idée en une phrase
> LACP fait de plusieurs câbles **un seul lien logique** : STP n’y voit qu’un port, tous les câbles transportent du trafic, et si l’un tombe, les autres continuent.

## Comment ça marche

1. On déclare plusieurs ports comme membres d’un même **agrégat** (port-channel).
2. Les deux switches s’échangent des messages LACP pour vérifier qu’ils parlent bien du même agrégat, avec des ports compatibles.
3. Les ports validés deviennent un seul lien logique, `Port-channel1`.
4. Le switch répartit le trafic entre les câbles. Si un câble tombe, le trafic passe sur les autres en une fraction de seconde.

```topologie
titre: Deux liens 10 Gb/s agrégés
ACC switch 0,0 "Switch d’accès"
DIST l3 3,0 "Distribution"
ACC == DIST "Port-channel1 : 2 × 10 Gb/s"
```

## Le piège du « 20 Gb/s »

Deux liens de 10 Gb/s agrégés **ne font pas un tuyau de 20 Gb/s** pour une seule copie de fichier. Pour que les paquets d’une même conversation arrivent dans l’ordre, le switch place **chaque flux sur un seul câble**, en calculant une sorte d’empreinte (hachage) à partir des adresses. Un transfert unique plafonne donc à 10 Gb/s. Ce sont **plusieurs flux simultanés** (plusieurs utilisateurs, plusieurs serveurs) qui profitent des 20 Gb/s.

> [!TIP] L’analogie des caisses de supermarché
> Ouvrir une deuxième caisse permet de servir deux fois plus de clients, mais ne fait pas passer **un** client plus vite. Chaque client (chaque flux) reste à sa caisse.

## Erreurs fréquentes

- **Configurer un côté en LACP et l’autre en statique** (`active` d’un côté, `on` de l’autre) : l’agrégat ne se forme pas correctement.
- **Câbles membres configurés différemment** : un port avec une liste de VLAN différente est exclu (*suspended*).
- **Brancher les deux câbles avant de configurer l’agrégat** des deux côtés : STP bloque l’un d’eux (au mieux), ou une boucle se forme (au pire).

## Les mots à connaître

- **Agrégation de liens** — Regroupement de plusieurs liens physiques en un seul lien logique.
- **Port-channel** — Interface logique qui représente l’agrégat sur un équipement Cisco ; aussi appelée EtherChannel.
- **LACP** — Protocole standard qui négocie et surveille un agrégat de liens.
- **Hachage** — Calcul qui choisit le lien membre utilisé par chaque flux, à partir des adresses ou des ports.

## Teste-toi

**1.** Un serveur relié par deux liens de 1 Gb/s agrégés copie un gros fichier vers un autre serveur. Quel débit maximal peut-il espérer ?

<details><summary>Voir le corrigé</summary>

**1 Gb/s.** Un seul flux utilise un seul lien membre. Plusieurs copies simultanées vers des destinations différentes pourraient, elles, utiliser les deux liens.

</details>

**2.** Pourquoi STP ne bloque-t-il pas un des câbles d’un agrégat ?

<details><summary>Voir le corrigé</summary>

Parce que STP voit le port-channel comme **un seul port logique**. Il n’y a donc pas de boucle de son point de vue : un seul lien relie les deux switches.

</details>

<!-- approfondir -->

## Modes de négociation

| Côté A \ Côté B | `active` | `passive` | `on` |
|---|---|---|---|
| `active` | ✓ agrégat LACP | ✓ agrégat LACP | ✗ incohérent |
| `passive` | ✓ | ✗ personne ne commence | ✗ |
| `on` | ✗ incohérent | ✗ | ✓ agrégat statique, sans protocole |

- `active` : envoie des LACPDU et forme l’agrégat si le voisin répond.
- `passive` : répond seulement si le voisin envoie.
- `on` : force l’agrégat **sans aucun contrôle**. Si le voisin n’est pas configuré de la même façon, une boucle peut se former. À éviter.
- PAgP (`desirable`/`auto`) est l’équivalent propriétaire Cisco, aujourd’hui supplanté par LACP.

LACP envoie une LACPDU toutes les 30 s (*slow*) ou toutes les secondes (*fast*, `lacp rate fast`). Un membre qui cesse de recevoir des LACPDU est retiré, ce qui protège aussi contre les liens unidirectionnels.

## Configuration (Cisco IOS)

```cisco
! Les deux interfaces membres
interface range TenGigabitEthernet1/1/1 - 2
 description Uplink vers DIST1
 channel-group 1 mode active
!
! L'interface logique porte la configuration de couche 2
interface Port-channel1
 description Agrégat vers DIST1
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,99
!
! Hachage : inclure les ports pour mieux répartir
port-channel load-balance src-dst-mixed-ip-port
```

Configure de préférence le port-channel **avant** de brancher le second câble, et applique les modifications de couche 2 sur l’interface `Port-channel`, qui les recopie sur les membres.

## Vérification

```cisco
ACC1# show etherchannel summary
Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        S - Layer2      U - in use
Group  Port-channel  Protocol    Ports
------+-------------+-----------+-----------------------------------------------
1      Po1(SU)         LACP        Te1/1/1(P)   Te1/1/2(s)
```

- `Po1(SU)` : agrégat de couche 2, en service.
- `Te1/1/1(P)` : membre actif.
- `Te1/1/2(s)` : membre **suspendu**, en général parce que sa configuration diffère (VLAN autorisés, vitesse) ou parce que le voisin n’est pas dans le même agrégat.

```cisco
ACC1# show lacp neighbor
ACC1# show interfaces Te1/1/2 etherchannel
ACC1# show etherchannel load-balance
```

## Agrégat vers deux switches différents (MC-LAG)

Un agrégat classique relie **deux** équipements. Pour qu’un switch d’accès se relie à **deux** switches de distribution par un seul agrégat (et survive à la perte de l’un d’eux), ces deux switches doivent se présenter comme un seul partenaire LACP : c’est le rôle du **stacking**, de **StackWise Virtual**, de **vPC** (Nexus) ou des solutions MLAG. Voir [Redondance de switches](../niveau-5/redondance-switches.md).

## Exercices

**1.** `show etherchannel summary` affiche `Po1(SD)` et les deux membres en `(I)`. Que signifie-t-il, et que vérifier ?

<details><summary>Voir le corrigé</summary>

L’agrégat est **down** et les ports fonctionnent **individuellement** (*stand-alone*) : le voisin ne répond pas en LACP. Vérifier que le voisin est configuré avec `channel-group` en mode `active` ou `passive`, sur les bons ports, et qu’aucun côté n’est en `on`.

</details>

**2.** Un agrégat de 4 × 1 Gb/s relie un serveur de sauvegarde à un switch. Toutes les sauvegardes viennent d’un seul serveur de fichiers, et le hachage est `src-dst-mac`. Pourquoi un seul lien est-il chargé ?

<details><summary>Voir le corrigé</summary>

Avec `src-dst-mac`, tous les paquets entre les deux mêmes MAC donnent le **même** résultat de hachage : un seul lien est utilisé. Passer à un hachage incluant **IP et ports** (`src-dst-mixed-ip-port`), et paralléliser la sauvegarde en plusieurs connexions, répartira mieux la charge.

</details>

**3.** Un administrateur ajoute le VLAN 40 sur Te1/1/1 uniquement, et non sur l’interface Port-channel1. Conséquence ?

<details><summary>Voir le corrigé</summary>

Les membres n’ont plus la **même configuration** : Te1/1/1 est **suspendu** (ou l’ajout est refusé selon la plateforme). L’agrégat continue sur les autres membres avec moins de capacité. Il faut toujours modifier l’interface `Port-channel`.

</details>
