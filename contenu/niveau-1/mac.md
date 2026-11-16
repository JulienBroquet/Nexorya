---
titre: Adresse MAC
nom: Media Access Control
idee: L’adresse MAC identifie une carte réseau sur le réseau local ; le switch apprend sur quel port se trouve chaque adresse MAC pour y livrer les trames.
osi: "2"
duree: [8, 16]
prerequis: [ethernet]
retenir:
  - Une adresse MAC fait **48 bits**, écrits en 6 octets hexadécimaux ; les 3 premiers identifient le **fabricant**.
  - Le switch **apprend** avec l’adresse MAC **source** et **décide** avec l’adresse MAC **destination**.
  - Destination inconnue ou broadcast — le switch **inonde** la trame sur tous les ports du VLAN, sauf celui d’arrivée.
  - Les adresses MAC **changent à chaque routeur** ; les adresses IP restent celles de bout en bout.
---

## Le problème : livrer au bon appareil du réseau local

Un switch reçoit une trame sur un de ses 48 ports. Sur lequel doit-il la renvoyer ? Il lui faut un identifiant pour chaque appareil, et un moyen de savoir **où** se trouve chaque identifiant. Cet identifiant, c’est l’**adresse MAC**.

> [!IMPORTANT] L’idée en une phrase
> Chaque carte réseau possède une adresse MAC unique. Le switch note, pour chaque adresse, le port par lequel elle est arrivée, et s’en sert pour livrer les trames suivantes au bon endroit.

## À quoi ressemble une adresse MAC ?

`3C:22:FB:1A:09:7E` — six octets en hexadécimal, soit 48 bits. Selon les systèmes, on l’écrit avec des deux-points, des tirets (`3C-22-FB-1A-09-7E`) ou par groupes de quatre (`3c22.fb1a.097e`, notation Cisco).

- Les **trois premiers octets** identifient le **fabricant** (c’est l’OUI, attribué par l’IEEE).
- Les **trois derniers** sont attribués par le fabricant à chaque carte.
- L’adresse spéciale `FF:FF:FF:FF:FF:FF` est le **broadcast** : « à tout le monde ».

## Comment le switch apprend

Le switch tient une **table MAC** : une liste « adresse MAC → port ». Il la remplit tout seul, en observant le trafic.

```topologie
titre: Un switch et trois PC
SW switch 1,0 "Switch"
A pc 0,1 "PC A" "port 1"
B pc 1,1 "PC B" "port 5"
C pc 2,1 "PC C" "port 9"
SW -- A
SW -- B
SW -- C
```

1. **A envoie une trame à B.** Le switch regarde l’adresse **source** : il note « A est sur le port 1 ».
2. Il regarde l’adresse **destination**, B : il ne la connaît pas encore. Il **inonde** la trame sur tous les autres ports (5 et 9). C reçoit la trame, voit qu’elle ne lui est pas destinée et l’ignore.
3. **B répond à A.** Le switch apprend « B est sur le port 5 ». Il connaît A : il envoie la réponse **uniquement** sur le port 1.
4. À partir de là, A et B communiquent sans que C ne reçoive plus rien.

| Situation | Ce que fait le switch |
|---|---|
| Destination connue dans la table | Il envoie la trame sur **ce seul port**. |
| Destination inconnue | Il l’**inonde** sur tous les ports du VLAN, sauf celui d’arrivée. |
| Destination broadcast (FF:FF…) | Il l’**inonde** de la même façon. |
| Destination sur le port d’arrivée | Il la **jette** (le destinataire l’a déjà reçue). |

> [!TIP] Le moyen mnémotechnique
> Le switch **apprend avec la source, décide avec la destination**.

## Les adresses MAC changent à chaque routeur

Une adresse MAC n’a de sens **que sur le réseau local**. Quand un PC envoie un paquet à un serveur situé dans un autre réseau, la trame est adressée à la MAC du **routeur** (la passerelle), pas à celle du serveur. Le routeur fabrique ensuite une nouvelle trame pour le lien suivant. L’adresse **IP** de destination, elle, reste celle du serveur tout au long du voyage.

## Les mots à connaître

- **Adresse MAC** — Identifiant de 48 bits d’une carte réseau, utilisé pour livrer les trames sur le réseau local.
- **OUI** — *Organizationally Unique Identifier*, les trois premiers octets d’une adresse MAC, qui désignent le fabricant.
- **Table MAC** — Table d’un switch qui associe chaque adresse MAC au port où elle a été vue ; aussi appelée table CAM.
- **Inondation** — Envoi d’une trame sur tous les ports d’un VLAN quand la destination est inconnue ou broadcast ; *flooding* en anglais.
- **Broadcast** — Adresse FF:FF:FF:FF:FF:FF, qui désigne tous les appareils du réseau local.

## Teste-toi

**1.** Un switch vient de démarrer. Le PC A (port 1) envoie une trame au PC B (port 5). Que retient le switch, et que fait-il de la trame ?

<details><summary>Voir le corrigé</summary>

Il retient que **A est sur le port 1** (adresse source). Il ne connaît pas encore B, donc il **inonde** la trame sur tous les ports du VLAN sauf le port 1. Il apprendra où se trouve B quand B répondra.

</details>

**2.** Le PC `10.1.1.10` envoie un paquet au serveur `10.2.2.20`, situé derrière le routeur R1. Quelle est l’adresse MAC de destination de la trame qui sort du PC ?

<details><summary>Voir le corrigé</summary>

**La MAC du routeur R1**, sa passerelle. Le serveur n’est pas dans le réseau local du PC : le PC confie le paquet à R1. L’IP de destination reste `10.2.2.20`.

