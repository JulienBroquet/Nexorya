---
titre: Proxy et répartiteur de charge
nom: Proxy, reverse proxy et load balancer
idee: Un proxy fait les requêtes à la place des postes pour les contrôler ; un reverse proxy reçoit les requêtes à la place des serveurs pour les protéger et répartir la charge entre eux.
osi: "4 à 7"
duree: [8, 18]
cle: true
prerequis: [http, tls]
retenir:
  - "**Proxy** (direct) — côté utilisateurs, il sort sur Internet à leur place (filtrage, journalisation, cache)."
  - "**Reverse proxy** — côté serveurs, il reçoit les requêtes d’Internet et les transmet aux serveurs internes."
  - "Un **load balancer** répartit les requêtes entre plusieurs serveurs et retire ceux qui ne répondent plus (**sondes de santé**)."
  - "Derrière un reverse proxy, le serveur voit l’adresse du proxy — l’adresse du client est dans **X-Forwarded-For**."
---

## Le problème

Deux besoins différents, une même idée :

- **Côté utilisateurs**, l’entreprise veut contrôler la navigation : bloquer des catégories de sites, analyser les téléchargements, journaliser.
- **Côté serveurs**, un site très fréquenté a besoin de **plusieurs** serveurs, sans que l’utilisateur le sache, et l’on veut les protéger d’un accès direct depuis Internet.

> [!IMPORTANT] L’idée en une phrase
> Un proxy est un intermédiaire qui termine la connexion d’un côté et en ouvre une nouvelle de l’autre : il peut donc observer, filtrer, transformer et répartir.

## Proxy direct et reverse proxy

```topologie
titre: Proxy côté utilisateurs, reverse proxy côté serveurs
U pc 0,0 "Postes"
PX serveur 1.3,0 "Proxy" "filtrage Web"
NET nuage 2.6,0.5 "Internet"
RP serveur 3.9,1 "Reverse proxy" "load balancer"
S1 serveur 5.2,0.5 "Serveur Web 1"
S2 serveur 5.2,1.5 "Serveur Web 2"
C portable 1.3,1 "Client externe"
U -- PX
PX -- NET
C -- NET
NET -- RP
RP ++ S1
RP ++ S2
```

| | Proxy (direct) | Reverse proxy |
|---|---|---|
| Placé devant… | les **utilisateurs** | les **serveurs** |
| Qui le configure ? | les postes (ou le réseau, en mode transparent) | personne : le nom du site pointe vers lui |
| Rôle | filtrer, journaliser, mettre en cache la navigation | publier, protéger, répartir, terminer TLS |

## Le répartiteur de charge

Un **load balancer** est un reverse proxy spécialisé. Il :

1. reçoit les requêtes sur une **adresse virtuelle** (VIP), celle que pointe le DNS du site ;
2. choisit un serveur parmi un **groupe** (*pool*), selon une méthode (à tour de rôle, le moins chargé…) ;
3. vérifie en permanence la **santé** de chaque serveur (une requête de test toutes les quelques secondes) et retire ceux qui échouent ;
4. peut garder un même utilisateur sur le même serveur (**persistance**), si l’application l’exige.

## Les mots à connaître

- **Proxy** — Intermédiaire qui effectue les requêtes des utilisateurs vers Internet.
- **Reverse proxy** — Intermédiaire placé devant des serveurs, qui reçoit les requêtes à leur place.
- **Load balancer** — Équipement ou logiciel qui répartit les requêtes entre plusieurs serveurs.
- **VIP** — Adresse IP virtuelle sur laquelle le répartiteur reçoit les requêtes.
- **Sonde de santé** — Test régulier qui vérifie qu’un serveur répond correctement ; *health check*.
- **Persistance** — Maintien d’un utilisateur sur le même serveur pendant sa session.

## Teste-toi

**Un site est servi par deux serveurs derrière un load balancer. Le serveur 2 tombe en panne. Que voient les utilisateurs ?**

<details><summary>Voir le corrigé</summary>

