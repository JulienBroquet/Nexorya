---
titre: DNS
nom: Domain Name System
idee: Le DNS est l’annuaire d’Internet — il traduit un nom comme www.exemple.fr en adresse IP, en interrogeant une hiérarchie de serveurs de la racine jusqu’au serveur qui fait autorité.
osi: "7 (UDP et TCP 53)"
duree: [10, 22]
prerequis: [adresses, udp]
retenir:
  - Le poste interroge un **résolveur**, qui remonte la hiérarchie **racine → TLD → domaine** et met la réponse en **cache**.
  - "Enregistrements clés — **A** (IPv4), **AAAA** (IPv6), **CNAME** (alias), **MX** (messagerie), **PTR** (inverse), **TXT**, **NS**."
  - Le **TTL** fixe la durée du cache — à baisser **avant** un changement d’adresse.
  - "Symptôme typique — le service répond par **adresse IP** mais pas par **nom**."
---

## Le problème : retenir des milliards d’adresses

Personne ne retient `142.250.201.68`. Et si l’adresse d’un serveur change, il faudrait prévenir tous ses utilisateurs. Il faut un **annuaire** qui associe des noms faciles à retenir aux adresses, mis à jour en un seul endroit, et capable de répondre à des milliards de questions par jour.

> [!IMPORTANT] L’idée en une phrase
> Le DNS traduit les noms en adresses IP. Aucune machine ne connaît tous les noms : chacune connaît sa partie, et sait à qui demander pour le reste.

## La hiérarchie des noms

Un nom se lit **de droite à gauche** :

```text
www  .  exemple  .  fr  .
 │        │        │   └── la racine (le point final, souvent omis)
 │        │        └────── domaine de premier niveau (TLD) : fr, com, org…
 │        └─────────────── domaine : exemple.fr
 └──────────────────────── nom d’une machine ou d’un service dans ce domaine
```

Chaque niveau **délègue** le niveau suivant : la racine sait qui gère `.fr`, le serveur de `.fr` sait qui gère `exemple.fr`, et le serveur d’`exemple.fr` connaît `www.exemple.fr`.

## Comment une question est résolue

```sequence
titre: Résolution de www.exemple.fr
Poste | Résolveur | Racine | Serveur .fr | Serveur exemple.fr
Poste -> Résolveur : « adresse de www.exemple.fr ? »
Résolveur -> Racine : www.exemple.fr ?
Racine --> Résolveur : « demande aux serveurs de .fr »
Résolveur -> Serveur .fr : www.exemple.fr ?
Serveur .fr --> Résolveur : « demande aux serveurs d’exemple.fr »
Résolveur -> Serveur exemple.fr : www.exemple.fr ?
Serveur exemple.fr --> Résolveur : « 203.0.113.10, valable 1 heure »
Résolveur --> Poste : 203.0.113.10 (mis en cache 1 heure)
```

- Le **poste** pose une seule question à son **résolveur** (le serveur DNS de l’entreprise ou du fournisseur d’accès).
- Le **résolveur** fait tout le travail, puis garde la réponse en **cache** pendant la durée indiquée (le **TTL**). Les questions suivantes sont servies immédiatement.
- Le serveur d’`exemple.fr` **fait autorité** : c’est lui qui détient la vraie réponse.

## Les types d’enregistrements

| Type | Rôle | Exemple |
|---|---|---|
| **A** | nom → adresse IPv4 | `www.exemple.fr → 203.0.113.10` |
| **AAAA** | nom → adresse IPv6 | `www.exemple.fr → 2001:db8::10` |
| **CNAME** | alias vers un autre nom | `intranet → srv-web01.exemple.fr` |
| **MX** | serveur de messagerie du domaine | `exemple.fr → 10 mx1.exemple.fr` |
| **PTR** | adresse → nom (résolution inverse) | `10.113.0.203.in-addr.arpa → www.exemple.fr` |
| **NS** | serveurs qui font autorité pour un domaine | `exemple.fr → ns1.exemple.fr` |
| **TXT** | texte libre : vérifications, politiques anti-usurpation d’e-mails (SPF, DMARC) | `"v=spf1 mx -all"` |
| **SRV** | emplacement d’un service | `_ldap._tcp.exemple.fr → dc1.exemple.fr:389` |

