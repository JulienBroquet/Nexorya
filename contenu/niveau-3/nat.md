---
titre: NAT
nom: Network Address Translation
idee: Le NAT remplace les adresses privées d’un réseau par une adresse publique à la sortie vers Internet, et fait le chemin inverse pour les réponses ; toute une entreprise peut ainsi partager une seule adresse publique.
osi: "3 et 4"
duree: [8, 18]
prerequis: [ipv4]
retenir:
  - Le **PAT** (NAT avec ports) fait partager **une** adresse publique à des milliers de machines, en distinguant les connexions par le **port**.
  - Le routeur garde une **table de traduction** — les réponses retrouvent ainsi le bon poste.
  - "Depuis Internet, on ne peut pas joindre un poste interne **sans règle explicite** (NAT statique, redirection de port)."
  - Le NAT complique les protocoles qui transportent des adresses dans leurs données (SIP, FTP actif).
---

## Le problème : pas assez d’adresses publiques

Une entreprise de 800 postes dispose d’une seule adresse IPv4 publique, attribuée par son opérateur. Ses postes utilisent des adresses **privées** (`10.x.x.x`), qui ne sont pas acheminées sur Internet. Comment peuvent-ils tous naviguer en même temps ?

> [!IMPORTANT] L’idée en une phrase
> En sortant vers Internet, le routeur remplace l’adresse privée de chaque paquet par son adresse publique, note la correspondance, et fait l’opération inverse sur les réponses.

## Comment ça marche (PAT)

```sequence
titre: Deux postes partagent une seule adresse publique
PC A (10.10.0.57) | PC B (10.10.0.58) | Routeur NAT (198.51.100.7) | Serveur Web
PC A (10.10.0.57) -> Routeur NAT (198.51.100.7) : de 10.10.0.57:51544 vers 203.0.113.10:443
note Routeur NAT (198.51.100.7) : traduit : 10.10.0.57:51544 ↔ 198.51.100.7:40001
Routeur NAT (198.51.100.7) -> Serveur Web : de 198.51.100.7:40001 vers 203.0.113.10:443
PC B (10.10.0.58) -> Routeur NAT (198.51.100.7) : de 10.10.0.58:51544 vers 203.0.113.10:443
note Routeur NAT (198.51.100.7) : traduit : 10.10.0.58:51544 ↔ 198.51.100.7:40002
Serveur Web --> Routeur NAT (198.51.100.7) : réponse vers 198.51.100.7:40002
Routeur NAT (198.51.100.7) --> PC B (10.10.0.58) : retraduit vers 10.10.0.58:51544
```

Le serveur Web voit deux connexions venant **de la même adresse**, mais de deux **ports** différents. Le routeur sait, grâce à sa table, à quel poste rendre chaque réponse.

## Les trois formes de NAT

| Forme | Principe | Usage |
|---|---|---|
| **PAT** (*overload*, NAT dynamique avec ports) | plusieurs adresses privées → une adresse publique, distinguées par les ports | accès Internet des postes |
| **NAT statique** | une adresse privée ↔ une adresse publique, de façon permanente | rendre un serveur interne joignable depuis Internet |
| **Redirection de port** (NAT statique avec port) | « le port 443 de l’adresse publique va vers 10.20.0.15:443 » | publier un service avec une seule adresse publique |

## Le NAT n’est pas un pare-feu… mais il en a l’air

Comme la table de traduction n’est créée que par des connexions **sortantes**, une connexion qui arrive d’Internet sans correspondance ne sait pas où aller : elle est jetée. Cela protège de fait les postes. Mais ce n’est pas une politique de sécurité : un seul NAT statique mal placé expose une machine. La sécurité se fait avec des règles de filtrage explicites.

## Les mots à connaître

- **NAT** — Traduction d’adresses entre un réseau privé et un réseau public.
- **PAT** — *Port Address Translation*, NAT qui utilise les numéros de port pour partager une adresse publique.
- **Table de traduction** — Liste des correspondances entre adresses et ports internes et externes.
- **Redirection de port** — Règle qui envoie les connexions reçues sur un port public vers une machine interne ; *port forwarding*.

## Teste-toi

**1.** Un serveur Web interne (10.20.0.15) doit être accessible depuis Internet sur l’adresse publique de l’entreprise. Le PAT des postes fonctionne. Que faut-il ajouter ?

