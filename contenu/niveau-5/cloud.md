---
titre: Réseau cloud
nom: Le réseau dans le cloud public
idee: Dans le cloud public, on retrouve les mêmes concepts — réseaux privés, sous-réseaux, routage, filtrage, VPN — mais on les crée par API, et le fournisseur gère le matériel.
osi: "3 à 7"
duree: [9, 18]
prerequis: [subnet, vpn, acl]
retenir:
  - "**VPC / VNet** = ton réseau privé dans le cloud ; découpé en **sous-réseaux** publics et privés."
  - "Filtrage par **groupes de sécurité** (au niveau des instances) et listes de contrôle (au niveau des sous-réseaux)."
  - "Raccordement à l’entreprise — **VPN IPsec** ou **lien dédié** (Direct Connect, ExpressRoute, Interconnect)."
  - Prévoir les plages d’adresses **sans chevauchement** avec le réseau de l’entreprise.
---

## Le problème : la même chose, ailleurs

L’entreprise déplace une partie de ses applications vers un cloud public. Il n’y a plus de switches ni de routeurs à brancher, mais il faut toujours : des réseaux isolés, des adresses, du routage, du filtrage, et un lien sécurisé avec les sites.

> [!IMPORTANT] L’idée en une phrase
> Le réseau cloud reprend les concepts que tu connais, mais **virtualisés** : on crée réseaux, routes et filtres par une console ou une API, et ils existent en quelques secondes.

## Correspondance des notions

| Sur site | Dans le cloud (noms AWS / Azure) |
|---|---|
| réseau privé de l’entreprise | **VPC** / **VNet** |
| VLAN / sous-réseau | **subnet** |
| table de routage du routeur | **route table** |
| pare-feu devant un serveur | **security group** / **NSG** |
| ACL sur une interface | **network ACL** |
| accès Internet | **Internet gateway** |
| NAT pour les serveurs privés | **NAT gateway** |
| VPN site à site | **VPN gateway** |
| liaison louée | **Direct Connect** / **ExpressRoute** |

## Une architecture typique

```topologie
titre: Un VPC raccordé à l’entreprise
zone "VPC 10.200.0.0/16" 1.2,1.4 5.3,2.6
INT nuage 2,0 "Internet"
LB serveur 2,1.4 "Répartiteur" "sous-réseau public"
APP vm 3.7,1.4 "Application" "sous-réseau privé"
DB vm 5.3,1.4 "Base" "sous-réseau privé"
GW routeur 3.7,2.6 "Passerelle VPN"
SIE l3 0,2.6 "Siège" "10.0.0.0/12"
INT -- LB
LB -- APP
APP -- DB
GW -- APP
SIE ++ GW "IPsec"
```

- Le **répartiteur** est le seul exposé à Internet (sous-réseau public).
- L’application et la base sont dans des **sous-réseaux privés**, sans adresse publique.
- Le siège rejoint le VPC par un **tunnel IPsec** (ou un lien dédié).

## Les mots à connaître

- **VPC** — *Virtual Private Cloud*, réseau privé isolé chez un fournisseur cloud (VNet chez Azure).
- **Groupe de sécurité** — Pare-feu à états appliqué aux instances, défini par des règles d’autorisation.
- **Sous-réseau public** — Sous-réseau dont la route par défaut mène à une passerelle Internet.
- **Sous-réseau privé** — Sous-réseau sans accès entrant depuis Internet.
- **Direct Connect / ExpressRoute** — Liaison privée dédiée entre l’entreprise et le fournisseur cloud.

## Teste-toi

**L’entreprise utilise 10.0.0.0/8 partout sur ses sites. Quel problème si le VPC est créé en 10.0.0.0/16 ?**

<details><summary>Voir le corrigé</summary>

Les plages **se chevauchent** : une fois le VPN en place, une destination 10.0.x.x pourrait être sur site ou dans le cloud, et le routage devient ambigu. Il faut réserver au cloud une plage **unique** dans le plan d’adressage de l’entreprise (et, si 10.0.0.0/8 est entièrement utilisé, revoir le plan).

</details>

<!-- approfondir -->

## Groupes de sécurité : penser en rôles

Les groupes de sécurité peuvent se référencer entre eux : « la base accepte le port 5432 **depuis le groupe Application** », plutôt que depuis une liste d’adresses. Quand des instances apparaissent ou disparaissent, les règles restent justes.

```hcl
# Terraform (AWS) : la base n'accepte que l'application
resource "aws_security_group_rule" "db_depuis_app" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.base.id
  source_security_group_id = aws_security_group.application.id
}
```

## Ce qui change vraiment

- **Pas de broadcast** ni de multicast en général : ARP est simulé par le fournisseur, VRRP et les protocoles qui en dépendent ne fonctionnent pas comme sur site. La haute disponibilité passe par plusieurs **zones de disponibilité** et des répartiteurs gérés.
- **Le coût du trafic** : le trafic sortant du cloud (vers Internet ou l’entreprise) est facturé, parfois aussi entre zones. Les choix d’architecture ont un impact financier.
- **Tout est API** : l’infrastructure se décrit en code (Terraform, CloudFormation, Bicep) et passe par Git, comme l’[automatisation](automatisation.md) du réseau.
- **Responsabilité partagée** : le fournisseur sécurise le matériel et la plateforme ; la configuration (groupes ouverts, stockage public) reste **ta** responsabilité.

## Raccorder plusieurs VPC

Avec de nombreux VPC (un par application ou par environnement), les raccorder deux à deux devient ingérable. On utilise un **hub** : *Transit Gateway* (AWS), *Virtual WAN* ou hub VNet (Azure). Les VPC et les sites s’y raccordent une seule fois, et des tables de routage séparées gardent les environnements isolés — le même principe que les [VRF](vrf.md).

## Exercice

**Un serveur dans un sous-réseau privé n’arrive pas à télécharger ses mises à jour sur Internet. Le groupe de sécurité autorise tout en sortie. Que manque-t-il ?**

<details><summary>Voir le corrigé</summary>

Un sous-réseau privé n’a pas de route vers la passerelle Internet, et le serveur n’a pas d’adresse publique. Il faut une **NAT gateway** (placée dans un sous-réseau public) et une route par défaut `0.0.0.0/0 → NAT gateway` dans la table de routage du sous-réseau privé. Le serveur pourra sortir, sans être joignable depuis Internet.

</details>
