---
titre: HTTPS
nom: HTTP protégé par TLS
idee: HTTPS, c’est HTTP transporté dans une connexion TLS, sur le port 443 ; le cadenas du navigateur signifie que la connexion est chiffrée et que le serveur a prouvé son identité.
osi: "7 (TCP 443, ou UDP 443 avec HTTP/3)"
duree: [6, 12]
prerequis: [http, tls]
retenir:
  - HTTPS = **HTTP dans TLS**, port **443**.
  - "Le cadenas garantit — connexion **chiffrée** et serveur **authentifié** ; pas que le site soit honnête."
  - "On redirige systématiquement HTTP vers HTTPS, et l’on active **HSTS**."
  - Les certificats publics durent désormais quelques mois — leur **renouvellement automatique** (ACME) est indispensable.
---

## Le problème

HTTP circule **en clair** : mots de passe, cookies de session, contenu des pages sont lisibles et modifiables par n’importe qui sur le chemin. Aujourd’hui, aucun site — même une simple vitrine — ne devrait être servi en HTTP.

> [!IMPORTANT] L’idée en une phrase
> HTTPS ouvre d’abord une connexion [TLS](tls.md), puis fait passer les échanges [HTTP](http.md) à l’intérieur. Pour un observateur, on ne voit plus que l’adresse du serveur et, souvent, le nom du site.

## Ce que garantit le cadenas… et ce qu’il ne garantit pas

| Garanti | Pas garanti |
|---|---|
| Personne sur le chemin ne peut lire ni modifier les échanges | que le site soit légitime : un site d’hameçonnage peut avoir un certificat valide pour **son propre** nom |
| Le serveur possède un certificat valide **pour le nom affiché** | que le serveur lui-même soit sûr |

> [!WARNING]
> « Il y a un cadenas, donc c’est sûr » est une idée fausse exploitée par les hameçonneurs. Le cadenas prouve que tu parles **en privé** à `banque-securite-verif.com` — pas que ce soit ta banque.

## Passer un site en HTTPS

1. Obtenir un certificat (autorité publique comme Let’s Encrypt pour un site public ; autorité interne pour un intranet).
2. Configurer le serveur Web avec le certificat et sa **chaîne complète**.
3. **Rediriger** toutes les requêtes `http://` vers `https://` (code 301).
4. Activer **HSTS** pour que les navigateurs n’essaient plus jamais HTTP sur ce site.
5. **Automatiser** le renouvellement.

## Les mots à connaître

- **HTTPS** — HTTP sécurisé par TLS, sur le port 443.
- **HSTS** — *HTTP Strict Transport Security*, en-tête qui oblige le navigateur à n’utiliser que HTTPS pour un site.
- **ACME** — Protocole de délivrance et de renouvellement automatique de certificats (utilisé par Let’s Encrypt).

## Teste-toi

**Un site d’hameçonnage affiche un cadenas. Le certificat est-il forcément faux ?**

<details><summary>Voir le corrigé</summary>

**Non.** Le site peut avoir obtenu un certificat parfaitement valide pour **son propre nom de domaine** (qui ressemble à celui de la vraie banque). Le cadenas prouve seulement le chiffrement et l’identité du nom affiché, pas l’honnêteté du site.

</details>

<!-- approfondir -->

## Configuration type (nginx)

```text
server {
    listen 80;
    server_name www.exemple.fr exemple.fr;
    return 301 https://www.exemple.fr$request_uri;
}
server {
    listen 443 ssl;
    http2 on;
    server_name www.exemple.fr;
    ssl_certificate     /etc/ssl/exemple/fullchain.pem;   # certificat + intermédiaires
    ssl_certificate_key /etc/ssl/exemple/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

## Durée de vie des certificats

Les navigateurs ont décidé de raccourcir fortement la durée de vie maximale des certificats publics : elle diminue par étapes depuis 2026, jusqu’à environ 47 jours à l’horizon 2029. Un renouvellement manuel n’est plus tenable : on utilise un client **ACME** (certbot, acme.sh, intégration du serveur ou du reverse proxy) et l’on **supervise** les dates d’expiration.

## Quelques vérifications

```bash
$ curl -sI https://www.exemple.fr | grep -i strict
strict-transport-security: max-age=31536000; includeSubDomains
$ echo | openssl s_client -connect www.exemple.fr:443 -servername www.exemple.fr 2>/dev/null | openssl x509 -noout -enddate
notAfter=Feb 12 08:12:00 2027 GMT
```

## Exercice

**On active HSTS avec `includeSubDomains` sur `exemple.fr`. Un vieux serveur `ged.exemple.fr` n’a qu’un accès HTTP. Que se passe-t-il pour les utilisateurs ?**

<details><summary>Voir le corrigé</summary>

Les navigateurs qui ont reçu l’en-tête HSTS **refusent** désormais toute connexion HTTP à `ged.exemple.fr` et tentent HTTPS, qui échoue : le service devient inaccessible, sans possibilité de contourner l’avertissement. Avant d’activer `includeSubDomains`, il faut s’assurer que **tous** les sous-domaines sont servis en HTTPS.

</details>