<details><summary>Voir le corrigé</summary>

Une **redirection de port** (NAT statique) : port 443 de l’adresse publique vers `10.20.0.15:443`, **et** une règle de pare-feu qui autorise ce flux. Le PAT ne crée des correspondances que pour les connexions sortantes.

</details>

**2.** Pourquoi le NAT est-il beaucoup moins nécessaire en IPv6 ?

<details><summary>Voir le corrigé</summary>

Parce qu’IPv6 fournit assez d’adresses pour que chaque machine ait une **adresse publique**. La pénurie qui a justifié le NAT disparaît. La protection des postes est assurée par un pare-feu à états, pas par la traduction.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
interface GigabitEthernet0/0/0
 description Internet
 ip address 198.51.100.7 255.255.255.248
 ip nat outside
interface Vlan10
 ip nat inside
!
! PAT : les réseaux internes sortent avec l'adresse de l'interface Internet
ip access-list standard NAT-INTERNES
 permit 10.0.0.0 0.255.255.255
ip nat inside source list NAT-INTERNES interface GigabitEthernet0/0/0 overload
!
! Publication d'un serveur Web
ip nat inside source static tcp 10.20.0.15 443 198.51.100.7 443 extendable
```

```cisco
R1# show ip nat translations
Pro Inside global        Inside local        Outside local       Outside global
tcp 198.51.100.7:40001   10.10.0.57:51544    203.0.113.10:443    203.0.113.10:443
tcp 198.51.100.7:443     10.20.0.15:443      ---                 ---
R1# show ip nat statistics
R1# clear ip nat translation *
```

Vocabulaire Cisco : **inside local** (adresse réelle du poste), **inside global** (la même vue d’Internet), **outside** (le correspondant).

## Ce que le NAT complique

| Situation | Problème | Solution courante |
|---|---|---|
| SIP, voix sur IP | les adresses des flux audio sont écrites **dans** les messages SIP | ALG SIP (souvent source de bugs), SBC, STUN/TURN/ICE |
| FTP actif | le client annonce son adresse et un port dans les données | mode passif, ALG FTP |
| IPsec | AH ne supporte pas la modification de l’en-tête ; ESP n’a pas de ports | NAT-T : encapsulation dans UDP 4500 |
| Connexions entrantes vers un poste | pas de correspondance dans la table | redirections, ou relais applicatif |
| **Recouvrement d’adresses** | deux réseaux privés utilisent `192.168.10.0/24` et doivent communiquer (fusion, VPN) | NAT des deux côtés vers des plages neutres |

## Épuisement des ports et CGNAT

Une adresse publique offre environ 64 000 ports par protocole et par destination. Un PAT très chargé (milliers de postes, applications qui ouvrent beaucoup de connexions) peut **manquer de ports** : de nouvelles connexions échouent au hasard. On ajoute alors des adresses publiques (un *pool* au lieu d’une interface).

Les opérateurs appliquent parfois un second niveau de NAT, le **CGNAT** (plage `100.64.0.0/10`) : le client n’a même plus d’adresse publique propre, ce qui empêche toute publication de service depuis chez lui.

## Exercices

**1.** Deux entreprises qui fusionnent utilisent toutes deux `192.168.10.0/24`. Un VPN doit les relier rapidement. Que proposer ?

<details><summary>Voir le corrigé</summary>

Une **double traduction** aux extrémités du VPN : chaque site voit l’autre derrière une plage neutre (par exemple `10.201.10.0/24` pour l’entreprise A, `10.202.10.0/24` pour B). Les flux sont traduits en entrant et en sortant du tunnel. À plus long terme, renuméroter un des deux réseaux.

</details>

**2.** Une redirection de port 443 vers un serveur interne est configurée, mais le site n’est pas joignable depuis Internet. `show ip nat translations` montre bien l’entrée statique. Que vérifier ?

<details><summary>Voir le corrigé</summary>

Le **filtrage** : ACL ou pare-feu sur l’interface Internet qui doit autoriser TCP 443 vers l’adresse publique ; la **route retour** du serveur (sa passerelle doit être le routeur qui fait le NAT, sinon la réponse sort par ailleurs sans être retraduite) ; enfin le service lui-même.

</details>
