---
titre: DNS approfondi
nom: DNSSEC, filtrage, redondance et attaques
idee: Le DNS est un point critique — s’il tombe, plus rien ne marche ; s’il ment, les utilisateurs partent au mauvais endroit. On le rend redondant, on le signe (DNSSEC) et on s’en sert pour filtrer les menaces.
osi: "7"
duree: [8, 18]
cle: true
prerequis: [dns]
retenir:
  - Toujours **au moins deux** résolveurs et deux serveurs faisant autorité, sur des sites ou des réseaux différents.
  - "**DNSSEC** prouve que les réponses n’ont pas été falsifiées — il ne les **chiffre** pas."
  - "Chiffrer les requêtes — **DoT** (TLS) ou **DoH** (HTTPS) ; cela protège la vie privée, mais peut contourner le DNS de l’entreprise."
  - Le DNS sert aussi de **capteur de sécurité** — les journaux de requêtes révèlent les machines infectées.
---

## Le problème : tout dépend du DNS

Avant presque chaque connexion — un site, la messagerie, l’ouverture de session Windows, une application dans le cloud —, il y a une question DNS. Si les résolveurs tombent, « plus rien ne marche », même si le réseau va parfaitement bien. Et si un attaquant peut **falsifier** une réponse, il envoie les utilisateurs vers un faux site sans qu’ils s’en aperçoivent.

> [!IMPORTANT] L’idée en une phrase
> On rend le DNS **redondant** pour qu’il ne tombe jamais, **vérifiable** (DNSSEC) pour qu’on ne puisse pas lui faire mentir, et **observable** pour détecter les menaces.

## Trois risques, trois réponses

| Risque | Exemple | Réponse |
|---|---|---|
| **Panne** | le seul serveur DNS redémarre : toute l’entreprise est bloquée | deux résolveurs au minimum, sur des équipements et sites distincts |
| **Falsification** | un attaquant injecte une fausse adresse pour `banque.fr` dans un cache | **DNSSEC** : les réponses sont signées et vérifiées |
| **Espionnage** | sur un Wi-Fi public, quelqu’un lit tous les noms consultés | requêtes chiffrées : **DoT** ou **DoH** |

## Le DNS au service de la sécurité

Un logiciel malveillant installé sur un poste doit contacter son **serveur de commande**. Il commence presque toujours par une question DNS. Un résolveur d’entreprise peut donc :

- **bloquer** les domaines malveillants connus (listes de réputation, *RPZ*) ;
- **journaliser** les requêtes pour repérer un poste qui interroge des noms suspects ;
- **détecter** des usages anormaux (des milliers de noms aléatoires, des enregistrements TXT géants : signes de tunnels DNS).

## Les mots à connaître

- **DNSSEC** — Extensions de sécurité qui signent les données DNS pour en garantir l’authenticité.
- **Empoisonnement de cache** — Attaque qui insère une fausse réponse dans le cache d’un résolveur.
- **DoT / DoH** — DNS sur TLS (port 853) / DNS sur HTTPS (port 443) : requêtes DNS chiffrées.
- **RPZ** — *Response Policy Zone*, liste de règles qui permet à un résolveur de bloquer ou réécrire certains noms.

## Teste-toi

**DNSSEC empêche-t-il un observateur de voir quels sites tu consultes ?**

<details><summary>Voir le corrigé</summary>

**Non.** DNSSEC **signe** les réponses pour prouver qu’elles sont authentiques, mais elles circulent **en clair**. Pour cacher les noms consultés, il faut chiffrer les requêtes (DoT, DoH).

</details>

<!-- approfondir -->

## DNSSEC en pratique

- Chaque zone signée publie des clés (**DNSKEY**) et des signatures (**RRSIG**) pour ses enregistrements.
- Le domaine parent publie une empreinte de la clé de l’enfant (**DS**) : on construit ainsi une **chaîne de confiance** de la racine jusqu’au domaine.
- Le **résolveur validant** vérifie toute la chaîne. Si une signature est fausse ou expirée, il renvoie **SERVFAIL** : l’utilisateur n’obtient pas de réponse plutôt qu’une réponse falsifiée.

