---
titre: VPN
nom: Réseaux privés virtuels
idee: Un VPN crée un tunnel chiffré à travers un réseau non sûr ; il relie des sites entre eux, ou un salarié en télétravail au réseau de l’entreprise.
osi: "2 à 7 selon la technologie"
duree: [8, 16]
prerequis: [ipsec]
retenir:
  - "Deux usages — **site à site** (entre routeurs) et **accès distant** (un poste vers l’entreprise)."
  - "Technologies — **IPsec/IKEv2**, **VPN TLS/SSL** (AnyConnect, GlobalProtect…), **WireGuard**."
  - "**Tunnel complet** (tout passe par l’entreprise) ou **tunnel partagé** (seul le trafic interne passe par le VPN)."
  - Le VPN d’accès distant exige une **MFA** et devrait vérifier l’état du poste.
---

## Le problème

Un salarié travaille de chez lui et doit accéder au serveur de fichiers, à l’ERP, à l’intranet. Ces services ne sont pas publiés sur Internet, et ne doivent pas l’être. Il faut que son ordinateur se retrouve « virtuellement » dans le réseau de l’entreprise.

> [!IMPORTANT] L’idée en une phrase
> Le VPN crée un tunnel chiffré entre l’ordinateur (ou le site) et la passerelle de l’entreprise : le trafic interne voyage dans ce tunnel comme s’il était sur un réseau privé.

## Les deux usages

| | Site à site | Accès distant |
|---|---|---|
| Extrémités | deux routeurs ou pare-feu | un client logiciel sur le poste et une passerelle VPN |
| Toujours actif ? | oui | à la demande (ou permanent sur les postes gérés) |
| Authentification | clés ou certificats des équipements | utilisateur (MFA) + poste (certificat) |
| Technologie courante | IPsec IKEv2 | VPN TLS, IKEv2, WireGuard |

## Tunnel complet ou partagé ?

- **Tunnel complet** (*full tunnel*) : tout le trafic du poste, y compris Internet, passe par l’entreprise. Contrôle maximal (filtrage Web, journaux), mais charge et latence sur la passerelle.
- **Tunnel partagé** (*split tunnel*) : seul le trafic vers les réseaux internes passe par le VPN ; Internet (et souvent les services cloud comme la visioconférence) sort directement. Meilleures performances, moins de contrôle.

## Les mots à connaître

- **VPN** — *Virtual Private Network*, tunnel chiffré qui relie un poste ou un site à un réseau privé.
- **Passerelle VPN** — Équipement qui termine les tunnels du côté de l’entreprise ; *VPN concentrator*.
- **Tunnel partagé** — Configuration où seul le trafic vers l’entreprise passe dans le VPN ; *split tunneling*.

## Teste-toi

**Un télétravailleur connecté au VPN en tunnel partagé ouvre `intranet.exemple.fr` et obtient « site introuvable ». Les adresses IP internes répondent au ping. Quelle hypothèse ?**

<details><summary>Voir le corrigé</summary>

Le poste utilise toujours le **DNS de sa box** au lieu du DNS interne, qui seul connaît `intranet.exemple.fr`. Il faut que le VPN pousse les **serveurs DNS internes** et le **domaine** à leur envoyer.

</details>

<!-- approfondir -->

## VPN d’accès distant : ce qu’on configure

| Élément | Exemple |
|---|---|
| Authentification utilisateur | SAML vers le fournisseur d’identité, avec MFA (FIDO2 de préférence) |
| Authentification du poste | certificat machine délivré par la PKI |
| Vérification de conformité | antivirus actif, chiffrement du disque, système à jour |
| Pool d’adresses | `10.200.0.0/20`, routé vers la passerelle VPN |
| Routes poussées (tunnel partagé) | `10.0.0.0/8`, `172.16.0.0/12` |
| DNS poussé | `10.99.0.53`, `10.99.1.53`, domaine `exemple.fr` |
| Filtrage | règles par groupe d’utilisateurs (comptabilité → ERP seulement) |

## WireGuard en bref

WireGuard est un VPN moderne et minimaliste (UDP, port configurable) : configuration très courte, cryptographie fixe et récente, excellentes performances.

```text
[Interface]
PrivateKey = <clé privée du poste>
Address = 10.200.0.15/32
DNS = 10.99.0.53

[Peer]
PublicKey = <clé publique de la passerelle>
Endpoint = vpn.exemple.fr:51820
AllowedIPs = 10.0.0.0/8          # tunnel partagé : seuls les réseaux internes
PersistentKeepalive = 25
```

`AllowedIPs` joue deux rôles : les destinations envoyées dans le tunnel, et les sources acceptées depuis ce pair.

## Dépannage côté utilisateur

| Symptôme | Pistes |
|---|---|
| Connexion impossible | port de la passerelle filtré sur le réseau de l’utilisateur (hôtel, 4G), certificat, MFA |
| Connecté, mais rien d’interne | routes non poussées, pool d’adresses non routé dans l’entreprise, règles de filtrage |
| Noms internes non résolus | DNS non poussé ou ignoré par le système |
| Lenteurs, coupures de grosses pages | MTU / MSS dans le tunnel |
| Conflit d’adresses | le réseau de la maison utilise la même plage que l’entreprise (`192.168.1.0/24`) |

## Vers le ZTNA

Un VPN classique donne, une fois connecté, un accès **réseau** souvent large. Les approches **ZTNA** (*Zero Trust Network Access*) donnent plutôt accès à des **applications précises**, après vérification de l’utilisateur et du poste à chaque connexion. Voir [Zero Trust](zero-trust.md).

## Exercice

**La maison d’un salarié utilise `10.10.0.0/24`, qui est aussi le réseau des postes du siège. Connecté au VPN, il n’atteint pas un serveur du siège en `10.10.0.40`. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

Pour son poste, `10.10.0.0/24` est **directement connecté** (réseau de la maison) : la route locale est plus précise ou prioritaire, et le trafic part vers la box au lieu du tunnel. Solutions : éviter de placer des serveurs dans des plages très courantes, pousser des routes plus précises (/32 pour les serveurs critiques), ou utiliser une passerelle qui traduit ces adresses.

</details>
