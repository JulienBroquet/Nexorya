---
titre: VLAN
nom: Virtual Local Area Network (IEEE 802.1Q)
idee: Un VLAN découpe un switch physique en plusieurs réseaux locaux séparés ; les machines de deux VLAN différents ne se voient pas sans passer par un routeur.
osi: "2"
duree: [8, 18]
prerequis: [switch]
retenir:
  - Un **VLAN** est un réseau local logique — même switch, réseaux séparés.
  - "**Un VLAN = un domaine de diffusion = en général un sous-réseau IP.**"
  - Un port **d’accès** appartient à un seul VLAN ; un port **trunk** transporte plusieurs VLAN entre switches.
  - Pour passer d’un VLAN à l’autre, il faut un **routeur** ou un switch de niveau 3 — et c’est là qu’on filtre.
---

## Le problème : séparer sans racheter des switches

Dans une entreprise, les postes des employés, les téléphones, les imprimantes, les caméras et les visiteurs sont branchés sur les mêmes switches. Pourtant, on ne veut pas qu’un visiteur puisse voir les ordinateurs de la comptabilité, ni qu’une caméra piratée puisse attaquer un serveur. Acheter un switch séparé pour chaque groupe serait coûteux et absurde.

> [!IMPORTANT] L’idée en une phrase
> Un VLAN découpe un switch en **plusieurs switches virtuels**. Chaque port est rangé dans un VLAN ; les machines de VLAN différents ne se voient pas, comme si elles étaient sur des switches distincts.

## Comment ça marche

1. L’administrateur crée des VLAN, chacun avec un **numéro** et un nom : VLAN 10 « Employés », VLAN 20 « Téléphones », VLAN 30 « Invités ».
2. Il range chaque **port d’accès** dans un VLAN : le port 3 dans le VLAN 10, le port 4 dans le VLAN 30…
3. Le switch ne transmet une trame **qu’aux ports du même VLAN**. Les broadcasts aussi restent dans le VLAN.
4. Pour qu’un employé imprime sur une imprimante d’un autre VLAN, le trafic passe par un **routeur** (ou un switch de niveau 3), qui peut appliquer des règles de filtrage.

```topologie
titre: Un seul switch, trois réseaux séparés
SW switch 1.5,0 "Switch d’étage"
E1 pc 0,1 "Employé" "VLAN 10"
E2 pc 1,1 "Employé" "VLAN 10"
T telephone 2,1 "Téléphone" "VLAN 20"
V portable 3,1 "Visiteur" "VLAN 30"
SW -- E1
SW -- E2
SW -- T
SW -- V
```

Les deux employés communiquent directement. Le visiteur, lui, ne reçoit rien des employés, même branché sur le même switch.

## Port d’accès et port trunk

| Type de port | VLAN transportés | Branché vers | Les trames portent-elles une étiquette ? |
|---|---|---|---|
| **Accès** | un seul | un PC, une imprimante, une caméra | non, l’appareil ne sait même pas qu’il est dans un VLAN |
| **Trunk** | plusieurs | un autre switch, un routeur, un serveur de virtualisation | oui, une étiquette indique le VLAN de chaque trame |

Le fonctionnement des étiquettes est expliqué dans la fiche [802.1Q](802-1q.md).

## Un VLAN, un sous-réseau

En pratique, chaque VLAN reçoit sa propre plage d’adresses IP : VLAN 10 = `10.10.0.0/24`, VLAN 20 = `10.20.0.0/24`… C’est logique : un VLAN est un domaine de diffusion, et un sous-réseau IP aussi. Une astuce courante consiste à reprendre le numéro de VLAN dans l’adresse, pour s’y retrouver d’un coup d’œil.

## Erreurs fréquentes

- **Croire qu’un VLAN est une protection suffisante.** Dès qu’un routeur relie les VLAN sans filtrage, tout le monde peut à nouveau communiquer. La séparation devient réelle avec des règles de filtrage (ACL, pare-feu).
- **Oublier de créer le VLAN sur tous les switches** traversés : le trafic s’arrête au premier switch qui ne le connaît pas.
- **Laisser des ports inutilisés dans le VLAN par défaut (VLAN 1)** : n’importe qui peut s’y brancher.

## Les mots à connaître

- **VLAN** — Réseau local virtuel : groupe de ports d’un ou plusieurs switches qui forment un réseau séparé des autres.
- **Port d’accès** — Port de switch rangé dans un seul VLAN, pour brancher un appareil final.
- **Trunk** — Lien entre équipements qui transporte plusieurs VLAN, chaque trame portant l’étiquette de son VLAN.
- **VLAN 1** — VLAN par défaut de tous les ports d’un switch neuf.

## Teste-toi

**1.** Un visiteur est branché sur le port 12 (VLAN 30) et un serveur sur le port 13 (VLAN 10) du même switch. Le visiteur peut-il joindre le serveur ?

<details><summary>Voir le corrigé</summary>

**Pas directement.** Ils sont dans deux VLAN différents : le switch ne transmet pas les trames de l’un à l’autre. Il faudrait passer par un routeur… qui, s’il existe, doit justement **bloquer** ce trafic avec une règle.

</details>

**2.** Pourquoi met-on les téléphones IP dans un VLAN différent de celui des ordinateurs ?

<details><summary>Voir le corrigé</summary>

Pour **donner la priorité** à la voix (qualité de service appliquée au VLAN voix), pour **limiter** les broadcasts que les téléphones reçoivent, et pour **filtrer** plus facilement les échanges entre les deux mondes. Un téléphone n’a pas besoin de joindre les postes de travail.

