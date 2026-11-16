---
titre: HTTP
nom: Hypertext Transfer Protocol
idee: HTTP est le langage du Web — le navigateur envoie une requête (une méthode et une adresse), le serveur répond par un code d’état et un contenu.
osi: "7 (TCP 80 ; 443 avec TLS)"
duree: [8, 18]
prerequis: [tcp, dns]
retenir:
  - "Une requête = **méthode** (GET, POST…) + **chemin** + **en-têtes** (dont `Host`)."
  - "Une réponse = **code d’état** + en-têtes + contenu. 2xx succès, 3xx redirection, 4xx erreur du client, 5xx erreur du serveur."
  - HTTP est **sans état** — les sessions reposent sur des **cookies**.
  - HTTP en clair ne doit plus servir qu’à **rediriger vers HTTPS**.
---

## Le problème : demander une page à un serveur

Le navigateur doit demander « la page d’accueil de ce site », puis l’image du logo, la feuille de style, les scripts… Le serveur doit répondre « voilà », « cette page a déménagé », ou « je n’ai pas trouvé ». Il faut un format de conversation simple et commun à tous les navigateurs et tous les serveurs.

> [!IMPORTANT] L’idée en une phrase
> HTTP est une conversation question-réponse : le client **demande** une ressource avec une méthode et une adresse, le serveur **répond** avec un code d’état et le contenu.

## Une requête et sa réponse

```text
GET /catalogue/index.html HTTP/1.1
Host: www.exemple.fr
User-Agent: Mozilla/5.0 …
Accept: text/html
Cookie: session=8f3a…

HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 18342
Cache-Control: max-age=300

<!doctype html> …
```

- **GET** : la méthode, « donne-moi ».
- **Host** : le nom du site demandé. Un même serveur peut héberger des dizaines de sites : c’est cet en-tête qui les distingue.
- **200 OK** : le code d’état, « voilà ».

## Les codes d’état à connaître

| Code | Signification | Exemple de situation |
|---|---|---|
| **200** | OK | page affichée |
| **301 / 302** | redirection permanente / temporaire | `http://` redirigé vers `https://` |
| **304** | non modifié | le navigateur réutilise sa copie en cache |
| **401** | authentification requise | mot de passe demandé |
| **403** | interdit | droits insuffisants, filtrage |
| **404** | introuvable | lien cassé |
| **500** | erreur interne du serveur | bug applicatif |
| **502 / 504** | passerelle en erreur / délai dépassé | le reverse proxy n’obtient pas de réponse du serveur applicatif |
| **503** | service indisponible | maintenance, surcharge |

> [!TIP]
> Un code 4xx ou 5xx est une **excellente nouvelle pour l’équipe réseau** : il prouve que la connexion est passée et qu’un serveur HTTP a répondu. Le problème est dans l’application, les droits ou la configuration du serveur.

## Les mots à connaître

- **HTTP** — Protocole de requêtes et de réponses utilisé par le Web.
- **Méthode** — Action demandée : GET (lire), POST (envoyer), PUT, DELETE…
- **URL** — Adresse complète d’une ressource : `https://www.exemple.fr/catalogue/index.html`.
- **Code d’état** — Nombre à trois chiffres qui résume le résultat d’une requête.
- **Cookie** — Petite donnée déposée par le serveur et renvoyée par le navigateur à chaque requête, pour maintenir une session.

## Teste-toi

**1.** Un site interne renvoie « 502 Bad Gateway ». Le réseau est-il en cause ?

<details><summary>Voir le corrigé</summary>

**Probablement pas entre l’utilisateur et le site** : un serveur HTTP (en général un **reverse proxy**) a bien répondu. Il signale qu’il n’a pas obtenu de réponse valide du serveur **applicatif** derrière lui. Il faut regarder ce serveur, ou le lien entre le proxy et lui.

</details>

**2.** Pourquoi l’en-tête `Host` est-il indispensable ?

<details><summary>Voir le corrigé</summary>

Parce qu’un même serveur, avec une même adresse IP, héberge souvent plusieurs sites. Seul l’en-tête `Host` indique **quel site** le navigateur demande.

</details>

<!-- approfondir -->

## Les versions

| Version | Transport | Apports |
|---|---|---|
| HTTP/1.1 | TCP | connexions persistantes ; une requête à la fois par connexion (les navigateurs en ouvrent ~6 par site) |
| HTTP/2 | TCP + TLS | **multiplexage** de nombreuses requêtes sur une seule connexion, en-têtes compressés, format binaire |
| HTTP/3 | **QUIC** (UDP 443) | plus de blocage en tête de file dû à TCP, connexion plus rapide, migration de connexion ; voir [QUIC](quic.md) |

## Interroger un serveur à la main

```bash
$ curl -sv https://www.exemple.fr/ -o /dev/null
*   Trying 203.0.113.10:443...
* Connected to www.exemple.fr (203.0.113.10) port 443
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* Server certificate:
*  subject: CN=www.exemple.fr
*  expire date: Feb 12 23:59:59 2027 GMT
> GET / HTTP/2
> Host: www.exemple.fr
< HTTP/2 200
< content-type: text/html; charset=utf-8
< server: nginx
```

Cette seule commande vérifie la **résolution DNS**, la **connexion TCP**, la **négociation TLS** (version, certificat) et la **réponse HTTP**. C’est l’outil de diagnostic le plus efficace pour un service Web.

```bash
$ curl -I http://www.exemple.fr/                       # en-têtes seulement
HTTP/1.1 301 Moved Permanently
Location: https://www.exemple.fr/
$ curl --resolve www.exemple.fr:443:10.20.0.15 https://www.exemple.fr/   # tester un serveur précis
$ curl -w "dns:%{time_namelookup} tcp:%{time_connect} tls:%{time_appconnect} total:%{time_total}\n" -o /dev/null -s https://www.exemple.fr/
```

La dernière commande décompose le temps : DNS, connexion TCP, négociation TLS, réponse complète. Elle indique **quelle étape** est lente.

## En-têtes qui comptent pour l’exploitation

| En-tête | Rôle |
|---|---|
| `Host` | site demandé |
| `X-Forwarded-For` / `Forwarded` | adresse du client réel, ajoutée par un proxy |
| `Cache-Control`, `ETag` | règles de mise en cache |
| `Strict-Transport-Security` | oblige le navigateur à n’utiliser que HTTPS pour ce site (HSTS) |
| `Set-Cookie` (`Secure`, `HttpOnly`, `SameSite`) | protection des cookies de session |
| `Location` | cible d’une redirection |

## Exercices

**1.** Un utilisateur obtient une erreur 403 sur l’intranet, son collègue non. Où chercher ?

<details><summary>Voir le corrigé</summary>

Le serveur a répondu : le réseau fonctionne. Le **403** indique un refus d’autorisation : droits de l’utilisateur (groupe Active Directory), règle d’accès par adresse IP source sur le serveur ou le proxy, ou politique d’un pare-feu applicatif. Comparer les deux utilisateurs et consulter les journaux du serveur.

</details>

**2.** `curl -w` montre `dns:0.004 tcp:0.012 tls:0.031 total:4.870`. Quelle partie est lente ?

<details><summary>Voir le corrigé</summary>

Le DNS (4 ms), le TCP (12 ms) et le TLS (31 ms) sont rapides. Le temps est passé **après** la négociation, à attendre la réponse : c’est le **serveur applicatif** qui met près de 5 secondes à produire la page, pas le réseau.

</details>
