---
titre: RADIUS
nom: Remote Authentication Dial-In User Service
idee: RADIUS est le protocole par lequel un switch, une borne Wi-Fi ou un VPN demande à un serveur central si un utilisateur ou un appareil a le droit d’accéder au réseau, et avec quels droits.
osi: "7 (UDP 1812 authentification, 1813 traçabilité)"
duree: [8, 16]
prerequis: [aaa]
retenir:
  - "Le NAS envoie **Access-Request** ; le serveur répond **Access-Accept**, **Access-Reject** ou **Access-Challenge**."
  - "L’Access-Accept peut contenir des **attributs** — VLAN à attribuer, ACL à appliquer, durée de session."
  - "Le NAS et le serveur partagent un **secret** ; seuls certains champs (dont le mot de passe) sont protégés."
  - "Usages — **802.1X** (filaire, Wi-Fi), **VPN**, parfois l’administration des équipements."
---

## Le problème

Un salarié se connecte au Wi-Fi d’entreprise avec ses identifiants. La borne Wi-Fi ne connaît pas les salariés. Elle doit demander à quelqu’un : « cet utilisateur a-t-il le droit d’entrer ? Si oui, dans quel VLAN ? ».

> [!IMPORTANT] L’idée en une phrase
> RADIUS transporte la question « peut-il entrer ? » de l’équipement d’accès vers le serveur central, et ramène la réponse avec les droits à appliquer.

## Comment ça marche

```sequence
titre: Accès au Wi-Fi d’entreprise avec RADIUS
Ordinateur | Borne Wi-Fi (NAS) | Serveur RADIUS | Annuaire
Ordinateur -> Borne Wi-Fi (NAS) : identité (via 802.1X / EAP)
Borne Wi-Fi (NAS) -> Serveur RADIUS : Access-Request
Serveur RADIUS --> Borne Wi-Fi (NAS) : Access-Challenge (échanges EAP, plusieurs allers-retours)
Serveur RADIUS -> Annuaire : alice existe ? groupes ?
Annuaire --> Serveur RADIUS : oui, groupe « Compta »
Serveur RADIUS --> Borne Wi-Fi (NAS) : Access-Accept + VLAN 10
Borne Wi-Fi (NAS) --> Ordinateur : accès ouvert dans le VLAN 10
Borne Wi-Fi (NAS) -> Serveur RADIUS : Accounting-Start (début de session)
```

## Ce que le serveur peut décider

Le serveur RADIUS applique des **politiques** : selon le groupe de l’utilisateur, le type d’appareil, l’heure, l’endroit, il peut répondre :

- **Accept** + VLAN 10 pour les employés de la comptabilité ;
- **Accept** + VLAN 30 (invités) pour un appareil personnel ;
- **Accept** + ACL restrictive pour une imprimante ;
- **Reject** pour un compte désactivé.

## Les mots à connaître

- **RADIUS** — Protocole d’authentification et d’autorisation des accès au réseau.
- **Access-Request / Accept / Reject / Challenge** — Messages RADIUS : demande, acceptation, refus, demande d’informations supplémentaires.
- **Attribut RADIUS** — Information transmise dans un message (identité, VLAN, durée…).
- **Secret partagé** — Clé commune au NAS et au serveur, qui protège une partie des échanges.

## Teste-toi

**Le serveur RADIUS est injoignable. Que se passe-t-il pour les salariés qui se connectent au Wi-Fi 802.1X ?**

<details><summary>Voir le corrigé</summary>

Les nouvelles connexions **échouent** : personne ne peut valider leur identité. C’est pourquoi on déploie au moins **deux serveurs RADIUS** et, sur les switches, une politique de secours (VLAN critique) pour les postes filaires.

</details>

<!-- approfondir -->

## Attributs courants

