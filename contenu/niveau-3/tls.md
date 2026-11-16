---
titre: TLS
nom: Transport Layer Security
idee: TLS chiffre une connexion et prouve au client qu’il parle au bon serveur, grâce à un certificat signé par une autorité de confiance.
osi: "entre 4 et 7"
duree: [10, 22]
prerequis: [tcp]
retenir:
  - "TLS apporte trois garanties — **confidentialité** (chiffrement), **intégrité** (rien n’a été modifié), **authentification** du serveur (certificat)."
  - "Le certificat doit être **valide** — bon **nom** (SAN), **dates** correctes, **chaîne** jusqu’à une autorité de confiance."
  - Une **horloge** fausse sur le poste ou le serveur suffit à faire échouer TLS.
  - "Versions à utiliser — **TLS 1.2 et 1.3** ; les versions plus anciennes sont à désactiver."
---

## Le problème : parler en secret à un inconnu

Quand tu te connectes à ta banque depuis un café, tes données traversent le Wi-Fi public, la box, plusieurs opérateurs. N’importe qui sur le chemin pourrait les lire ou les modifier. Et comment être sûr que le serveur qui répond est bien celui de ta banque, et pas un imposteur ?

> [!IMPORTANT] L’idée en une phrase
> TLS établit un chiffrement entre le client et le serveur, et le serveur prouve son identité avec un **certificat** signé par une autorité reconnue.

> [!TIP] L’analogie de la carte d’identité
> Le certificat est la carte d’identité du serveur. Elle porte son **nom**, une **date d’expiration**, et elle est **signée par une autorité** (comme l’État pour une carte d’identité). Ton navigateur connaît la liste des autorités de confiance et vérifie la signature, le nom et la date.

## Comment ça marche (TLS 1.3, simplifié)

```sequence
titre: Négociation TLS 1.3
Navigateur | Serveur www.exemple.fr
Navigateur -> Serveur www.exemple.fr : ClientHello : versions et algorithmes acceptés, nom du site (SNI), part de clé
Serveur www.exemple.fr --> Navigateur : ServerHello : choix + part de clé ; certificat ; preuve ; Finished
note Navigateur : vérifie le certificat : nom, dates, signature de l’autorité
Navigateur -> Serveur www.exemple.fr : Finished
Navigateur -> Serveur www.exemple.fr : requêtes HTTP chiffrées
```

1. Le client propose les versions et algorithmes qu’il connaît, et indique le **nom** du site visé (SNI).
2. Le serveur choisit, et envoie son **certificat**.
3. Le client **vérifie** le certificat.
4. Les deux calculent une **clé de session** commune, sans jamais l’envoyer sur le réseau.
5. Toute la suite est chiffrée.

## Pourquoi un certificat est refusé

| Message du navigateur | Cause |
|---|---|
| « Le certificat n’est pas valide pour ce nom » | le nom tapé ne figure pas dans le certificat (SAN) |
| « Le certificat a expiré » | date dépassée… ou **horloge du poste** fausse |
| « Émetteur inconnu » / « autorité non approuvée » | certificat auto-signé, autorité interne non installée sur le poste, **chaîne incomplète** sur le serveur |
| « Certificat révoqué » | l’autorité a annulé le certificat |

## Les mots à connaître

- **TLS** — Protocole qui chiffre et authentifie une connexion ; successeur de SSL.
- **Certificat** — Document numérique qui lie un nom à une clé publique, signé par une autorité de certification.
- **Autorité de certification (CA)** — Organisme dont la signature rend un certificat digne de confiance.
- **SAN** — *Subject Alternative Name*, liste des noms pour lesquels un certificat est valide.
- **SNI** — *Server Name Indication*, nom du site envoyé par le client au début de la négociation.
- **Chaîne de certificats** — Suite de certificats qui relie celui du serveur à une autorité racine de confiance.

## Teste-toi

**1.** Un portail interne affiche « certificat expiré » sur un seul poste, alors que le certificat est valide jusqu’en 2027. Que vérifies-tu ?

<details><summary>Voir le corrigé</summary>

