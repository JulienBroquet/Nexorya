---
titre: ARP
nom: Address Resolution Protocol
idee: ARP trouve l’adresse MAC qui correspond à une adresse IP du réseau local, en demandant à tout le monde « qui a cette IP ? ».
osi: "2 et 3"
duree: [7, 15]
prerequis: [ipv4, mac]
retenir:
  - La **requête** ARP est un **broadcast** — « qui a 192.168.1.1 ? » ; la **réponse** est un unicast — « c’est moi, voici ma MAC ».
  - Le résultat est gardé dans un **cache ARP** (`arp -a`).
  - Pour joindre un autre réseau, on demande la MAC de la **passerelle**, jamais celle de la destination finale.
  - ARP n’est pas authentifié — une machine peut mentir (**usurpation ARP**) ; la parade s’appelle DAI.
---

## Le problème : connaître l’IP ne suffit pas

Ton PC veut envoyer un paquet à `192.168.1.1`, sa passerelle. Il connaît l’adresse IP, mais pour fabriquer la trame Ethernet, il lui faut **l’adresse MAC** de la passerelle. Où la trouver ?

> [!IMPORTANT] L’idée en une phrase
> ARP pose la question à **tout le réseau local** : « qui a l’adresse 192.168.1.1 ? ». Seule la machine concernée répond, en donnant son adresse MAC.

## Comment ça marche

```sequence
titre: Résolution ARP de la passerelle
PC (192.168.1.20) | Switch | Routeur (192.168.1.1)
PC (192.168.1.20) -> Switch : requête ARP en broadcast : « qui a 192.168.1.1 ? »
Switch -> Routeur (192.168.1.1) : le broadcast est inondé à tout le VLAN
Routeur (192.168.1.1) --> PC (192.168.1.20) : réponse unicast : « 192.168.1.1 est à 00:aa:0b:00:00:01 »
note PC (192.168.1.20) : enregistre l’association dans son cache ARP
PC (192.168.1.20) -> Routeur (192.168.1.1) : les paquets partent, adressés à cette MAC
```

1. Le PC regarde dans son **cache ARP** : s’il connaît déjà la MAC, il l’utilise.
2. Sinon, il envoie une **requête ARP en broadcast** : toutes les machines du VLAN la reçoivent.
3. Seule la machine qui possède l’adresse IP demandée **répond**, directement au PC.
4. Le PC garde l’association **IP → MAC** dans son cache pendant quelques minutes.

## Et pour joindre Internet ?

Si la destination est **dans un autre réseau** (un serveur sur Internet), le PC ne demande **pas** la MAC du serveur : ce serait inutile, le serveur n’est pas sur son réseau local. Il demande la MAC de sa **passerelle**, et lui confie le paquet.

## Voir le cache ARP

```powershell
C:\> arp -a
Interface : 192.168.1.20 --- 0x7
  Adresse Internet      Adresse physique      Type
  192.168.1.1           00-aa-0b-00-00-01     dynamique
  192.168.1.40          3c-22-fb-1a-09-7e     dynamique
  192.168.1.255         ff-ff-ff-ff-ff-ff     statique
```

Sous Linux : `ip neigh`.

## Les mots à connaître

- **ARP** — *Address Resolution Protocol*, protocole qui trouve l’adresse MAC correspondant à une adresse IPv4 du réseau local.
- **Cache ARP** — Mémoire temporaire des associations IP → MAC déjà résolues.
- **ARP gratuit** — Annonce ARP non sollicitée par laquelle une machine annonce sa propre association IP → MAC.
- **Usurpation ARP** — Attaque qui consiste à répondre faussement à des requêtes ARP pour détourner le trafic ; *ARP spoofing*.

## Teste-toi

**1.** Le PC `192.168.1.20/24` veut joindre `8.8.8.8`. Pour quelle adresse IP envoie-t-il une requête ARP ?

<details><summary>Voir le corrigé</summary>

Pour l’adresse de sa **passerelle** (par exemple `192.168.1.1`). `8.8.8.8` est hors de son réseau : le paquet sera remis à la passerelle, dont il faut connaître la MAC.

</details>

**2.** Pourquoi la requête ARP est-elle un broadcast, alors que la réponse est un unicast ?

<details><summary>Voir le corrigé</summary>

Au moment de la requête, le PC **ne connaît pas** la MAC du destinataire : il doit demander à tout le monde. Le destinataire, lui, connaît la MAC du demandeur (elle figure dans la requête) : il lui répond directement.

</details>

<!-- approfondir -->

## Le message ARP

ARP est transporté directement dans une trame Ethernet (EtherType `0x0806`), sans en-tête IP.

| Champ | Requête | Réponse |
|---|---|---|
| Opération | 1 (request) | 2 (reply) |
| MAC émetteur | MAC du PC | MAC du routeur |
| IP émetteur | 192.168.1.20 | 192.168.1.1 |
| MAC cible | 00:00:00:00:00:00 (inconnue) | MAC du PC |
| IP cible | 192.168.1.1 | 192.168.1.20 |
| MAC destination de la trame | ff:ff:ff:ff:ff:ff | MAC du PC |

