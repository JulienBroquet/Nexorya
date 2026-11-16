---
titre: Routage statique
nom: Routes configurées à la main
idee: Une route statique est une règle écrite par l’administrateur — « pour ce réseau, passe par ce voisin » ; simple et prévisible, mais elle ne s’adapte pas toute seule aux pannes.
osi: "3"
duree: [7, 15]
prerequis: [passerelle]
retenir:
  - "`ip route <réseau> <masque> <prochain saut>` — une ligne par réseau à joindre."
  - Idéal pour les **petits réseaux**, les **sites en étoile** et la **route par défaut** vers Internet.
  - Une route statique **ne détecte pas** une panne au-delà du lien direct — on la couple à IP SLA, ou on passe au routage dynamique.
  - Les routes doivent exister **dans les deux sens** — penser au chemin retour.
---

## Le problème : apprendre au routeur où sont les réseaux

Un routeur connaît automatiquement les réseaux **directement branchés** sur ses interfaces. Pour tous les autres, il faut lui dire par où passer. La façon la plus simple : l’écrire à la main.

> [!IMPORTANT] L’idée en une phrase
> Une route statique est une instruction fixe : « pour joindre tel réseau, envoie les paquets à tel voisin ». Le routeur l’applique sans réfléchir, même si le chemin ne fonctionne plus.

## Exemple : une agence reliée au siège

```topologie
titre: Une agence reliée au siège
LANA switch 0,0 "LAN agence" "192.168.20.0/24"
RA routeur 1.5,0 "Routeur agence"
RS routeur 3.5,0 "Routeur siège"
LANS switch 5,0 "LAN siège" "10.0.0.0/16"
Net nuage 3.5,1 "Internet"
LANA -- RA ".1"
RA -- RS "lien 172.16.0.0/30 (.1 et .2)"
RS -- LANS
RS -- Net
```

Sur le **routeur de l’agence**, une seule route suffit : tout ce qui n’est pas local part vers le siège.

```cisco
ip route 0.0.0.0 0.0.0.0 172.16.0.2
```

Sur le **routeur du siège**, il faut indiquer comment revenir vers l’agence :

```cisco
ip route 192.168.20.0 255.255.255.0 172.16.0.1
```

> [!WARNING]
> Oublier la route **retour** est l’erreur la plus fréquente : le paquet arrive au serveur du siège, mais la réponse ne sait pas revenir vers l’agence. Le ping échoue alors que la route « aller » est parfaite. Pense toujours aux deux sens.

## Avantages et limites

| Avantages | Limites |
|---|---|
| Simple à comprendre et à vérifier | Fastidieux au-delà de quelques réseaux |
| Aucune consommation de processeur ni de bande passante | Ne s’adapte pas aux pannes (sauf liens directs) |
| Totalement prévisible | Chaque nouveau réseau oblige à modifier plusieurs routeurs |
| Aucun échange : rien à usurper | Risque d’erreur humaine |

On l’utilise donc pour la **route par défaut** vers Internet, les **petites agences** reliées en étoile, et comme **secours** d’un protocole dynamique.

## Les mots à connaître

- **Route statique** — Route configurée manuellement par l’administrateur.
- **Prochain saut** — Adresse IP du routeur voisin à qui confier le paquet ; *next hop*.
- **Route par défaut** — Route 0.0.0.0/0 qui couvre toutes les destinations sans route plus précise.
- **Route retour** — Route nécessaire pour que les réponses reviennent vers l’expéditeur.

## Teste-toi

**Depuis l’agence, un ping vers un serveur du siège échoue. Le routeur de l’agence a bien sa route par défaut vers le siège. Quelle est la première chose à vérifier côté siège ?**

<details><summary>Voir le corrigé</summary>

La **route retour** : le routeur du siège (et, s’il y en a un, le pare-feu ou le switch de cœur) doit savoir que `192.168.20.0/24` se trouve derrière le routeur de l’agence. Sans elle, les réponses partent vers la route par défaut du siège (Internet) et se perdent.

</details>

<!-- approfondir -->

## Les formes de la commande (Cisco IOS)