## Exemple : l’ERP joignable par IP mais pas par nom

Un utilisateur ouvre `http://10.20.0.15` : l’ERP s’affiche. Avec `http://erp.exemple.fr`, rien. Le réseau et le serveur fonctionnent ; c’est la **traduction du nom** qui échoue. On vérifie la configuration DNS du poste, puis on interroge le résolveur :

```powershell
C:\> nslookup erp.exemple.fr
Serveur :   dns1.exemple.fr
Address:    10.99.0.53
*** dns1.exemple.fr ne parvient pas à trouver erp.exemple.fr : Non-existent domain
```

« Non-existent domain » : l’enregistrement n’existe pas (ou a été supprimé) dans la zone. Il faut le créer sur le serveur qui fait autorité.

## Les mots à connaître

- **DNS** — *Domain Name System*, système de traduction des noms de domaine en adresses IP.
- **Résolveur** — Serveur DNS qui interroge la hiérarchie pour le compte des postes et met les réponses en cache.
- **Serveur faisant autorité** — Serveur qui détient la zone d’un domaine et donne les réponses officielles.
- **Zone** — Ensemble des enregistrements d’un domaine gérés par un serveur faisant autorité.
- **TTL (DNS)** — Durée pendant laquelle une réponse peut être gardée en cache.
- **Enregistrement** — Ligne d’une zone DNS : un nom, un type (A, MX…) et une valeur.

## Teste-toi

**1.** Tu changes l’adresse IP d’un site Web, mais une partie des utilisateurs arrive encore sur l’ancien serveur pendant des heures. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Les résolveurs gardent l’ancienne réponse **en cache** jusqu’à l’expiration de son **TTL**. Si le TTL était de 24 heures, certains utilisateurs verront l’ancienne adresse pendant 24 heures. Avant un changement, on **baisse le TTL** (par exemple à 300 s) un ou deux jours à l’avance.

</details>

**2.** Quel enregistrement indique à quel serveur envoyer les e-mails destinés à `@exemple.fr` ?

<details><summary>Voir le corrigé</summary>

L’enregistrement **MX** du domaine `exemple.fr`. Il désigne un ou plusieurs serveurs de messagerie, avec une priorité (le plus petit nombre est essayé en premier).

</details>

<!-- approfondir -->

## Récursif et itératif

- Le poste envoie une requête **récursive** : « trouve-moi la réponse finale ».
- Le résolveur envoie des requêtes **itératives** : chaque serveur répond par la réponse ou par une **délégation** (« demande à tel serveur »).
- Un serveur faisant autorité ne devrait **pas** accepter de requêtes récursives venant d’Internet (*open resolver*) : il serait utilisé pour des attaques par amplification.

## Le transport

- Les requêtes passent en **UDP 53**. Si la réponse est trop grande (DNSSEC, nombreux enregistrements), le serveur répond avec le drapeau **TC** (tronqué) et le client recommence en **TCP 53**. Bloquer TCP 53 provoque donc des échecs **aléatoires**, sur les grosses réponses seulement.
- **EDNS(0)** permet des réponses UDP plus grandes que 512 octets ; la valeur recommandée aujourd’hui est d’environ 1 232 octets, pour éviter la fragmentation.
- Les **transferts de zone** entre serveurs (AXFR, IXFR) utilisent TCP 53 et doivent être limités aux serveurs secondaires autorisés.

## Lire une zone

```text
$ORIGIN exemple.fr.
$TTL 3600
@        IN SOA  ns1.exemple.fr. hostmaster.exemple.fr. (
                 2026111501 ; numéro de série (date + compteur)
                 7200       ; refresh : les secondaires vérifient toutes les 2 h
                 900        ; retry
                 1209600    ; expire : 14 jours sans contact, la zone n'est plus servie
                 300 )      ; TTL des réponses négatives (NXDOMAIN)
@        IN NS   ns1.exemple.fr.
@        IN NS   ns2.exemple.fr.
@        IN MX   10 mx1.exemple.fr.
www      IN A    203.0.113.10
www      IN AAAA 2001:db8::10
intranet IN CNAME srv-web01.exemple.fr.
```

