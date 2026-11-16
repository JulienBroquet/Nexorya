---
titre: DAI
nom: Dynamic ARP Inspection
idee: DAI vérifie chaque message ARP reçu sur un port d’accès et rejette ceux qui ne correspondent pas aux adresses réellement attribuées ; un poste ne peut plus se faire passer pour la passerelle.
osi: "2"
duree: [6, 12]
prerequis: [arp, dhcp-snooping]
retenir:
  - DAI s’appuie sur la **table de liaisons** du DHCP Snooping (IP ↔ MAC ↔ port ↔ VLAN).
  - Les messages ARP incohérents arrivant par un port **non fiable** sont **jetés** (et le port peut être coupé en cas de rafale).
  - Les machines à **adresse fixe** doivent être déclarées (liaison statique ou ACL ARP).
---

## Le problème : l’usurpation de la passerelle

ARP n’a aucune authentification. Un attaquant branché sur une prise du VLAN peut annoncer « l’adresse 10.10.0.1 (la passerelle), c’est moi ». Les postes le croient et lui envoient tout leur trafic : il peut l’observer et le modifier (homme du milieu). Voir [ARP](../niveau-2/arp.md).

> [!IMPORTANT] L’idée en une phrase
> Le switch connaît, grâce au DHCP Snooping, quelle adresse IP a été donnée à quelle adresse MAC sur quel port ; DAI rejette tout message ARP qui contredit ces informations.

## Comment ça marche

1. Le DHCP Snooping construit la **table de liaisons** : « 10.10.0.57 = 3c22.fb1a.097e sur Gi1/0/5, VLAN 10 ».
2. DAI intercepte chaque requête et réponse ARP reçue sur un port **non fiable** (les ports d’accès).
3. Si l’association IP–MAC annoncée **correspond** à une liaison connue sur ce port, le message passe ; sinon, il est **jeté** et journalisé.
4. Les ports vers les autres switches et les routeurs sont déclarés **de confiance** : leurs ARP ne sont pas vérifiés.

```sequence
titre: Dynamic ARP Inspection bloque une réponse ARP falsifiée
Attaquant | Switch | Poste
Attaquant -> Switch : ARP : « 10.10.0.1 (la passerelle), c’est ma MAC »
note Switch : compare avec la table DHCP snooping : 10.10.0.1 n’est pas sur ce port
Switch -x Poste : réponse ARP jetée, événement journalisé
note Poste : continue d’envoyer son trafic à la vraie passerelle
```

## Les mots à connaître

- **DAI** — *Dynamic ARP Inspection*, vérification des messages ARP par le switch.
- **Usurpation ARP** — Annonce mensongère d’une association IP–MAC pour détourner du trafic.
- **Port de confiance (DAI)** — Port dont les messages ARP ne sont pas vérifiés, vers les switches et routeurs.

## Teste-toi

**Pourquoi faut-il activer le DHCP Snooping avant DAI ?**

<details><summary>Voir le corrigé</summary>

Parce que DAI s’appuie sur la **table de liaisons** que construit le DHCP Snooping. Sans elle, DAI ne sait pas quelles associations IP–MAC sont légitimes, et rejetterait tous les ARP des ports non fiables.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS)

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10,20
ip arp inspection vlan 10,20
ip arp inspection validate src-mac dst-mac ip
!
interface Port-channel1
 description Uplink
 ip dhcp snooping trust
 ip arp inspection trust
!
interface range GigabitEthernet1/0/1 - 46
 ip arp inspection limit rate 15        ! au-delà de 15 ARP/s, le port passe en err-disabled
!
! Imprimante à adresse fixe : ACL ARP
arp access-list FIXES-VLAN10
 permit ip host 10.10.0.200 mac host 0011.2233.4455
ip arp inspection filter FIXES-VLAN10 vlan 10
```

## Vérification

```cisco
SW1# show ip arp inspection statistics vlan 10
 Vlan      Forwarded        Dropped     DHCP Drops      ACL Drops
 ----      ---------        -------     ----------      ---------
   10          84122             37             37              0
SW1# show logging | include DAI
%SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs (Res) on Gi1/0/22, vlan 10.
([0050.56aa.00ff/10.10.0.1/3c22.fb1a.097e/10.10.0.57/09:12:44 CET Sun Nov 15 2026])
```

Le message révèle qu’un appareil sur **Gi1/0/22** a prétendu être `10.10.0.1` (la passerelle) avec la MAC `0050.56aa.00ff` : tentative d’usurpation, ou machine mal configurée.

## Exercice

**Après l’activation de DAI, une imprimante à adresse fixe n’est plus joignable. Qu’ajouter ?**

<details><summary>Voir le corrigé</summary>

Une **ACL ARP** (ou une liaison statique dans la table du DHCP Snooping) qui associe l’adresse IP de l’imprimante à sa MAC. Sans liaison connue, ses réponses ARP sont considérées comme invalides et jetées.

</details>
