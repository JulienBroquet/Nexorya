---
titre: Subnetting, CIDR et VLSM
nom: Découper un réseau sans se tromper
idee: Le préfixe (/24, /26…) indique combien de bits désignent le réseau ; en le déplaçant, on découpe un bloc d’adresses en sous-réseaux de la taille voulue.
osi: "3"
duree: [15, 30]
cle: true
prerequis: [ipv4]
retenir:
  - "Adresses = 2^(32 − préfixe) ; hôtes utilisables = adresses − 2."
  - "**Taille du bloc = 256 − octet du masque** ; les sous-réseaux commencent aux multiples de cette taille."
  - "VLSM — attribuer **du plus grand au plus petit**, chaque sous-réseau aligné sur un multiple de sa taille."
  - La passerelle est **dans le même sous-réseau** que les postes ; un masque faux d’un côté suffit à casser la communication.
---

> [!IMPORTANT] L’idée en une phrase
> Une adresse IPv4 contient deux informations : **le réseau** (le « quartier ») et **l’hôte** (la « maison »). Le **préfixe** indique combien de bits, en partant de la gauche, désignent le réseau. Tout le subnetting consiste à déplacer cette frontière.

## Pourquoi découper un réseau ?

Une PME reçoit le bloc `192.168.40.0/24` : 256 adresses. Elle pourrait tout mettre dans un seul réseau, mais :

- **les broadcasts** (ARP, DHCP…) atteindraient toutes les machines : plus le réseau est grand, plus ce bruit augmente ;
- **la sécurité** serait impossible à organiser : on ne peut filtrer qu’entre deux réseaux, au niveau du routeur ou du pare-feu ;
- **l’organisation** serait illisible : impossible de savoir, à la vue d’une adresse, s’il s’agit d’une imprimante ou d’un serveur.

On découpe donc le bloc en **sous-réseaux** (*subnets*) : un pour le personnel, un pour les imprimantes, un pour l’administration des équipements, etc. En général, **un VLAN = un sous-réseau**.

## L’adresse en binaire : la seule chose à vraiment comprendre

Une adresse IPv4 fait **32 bits**, écrits en 4 octets décimaux. Chaque octet vaut de 0 à 255 et correspond à 8 bits dont les « poids » sont :

| Bit | 1ᵉʳ | 2ᵉ | 3ᵉ | 4ᵉ | 5ᵉ | 6ᵉ | 7ᵉ | 8ᵉ |
|---|---|---|---|---|---|---|---|---|
| **Poids** | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

Exemple : `77` = 64 + 8 + 4 + 1 → `0100 1101`.

Le **masque** est une suite de bits à 1 (la partie réseau) suivie de bits à 0 (la partie hôte). Le **préfixe** (/26) donne simplement le **nombre de 1** :

| Préfixe | Masque | Dernier octet en binaire | Adresses par sous-réseau | Hôtes utilisables |
|---|---|---|---|---|
| /24 | 255.255.255.0 | `0000 0000` | 256 | 254 |
| /25 | 255.255.255.128 | `1000 0000` | 128 | 126 |
| /26 | 255.255.255.192 | `1100 0000` | 64 | 62 |
| /27 | 255.255.255.224 | `1110 0000` | 32 | 30 |
| /28 | 255.255.255.240 | `1111 0000` | 16 | 14 |
| /29 | 255.255.255.248 | `1111 1000` | 8 | 6 |
| /30 | 255.255.255.252 | `1111 1100` | 4 | 2 |

**Pourquoi « − 2 » ?** Dans chaque sous-réseau classique, deux adresses sont réservées :

- la **première** (tous les bits d’hôte à 0) est l’**adresse du réseau** : elle désigne le sous-réseau lui-même, dans les tables de routage ;
- la **dernière** (tous les bits d’hôte à 1) est l’**adresse de broadcast** : un paquet qui lui est envoyé atteint toutes les machines du sous-réseau.

**Formules :** nombre d’adresses = 2^(32 − préfixe) ; hôtes utilisables = 2^(32 − préfixe) − 2.

## La méthode du « nombre magique » (sans binaire)

Pour un masque qui « coupe » dans le dernier octet :

1. **Taille du bloc** = 256 − valeur du masque dans l’octet coupé. Pour /26 : 256 − 192 = **64**.
2. Les sous-réseaux commencent aux **multiples** de cette taille : .0, .64, .128, .192.
3. Le sous-réseau d’une adresse est le **multiple juste en dessous** (ou égal).
4. Le broadcast est **le multiple suivant − 1**.

### Exemple résolu : à quel sous-réseau appartient 192.168.40.77/26 ?

