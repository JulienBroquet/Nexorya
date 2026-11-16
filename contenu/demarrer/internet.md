---
titre: Ma box et Internet
nom: Le voyage d’une page Web, de bout en bout
idee: Pour afficher une page, ton ordinateur obtient une adresse, traduit le nom du site, envoie la demande à sa box, qui la fait suivre de réseau en réseau jusqu’au serveur.
duree: [10]
retenir:
  - Au démarrage, l’appareil reçoit de la box (DHCP) son **adresse IP**, sa **passerelle** et son **serveur DNS**.
  - Le **DNS** traduit le nom du site ; la **passerelle** fait sortir la demande vers Internet.
  - La box **traduit les adresses** (NAT) — tous les appareils de la maison partagent une seule adresse IP publique.
---

## Ce qui se passe en une seconde

Tu ouvres ton navigateur et tu tapes `www.exemple.fr`. Moins d’une seconde plus tard, la page s’affiche. Entre-temps, une dizaine d’échanges ont eu lieu. Les voici, dans l’ordre, en reprenant tout ce que tu as vu dans les fiches précédentes.

## Étape 1 — Obtenir une adresse

Quand ton ordinateur se connecte au réseau de la maison, il n’a pas encore d’adresse IP. Il demande à la box, qui joue le rôle de serveur **DHCP** :

```sequence
titre: L’ordinateur reçoit sa configuration réseau
Ordinateur | Box
Ordinateur -> Box : « Je viens d’arriver, quelqu’un peut me donner une adresse ? »
Box --> Ordinateur : « Prends 192.168.1.20 »
Ordinateur -> Box : « D’accord, je la prends »
Box --> Ordinateur : « Confirmé. Passerelle 192.168.1.1, DNS 192.168.1.1 »
```

Il reçoit trois informations essentielles : **son adresse IP**, **l’adresse de la passerelle** (la box, pour sortir du réseau) et **l’adresse du serveur DNS** (pour traduire les noms).

## Étape 2 — Traduire le nom

Le navigateur demande au DNS l’adresse IP de `www.exemple.fr`. La box transmet la question au DNS de ton fournisseur d’accès, qui répond par exemple `203.0.113.10`.

## Étape 3 — Sortir du réseau local

L’ordinateur compare l’adresse `203.0.113.10` avec la sienne : elle n’est pas dans son réseau `192.168.1.x`. Il confie donc le paquet à sa **passerelle**, la box.

## Étape 4 — La box traduit l’adresse

Les adresses `192.168.x.x` sont des **adresses privées** : elles peuvent exister dans des millions de maisons en même temps, et ne sont donc pas utilisables sur Internet. La box remplace l’adresse privée de l’expéditeur par **son adresse publique**, unique au monde, attribuée par le fournisseur d’accès. Elle note la correspondance pour savoir à qui rendre la réponse. Cette traduction s’appelle le **NAT**.

```topologie
titre: Une seule adresse publique pour toute la maison
PC pc 0,0 "Ordinateur" "192.168.1.20"
Tel portable 0,1 "Téléphone" "192.168.1.21"
Box routeur 2,0 "Box" "publique 198.51.100.7"
FAI nuage 3,0 "Fournisseur d’accès"
Web serveur 5,0 "Serveur Web" "203.0.113.10"
Inter nuage 4,1 "Autres réseaux"
PC -- Box
Tel ~~ Box "Wi-Fi"
Box -- FAI "fibre"
FAI -- Inter
Inter -- Web
FAI -- Web
```

## Étape 5 — De réseau en réseau

Le paquet traverse le réseau de ton fournisseur d’accès, puis éventuellement ceux d’autres opérateurs. À chaque étape, un **routeur** lit l’adresse IP de destination et l’envoie vers le routeur suivant le plus proche de la destination. Il y a souvent entre 8 et 20 routeurs sur le chemin.

## Étape 6 — Le serveur répond

Le serveur Web reçoit la demande sur son **port 443** (HTTPS), prépare la page et la renvoie à l’adresse publique de ta box. La box consulte sa table de traduction, retrouve que la demande venait de `192.168.1.20`, et lui remet la réponse. Le navigateur affiche la page.

> [!IMPORTANT] Les questions à te poser quand « Internet ne marche pas »
> 1. Mon appareil a-t-il une adresse IP ? (étape 1)
> 2. Le nom du site est-il traduit ? (étape 2)
> 3. Est-ce que j’atteins ma box ? (étape 3)
> 4. Est-ce que la box atteint Internet ? (étapes 4 et 5)
> 5. Le site lui-même répond-il ? (étape 6)
>
> La fiche [Les commandes de base](commandes.md) te montre comment répondre à chacune de ces questions.

## Les mots à connaître

- **Adresse privée** — Adresse IP réservée aux réseaux internes (192.168.x.x, 10.x.x.x, 172.16 à 31.x.x), inutilisable directement sur Internet.
- **Adresse publique** — Adresse IP unique au monde, attribuée par un fournisseur d’accès, joignable sur Internet.
- **NAT** — *Network Address Translation*, traduction des adresses privées en adresse publique par la box ou le routeur.
- **Fournisseur d’accès** — Opérateur qui relie ton réseau à Internet (FAI, ou *ISP* en anglais).

## Teste-toi

**1.** Chez toi, ton ordinateur a l’adresse `192.168.1.20`. Un site Web qui affiche « ton adresse IP » indique `198.51.100.7`. Pourquoi ces deux adresses sont-elles différentes ?

<details><summary>Voir la réponse</summary>

`192.168.1.20` est l’adresse **privée** de ton ordinateur dans ton réseau local. `198.51.100.7` est l’adresse **publique** de ta box : c’est elle que voit le site, parce que la box a traduit l’adresse au passage (NAT).

</details>

**2.** Ton ordinateur obtient l’adresse `169.254.12.34` au lieu de `192.168.1.x`. Quelle étape a échoué ?

<details><summary>Voir la réponse</summary>

**L’étape 1.** Une adresse en `169.254.x.x` est une adresse que l’ordinateur s’attribue lui-même quand **personne ne lui a répondu en DHCP**. Il faut vérifier la connexion à la box (câble, Wi-Fi) et le service DHCP de la box.

</details>