> [!WARNING]
> Oublier d’augmenter le **numéro de série** après une modification empêche les serveurs secondaires de se mettre à jour : ils continuent de servir l’ancienne version, et seuls certains utilisateurs voient le changement.

## Les outils

```bash
$ dig www.exemple.fr A +noall +answer
www.exemple.fr.   3412  IN  A  203.0.113.10       # 3412 = TTL restant dans le cache
$ dig @ns1.exemple.fr www.exemple.fr +norecurse     # interroger directement le serveur qui fait autorité
$ dig +trace www.exemple.fr                         # suivre toute la chaîne de délégations
$ dig -x 203.0.113.10                               # résolution inverse (PTR)
```

```powershell
PS> Resolve-DnsName www.exemple.fr -Type AAAA
PS> Resolve-DnsName www.exemple.fr -Server 10.99.0.53 -DnsOnly
PS> Get-DnsClientCache | Where-Object Entry -like "*exemple*"
PS> Clear-DnsClientCache          # équivalent de ipconfig /flushdns
```

## Les réponses à reconnaître

| Code | Signification | Pistes |
|---|---|---|
| NOERROR avec réponse | tout va bien | — |
| **NXDOMAIN** | le nom n’existe pas | faute de frappe, enregistrement absent, mauvais suffixe |
| NOERROR sans réponse (*NODATA*) | le nom existe, mais pas ce type | par exemple un A existe mais pas d’AAAA |
| **SERVFAIL** | le résolveur n’a pas pu obtenir de réponse | serveur faisant autorité injoignable, échec de validation DNSSEC |
| REFUSED | le serveur refuse de répondre | récursion non autorisée pour ce client |
| délai d’attente | aucune réponse | serveur injoignable, UDP 53 filtré |

## DNS interne et DNS public

Une entreprise a souvent deux vues du même domaine (*split DNS*) : en interne, `intranet.exemple.fr` pointe vers `10.20.0.15` ; depuis Internet, le nom n’existe pas ou pointe vers un portail public. Les postes en VPN doivent utiliser le DNS interne, sinon ils reçoivent la réponse publique. C’est une cause fréquente de « ça marche au bureau mais pas en télétravail ».

La sécurisation du DNS (DNSSEC, chiffrement, filtrage) est détaillée dans [DNS approfondi](dns-avance.md).

## Exercices

**1.** `nslookup erp.exemple.fr` renvoie la bonne adresse depuis le bureau, mais pas depuis un poste en télétravail connecté au VPN, qui obtient « Non-existent domain ». Quelle hypothèse ?

<details><summary>Voir le corrigé</summary>

Le poste en VPN interroge un **résolveur public** (celui de sa box) au lieu du DNS interne : le nom n’existe que dans la vue **interne**. Vérifier la configuration DNS poussée par le VPN (serveurs et domaines de recherche) et la règle qui envoie les requêtes `*.exemple.fr` vers le DNS interne.

</details>

**2.** Un domaine fonctionne pour la plupart des utilisateurs, mais certaines résolutions de noms avec beaucoup d’enregistrements échouent. Le pare-feu autorise UDP 53 uniquement. Explique.

<details><summary>Voir le corrigé</summary>

Les grosses réponses sont **tronquées** en UDP (drapeau TC) ; le client recommence en **TCP 53**, qui est bloqué. Seules les grosses réponses échouent. Il faut autoriser **TCP 53** vers les résolveurs.

</details>

**3.** On veut migrer `www.exemple.fr` vers un nouveau serveur vendredi à 20 h, avec le moins de coupure possible. Le TTL actuel est de 86 400 s. Que fais-tu, et quand ?

<details><summary>Voir le corrigé</summary>

**Au moins 24 heures avant** (le TTL actuel), baisser le TTL de l’enregistrement à **300 s** et incrémenter le numéro de série. Vendredi à 20 h, changer l’adresse : en 5 minutes, tous les caches auront expiré. Une fois la migration validée, remonter le TTL.

</details>