- Taille du bloc : 256 − 192 = 64. Multiples : 0, **64**, 128, 192.
- 77 est entre 64 et 128 → **réseau `192.168.40.64`**.
- Broadcast : 128 − 1 = **`192.168.40.127`**.
- Hôtes utilisables : **`.65` à `.126`** (62 adresses). La passerelle prend souvent la première : `.65`.

**Vérification en binaire** (ce que fait réellement l’ordinateur, avec un ET logique bit à bit) :

```text
Adresse  77  = 0100 1101
Masque  192  = 1100 0000
ET logique   = 0100 0000  = 64   → réseau 192.168.40.64
```

Le ET garde les bits de l’adresse là où le masque vaut 1 et met les autres à 0 : on obtient exactement l’adresse du réseau.

> [!NOTE] Comment un PC décide-t-il d’utiliser sa passerelle ?
> Il applique son masque à sa propre adresse **et** à l’adresse de destination. Si les deux résultats sont identiques, la destination est dans son réseau : il la joint directement (via ARP). Sinon, il envoie le paquet à sa **passerelle**. Un masque faux, et ce choix devient faux.

## Choisir le bon préfixe pour un besoin

Question à se poser : **quelle est la plus petite puissance de 2 qui, moins 2, couvre le besoin (avec une marge de croissance) ?**

| Besoin | Calcul | Préfixe retenu |
|---|---|---|
| 50 postes | 2⁶ − 2 = 62 ≥ 50 (2⁵ − 2 = 30 trop petit) | **/26** |
| 20 imprimantes | 2⁵ − 2 = 30 ≥ 20 | **/27** |
| 10 équipements à administrer | 2⁴ − 2 = 14 ≥ 10 | **/28** |
| Lien entre deux routeurs | 2 adresses | **/30** (ou /31, voir plus bas) |

## Les mots à connaître

- **Sous-réseau** — Partie d’un bloc d’adresses, découpée avec un préfixe plus long ; *subnet*.
- **Préfixe** — Nombre de bits de la partie réseau, noté après une barre oblique : /26.
- **VLSM** — *Variable Length Subnet Mask*, découpage d’un bloc en sous-réseaux de tailles différentes.
- **Taille de bloc** — Nombre d’adresses d’un sous-réseau ; 64 pour un /26. On l’appelle aussi « nombre magique ».

## Teste-toi

**1.** Combien d’hôtes utilisables dans un /28 ?

<details><summary>Voir le corrigé</summary>

32 − 28 = 4 bits d’hôte → 2⁴ = 16 adresses → **14 hôtes**.

</details>

**2.** À quel sous-réseau appartient `192.168.40.130/26` ?

<details><summary>Voir le corrigé</summary>

Taille du bloc : 256 − 192 = 64. Multiples : 0, 64, **128**, 192. 130 est entre 128 et 192 → réseau **192.168.40.128**, broadcast .191, hôtes .129 à .190.

</details>

<!-- approfondir -->

## VLSM : des sous-réseaux de tailles différentes

**VLSM** (*Variable Length Subnet Mask*) permet d’utiliser des préfixes différents dans un même bloc. Règle d’or : **placer les plus grands sous-réseaux en premier**, chacun commençant à un multiple de sa propre taille. Sinon, on crée des trous ou des chevauchements.

### Exemple résolu : découper 192.168.40.0/24

| Ordre | Besoin | Préfixe | Réseau | Plage d’hôtes | Broadcast | Passerelle |
|---|---|---|---|---|---|---|
| 1 | Personnel (50) | /26 | 192.168.40.**0** | .1 – .62 | .63 | .1 |
| 2 | Imprimantes (20) | /27 | 192.168.40.**64** | .65 – .94 | .95 | .65 |
| 3 | Gestion (10) | /28 | 192.168.40.**96** | .97 – .110 | .111 | .97 |
| 4 | Lien vers le routeur WAN | /30 | 192.168.40.**112** | .113 – .114 | .115 | — |
| — | **Libre pour la croissance** | | .116 à .255 | | | |

Contrôle : chaque réseau commence juste après le broadcast du précédent (.63 → .64, .95 → .96, .111 → .112) et à un multiple de sa taille (64, 32, 16, 4). Aucun chevauchement.

> [!WARNING] Attention à l’espace libre
> De .116 à .255, tout n’est pas utilisable n’importe comment : un futur /26 (64 adresses) doit commencer à un multiple de 64, donc à **.128** — pas à .116.

## Vérifier sur un équipement Cisco

```cisco
show ip interface brief
show ip interface vlan 10
show ip route connected
```

- `show ip interface vlan 10` affiche `Internet address is 192.168.40.1/26` : vérifier **l’adresse ET le préfixe**.
- `show ip route connected` liste les réseaux directement connectés : `C 192.168.40.0/26 is directly connected, Vlan10`. Si le préfixe affiché n’est pas celui du plan d’adressage, le masque est faux.