</details>

<!-- approfondir -->

## Structure fine d’une adresse MAC

Les deux bits de poids faible du **premier octet** ont un rôle particulier :

| Bit | Valeur 0 | Valeur 1 |
|---|---|---|
| I/G (bit 0) | adresse **individuelle** (unicast) | adresse de **groupe** (multicast ou broadcast) |
| U/L (bit 1) | adresse **universelle** (attribuée par le fabricant) | adresse **administrée localement** |

Exemples : `01:00:5E:xx:xx:xx` (premier octet impair) est une adresse multicast IPv4 ; `33:33:xx:xx:xx:xx` une adresse multicast IPv6. Une adresse dont le deuxième chiffre hexadécimal est 2, 6, A ou E (`x2:…`, `xA:…`) est administrée localement : c’est le cas des **adresses aléatoires** que les téléphones et Windows utilisent sur les réseaux Wi-Fi pour protéger la vie privée, ainsi que des MAC de machines virtuelles.

> [!NOTE]
> Les adresses MAC aléatoires compliquent les réseaux qui identifient les appareils par leur MAC (portails invités, réservations DHCP, filtrage). Les solutions modernes s’appuient sur l’authentification 802.1X plutôt que sur l’adresse MAC.

## La table MAC en pratique (Cisco IOS)

```cisco
SW1# show mac address-table dynamic vlan 10
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
  10    3c22.fb1a.097e    DYNAMIC     Gi1/0/1
  10    0050.56aa.0001    DYNAMIC     Gi1/0/48
  10    7c21.0e4a.1b30    DYNAMIC     Gi1/0/48
Total Mac Addresses for this criterion: 3

SW1# show mac address-table address 3c22.fb1a.097e
SW1# show mac address-table aging-time
Global Aging Time:  300
```

- Plusieurs adresses sur **Gi1/0/48** : c’est normal pour un lien vers un autre switch, derrière lequel se trouvent de nombreuses machines.
- Les entrées dynamiques **expirent** après 300 secondes sans trafic (*aging time*), pour que la table suive les déplacements.
- La table est **par VLAN** : la même MAC peut apparaître dans deux VLAN différents.

**Retrouver un poste dans un réseau** : on cherche sa MAC sur le switch de cœur, on suit le port indiqué vers le switch suivant, et ainsi de suite jusqu’à un port d’accès. `show cdp neighbors` ou `show lldp neighbors` indique quel switch se trouve derrière chaque port.

## Les incidents liés à la table MAC

**MAC flapping.** La même adresse est apprise alternativement sur deux ports :

```text
%SW_MATM-4-MACFLAP_NOTIF: Host 0050.56aa.0001 in vlan 10 is flapping
between port Gi1/0/1 and port Gi1/0/2
```

C’est le signe d’une **boucle** (voir [STP](stp.md)), d’un agrégat de liens mal configuré (voir [LACP](lacp.md)), ou parfois d’un serveur dont deux cartes utilisent la même adresse sans être agrégées.

**Saturation de la table.** Une table MAC a une taille finie (quelques milliers à quelques centaines de milliers d’entrées). Un attaquant qui envoie des milliers de trames avec des MAC source aléatoires la remplit : les vraies adresses ne peuvent plus être apprises, leurs trames sont **inondées** partout, et l’attaquant peut les capturer. **Port Security**, qui limite le nombre de MAC par port, empêche cette attaque.

```cisco
interface GigabitEthernet1/0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
```

## Le flooding d’unicast inconnu, un symptôme subtil

Si un serveur n’envoie presque jamais de trafic mais en reçoit beaucoup (un serveur de journaux, par exemple), son entrée MAC peut **expirer** (300 s) alors que son entrée ARP chez les émetteurs dure bien plus longtemps (4 heures par défaut sur Cisco). Le switch ne sait plus où il se trouve : tout le trafic qui lui est destiné est **inondé** dans le VLAN. Solutions : aligner les temporisateurs (aging MAC ≥ délai ARP) ou faire émettre régulièrement le serveur.

## Exercices

**1.** L’adresse `02:42:ac:11:00:02` apparaît sur un serveur Linux. Est-ce une adresse de fabricant ?

<details><summary>Voir le corrigé</summary>

**Non.** Le premier octet `02` a le bit U/L à 1 : c’est une adresse **administrée localement**. Ce préfixe `02:42` est typiquement celui des conteneurs Docker.

</details>

**2.** `show mac address-table` sur un switch d’accès montre 400 adresses sur un port utilisateur. Que soupçonnes-tu ?

<details><summary>Voir le corrigé</summary>

Un port utilisateur ne devrait voir qu’une à trois adresses (PC, téléphone, éventuellement une machine virtuelle). 400 adresses désignent soit un **switch non autorisé** branché sur la prise, soit une **attaque de saturation** de la table MAC. Vérifier avec `show cdp neighbors`, `show lldp neighbors`, et configurer **Port Security** avec un nombre maximal d’adresses.

</details>

**3.** Après le remplacement de la carte mère d’un serveur, des utilisateurs ne le joignent plus pendant quelques minutes, puis tout rentre dans l’ordre. Explique.

<details><summary>Voir le corrigé</summary>

La nouvelle carte a une **nouvelle adresse MAC**. Les postes et le routeur gardaient en mémoire (cache ARP) l’ancienne association IP → MAC et envoyaient leurs trames à une adresse qui n’existe plus. Les choses rentrent dans l’ordre à l’expiration des caches ARP, ou dès que le serveur envoie un **ARP gratuit** pour annoncer sa nouvelle MAC.

</details>
