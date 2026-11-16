---
titre: AAA
nom: Authentication, Authorization, Accounting
idee: AAA répond à trois questions pour chaque accès — qui es-tu (authentification), qu’as-tu le droit de faire (autorisation), qu’as-tu fait (traçabilité).
osi: "7"
duree: [7, 15]
retenir:
  - "**A**uthentification — prouver son identité ; **A**utorisation — recevoir des droits ; **A**ccounting — garder la trace."
  - Les équipements délèguent ces décisions à un **serveur central** (RADIUS ou TACACS+).
  - Comptes **nominatifs**, droits **minimaux**, et toujours un **compte local de secours** si le serveur est injoignable.
---

## Le problème : 300 équipements, 300 listes de comptes

Sans organisation, chaque switch, routeur et borne Wi-Fi a ses propres comptes locaux, souvent un compte `admin` partagé dont le mot de passe n’a jamais changé. Quand un administrateur quitte l’entreprise, il faudrait modifier 300 équipements. Et lors d’un incident, impossible de savoir **qui** a fait **quoi**.

> [!IMPORTANT] L’idée en une phrase
> AAA centralise trois décisions : vérifier l’identité de chaque personne, lui donner seulement les droits nécessaires, et enregistrer ce qu’elle fait.

## Les trois A

| A | Question | Exemple |
|---|---|---|
| **Authentification** | Qui es-tu ? | identifiant + mot de passe + code MFA, ou certificat |
| **Autorisation** | Qu’as-tu le droit de faire ? | le technicien peut lire la configuration ; seul l’ingénieur peut la modifier ; un poste reçoit le VLAN 10 |
| **Accounting** (traçabilité) | Qu’as-tu fait, et quand ? | « bruno a tapé `no shutdown` sur Gi1/0/4 à 14 h 02 » ; durée d’une session VPN |

## Un serveur au centre

```topologie
titre: Les équipements demandent au serveur AAA
SW switch 0,0 "Switches"
R routeur 0,1 "Routeurs"
AP ap 0,2 "Bornes Wi-Fi"
AAA serveur 2,1 "Serveur AAA" "RADIUS / TACACS+"
AD serveur 3.5,1 "Annuaire" "comptes et groupes"
SW -- AAA
R -- AAA
AP -- AAA
AAA -- AD
```

Les équipements (appelés **NAS** ou clients AAA) ne connaissent pas les utilisateurs : ils transmettent chaque demande au serveur AAA, qui consulte l’annuaire et répond « accepté, avec tels droits » ou « refusé ».

## Deux protocoles

- **RADIUS** : surtout pour l’**accès au réseau** — Wi-Fi d’entreprise, 802.1X sur les prises, VPN. Voir [RADIUS](radius.md).
- **TACACS+** : surtout pour l’**administration des équipements** — qui peut se connecter au switch, quelles commandes il peut taper. Voir [TACACS+](tacacs.md).

## Les mots à connaître

- **AAA** — Authentification, autorisation et traçabilité des accès.
- **Authentification** — Vérification de l’identité d’une personne ou d’un appareil.
- **Autorisation** — Attribution des droits après l’authentification.
- **Accounting** — Enregistrement des actions et des sessions ; on dit aussi traçabilité ou comptabilité.
- **NAS** — *Network Access Server*, équipement qui transmet les demandes d’accès au serveur AAA.

## Teste-toi

**Pourquoi garder un compte local sur chaque équipement, alors que l’authentification est centralisée ?**

<details><summary>Voir le corrigé</summary>

Pour pouvoir se connecter **si le serveur AAA est injoignable** — justement pendant une panne réseau, quand on a le plus besoin d’accéder aux équipements. Ce compte de secours a un mot de passe fort, stocké dans un coffre, et son usage est surveillé.

</details>

<!-- approfondir -->

## AAA sur un équipement Cisco

```cisco
aaa new-model
!
tacacs server ISE-1
 address ipv4 10.99.0.80
 key Une-Cle-Longue-Et-Unique
tacacs server ISE-2
 address ipv4 10.99.1.80
 key Une-Cle-Longue-Et-Unique
aaa group server tacacs+ ADMIN-AAA
 server name ISE-1
 server name ISE-2
 ip tacacs source-interface Loopback0
!
aaa authentication login default group ADMIN-AAA local
aaa authorization exec default group ADMIN-AAA local if-authenticated
aaa authorization commands 15 default group ADMIN-AAA local if-authenticated
aaa accounting exec default start-stop group ADMIN-AAA
aaa accounting commands 15 default start-stop group ADMIN-AAA
!
username secours privilege 15 algorithm-type scrypt secret Mot-De-Passe-Coffre
```

Lecture de `group ADMIN-AAA local` : essayer d’abord les serveurs TACACS+ ; **seulement s’ils ne répondent pas**, utiliser les comptes locaux. Si le serveur répond « refusé », on ne passe **pas** au compte local.

> [!CAUTION]
> `aaa new-model` change immédiatement la façon dont les connexions sont authentifiées. Configure-le avec une session console ou une session ouverte de secours, et teste une nouvelle connexion **avant** de fermer la tienne.

## Le moindre privilège

| Profil | Droits typiques |
|---|---|
| Support niveau 1 | `show` seulement, sur les switches d’accès |
| Administrateur réseau | configuration des switches et routeurs, hors sécurité |
| Ingénieur sécurité | pare-feu, ACL, AAA |
| Compte de service (sauvegarde, supervision) | lecture seule, depuis une adresse précise |

L’autorisation par commande (TACACS+) permet d’aller très finement : autoriser `interface`, `shutdown`, `switchport access vlan`, mais pas `no aaa` ni `crypto key zeroize`.

## Exercices

**1.** Le serveur TACACS+ est joignable mais refuse le compte de bruno (mot de passe expiré). Bruno a aussi un compte local identique. Peut-il se connecter avec `aaa authentication login default group ADMIN-AAA local` ?

<details><summary>Voir le corrigé</summary>

**Non.** La méthode suivante (`local`) n’est utilisée que si le serveur **ne répond pas**. Un refus explicite (*REJECT*) arrête le processus. C’est voulu : sinon, un compte désactivé dans l’annuaire resterait utilisable localement.

</details>

**2.** Pourquoi les traces de l’accounting doivent-elles être stockées hors des équipements ?

<details><summary>Voir le corrigé</summary>

Un administrateur malveillant ou un attaquant pourrait **effacer** les traces stockées sur l’équipement qu’il a modifié, et un redémarrage les ferait disparaître. Centralisées sur le serveur AAA (et dans le SIEM), elles restent disponibles pour l’enquête.

</details>
