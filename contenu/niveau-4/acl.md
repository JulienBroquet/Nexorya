---
titre: ACL
nom: Listes de contrôle d’accès
idee: Une ACL est une liste de règles « autoriser » ou « refuser » appliquée aux paquets qui traversent une interface ; c’est le premier outil pour filtrer le trafic entre réseaux.
osi: "3 et 4"
duree: [10, 22]
prerequis: [ipv4, tcp]
retenir:
  - Les règles sont lues **de haut en bas** ; la **première** qui correspond s’applique.
  - Toute ACL se termine par un **refus implicite** — ce qui n’est pas autorisé est bloqué.
  - "Une ACL **standard** filtre sur la source ; une ACL **étendue** sur la source, la destination, le protocole et les ports."
  - Une ACL s’applique **sur une interface et dans un sens** (in ou out).
---

## Le problème : les VLAN séparent, mais le routeur relie

On a séparé les invités, les employés et les serveurs dans des VLAN. Mais le switch de niveau 3 qui sert de passerelle **route** entre tous ces VLAN : sans filtrage, un invité peut joindre les serveurs. Il faut dire au routeur ce qui est autorisé.

> [!IMPORTANT] L’idée en une phrase
> Une ACL est une liste de règles que le routeur vérifie pour chaque paquet : il applique la première règle qui correspond, et refuse tout ce qui n’a pas été explicitement autorisé.

## Comment une ACL est lue

```text
ip access-list extended INVITES-ENTREE
 10 permit udp 10.30.0.0 0.0.0.255 host 10.99.0.53 eq domain     ← DNS interne autorisé
 20 deny   ip  10.30.0.0 0.0.0.255 10.0.0.0 0.255.255.255        ← tout le reste vers l’interne : refusé
 30 permit ip  10.30.0.0 0.0.0.255 any                           ← Internet autorisé
 (refus implicite de tout le reste)
```

Pour un paquet d’un invité vers un serveur `10.20.0.15` en HTTPS :

1. Règle 10 : est-ce du DNS vers `10.99.0.53` ? Non, on continue.
2. Règle 20 : source dans `10.30.0.0/24` et destination dans `10.0.0.0/8` ? **Oui** → **refusé**. On s’arrête là.

Pour un paquet d’un invité vers un site Internet : règles 10 et 20 ne correspondent pas, la règle 30 **autorise**.

> [!WARNING]
> L’**ordre** est déterminant. Si la règle 30 (« tout autoriser vers any ») était placée en premier, les règles suivantes ne seraient jamais lues : les invités pourraient joindre l’interne.

## Le masque générique

Les ACL Cisco utilisent un **masque générique** (*wildcard*), l’inverse d’un masque de sous-réseau : les bits à **0 doivent correspondre**, les bits à **1 sont libres**.

| Ce qu’on veut désigner | Écriture |
|---|---|
| Le réseau 10.30.0.0/24 | `10.30.0.0 0.0.0.255` |
| Le réseau 10.0.0.0/8 | `10.0.0.0 0.255.255.255` |
| Une seule machine | `host 10.99.0.53` (= `10.99.0.53 0.0.0.0`) |
| N’importe quelle adresse | `any` |

```topologie
titre: Une ACL étendue placée au plus près de la source
INV pc 0,0 "Invités" "VLAN 30"
UTI pc 0,1.4 "Utilisateurs" "VLAN 10"
R l3 1.6,0.7 "Switch de cœur" "ACL en entrée sur VLAN 30"
SRV serveur 3.4,0 "Serveurs internes"
NET nuage 3.4,1.4 "Internet"
INV -- R
UTI -- R
R -x- SRV "invités → serveurs : refusé"
R -- NET "invités → Internet : autorisé"
```

## Les mots à connaître

- **ACL** — *Access Control List*, liste de règles qui autorisent ou refusent des paquets.
- **Refus implicite** — Règle invisible, à la fin de chaque ACL, qui refuse tout ce qui n’a pas été autorisé.
- **ACL standard / étendue** — ACL qui filtre sur l’adresse source seulement / sur source, destination, protocole et ports.
- **Masque générique** — Masque où les bits à 1 indiquent les positions libres ; *wildcard mask*.

## Teste-toi

**Une ACL contient une seule ligne : `permit tcp any host 10.20.0.15 eq 443`. Un poste peut-il pinguer ce serveur à travers elle ?**

<details><summary>Voir le corrigé</summary>