```cisco
! Prochain saut (recommandé sur Ethernet)
ip route 10.30.0.0 255.255.0.0 10.255.0.6
! Interface de sortie seule (à réserver aux liens point à point : tunnel, série)
ip route 10.30.0.0 255.255.0.0 Tunnel0
! Interface + prochain saut (précis, évite les ambiguïtés)
ip route 10.30.0.0 255.255.0.0 GigabitEthernet0/0/2 10.255.0.6
! Route flottante (secours) : distance administrative 200
ip route 0.0.0.0 0.0.0.0 192.0.2.1 200
! Route vers nulle part : jeter le trafic (anti-boucle pour un agrégat annoncé)
ip route 10.0.0.0 255.0.0.0 Null0
! IPv6
ipv6 route ::/0 2001:db8:ffff::1
```

> [!CAUTION]
> Une route statique vers une **interface Ethernet seule** (sans prochain saut) fait croire au routeur que toutes les destinations sont directement connectées : il envoie une requête ARP pour **chaque** adresse de destination, et dépend du proxy ARP du voisin. Sur Ethernet, indique toujours le prochain saut.

## Quand une route statique disparaît-elle ?

Une route statique reste dans la table tant que **son prochain saut est joignable selon la table de routage** — en pratique, tant que l’interface vers ce voisin est active. Si la panne se trouve **au-delà** (le routeur voisin est en vie mais a perdu son lien vers Internet), la route reste, et le trafic part dans un trou noir.

La solution : associer la route à une **sonde** qui vérifie le chemin de bout en bout.

```cisco
ip sla 10
 icmp-echo 198.51.100.1 source-interface GigabitEthernet0/0/0
 frequency 5
ip sla schedule 10 life forever start-time now
track 10 ip sla 10 reachability
!
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 10      ! lien principal
ip route 0.0.0.0 0.0.0.0 192.0.2.1 200             ! secours flottant
```

Si la sonde échoue, la route principale est retirée et la route de secours apparaît. Voir [IP SLA](ipsla.md).

## Résumer pour simplifier

Plutôt que dix routes vers dix réseaux d’un site (`10.30.0.0/24`, `10.30.1.0/24`…), on écrit **une seule route** vers le bloc qui les contient (`10.30.0.0/16`). C’est possible uniquement si le **plan d’adressage** a été pensé par site : un argument de plus pour un bon [découpage en sous-réseaux](subnet.md).

## Vérification et dépannage

```cisco
R1# show ip route static
S*    0.0.0.0/0 [1/0] via 203.0.113.1
S     192.168.20.0/24 [1/0] via 172.16.0.1
R1# show ip route 192.168.20.5
R1# ping 192.168.20.5 source GigabitEthernet0/0/1
R1# traceroute 192.168.20.5
```

Un `ping` **depuis le routeur** part par défaut avec l’adresse de l’interface de sortie. Pour tester le chemin comme le ferait un poste du LAN, utilise `source` avec l’interface LAN : la réponse devra alors trouver la route retour vers ce LAN.

## Exercices

**1.** Le siège a les réseaux `10.0.0.0/24` à `10.0.15.0/24`. Quelle route unique l’agence peut-elle utiliser pour tous les joindre ?

<details><summary>Voir le corrigé</summary>

16 réseaux /24 consécutifs à partir de `10.0.0.0` = un bloc de 16 × 256 = 4 096 adresses = **`10.0.0.0/20`** (masque 255.255.240.0).

</details>

**2.** Un routeur d’agence a deux routes par défaut : `via 203.0.113.1` (fibre) et `via 192.0.2.1 200` (4G). La box fibre est allumée mais n’a plus accès à Internet. Que se passe-t-il, et comment corriger ?

<details><summary>Voir le corrigé</summary>

L’interface vers la box reste active : la route principale **reste installée** et le trafic part vers une box qui ne mène nulle part. La 4G n’est jamais utilisée. Corriger avec une sonde **IP SLA** vers une adresse sur Internet, et `track` sur la route principale.

</details>

**3.** Un ping depuis le routeur de l’agence vers un serveur du siège fonctionne, mais un ping depuis un PC de l’agence échoue. Quelle hypothèse ?

<details><summary>Voir le corrigé</summary>

Le ping du routeur part avec l’adresse du **lien** (`172.16.0.1`), que le siège sait joindre (réseau connecté). Le PC utilise une adresse du **LAN de l’agence** (`192.168.20.x`), pour laquelle le siège n’a **pas de route retour**. Vérifier avec `ping … source` depuis l’interface LAN de l’agence, puis ajouter la route au siège.

</details>
