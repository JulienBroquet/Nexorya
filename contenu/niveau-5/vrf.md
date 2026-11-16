---
titre: VRF
nom: Virtual Routing and Forwarding
idee: Une VRF crée plusieurs tables de routage indépendantes dans un même routeur ; c’est l’équivalent, pour le routage, de ce que les VLAN sont pour les switches.
osi: "3"
duree: [7, 15]
prerequis: [passerelle, vlan]
retenir:
  - Chaque VRF a sa **propre table de routage** et ses propres interfaces.
  - Deux VRF peuvent contenir le **même préfixe** sans conflit.
  - Le trafic **ne passe pas** d’une VRF à l’autre, sauf si on l’organise (fuite de routes, pare-feu).
  - "Usages — séparer des clients, isoler l’administration, forcer le passage par un pare-feu entre zones."
---

## Le problème

Sur un switch de cœur, tous les VLAN sont routés entre eux par une seule table de routage. Pour isoler fortement certaines zones (administration, partenaires, objets connectés), une ACL est possible mais fragile : une erreur, et tout se mélange. Et un hébergeur voudrait accueillir plusieurs clients qui utilisent les mêmes adresses.

> [!IMPORTANT] L’idée en une phrase
> Une VRF découpe un routeur en plusieurs routeurs virtuels, chacun avec sa propre table de routage : ce qui est dans une VRF ne voit pas ce qui est dans une autre.

## Comment ça marche

```topologie
titre: Un switch de cœur, trois routeurs virtuels
CO l3 2,0 "Cœur"
FW parefeu 2,1.3 "Pare-feu"
UTI switch 0,0 "VLAN utilisateurs" "VRF UTILISATEURS"
SRV serveur 4,0 "Serveurs" "VRF SERVEURS"
ADM serveur 4,1.3 "Administration" "VRF GESTION"
UTI -- CO
CO -- SRV
CO -- FW "passage obligé entre VRF"
CO -- ADM
```

1. On crée des VRF : `UTILISATEURS`, `SERVEURS`, `GESTION`.
2. On rattache chaque interface (SVI, port routé) à une VRF.
3. Chaque VRF a sa table : une route présente dans `UTILISATEURS` n’existe pas dans `SERVEURS`.
4. Pour communiquer, le trafic passe par un **pare-feu** relié aux deux VRF : toute communication entre zones est contrôlée.

## VLAN et VRF

| | VLAN | VRF |
|---|---|---|
| Couche | 2 | 3 |
| Sépare | les domaines de diffusion | les tables de routage |
| Analogie | plusieurs switches virtuels | plusieurs routeurs virtuels |

## Les mots à connaître

- **VRF** — *Virtual Routing and Forwarding*, table de routage indépendante dans un routeur.
- **VRF-Lite** — Usage des VRF sans MPLS, dans un réseau d’entreprise.
- **Fuite de routes** — Partage contrôlé de certaines routes entre deux VRF ; *route leaking*.

## Teste-toi

**Deux VRF contiennent le préfixe `10.10.0.0/16`. Est-ce une erreur ?**

<details><summary>Voir le corrigé</summary>

**Non.** Les deux tables sont **indépendantes** : le même préfixe peut exister dans chacune. C’est justement ce qui permet à un hébergeur ou un opérateur d’accueillir des clients aux adresses qui se chevauchent.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS-XE, VRF-Lite)

```cisco
vrf definition GESTION
 address-family ipv4
!
vrf definition SERVEURS
 address-family ipv4
!
interface Vlan99
 vrf forwarding GESTION              ! attention : retire l'adresse IP existante de l'interface
 ip address 10.99.0.1 255.255.255.0
!
interface Vlan20
 vrf forwarding SERVEURS
 ip address 10.20.0.1 255.255.255.0
!
ip route vrf GESTION 0.0.0.0 0.0.0.0 10.99.255.1
router ospf 20 vrf SERVEURS
 network 10.20.0.0 0.0.255.255 area 0
```

> [!CAUTION]
> `vrf forwarding` sur une interface **efface son adresse IP**. Si c’est l’interface par laquelle tu administres l’équipement, tu perds la main. Prépare la configuration complète, utilise la console ou une autre interface.

## Vérifier et tester dans une VRF

```cisco
SW1# show vrf
  Name                Default RD    Protocols   Interfaces
  GESTION             <not set>     ipv4        Vl99
  SERVEURS            <not set>     ipv4        Vl20
SW1# show ip route vrf SERVEURS
SW1# ping vrf GESTION 10.99.0.50
SW1# traceroute vrf SERVEURS 10.20.0.40
```

Toutes les commandes de test doivent préciser la VRF : un `ping` sans `vrf` part de la table **globale**, où la destination n’existe peut-être pas.

## Gestion hors bande

Beaucoup d’équipements ont un port de gestion dédié, placé d’office dans une VRF de gestion (`Mgmt-vrf`, `management`). Les services d’administration (SSH, SNMP, Syslog, NTP, TACACS+) doivent alors être configurés **dans cette VRF**, sinon ils tentent de sortir par la table globale :

```cisco
ip ssh source-interface GigabitEthernet0/0
logging host 10.99.0.60 vrf Mgmt-vrf
ntp server vrf Mgmt-vrf 10.99.0.123
ip tacacs source-interface GigabitEthernet0/0 vrf Mgmt-vrf
```

## Exercices

**1.** `ping 10.20.0.40` échoue depuis le switch de cœur, alors que le serveur répond aux postes. Le VLAN 20 est dans la VRF SERVEURS. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Le `ping` sans précision utilise la **table globale**, où `10.20.0.0/24` n’existe pas. Il faut `ping vrf SERVEURS 10.20.0.40`.

</details>

**2.** Pourquoi les VRF sont-elles un bon moyen d’obliger tout le trafic entre utilisateurs et serveurs à passer par le pare-feu ?

<details><summary>Voir le corrigé</summary>

Parce que la VRF UTILISATEURS ne contient **aucune route** vers les serveurs, sauf une route (souvent par défaut) qui pointe vers le pare-feu ; et réciproquement. Aucune erreur d’ACL ne peut créer un raccourci : le seul chemin entre les deux zones passe physiquement par le pare-feu.

</details>