```bash
$ dig exemple.fr A +dnssec +multi
;; flags: qr rd ra ad;           # "ad" = Authenticated Data : réponse validée
$ delv @1.1.1.1 exemple.fr       # outil de validation détaillée
```

> [!CAUTION]
> Une signature **expirée** (renouvellement automatique en panne) rend le domaine injoignable pour tous les utilisateurs de résolveurs validants, c’est-à-dire une grande partie d’Internet. Superviser l’échéance des signatures est aussi important que superviser un certificat TLS.

## Résolveurs d’entreprise : architecture type

```topologie
titre: Résolveurs internes redondants et sortie contrôlée
PC pc 0,1 "Postes"
R1 serveur 1.5,0.5 "Résolveur 1" "site A"
R2 serveur 1.5,1.5 "Résolveur 2" "site B"
AD serveur 3,0 "DNS Active Directory" "zones internes"
FW parefeu 3,1.5 "Pare-feu"
NET nuage 4.5,1.5 "Internet"
PC -- R1
PC -- R2
R1 -- AD "zones internes"
R2 -- AD
R1 -- FW
R2 -- FW "seuls les résolveurs sortent en 53"
FW -- NET
```

- Les postes reçoivent **deux** résolveurs par DHCP.
- Les résolveurs transmettent les zones internes aux serveurs Active Directory (ou aux serveurs de zone), et le reste à Internet (directement ou via un service de filtrage).
- Le pare-feu **interdit le DNS sortant** (UDP/TCP 53, et TCP 853 pour DoT) à tout autre équipement : les postes ne peuvent pas contourner le filtrage.

## DoH : le casse-tête de l’entreprise

DoH envoie les requêtes DNS dans du **HTTPS ordinaire** vers un service public. C’est excellent pour la vie privée sur un Wi-Fi public, mais en entreprise, un navigateur qui active DoH **contourne** le résolveur interne : plus de filtrage, plus de journaux, et plus d’accès aux noms internes. Les réponses habituelles :

- désactiver DoH par **politique** sur les navigateurs gérés, ou le pointer vers le résolveur de l’entreprise ;
- utiliser le **domaine canari** (`use-application-dns.net`) que Firefox consulte avant d’activer DoH ;
- bloquer les serveurs DoH publics connus au pare-feu. Voir [DoH](../niveau-4/doh.md).

## Les attaques à connaître

| Attaque | Principe | Protection |
|---|---|---|
| Empoisonnement de cache | réponses forgées acceptées par un résolveur | ports source aléatoires, DNSSEC |
| Amplification | petites requêtes avec une source usurpée, grosses réponses vers la victime | pas de résolveur ouvert, limitation de débit (RRL) |
| Tunnel DNS | données exfiltrées dans des noms de requêtes | journaux, détection d’anomalies, limiter le DNS sortant |
| Détournement de domaine | compte du registrar compromis, NS modifiés | MFA chez le registrar, verrouillage du domaine |
| NXDOMAIN massif | requêtes vers des noms aléatoires pour saturer les serveurs | limitation de débit, capacité, filtrage |

## Exercices

**1.** Après une mise à jour, plus personne n’accède à `exemple.fr` depuis certains opérateurs, alors que ça fonctionne depuis l’entreprise. `dig` depuis un résolveur public renvoie SERVFAIL. Quelle piste ?

<details><summary>Voir le corrigé</summary>

Un problème **DNSSEC** : signatures expirées ou enregistrement DS du parent qui ne correspond plus à la clé de la zone (après un changement de clé mal mené). Les résolveurs **validants** refusent la réponse (SERVFAIL) ; le résolveur interne ne valide peut-être pas, d’où la différence. Vérifier avec `delv` ou un outil d’analyse DNSSEC.

</details>

**2.** Le SOC remarque qu’un poste envoie des milliers de requêtes vers des noms comme `a8f3k2…q9.exfil-exemple.net`. Que soupçonner et que faire ?

<details><summary>Voir le corrigé</summary>

Un **tunnel DNS** : des données sont encodées dans les noms et envoyées au serveur qui fait autorité pour ce domaine, contrôlé par l’attaquant. Isoler le poste, bloquer le domaine sur le résolveur (RPZ), vérifier qu’aucun autre poste ne l’interroge, et confirmer que le DNS sortant direct est interdit.

</details>