</details>

<!-- approfondir -->

## Les numéros de VLAN

| Plage | Usage |
|---|---|
| 0 et 4095 | réservés (0 = trame de priorité sans VLAN) |
| 1 | VLAN par défaut ; ne peut pas être supprimé sur Cisco |
| 2 à 1001 | plage normale |
| 1002 à 1005 | réservés historiquement (Token Ring, FDDI) sur Cisco |
| 1006 à 4094 | plage étendue |

Le numéro est codé sur **12 bits** dans l’étiquette 802.1Q : 4 094 VLAN utilisables au maximum. Cette limite explique l’existence de [QinQ](qinq.md) chez les opérateurs et de VXLAN dans les datacenters.

## Configurer des VLAN (Cisco IOS)

```cisco
! Créer et nommer les VLAN
vlan 10
 name EMPLOYES
vlan 20
 name VOIX
vlan 30
 name INVITES
vlan 999
 name PARKING
!
! Port d'un poste de travail avec téléphone IP chaîné
interface GigabitEthernet1/0/5
 description Bureau 214
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
!
! Ports inutilisés : VLAN « parking » sans routage, et port éteint
interface range GigabitEthernet1/0/40 - 48
 switchport mode access
 switchport access vlan 999
 shutdown
```

- `switchport mode access` fixe le port en accès : il ne négociera jamais de trunk (voir [DTP](dtp.md)).
- `switchport voice vlan 20` : le téléphone envoie ses trames **étiquetées** VLAN 20 (il l’apprend par CDP ou LLDP-MED), le PC branché derrière lui envoie des trames **non étiquetées**, rangées dans le VLAN 10.

## Vérifier

```cisco
SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active
10   EMPLOYES                         active    Gi1/0/5, Gi1/0/6, Gi1/0/7
20   VOIX                             active    Gi1/0/5, Gi1/0/6
30   INVITES                          active    Gi1/0/12
999  PARKING                          active    Gi1/0/40, Gi1/0/41, …

SW1# show interfaces GigabitEthernet1/0/5 switchport
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 10 (EMPLOYES)
Voice VLAN: 20 (VOIX)
```

`show vlan brief` ne liste que les ports **d’accès** : les trunks n’y apparaissent pas. Pour eux, utilise `show interfaces trunk`.

## Plan de VLAN type pour une PME

| VLAN | Nom | Sous-réseau | Passerelle | Remarque |
|---|---|---|---|---|
| 10 | EMPLOYES | 10.10.0.0/24 | 10.10.0.1 | postes de travail |
| 20 | VOIX | 10.20.0.0/24 | 10.20.0.1 | téléphones, QoS prioritaire |
| 30 | INVITES | 10.30.0.0/24 | 10.30.0.1 | accès Internet seulement |
| 40 | IMPRIMANTES | 10.40.0.0/24 | 10.40.0.1 | joignables depuis le VLAN 10 seulement |
| 50 | CAMERAS | 10.50.0.0/24 | 10.50.0.1 | vers l’enregistreur seulement |
| 99 | GESTION | 10.99.0.0/24 | 10.99.0.1 | administration des équipements, accès restreint |
| 999 | PARKING | — | — | ports inutilisés, aucun routage |

## Dépannage d’un VLAN

Un utilisateur n’a pas de réseau, ses voisins oui :

1. **Le port** : `show interfaces Gi1/0/x status` — connecté ? dans quel VLAN ?
2. **Le VLAN existe** sur ce switch : `show vlan brief`. Un port affecté à un VLAN inexistant est **inactif**.
3. **Le VLAN traverse les trunks** jusqu’au switch de cœur : `show interfaces trunk` sur chaque lien (VLAN autorisé, actif et en forwarding).
4. **La passerelle** (SVI) existe et est active : `show ip interface brief | include Vlan`.
5. **L’adressage** du poste correspond au sous-réseau du VLAN (DHCP, ou erreur de configuration manuelle).

## Exercices

**1.** Le port Gi1/0/8 est configuré `switchport access vlan 60`, mais le VLAN 60 n’a jamais été créé. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

Selon les versions, le switch crée le VLAN automatiquement ou laisse le port **inactif** (`show interfaces switchport` affiche « Inactive »). Dans tous les cas, le VLAN n’existe pas sur les autres switches ni sur les trunks : le poste ne joindra pas sa passerelle. Il faut créer le VLAN partout où il doit passer.

</details>

**2.** On veut que les imprimantes (VLAN 40) soient joignables depuis les employés (VLAN 10) mais pas depuis les invités (VLAN 30). Où applique-t-on cette règle ?

<details><summary>Voir le corrigé</summary>

Sur l’équipement qui **route** entre les VLAN (switch de niveau 3 ou pare-feu), avec une **ACL** : autoriser 10.10.0.0/24 vers 10.40.0.0/24 sur les ports d’impression, refuser 10.30.0.0/24 vers les réseaux internes. Le VLAN sépare, le filtrage décide de ce qui est autorisé entre les morceaux.

</details>

**3.** Un PC branché derrière un téléphone IP obtient une adresse du réseau voix (10.20.0.x). Quelle erreur de configuration soupçonnes-tu ?

<details><summary>Voir le corrigé</summary>

Le port est probablement configuré avec le VLAN 20 comme **VLAN d’accès** (`switchport access vlan 20`) au lieu de `voice vlan 20`. Les trames non étiquetées du PC tombent alors dans le VLAN voix. Corriger : `switchport access vlan 10` et `switchport voice vlan 20`.

</details>
