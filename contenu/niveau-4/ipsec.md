---
titre: IPsec
nom: Sécurité au niveau IP
idee: IPsec chiffre et authentifie les paquets IP entre deux équipements ; il sert à relier des sites à travers Internet comme s’ils étaient sur un réseau privé.
osi: "3 (ESP = protocole IP 50 ; IKE = UDP 500 et 4500)"
duree: [10, 22]
prerequis: [pki]
retenir:
  - "**IKE** négocie et authentifie (UDP 500, 4500 avec NAT) ; **ESP** chiffre les paquets (protocole IP 50)."
  - "Deux phases — **IKE SA** (canal de contrôle), puis **IPsec SA** / Child SA (chiffrement du trafic)."
  - Les deux côtés doivent concorder — algorithmes, **sélecteurs de trafic** (réseaux protégés), identités, clés ou certificats.
  - "Symptôme classique — tunnel « UP » mais **compteurs de déchiffrement à zéro** → routage, sélecteurs ou pare-feu au retour."
---

## Le problème : relier deux sites à travers Internet

Une entreprise a un siège à Lyon et une agence à Nantes. Une liaison privée louée coûte cher ; Internet est partout et peu coûteux, mais rien n’y est confidentiel. Il faut que le trafic entre les deux sites soit **chiffré**, **authentifié** (venant bien de l’autre site) et **intact**.

> [!IMPORTANT] L’idée en une phrase
> Les deux routeurs se mettent d’accord sur des clés (IKE), puis chiffrent chaque paquet échangé entre les deux réseaux (ESP) : Internet ne voit passer que des données illisibles entre deux adresses publiques.

## Comment ça marche

```topologie
titre: Un tunnel IPsec entre deux sites
LA switch 0,0 "LAN siège" "10.10.0.0/16"
RA routeur 1.3,0 "Routeur siège" "198.51.100.7"
NET nuage 2.6,0 "Internet"
RB routeur 3.9,0 "Routeur agence" "203.0.113.20"
LB switch 5.2,0 "LAN agence" "10.50.0.0/24"
LA -- RA
RA -- NET
NET -- RB
RB -- LB
RA .. RB "tunnel chiffré"
```

1. **Phase 1 (IKE)** : les deux routeurs s’authentifient (clé partagée ou certificats) et établissent un canal de contrôle chiffré.
2. **Phase 2** : dans ce canal, ils négocient le chiffrement du trafic et les **réseaux à protéger** : « de 10.10.0.0/16 vers 10.50.0.0/24 ».
3. **Transfert** : chaque paquet entre ces réseaux est chiffré dans **ESP** et envoyé à l’adresse publique de l’autre routeur, qui le déchiffre.
4. Les clés sont **renouvelées** régulièrement.

## Les mots à connaître

- **IPsec** — Ensemble de protocoles qui sécurisent les paquets IP : chiffrement, intégrité, authentification.
- **IKE** — *Internet Key Exchange*, protocole qui authentifie les deux extrémités et négocie les clés (IKEv2 aujourd’hui).
- **ESP** — *Encapsulating Security Payload*, en-tête IPsec qui chiffre et protège les paquets.
- **SA** — *Security Association*, ensemble des paramètres de sécurité négociés pour un sens de communication.
- **Sélecteurs de trafic** — Réseaux source et destination que le tunnel doit protéger.

## Teste-toi

**Le tunnel IPsec entre le siège et l’agence est établi, mais aucun ping ne passe. Que vérifier en priorité ?**

<details><summary>Voir le corrigé</summary>

Que le trafic est bien **dirigé dans le tunnel** (route ou sélecteurs de trafic qui correspondent aux réseaux testés, des deux côtés), qu’aucun **NAT** ne modifie les adresses avant le chiffrement, et que les **pare-feu** des deux LAN autorisent le trafic. Un tunnel établi prouve seulement que la négociation a réussi.

</details>

<!-- approfondir -->

## Mode tunnel et mode transport

| Mode | Ce qui est protégé | Usage |
|---|---|---|
| **Tunnel** | tout le paquet d’origine, encapsulé dans un nouvel en-tête IP | VPN site à site, accès distant |
| **Transport** | seulement le contenu ; l’en-tête IP d’origine reste | protection entre deux hôtes, GRE sur IPsec |

