---
titre: SIP
nom: Session Initiation Protocol
idee: SIP sert à établir, modifier et terminer les appels en voix sur IP — il fait sonner le téléphone et négocie le format audio, mais ne transporte pas la voix elle-même.
osi: "7 (UDP/TCP 5060 ; TLS 5061)"
duree: [8, 16]
prerequis: [udp, nat]
retenir:
  - SIP **signale** l’appel (INVITE, 180 Ringing, 200 OK, ACK, BYE) ; la voix passe par **RTP**, sur d’autres ports.
  - La description du média (**SDP**) annonce l’adresse IP, les ports et les codecs — le **NAT** la rend souvent fausse.
  - "Symptôme classique — **l’appel s’établit mais pas de son** (ou son dans un seul sens)."
---

## Le problème : passer un appel sur un réseau de données

Pour téléphoner sur IP, il faut d’abord **trouver** le correspondant, le **faire sonner**, se mettre d’accord sur le **format** de la voix, puis **raccrocher**. Ce travail de signalisation est distinct du transport de la voix elle-même.

> [!IMPORTANT] L’idée en une phrase
> SIP fait le travail du standard téléphonique — appeler, faire sonner, décrocher, raccrocher —, et laisse RTP transporter la voix.

## Un appel, pas à pas

```sequence
titre: Établissement d’un appel SIP
Poste A | Serveur d’appels (PBX) | Poste B
Poste A -> Serveur d’appels (PBX) : INVITE (SDP : mon IP, mon port audio, mes codecs)
Serveur d’appels (PBX) -> Poste B : INVITE
Poste B --> Serveur d’appels (PBX) : 180 Ringing (le téléphone sonne)
Serveur d’appels (PBX) --> Poste A : 180 Ringing
Poste B --> Serveur d’appels (PBX) : 200 OK (B décroche ; SDP : son IP, son port, codec choisi)
Serveur d’appels (PBX) --> Poste A : 200 OK
Poste A -> Serveur d’appels (PBX) : ACK
note Poste A, Poste B : la voix circule en RTP, souvent directement entre les deux postes
Poste A -> Serveur d’appels (PBX) : BYE (A raccroche)
Serveur d’appels (PBX) --> Poste A : 200 OK
```

## Les codes de réponse

Comme HTTP : **1xx** en cours (180 Ringing), **2xx** succès (200 OK), **3xx** redirection, **4xx** erreur du client (401/407 authentification, 404 numéro inconnu, 486 occupé), **5xx** erreur du serveur, **6xx** refus global.

## « On s’entend pas » : le NAT

Dans l’INVITE, le poste écrit **son adresse IP et son port audio** (le SDP). Derrière un NAT, il écrit son adresse **privée** : le correspondant envoie sa voix vers une adresse injoignable. Résultat : l’appel sonne, on décroche… et **aucun son**, ou un son dans un seul sens.

## Les mots à connaître

- **SIP** — Protocole de signalisation des appels en voix sur IP.
- **INVITE / BYE** — Messages SIP d’ouverture et de fin d’appel.
- **SDP** — *Session Description Protocol*, description du média : adresse, ports, codecs.
- **PBX / IPBX** — Autocommutateur, serveur qui gère les appels de l’entreprise.
- **Trunk SIP** — Liaison SIP entre l’IPBX de l’entreprise et un opérateur téléphonique.

## Teste-toi

**Un appel s’établit (le téléphone sonne, on décroche) mais personne ne s’entend. SIP fonctionne-t-il ?**

<details><summary>Voir le corrigé</summary>

**Oui** : la signalisation a réussi, puisque l’appel s’est établi. C’est le **flux audio RTP** qui ne passe pas : ports RTP bloqués par un pare-feu, adresses fausses dans le SDP à cause du NAT, ou routage asymétrique.

</details>

<!-- approfondir -->

## Lire un INVITE

```text
INVITE sip:2042@pbx.exemple.fr SIP/2.0
Via: SIP/2.0/UDP 10.20.5.31:5060;branch=z9hG4bK776asdhds
From: <sip:2017@pbx.exemple.fr>;tag=1928301774
To: <sip:2042@pbx.exemple.fr>
Call-ID: a84b4c76e66710@10.20.5.31
CSeq: 314159 INVITE
Contact: <sip:2017@10.20.5.31:5060>
Content-Type: application/sdp

v=0
o=2017 2890844526 2890844526 IN IP4 10.20.5.31
c=IN IP4 10.20.5.31                 ← adresse où envoyer la voix
m=audio 16384 RTP/AVP 8 0 101       ← port audio 16384 ; codecs G.711 A (8), µ (0), DTMF (101)
a=rtpmap:8 PCMA/8000
```

## Traverser le NAT et les pare-feu

| Solution | Principe |
|---|---|
| **SBC** (*Session Border Controller*) | équipement en bordure qui termine et réécrit la signalisation et le média : la solution d’entreprise |
| STUN / TURN / ICE | le poste découvre son adresse publique, ou relaie le média par un serveur |
| ALG SIP du pare-feu | le pare-feu réécrit le SDP ; souvent **source de pannes**, et à désactiver quand un SBC est présent |
| Plages de ports fixes | ouvrir une plage RTP connue (ex. 16384–32767 UDP) |

## Diagnostic

```bash
$ sudo tcpdump -ni eth0 -s0 -w appel.pcap 'port 5060 or portrange 16384-32767'
# Wireshark : Téléphonie → Appels VoIP → sélectionner l'appel → Diagramme de flux / Lire les flux
```

Wireshark reconstitue l’échange SIP, montre les flux RTP de chaque sens et peut même **rejouer** l’audio. Un flux RTP présent dans un seul sens désigne immédiatement le côté bloqué.

## Exercices

**1.** Le poste A (10.20.5.31, derrière un NAT) appelle un correspondant externe. L’appel s’établit, A entend le correspondant, mais le correspondant n’entend pas A. La capture côté A montre du RTP sortant et entrant. Que se passe-t-il ?

<details><summary>Voir le corrigé</summary>

A envoie bien sa voix, mais elle n’arrive pas au correspondant : soit elle sort avec une adresse que le correspondant n’attend pas (NAT), soit elle est bloquée en sortie. À l’inverse, le correspondant arrive à joindre A, probablement grâce à une ouverture dynamique ou à un relais. Vérifier les adresses dans le SDP et la traduction NAT des flux RTP sortants, ou passer par un **SBC**.

</details>

**2.** Les appels entrants de l’opérateur échouent avec « 403 Forbidden » après la mise en place d’un nouveau pare-feu. Quelle piste ?

<details><summary>Voir le corrigé</summary>

Une réponse 403 vient d’un équipement **SIP** (l’IPBX, le SBC ou l’opérateur) qui refuse la requête : souvent une **adresse source** non reconnue (le nouveau pare-feu traduit l’adresse et l’IPBX n’accepte que celle de l’opérateur), ou une ALG SIP qui modifie les en-têtes. Vérifier le NAT appliqué et désactiver l’ALG si un SBC gère déjà la signalisation.

</details>