| Attribut | Usage |
|---|---|
| User-Name | identité |
| NAS-IP-Address, Called-Station-Id | quel équipement et quel SSID ou port |
| Calling-Station-Id | adresse MAC du client |
| **Tunnel-Type = VLAN (13), Tunnel-Medium-Type = 802 (6), Tunnel-Private-Group-ID** | VLAN à attribuer |
| Filter-Id, Cisco-AVPair | ACL à appliquer |
| Session-Timeout | durée maximale avant réauthentification |
| Class | étiquette reprise dans la traçabilité |

## Configuration côté switch (Cisco IOS-XE)

```cisco
aaa new-model
radius server ISE-1
 address ipv4 10.99.0.80 auth-port 1812 acct-port 1813
 key Une-Cle-Longue-Et-Unique
radius server ISE-2
 address ipv4 10.99.1.80 auth-port 1812 acct-port 1813
 key Une-Cle-Longue-Et-Unique
aaa group server radius RADIUS-ACCES
 server name ISE-1
 server name ISE-2
 ip radius source-interface Vlan99
aaa authentication dot1x default group RADIUS-ACCES
aaa authorization network default group RADIUS-ACCES
aaa accounting dot1x default start-stop group RADIUS-ACCES
radius-server dead-criteria time 5 tries 3
radius-server deadtime 10
```

`dead-criteria` et `deadtime` : déclarer un serveur hors service après 3 essais sans réponse, et ne plus l’interroger pendant 10 minutes. Cela accélère la bascule vers le second serveur.

## Sécurité du protocole

RADIUS est ancien : seul le mot de passe (attribut User-Password) est masqué avec le secret partagé ; le reste circule en clair, et l’intégrité des messages repose sur MD5. Les recommandations actuelles :

- secret **long et unique** par équipement ou groupe d’équipements ;
- attribut **Message-Authenticator** obligatoire (faille *Blast-RADIUS*, 2024) ;
- **RADIUS sur TLS** (RadSec, TCP 2083) quand les échanges traversent un réseau non maîtrisé ;
- de toute façon, en 802.1X, les identifiants de l’utilisateur sont protégés **par EAP**, à l’intérieur de RADIUS.

## Diagnostic

```cisco
SW1# test aaa group RADIUS-ACCES alice MotDePasse new-code
SW1# show aaa servers
RADIUS: id 1, priority 1, host 10.99.0.80, auth-port 1812, acct-port 1813
     State: current UP, duration 812733s, previous duration 0s
     Authen: request 4211, timeouts 0, failover 0, retransmission 0
SW1# show authentication sessions interface Gi1/0/5 details
```

Côté serveur, le journal d’authentification indique **pourquoi** une demande a été refusée (mauvais mot de passe, certificat inconnu, aucune politique correspondante). C’est presque toujours là que se trouve la réponse.

## Exercices

**1.** Les postes de la comptabilité sont acceptés en 802.1X, mais arrivent dans le VLAN par défaut du port au lieu du VLAN 10. Que vérifier ?

<details><summary>Voir le corrigé</summary>

Les **attributs de VLAN** dans l’Access-Accept (Tunnel-Type, Tunnel-Medium-Type, Tunnel-Private-Group-ID) : absents, mal écrits, ou un nom de VLAN qui n’existe pas sur le switch. Vérifier aussi `aaa authorization network`, sans lequel le switch ignore les attributs reçus.

</details>

**2.** Un switch affiche des timeouts vers le serveur RADIUS, alors que le serveur reçoit bien les requêtes. Le journal du serveur indique « unknown client ». Pourquoi ?

<details><summary>Voir le corrigé</summary>

Le serveur ne reconnaît pas l’**adresse source** du switch comme un client RADIUS déclaré : souvent parce que le switch envoie ses requêtes depuis une autre interface que celle enregistrée. Configurer `ip radius source-interface` avec l’adresse déclarée sur le serveur (ou déclarer la bonne adresse côté serveur), et vérifier le secret partagé.

</details>
