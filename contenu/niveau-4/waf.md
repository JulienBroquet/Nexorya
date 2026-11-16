---
titre: WAF
nom: Pare-feu applicatif Web
idee: Un WAF se place devant une application Web et bloque les requêtes malveillantes — injections SQL, scripts, accès anormaux — avant qu’elles n’atteignent le serveur.
osi: "7"
duree: [5, 10]
prerequis: [http, proxy]
retenir:
  - "Le WAF protège **une application Web** ; il comprend HTTP en détail (URL, paramètres, en-têtes, cookies)."
  - "Il bloque les attaques classiques — **injection SQL**, **XSS**, exploitation de vulnérabilités connues, robots abusifs."
  - Il complète, mais ne remplace pas, le **développement sécurisé** et les mises à jour.
---

## Le problème

Un portail client est publié sur Internet. Il reçoit chaque jour des requêtes piégées : un champ « nom » qui contient du code SQL pour lire toute la base de données, un commentaire qui contient un script pour voler les sessions des autres visiteurs. Le pare-feu réseau laisse tout passer : c’est du HTTPS vers le port 443, parfaitement autorisé.

> [!IMPORTANT] L’idée en une phrase
> Le WAF lit chaque requête HTTP comme le ferait l’application, et rejette celles qui ressemblent à une attaque.

```topologie
titre: Le WAF examine les requêtes avant le serveur Web
U utilisateur 0,0 "Visiteurs"
A utilisateur 0,1.2 "Attaquant" "injection SQL"
WAF parefeu 1.8,0.6 "WAF" "analyse HTTP"
WEB serveur 3.6,0.6 "Application Web"
U -- WAF "requêtes normales"
A -x- WAF "bloquée"
WAF ++ WEB "seulement le trafic sain"
```

## Exemple

```text
GET /clients?nom=Dupont' OR '1'='1 HTTP/1.1
Host: portail.exemple.fr
```

Un WAF reconnaît le motif d’**injection SQL** (`' OR '1'='1`) et renvoie un refus (403), sans transmettre la requête au serveur.

## Les mots à connaître

- **WAF** — *Web Application Firewall*, filtre qui protège une application Web au niveau HTTP.
- **Injection SQL** — Attaque qui glisse des commandes de base de données dans un champ de saisie.
- **XSS** — *Cross-Site Scripting*, attaque qui injecte un script exécuté dans le navigateur des autres utilisateurs.
- **Patch virtuel** — Règle WAF qui bloque l’exploitation d’une vulnérabilité en attendant la correction de l’application.

## Teste-toi

**Pourquoi un pare-feu réseau classique ne voit-il pas une injection SQL ?**

<details><summary>Voir le corrigé</summary>

Il ne regarde que les adresses, les ports et éventuellement l’application (HTTPS), et le trafic est **chiffré**. L’attaque se trouve dans le **contenu** de la requête HTTP déchiffrée. Seul un équipement qui termine TLS et lit HTTP (WAF, reverse proxy) peut la reconnaître.

</details>

<!-- approfondir -->

## Où placer un WAF

- **Intégré au reverse proxy ou au répartiteur de charge** (ModSecurity, modules des load balancers commerciaux).
- **Service cloud** devant le site (qui absorbe aussi les attaques par déni de service).
- **Dans le pare-feu NGFW**, pour des besoins simples.

Dans tous les cas, il doit **voir le trafic en clair** : il termine TLS lui-même, ou reçoit le trafic déchiffré.

## Règles et réglage

- Les jeux de règles génériques (comme l’**OWASP Core Rule Set**) couvrent les attaques classiques.
- On démarre en mode **détection**, on analyse les faux positifs (un champ « commentaire » qui contient légitimement des apostrophes), on crée des exceptions **précises**, puis on passe en **blocage**.
- Le **patch virtuel** permet de bloquer l’exploitation d’une faille publiée le jour même, en attendant la mise à jour de l’application.

## Exercice

**Après l’activation du WAF en blocage, les clients ne peuvent plus enregistrer de commentaires contenant le mot « select ». Que faire ?**

<details><summary>Voir le corrigé</summary>

C’est un **faux positif** de la règle d’injection SQL. Créer une exception **ciblée** : désactiver cette règle uniquement pour le paramètre « commentaire » de cette page, plutôt que pour tout le site. Vérifier en parallèle que l’application utilise bien des requêtes paramétrées (vraie protection contre l’injection).

</details>
