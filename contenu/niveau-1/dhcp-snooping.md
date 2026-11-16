---
titre: DHCP Snooping
nom: Protection contre les faux serveurs DHCP
idee: Le DHCP Snooping n’autorise les réponses DHCP que sur les ports qui mènent au vrai serveur ; une box branchée par erreur ne peut plus distribuer de fausses adresses.
osi: "2 et 7"
duree: [7, 14]
prerequis: [vlan]
retenir:
  - Les ports sont **de confiance** (trusted, vers le vrai serveur DHCP) ou **non fiables** (tous les autres).
  - Les **réponses** DHCP (OFFER, ACK) arrivant par un port non fiable sont **jetées**.
  - Le switch construit une **table de liaisons** (MAC, IP, port, VLAN) réutilisée par DAI et IP Source Guard.
---

## Le problème : la box personnelle qui casse un étage

Lundi matin, des postes du VLAN 10 reçoivent des adresses en `192.168.0.x` au lieu de `10.10.10.x`, et n’ont plus accès à rien. Un employé a branché sa **box Internet personnelle** sur sa prise réseau pour avoir du Wi-Fi au bureau. La box contient un serveur DHCP : elle répond aux demandes d’adresses plus vite que le vrai serveur, et distribue ses propres adresses, sa propre passerelle et son propre DNS.

Le même mécanisme peut être utilisé **volontairement** par un attaquant : en se déclarant passerelle, il fait passer tout le trafic des victimes par sa machine.

> [!IMPORTANT] L’idée en une phrase
> Le switch ne laisse passer les **réponses** DHCP que si elles arrivent par un port déclaré **de confiance** — celui qui mène au vrai serveur. Les autres sont jetées.

## Comment ça marche

```topologie
titre: Seul le port de confiance peut répondre en DHCP
SRV serveur 1,0 "Serveur DHCP" "le vrai"
SW switch 1,1 "Switch d’accès"
PC pc 0,2 "Poste"
BOX routeur 2,2 "Box personnelle" "faux serveur DHCP"
SRV ++ SW "port de confiance"
SW -- PC "non fiable"
SW -x- BOX "non fiable : réponses jetées"
```

1. L’administrateur active DHCP Snooping sur les VLAN utilisateurs.
2. Il déclare **de confiance** l’uplink qui mène au serveur DHCP. Tous les autres ports sont **non fiables** par défaut.
3. Les **demandes** des postes (DISCOVER, REQUEST) passent normalement.
4. Les **réponses** (OFFER, ACK) qui arrivent par un port non fiable sont jetées. La box peut rester branchée : elle ne trompe plus personne.

## Les mots à connaître

- **DHCP Snooping** — Fonction de switch qui filtre les messages DHCP selon la confiance accordée à chaque port.
- **Port de confiance** — Port autorisé à faire passer des réponses DHCP, en général l’uplink vers le serveur.
- **Serveur DHCP pirate** — Appareil non autorisé qui distribue des adresses sur le réseau (*rogue DHCP*).
- **Table de liaisons** — Liste construite par le switch des adresses IP attribuées, avec MAC, port et VLAN.

## Teste-toi

**1.** Pourquoi Port Security ne suffit-il pas à empêcher l’incident de la box ?

<details><summary>Voir le corrigé</summary>

Port Security limite le **nombre d’adresses MAC** sur un port. Une box n’utilise qu’une ou deux adresses MAC : elle passe la limite sans problème et continue de répondre en DHCP. Seul un contrôle du **contenu DHCP** (DHCP Snooping) l’en empêche.

</details>

**2.** Après avoir activé DHCP Snooping, plus aucun poste n’obtient d’adresse. Quel oubli est le plus probable ?

<details><summary>Voir le corrigé</summary>

L’administrateur n’a pas déclaré **de confiance** le port qui mène au vrai serveur DHCP (l’uplink). Les réponses légitimes sont jetées comme les autres.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10,20,30
no ip dhcp snooping information option        ! voir la remarque sur l'option 82
!
interface Port-channel1
 description Uplink vers la distribution (vers le serveur DHCP)
 ip dhcp snooping trust
!
interface range GigabitEthernet1/0/1 - 46
 ip dhcp snooping limit rate 15               ! paquets DHCP par seconde, contre l'épuisement
```

**L’option 82.** Par défaut, un switch Cisco qui fait du snooping **insère l’option 82** (informations sur le port et le switch) dans les demandes DHCP. Si le relais DHCP ou le serveur n’est pas prévu pour la recevoir, les demandes peuvent être **rejetées** et plus personne n’obtient d’adresse. Soit on la désactive (`no ip dhcp snooping information option`), soit on configure le serveur et le relais pour l’accepter (`ip dhcp relay information trust-all` sur le relais Cisco, par exemple).

## Vérification

```cisco
SW1# show ip dhcp snooping
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs: 10,20,30
Insertion of option 82 is disabled
Interface                  Trusted    Allow option    Rate limit (pps)
-----------------------    -------    ------------    ----------------
Port-channel1              yes        yes             unlimited
GigabitEthernet1/0/1       no         no              15

SW1# show ip dhcp snooping binding
MacAddress          IpAddress     Lease(sec)  Type           VLAN  Interface
------------------  -----------   ----------  -------------  ----  --------------------
3C:22:FB:1A:09:7E   10.10.10.57   85712       dhcp-snooping   10   GigabitEthernet1/0/1

SW1# show ip dhcp snooping statistics detail
 Packets Dropped Because
   Unknown output interface                             = 0
   Untrusted server messages                            = 214
```

Le compteur **Untrusted server messages** révèle qu’un faux serveur a tenté de répondre. On le localise ensuite avec la table MAC.

## La table de liaisons, socle d’autres protections

La table de liaisons est réutilisée par :

- **Dynamic ARP Inspection** ([DAI](../niveau-4/dai.md)) : rejette les réponses ARP qui ne correspondent pas à une liaison connue — protection contre l’usurpation de passerelle ;
- **IP Source Guard** : rejette le trafic dont l’adresse IP source ne correspond pas à celle attribuée sur ce port.

Les machines à **adresse fixe** n’apparaissent pas dans la table : il faut leur ajouter des entrées statiques, sinon DAI et IP Source Guard les bloqueraient.

Pour qu’un redémarrage du switch ne vide pas la table (et ne bloque pas les postes jusqu’au renouvellement de leur bail), on peut la sauvegarder : `ip dhcp snooping database flash:dhcp-snoop.db`.

## Exercices

**1.** Le compteur « Untrusted server messages » augmente sur un switch d’accès. Comment trouver le coupable ?

<details><summary>Voir le corrigé</summary>

Capturer ou journaliser les messages rejetés pour obtenir l’**adresse MAC source** du faux serveur, puis `show mac address-table address <mac>` pour trouver le **port**. On peut aussi provoquer une demande DHCP depuis un poste de test et observer la réponse. Ensuite, aller voir ce qui est branché sur ce port.

</details>

**2.** Un serveur d’impression a une adresse IP fixe. Après l’activation de DAI sur son VLAN, il n’est plus joignable. Pourquoi ?

<details><summary>Voir le corrigé</summary>

DAI s’appuie sur la table de liaisons du DHCP Snooping. Le serveur, configuré à la main, n’y figure pas : ses réponses ARP sont considérées comme suspectes et **rejetées**. Il faut ajouter une **liaison statique** (ou une ACL ARP) pour cette adresse.

</details>
