---
titre: PKI
nom: Infrastructure à clés publiques
idee: Une PKI est l’organisation qui délivre, renouvelle et révoque les certificats d’une entreprise ; elle permet aux machines et aux personnes de prouver leur identité avec des clés.
osi: "7"
duree: [8, 16]
retenir:
  - "Chaque titulaire a une **paire de clés** — la **privée** reste secrète, la **publique** figure dans le certificat."
  - "Une PKI comprend — une **autorité racine** (hors ligne), des **autorités intermédiaires**, des **politiques**, la **révocation** (CRL, OCSP)."
  - Un certificat lie une **identité** (nom, SAN) à une **clé publique**, pour une **durée** et des **usages** précis.
  - Le cycle de vie — **délivrer, renouveler, révoquer** — doit être automatisé et supervisé.
---

## Le problème : prouver qui l’on est, à grande échelle

Les serveurs Web, le RADIUS, les VPN, les postes en EAP-TLS, les contrôleurs Wi-Fi, les équipements réseau : tous ont besoin de prouver leur identité. Il faut un système qui **délivre** des « cartes d’identité numériques » fiables, les **renouvelle** avant expiration et les **annule** en cas de vol.

> [!IMPORTANT] L’idée en une phrase
> Une PKI est une organisation de confiance : des autorités signent des certificats qui associent une identité à une clé publique, et tout le monde fait confiance à la même racine.

## Clé publique, clé privée

- Ce qui est **chiffré** avec la clé publique ne peut être **déchiffré** qu’avec la clé privée.
- Ce qui est **signé** avec la clé privée peut être **vérifié** par tous avec la clé publique.

La clé publique peut donc être distribuée à tous (dans un certificat) ; la clé privée ne doit **jamais** quitter son titulaire.

## La chaîne de confiance

```topologie
titre: Une PKI d’entreprise à deux niveaux
ROOT serveur 2,0 "Autorité racine" "hors ligne, dans un coffre"
SUB1 serveur 1,1 "Autorité intermédiaire" "machines et utilisateurs"
SUB2 serveur 3,1 "Autorité intermédiaire" "serveurs et équipements"
PC pc 0.5,2 "Certificat de poste"
U utilisateur 1.5,2 "Certificat utilisateur"
WEB serveur 2.5,2 "Certificat de serveur Web"
RAD serveur 3.5,2 "Certificat RADIUS"
ROOT -- SUB1 "signe"
ROOT -- SUB2 "signe"
SUB1 -- PC
SUB1 -- U
SUB2 -- WEB
SUB2 -- RAD
```

Les postes de l’entreprise font confiance à la **racine**. Ils acceptent donc tout certificat signé par une intermédiaire elle-même signée par la racine. La racine reste **hors ligne** : si une intermédiaire est compromise, on la révoque sans tout reconstruire.

## Les mots à connaître

- **PKI** — Infrastructure à clés publiques : autorités, politiques et outils qui gèrent les certificats.
- **Clé privée / clé publique** — Paire de clés mathématiquement liées ; la privée reste secrète, la publique est diffusée.
- **Autorité racine** — Autorité au sommet de la chaîne, en qui tous les systèmes ont confiance.
- **Autorité intermédiaire** — Autorité signée par la racine, qui délivre les certificats au quotidien.
- **CRL / OCSP** — Liste des certificats révoqués / service en ligne qui répond « ce certificat est-il révoqué ? ».

## Teste-toi

**Pourquoi garde-t-on l’autorité racine hors ligne ?**

<details><summary>Voir le corrigé</summary>

Parce que si sa clé privée était volée, l’attaquant pourrait signer **n’importe quel certificat** auquel tous les systèmes feraient confiance, et il faudrait reconstruire toute la PKI. Hors ligne, elle ne sert qu’à signer de temps en temps les intermédiaires.

</details>

<!-- approfondir -->

## Le contenu d’un certificat X.509

| Champ | Exemple | Ce qu’on vérifie |
|---|---|---|
| Sujet | `CN=radius.exemple.fr` | identité (souvent secondaire) |
| **SAN** | `DNS:radius.exemple.fr` | **noms** réellement valides |
| Émetteur | `CN=Exemple Serveurs CA 1` | qui l’a signé |
| Validité | du 2026-11-01 au 2027-11-01 | dates (et horloge du vérificateur) |
| Clé publique | ECDSA P-256 | algorithme et taille |
| **Usages (KU / EKU)** | Signature numérique ; Authentification serveur | ce que le certificat a le droit de faire |
| Points de révocation | URL de CRL, URL OCSP | doivent être **joignables** par ceux qui vérifient |

## Le cycle de vie

1. **Demande** : le titulaire génère sa paire de clés et envoie une demande (CSR) contenant sa clé publique.
2. **Délivrance** : l’autorité vérifie selon sa politique et signe le certificat.
3. **Utilisation** et **supervision** des dates.
4. **Renouvellement** avant l’expiration, idéalement automatique (autoenrollment, SCEP, EST, ACME).
5. **Révocation** si la clé est compromise ou l’appareil retiré.

```bash
# Générer une clé et une demande pour un équipement
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
  -keyout radius.key -out radius.csr \
  -subj "/CN=radius.exemple.fr" -addext "subjectAltName=DNS:radius.exemple.fr"
# Lire un certificat délivré
openssl x509 -in radius.crt -noout -text | grep -A1 -E "Subject Alternative|Extended Key|Not After"
```

## Révocation : le point faible oublié

Si les vérificateurs (serveur RADIUS, pare-feu, postes) **ne peuvent pas joindre** la CRL ou le service OCSP, deux comportements existent : refuser (tout casse) ou accepter (la révocation ne sert à rien). Il faut publier les CRL à un endroit **haute disponibilité**, joignable depuis tous les réseaux concernés, et surveiller leur date de mise à jour.

## Exercices

**1.** Un certificat de serveur a pour sujet `CN=srv-web01` et pour SAN `DNS:intranet.exemple.fr`. Les utilisateurs se connectent à `https://srv-web01`. Le navigateur affiche-t-il une erreur ?

<details><summary>Voir le corrigé</summary>

**Oui.** Les navigateurs ne regardent que le **SAN**, et `srv-web01` n’y figure pas. Le champ CN est ignoré pour la vérification du nom.

</details>

**2.** Pourquoi les autorités intermédiaires ont-elles une durée de vie plus courte que la racine, et les certificats finaux une durée encore plus courte ?

<details><summary>Voir le corrigé</summary>

Plus une clé est utilisée et exposée, plus le risque de compromission augmente. Les certificats finaux, installés sur de nombreuses machines, ont donc des durées courtes (de quelques semaines à un an) ; les intermédiaires, plus protégées, quelques années ; la racine, hors ligne, une à deux décennies. Une durée courte limite aussi l’impact d’une révocation qui ne serait pas vérifiée.

</details>
