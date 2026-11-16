---
titre: "Labo 6 — Chasse aux pannes"
actif: pratique
chapeau: Dix pannes classiques, telles qu’on les rencontre en entreprise. Pour chacune, un symptôme rapporté par un utilisateur. À toi de trouver la cause avec méthode.
---

> [!IMPORTANT] La méthode
> 1. **Délimiter** : qui est touché, depuis quand, pour quoi ?
> 2. **Remonter les couches** : lien physique → adresse → passerelle → routage → nom (DNS) → application.
> 3. **Une hypothèse à la fois**, vérifiée par une commande.
> 4. **Corriger**, puis vérifier que le symptôme a disparu **et** que rien d’autre n’est cassé.
> 5. **Noter** la cause et la correction.

**Comment faire** : à deux, l’un introduit une panne dans le réseau du [labo 4](labo-4-routage.md) ou du [labo 2](labo-2-vlan.md) sans rien dire, l’autre la cherche. Seul, lis le symptôme, écris ton hypothèse et les commandes que tu taperais avant d’ouvrir la solution. **Fiches utiles** : [Les commandes de base](../demarrer/commandes.md), [Diagnostic](../niveau-3/diagnostic.md).

## Les pannes

**1. « Mon PC n’a plus Internet. »** `ipconfig` affiche `169.254.31.7`.

<details><summary>Piste et solution</summary>

Pas de réponse DHCP. Vérifier le lien (voyant, `show interfaces status`), le VLAN du port, puis le relais (`ip helper-address`) et le serveur. **Cause posée** : port du PC placé dans un mauvais VLAN, où aucun DHCP ne répond.

</details>

**2. « Je joins les autres PC de mon service, mais rien au-delà. »**

<details><summary>Piste et solution</summary>

Le réseau local fonctionne, la sortie non : **passerelle**. `ipconfig` → passerelle absente ou fausse ; `ping` de la passerelle. **Cause posée** : option passerelle erronée dans la plage DHCP.

</details>

**3. « Nantes ne joint plus ni Lyon ni le siège depuis ce matin. »** Les postes de Nantes joignent bien leur passerelle.

<details><summary>Piste et solution</summary>

Le réseau local va bien ; c’est le **routage**. `show ip route` sur R-NANTES : aucune route **O**. `show ip ospf neighbor` : aucun voisin. `show ip ospf interface brief` : les interfaces sont en **zone 1**, alors que tout le réseau est en zone 0. **Cause posée** : instruction `network … area 1` saisie lors d’une modification de la veille. Les voisins OSPF doivent être dans la même zone (et avoir les mêmes temporisateurs, le même masque, la même authentification).

</details>

**4. « Internet marche avec les adresses IP, mais pas avec les noms. »**

<details><summary>Piste et solution</summary>

`ping 8.8.8.8` répond, `nslookup www.exemple.fr` échoue : **DNS**. Vérifier le serveur DNS distribué par DHCP et son accessibilité (une ACL qui bloque UDP 53 ?). **Cause posée** : ACL sans la ligne autorisant le DNS.

</details>

**5. « Le réseau est très lent, tous les voyants du switch clignotent en même temps. »**

<details><summary>Piste et solution</summary>

**Boucle** de niveau 2 : tempête de broadcast. `show spanning-tree` (spanning tree désactivé ?), `show interfaces` (compteurs de broadcast qui explosent). Débrancher le lien suspect. **Cause posée** : petit switch de bureau branché en boucle sur deux prises, avec STP désactivé sur les ports. Prévention : BPDU Guard.

</details>

**6. « L’imprimante est injoignable pour tout le monde. »** Elle est sur SW2, en VLAN 30.

<details><summary>Piste et solution</summary>

`show interfaces trunk` sur SW1 et SW2 : le VLAN 30 n’est plus dans la liste autorisée sur le trunk entre eux. **Cause posée** : `switchport trunk allowed vlan 10,20` au lieu de `add 30`.

</details>

**7. « Mon PC marche une minute, puis plus rien, puis ça revient. »** Un collègue vient de recevoir le même PC portable que lui.

<details><summary>Piste et solution</summary>

**Conflit d’adresse IP** : deux machines avec la même adresse fixe. `arp -a` montre l’adresse MAC associée changer ; le journal du switch peut signaler l’oscillation. **Cause posée** : adresse fixe dans la plage du DHCP.

</details>

**8. « Le SSH vers R-NANTES ne marche plus depuis le PC d’admin. »** Le ping fonctionne.

<details><summary>Piste et solution</summary>

Le réseau passe, l’accès est filtré : `show access-lists` et `show running-config | section line vty`. **Cause posée** : `access-class` qui référence une ACL dont le réseau d’administration a été mal saisi (`10.0.9.0` au lieu de `10.0.99.0`).

</details>

**9. « Un port du bureau 12 ne fonctionne plus du tout. »** Le voyant est éteint, le câble est bon.

<details><summary>Piste et solution</summary>

`show interfaces status` : le port est **err-disabled**. `show port-security interface` ou le journal indique la cause (violation de port-security, BPDU Guard). **Cause posée** : un utilisateur a branché un switch personnel. Retirer l’appareil, puis `shutdown` / `no shutdown`.

</details>

**10. « Les PC de Lyon ont Internet, ceux de Nantes non. »** Les deux sites joignent le siège.

<details><summary>Piste et solution</summary>

Le routage interne fonctionne ; la sortie dépend du **NAT** et de la route par défaut. `show ip nat translations` ne montre aucune traduction pour 10.2.x.x ; l’ACL du NAT ne couvre que `10.1.0.0`. **Cause posée** : `access-list 1 permit 10.1.0.0 0.0.255.255` au lieu de l’ensemble de 10.0.0.0/8.

</details>

## Ton bilan

Pour chaque panne, compare ta démarche à la méthode : as-tu commencé par délimiter ? As-tu testé une seule hypothèse à la fois ? Les pannes que tu as trouvées le plus vite sont celles où tu as **remonté les couches dans l’ordre**.