**Non.** Le ping (ICMP) ne correspond pas à la seule règle, qui n’autorise que le TCP 443. Il tombe dans le **refus implicite**.

</details>

<!-- approfondir -->

## Où et dans quel sens appliquer ?

```cisco
interface Vlan30
 description Invités
 ip access-group INVITES-ENTREE in
```

- **in** : les paquets sont filtrés en **entrant** dans l’interface, depuis le VLAN invités, avant le routage.
- **out** : les paquets sont filtrés en **sortant** par l’interface, vers le VLAN.

Règle pratique :

- une ACL **étendue** se place **au plus près de la source** (on jette tôt le trafic indésirable) ;
- une ACL **standard**, qui ne voit que la source, se place **au plus près de la destination** (sinon, on bloquerait aussi l’accès à d’autres destinations).

## Le trafic retour

Une ACL **n’a pas de mémoire** : elle ne sait pas qu’un paquet est la réponse à une connexion autorisée. Si l’on filtre dans les deux sens, il faut autoriser aussi les réponses :

```cisco
ip access-list extended SERVEURS-VERS-INVITES
 permit tcp any 10.30.0.0 0.0.0.255 established     ! réponses TCP (drapeau ACK ou RST)
 permit udp host 10.99.0.53 eq domain 10.30.0.0 0.0.0.255
 deny ip any any log
```

`established` est une approximation (elle se contente de regarder les drapeaux TCP). Les pare-feu **à états** suivent réellement les connexions et autorisent automatiquement les réponses : c’est la principale différence avec une ACL. Voir [NGFW](ngfw.md).

## Modifier une ACL sans tout casser

```cisco
R1# show ip access-lists INVITES-ENTREE
Extended IP access list INVITES-ENTREE
    10 permit udp 10.30.0.0 0.0.0.255 host 10.99.0.53 eq domain (4512 matches)
    20 deny ip 10.30.0.0 0.0.0.255 10.0.0.0 0.255.255.255 (37 matches)
    30 permit ip 10.30.0.0 0.0.0.255 any (981223 matches)
!
R1(config)# ip access-list extended INVITES-ENTREE
R1(config-ext-nacl)# 15 permit tcp 10.30.0.0 0.0.0.255 host 10.40.0.20 eq 631    ! insérer l'impression
R1(config-ext-nacl)# no 15                                                       ! supprimer une ligne
```

- Les **compteurs** (`matches`) montrent quelles règles sont réellement utilisées.
- Les **numéros de séquence** permettent d’insérer une règle entre deux autres sans réécrire l’ACL.

> [!CAUTION]
> Appliquer une ACL vide ou incomplète sur une interface **coupe tout** le trafic (refus implicite). Prépare l’ACL complète, vérifie-la, puis applique-la ; en accès distant, programme un `reload in` de sécurité.

## Exercices

**1.** Écris une ACL étendue qui autorise le VLAN employés (`10.10.0.0/24`) à joindre l’imprimante `10.40.0.20` en IPP (TCP 631) et refuse tout autre accès au VLAN imprimantes (`10.40.0.0/24`), sans bloquer le reste.

<details><summary>Voir le corrigé</summary>

```cisco
ip access-list extended EMPLOYES-ENTREE
 10 permit tcp 10.10.0.0 0.0.0.255 host 10.40.0.20 eq 631
 20 deny   ip  10.10.0.0 0.0.0.255 10.40.0.0 0.0.0.255
 30 permit ip  10.10.0.0 0.0.0.255 any
interface Vlan10
 ip access-group EMPLOYES-ENTREE in
```

La règle 30 évite que le refus implicite bloque tout le reste du trafic des employés.

</details>

**2.** Le compteur de la règle 20 d’une ACL reste à 0 alors qu’on s’attend à ce qu’elle bloque des flux. Que soupçonner ?

<details><summary>Voir le corrigé</summary>

Une règle **placée avant** (10, par exemple) correspond déjà à ces flux et les autorise : la règle 20 n’est jamais atteinte. Ou bien l’ACL est appliquée sur la **mauvaise interface** ou dans le **mauvais sens**. Vérifier l’ordre et `show ip interface Vlan10 | include access list`.

</details>

**3.** Quel est le masque générique de `172.16.32.0/20` ?

<details><summary>Voir le corrigé</summary>

Masque /20 = 255.255.240.0 → masque générique = 255.255.255.255 − 255.255.240.0 = **0.0.15.255**. Écriture : `172.16.32.0 0.0.15.255`.

</details>