Toute machine qui reçoit une requête ARP **met à jour** son cache avec l’association de l’émetteur si elle la connaissait déjà : c’est une optimisation… et une faiblesse.

## Les variantes

- **ARP gratuit** (*gratuitous ARP*) : une machine annonce sa propre association, sans qu’on le lui demande. Utilisé au démarrage (détection de doublon d’adresse), après un changement de carte, et par les protocoles de passerelle redondante ([HSRP](hsrp.md), [VRRP](vrrp.md)) pour que les switches et les postes apprennent la MAC virtuelle lors d’une bascule.
- **Proxy ARP** : un routeur répond aux requêtes ARP **à la place** de machines situées dans un autre réseau. Il « rattrape » des postes mal configurés (masque trop large, pas de passerelle), mais masque les erreurs et peut provoquer des comportements inattendus. Souvent désactivé : `no ip proxy-arp`.

## Les durées de cache

| Système | Durée typique |
|---|---|
| Windows | 15 à 45 s, avec revérification (état *Reachable*/*Stale*) |
| Linux | quelques dizaines de secondes, avec revérification |
| Routeur Cisco IOS | **4 heures** |

L’écart entre le cache ARP des routeurs (4 h) et la table MAC des switches (5 min) explique le phénomène d’**inondation d’unicast inconnu** décrit dans la fiche [Adresse MAC](../niveau-1/mac.md).

## L’usurpation ARP

ARP n’a aucune authentification. Un attaquant peut envoyer des réponses ARP non sollicitées affirmant « 192.168.1.1 est à **ma** MAC ». Les victimes mettent à jour leur cache : tout leur trafic vers Internet passe par l’attaquant, qui peut l’observer ou le modifier avant de le relayer (*homme du milieu*).

```sequence
titre: Usurpation ARP de la passerelle
Victime | Attaquant | Routeur
Attaquant -> Victime : réponse ARP non sollicitée : « 192.168.1.1 est à MAC-attaquant »
Attaquant -> Routeur : réponse ARP : « 192.168.1.20 est à MAC-attaquant »
Victime -> Attaquant : trafic vers Internet (croit parler au routeur)
Attaquant -> Routeur : relaie le trafic, après l’avoir lu
```

Parades : **Dynamic ARP Inspection** sur les switches ([DAI](../niveau-4/dai.md)), qui vérifie chaque réponse ARP contre la table du DHCP Snooping ; chiffrement des échanges (TLS), qui rend l’interception inutile.

## Diagnostic

```cisco
R1# show ip arp vlan 10
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  192.168.1.1             -   00aa.0b00.0001  ARPA   Vlan10
Internet  192.168.1.20            3   3c22.fb1a.097e  ARPA   Vlan10
Internet  192.168.1.77            0   Incomplete      ARPA
```

- `Incomplete` : le routeur a envoyé une requête, **personne n’a répondu**. La machine est éteinte, dans un autre VLAN, ou l’adresse n’existe pas.
- Deux adresses IP avec la **même MAC** peuvent être normales (un routeur, un serveur avec plusieurs adresses) ou signaler une usurpation.

```bash
# Linux : forcer une nouvelle résolution
sudo ip neigh flush dev eth0
# Windows
arp -d *
```

## Exercices

**1.** Une imprimante a été remplacée ; elle a gardé son adresse IP. Les postes ne l’atteignent plus pendant quelques secondes à quelques minutes, sauf le routeur, qui ne l’atteint plus pendant des heures. Explique.

<details><summary>Voir le corrigé</summary>

La nouvelle imprimante a une **nouvelle MAC**. Les postes ont un cache ARP court : ils refont vite une requête. Le routeur garde l’ancienne association **4 heures** par défaut. Solutions : `clear ip arp 192.168.1.40` sur le routeur, ou s’assurer que l’imprimante envoie un ARP gratuit au démarrage.

</details>

**2.** `show ip arp` montre `Incomplete` pour un serveur dont tu es sûr qu’il est allumé. Quelles vérifications fais-tu ?

<details><summary>Voir le corrigé</summary>

Le serveur ne répond pas aux requêtes ARP du routeur : vérifier qu’il est dans le **bon VLAN** (port du switch), que son **adresse IP et son masque** sont corrects, et que la requête l’atteint (table MAC du switch, `show mac address-table`). Un pare-feu local ne bloque normalement pas ARP.

</details>

**3.** Pourquoi l’usurpation ARP ne permet-elle pas de détourner le trafic d’un autre VLAN ?

<details><summary>Voir le corrigé</summary>

Parce qu’ARP ne fonctionne que **dans le domaine de diffusion**. Les requêtes et réponses ARP ne traversent pas les routeurs : l’attaquant ne peut tromper que les machines de son propre VLAN.

</details>