L’encapsulation ajoute 50 à 70 octets : penser à la **MTU** et au **MSS** (`ip tcp adjust-mss`). Voir [MTU](../niveau-1/mtu.md).

## Configuration IKEv2 avec interface tunnel (Cisco IOS-XE)

```cisco
crypto ikev2 proposal PROP-AES
 encryption aes-gcm-256
 prf sha384
 group 19 20
crypto ikev2 policy POL
 proposal PROP-AES
crypto ikev2 keyring CLES
 peer AGENCE
  address 203.0.113.20
  pre-shared-key Une-Cle-Tres-Longue-Ou-Des-Certificats
crypto ikev2 profile PROF-AGENCE
 match identity remote address 203.0.113.20 255.255.255.255
 authentication remote pre-share
 authentication local pre-share
 keyring local CLES
!
crypto ipsec transform-set TS esp-gcm 256
 mode tunnel
crypto ipsec profile IPSEC-AGENCE
 set transform-set TS
 set ikev2-profile PROF-AGENCE
!
interface Tunnel10
 ip address 172.31.0.1 255.255.255.252
 ip mtu 1400
 ip tcp adjust-mss 1360
 tunnel source GigabitEthernet0/0/0
 tunnel destination 203.0.113.20
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile IPSEC-AGENCE
!
ip route 10.50.0.0 255.255.255.0 Tunnel10
```

Avec une **interface tunnel** (VTI), le choix du trafic chiffré se fait par le **routage** (route statique ou protocole de routage dans le tunnel), ce qui est plus simple à exploiter que les anciennes *crypto maps* fondées sur des ACL.

## Vérifier

```cisco
R1# show crypto ikev2 sa
 Tunnel-id Local                 Remote                fvrf/ivrf            Status
 1         198.51.100.7/500      203.0.113.20/500      none/none            READY
R1# show crypto ipsec sa interface Tunnel10 | include pkts|spi
    #pkts encaps: 18342, #pkts encrypt: 18342, #pkts digest: 18342
    #pkts decaps: 0, #pkts decrypt: 0, #pkts verify: 0
```

Lecture : on **chiffre** et envoie (encaps 18 342), mais on ne **reçoit** rien (decaps 0). Le problème est **de l’autre côté** ou **au retour** : route de l’agence vers le siège absente dans le tunnel, sélecteurs incohérents, ESP filtré par un équipement intermédiaire, ou NAT qui empêche ESP (il faut alors NAT-T sur UDP 4500).

## Pannes de négociation fréquentes

| Message ou symptôme | Cause |
|---|---|
| Aucune proposition acceptable | algorithmes différents des deux côtés |
| Échec d’authentification | clé partagée différente, identité inattendue, certificat non approuvé |
| Phase 1 OK, phase 2 refusée (`TS_UNACCEPTABLE`) | sélecteurs de trafic (réseaux) différents |
| Tunnel qui tombe toutes les heures | durées de vie incohérentes, renégociation qui échoue |
| Rien ne se négocie | UDP 500/4500 filtré, mauvaise adresse de pair |

## Exercices

**1.** `show crypto ipsec sa` montre `#pkts decaps: 25000` et `#pkts encaps: 0` sur le routeur du siège. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

Le siège **reçoit et déchiffre** le trafic de l’agence, mais n’envoie **rien** dans le tunnel : sa **route vers le LAN de l’agence** ne passe pas par le tunnel (ou ses sélecteurs ne correspondent pas). Les réponses partent ailleurs (souvent vers Internet). Vérifier `show ip route 10.50.0.0`.

</details>

**2.** L’agence est derrière une box qui fait du NAT. La phase 1 réussit, mais aucun paquet n’est déchiffré au siège. Quel mécanisme doit être actif, et sur quel port ?

<details><summary>Voir le corrigé</summary>

**NAT-T** (*NAT Traversal*) : ESP n’ayant pas de ports, la box ne peut pas le traduire correctement. IKE détecte le NAT et encapsule ESP dans **UDP 4500**. Il faut que l’UDP 4500 soit autorisé des deux côtés (et que NAT-T ne soit pas désactivé).

</details>