**Symptôme typique d’un masque erroné :** la passerelle est configurée en /26, un PC en /24. Le PC croit que `192.168.40.70` est dans son réseau et tente de le joindre directement par ARP au lieu de passer par la passerelle. Résultat : certaines destinations fonctionnent, d’autres non. **Toujours comparer les masques aux deux extrémités** avant d’ajouter une route.

## Cas particuliers et pièges

- **/31** (RFC 3021) : sur un lien point à point, les deux adresses sont utilisables, il n’y a ni adresse de réseau ni broadcast. Courant entre routeurs, pour économiser les adresses.
- **/32** : une seule adresse — on l’utilise pour une **route d’hôte** ou une interface *loopback*.
- **Masque qui coupe un autre octet.** `172.16.0.0/22` : masque 255.255.**252**.0, taille du bloc 256 − 252 = **4** dans le **3ᵉ octet**. Le réseau va de 172.16.**0**.0 à 172.16.**3**.255 : 1024 adresses, 1022 hôtes. `172.16.2.255` y est une adresse d’hôte valide, pas un broadcast.
- **Ne pas confondre** « nombre d’adresses » et « nombre d’hôtes » : un /26 contient 64 adresses mais 62 hôtes.

## Exercices progressifs

Essaie de répondre sur papier avant d’ouvrir chaque corrigé. Tu peux ensuite vérifier avec le [calculateur de sous-réseaux](../outils/cidr.html).

**Exercice 1 (découverte).** Combien d’hôtes utilisables dans un /29 ?

<details><summary>Voir le corrigé</summary>

32 − 29 = 3 bits d’hôte → 2³ = 8 adresses → **8 − 2 = 6 hôtes** utilisables.

</details>

**Exercice 2 (découverte).** Un service compte 100 postes. Quel est le plus petit préfixe adapté ?

<details><summary>Voir le corrigé</summary>

2⁶ − 2 = 62 : insuffisant. 2⁷ − 2 = 126 ≥ 100 → 7 bits d’hôte → **/25** (masque 255.255.255.128).

</details>

**Exercice 3 (pratique).** Donne le réseau, le broadcast et la plage d’hôtes de `10.0.5.200/27`.

<details><summary>Voir le corrigé</summary>

Masque /27 = 255.255.255.224 → taille du bloc 256 − 224 = **32**. Multiples : …, 160, **192**, 224. 200 est entre 192 et 224.
**Réseau `10.0.5.192`**, **broadcast `10.0.5.223`**, hôtes **`.193` à `.222`**.

</details>

**Exercice 4 (pratique).** `192.168.1.10/25` et `192.168.1.130/25` peuvent-ils communiquer sans routeur ?

<details><summary>Voir le corrigé</summary>

/25 → bloc de 128 : sous-réseaux `.0` (`.0`–`.127`) et `.128` (`.128`–`.255`). `.10` est dans le premier, `.130` dans le second. **Non** : ce sont deux réseaux différents, il faut passer par un routeur (la passerelle).

</details>

**Exercice 5 (diagnostic).** Un PC est configuré en `192.168.1.10/24` avec la passerelle `192.168.2.1`. Il joint les machines de son réseau, mais pas Internet. Pourquoi ?

<details><summary>Voir le corrigé</summary>

La passerelle **doit appartenir au même réseau que le PC**. Avec /24, le réseau du PC est `192.168.1.0` (`.1` à `.254`) ; `192.168.2.1` est hors de ce réseau. Le PC ne peut pas la joindre en ARP et ne peut donc rien lui confier. Il faut corriger la passerelle (probablement `192.168.1.1`) — ou le masque, si c’est lui qui est faux.

</details>

**Exercice 6 (expert — VLSM).** Découpe `10.20.0.0/24` pour : un VLAN de 120 postes, un de 60 postes, un de 25 caméras et deux liens point à point en /30. Donne chaque réseau.

<details><summary>Voir le corrigé</summary>

On trie du plus grand au plus petit, et chaque réseau commence à un multiple de sa taille :

| Besoin | Préfixe | Réseau | Hôtes | Broadcast |
|---|---|---|---|---|
| 120 postes | /25 (126) | 10.20.0.0 | .1 – .126 | .127 |
| 60 postes | /26 (62) | 10.20.0.128 | .129 – .190 | .191 |
| 25 caméras | /27 (30) | 10.20.0.192 | .193 – .222 | .223 |
| Lien 1 | /30 | 10.20.0.224 | .225 – .226 | .227 |
| Lien 2 | /30 | 10.20.0.228 | .229 – .230 | .231 |

Reste libre : `10.20.0.232` à `10.20.0.255`. Remarque : 60 postes dans un /26 ne laisse que 2 adresses de marge ; en production, on discuterait d’un /25 pour ce VLAN si la croissance est probable.

</details>