Si les **sondes de santé** sont bien configurées, le répartiteur retire le serveur 2 en quelques secondes : les utilisateurs ne voient presque rien (ceux qui étaient sur le serveur 2 peuvent perdre leur session si elle n’est pas partagée). Sans sonde, une requête sur deux échouerait.

</details>

<!-- approfondir -->

## Niveau 4 ou niveau 7 ?

| Répartition | Ce que voit l’équipement | Possibilités |
|---|---|---|
| **Niveau 4** (TCP/UDP) | adresses et ports | très rapide ; pas de lecture du contenu ; TLS traversé tel quel |
| **Niveau 7** (HTTP) | URL, en-têtes, cookies | routage selon le chemin (`/api` vers un groupe, `/images` vers un autre), réécriture, compression, WAF, **terminaison TLS** |

## Configuration type (HAProxy)

```text
frontend site_public
    bind :443 ssl crt /etc/haproxy/certs/www.exemple.fr.pem alpn h2,http/1.1
    http-request redirect scheme https unless { ssl_fc }
    default_backend web

backend web
    balance leastconn
    option httpchk GET /sante
    http-check expect status 200
    http-request set-header X-Forwarded-Proto https
    option forwardfor                       # ajoute X-Forwarded-For
    server web1 10.20.0.11:8080 check inter 3s fall 3 rise 2
    server web2 10.20.0.12:8080 check inter 3s fall 3 rise 2
```

- `check inter 3s fall 3 rise 2` : une sonde toutes les 3 s ; retiré après 3 échecs, réintégré après 2 succès.
- La sonde vise une page `/sante` qui vérifie réellement l’application (base de données comprise), pas seulement que le serveur Web tourne.

## Les pièges classiques

| Symptôme | Cause |
|---|---|
| Les journaux du serveur ne montrent que l’adresse du proxy | lire `X-Forwarded-For` (et ne lui faire confiance que s’il vient du proxy) |
| L’application génère des liens en `http://` | elle ne sait pas que le client est en HTTPS : transmettre `X-Forwarded-Proto` |
| Les utilisateurs sont déconnectés au hasard | sessions stockées localement sur chaque serveur, sans persistance ni stockage partagé |
| 502/504 sur certains appels longs | délais d’attente du proxy plus courts que le temps de traitement |
| Le serveur répond, mais pas au load balancer | retour asymétrique : la passerelle du serveur n’est pas le load balancer en mode routé |

## Proxy direct : explicite ou transparent

- **Explicite** : les navigateurs sont configurés (manuellement, par GPO, par fichier PAC ou WPAD) pour envoyer leurs requêtes au proxy, sur le port 3128 ou 8080. Pour HTTPS, le navigateur demande un tunnel avec la méthode `CONNECT`.
- **Transparent** : le réseau redirige le trafic Web vers le proxy sans configuration des postes ; plus simple à déployer, plus délicat avec HTTPS.

Aujourd’hui, le filtrage Web est souvent assuré par un **service cloud** (SWG, SSE) plutôt que par un proxy installé dans l’entreprise.

## Exercices

**1.** Un groupe de deux serveurs est sondé par une requête TCP sur le port 8080. L’application du serveur 1 renvoie des erreurs 500, mais il reste dans le groupe. Pourquoi, et que corriger ?

<details><summary>Voir le corrigé</summary>

Une sonde **TCP** ne vérifie que l’ouverture du port : le serveur Web écoute, donc il est jugé sain, même si l’application échoue. Utiliser une sonde **HTTP** sur une page de santé qui teste réellement l’application, et attendre un code 200.

</details>

**2.** Les administrateurs d’une application ont bloqué les adresses de quelques utilisateurs, mais le blocage ne fonctionne pas depuis que le site est derrière un reverse proxy. Expliquer.

<details><summary>Voir le corrigé</summary>

Le serveur voit **toutes** les connexions venir de l’adresse du reverse proxy. Les règles fondées sur l’adresse source doivent soit être appliquées **sur le proxy**, soit lire l’en-tête `X-Forwarded-For` côté serveur (en ne faisant confiance qu’au proxy pour cet en-tête).

</details>