**L’heure et la date du poste.** Si son horloge est fausse (pile du BIOS, synchronisation NTP en panne), le certificat lui paraît expiré ou pas encore valide.

</details>

**2.** Le site `https://intranet` affiche une erreur de nom, alors que `https://intranet.exemple.fr` fonctionne. Pourquoi ?

<details><summary>Voir le corrigé</summary>

Le certificat est délivré pour `intranet.exemple.fr`. Le nom court `intranet` **ne figure pas** dans sa liste de noms (SAN) : le navigateur refuse, à juste titre. Il faut utiliser le nom complet, ou ajouter le nom court au certificat (si l’autorité interne le permet).

</details>

<!-- approfondir -->

## Ce qui est négocié

- **Version** : TLS 1.3 (RFC 8446) ou 1.2. SSL 3.0, TLS 1.0 et 1.1 sont obsolètes et à désactiver.
- **Échange de clés** : Diffie-Hellman éphémère (ECDHE), qui apporte la **confidentialité persistante** : une clé privée volée plus tard ne permet pas de déchiffrer les échanges passés.
- **Chiffrement symétrique** : AES-GCM ou ChaCha20-Poly1305.
- **Signature** du serveur : RSA ou ECDSA.

TLS 1.3 ne demande qu’**un aller-retour** pour établir la connexion (zéro pour une reprise de session, avec des précautions), contre deux pour TLS 1.2.

## Inspecter un certificat

```bash
$ openssl s_client -connect www.exemple.fr:443 -servername www.exemple.fr </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
subject=CN = www.exemple.fr
issuer=C = US, O = Let's Encrypt, CN = R11
notBefore=Nov 14 08:12:01 2026 GMT
notAfter=Feb 12 08:12:00 2027 GMT
X509v3 Subject Alternative Name:
    DNS:www.exemple.fr, DNS:exemple.fr
```

```bash
# Vérifier la chaîne envoyée par le serveur
$ openssl s_client -connect www.exemple.fr:443 -servername www.exemple.fr -showcerts </dev/null
# "Verify return code: 0 (ok)" : chaîne valide
# "Verify return code: 21 (unable to verify the first certificate)" : certificat intermédiaire manquant
```

> [!WARNING]
> L’erreur la plus fréquente après un renouvellement : le serveur n’envoie **que son certificat**, sans le **certificat intermédiaire**. Certains navigateurs le retrouvent seuls (ils l’ont en cache), d’autres clients (applications, téléphones, scripts) échouent. Le résultat paraît aléatoire.

## Inspection TLS en entreprise

Certains pare-feu ou proxys **déchiffrent** le trafic TLS pour l’inspecter : ils présentent au poste un certificat généré à la volée, signé par une **autorité interne** installée sur les postes gérés. Conséquences :

- les postes **non gérés** (sans l’autorité interne) voient des erreurs de certificat ;
- les applications qui vérifient un certificat précis (*certificate pinning*) cassent : on les exclut de l’inspection ;
- c’est une décision juridique et organisationnelle (vie privée, sites bancaires et de santé souvent exclus).

## Exercices

**1.** Après le renouvellement du certificat d’un serveur, les navigateurs fonctionnent mais une application métier échoue avec « unable to get local issuer certificate ». Diagnostic ?

<details><summary>Voir le corrigé</summary>

**Chaîne incomplète** : le serveur n’envoie pas le certificat intermédiaire. Le navigateur le complète depuis son cache, l’application non. Installer la chaîne complète (certificat + intermédiaire) sur le serveur, et vérifier avec `openssl s_client -showcerts`.

</details>

**2.** Pourquoi la confidentialité persistante (*forward secrecy*) est-elle importante ?

<details><summary>Voir le corrigé</summary>

Sans elle (ancien échange de clés RSA), quelqu’un qui enregistre le trafic chiffré pendant des années et vole un jour la clé privée du serveur peut **tout déchiffrer rétroactivement**. Avec ECDHE, chaque session a une clé éphémère, détruite après usage : voler la clé privée ne permet que d’usurper le serveur à l’avenir, pas de lire le passé.

</details>
