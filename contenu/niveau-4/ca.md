---
titre: Autorité de certification
nom: CA publiques et autorités internes
idee: Une autorité de certification signe les certificats ; une CA publique est reconnue par tous les navigateurs, une CA interne n’est reconnue que par les appareils de l’entreprise où on l’a installée.
osi: "7"
duree: [5, 10]
prerequis: [pki]
retenir:
  - "**CA publique** — pour les sites accessibles depuis Internet ; elle ne vérifie que la maîtrise du nom de domaine."
  - "**CA interne** — pour l’intranet, le RADIUS, les postes, les équipements ; il faut **distribuer** sa racine aux appareils."
  - Un appareil non géré ne fait pas confiance à la CA interne — d’où les erreurs sur les postes personnels et les invités.
---

## Le problème

Qui a le droit de signer un certificat ? Pour un site public, le navigateur de n’importe quel visiteur doit lui faire confiance : il faut une autorité **reconnue de tous**. Pour le serveur RADIUS ou l’intranet, seuls les appareils de l’entreprise sont concernés : l’entreprise peut être **sa propre autorité**.

> [!IMPORTANT] L’idée en une phrase
> Une autorité de certification est un tiers de confiance qui signe les certificats ; on choisit une CA publique pour ce qui est vu depuis Internet, une CA interne pour ce qui ne concerne que l’entreprise.

## Publique ou interne ?

| | CA publique | CA interne |
|---|---|---|
| Reconnue par | tous les navigateurs et systèmes | les appareils où la racine a été installée |
| Exemples d’usage | site Web public, portail VPN, messagerie | intranet, RADIUS, EAP-TLS, équipements, inspection TLS |
| Vérification | contrôle du nom de domaine (DV), parfois de l’organisation (OV/EV) | selon la politique de l’entreprise |
| Noms internes (`srv-ad01.local`) | **impossible** | possible |
| Coût | gratuit (ACME) à payant | infrastructure à maintenir |

## Les mots à connaître

- **Autorité de certification (CA)** — Entité qui signe les certificats et en garantit le contenu.
- **Magasin de certificats** — Liste des autorités racines auxquelles un système fait confiance.
- **Certificat auto-signé** — Certificat signé par sa propre clé, reconnu par personne d’autre par défaut.

## Teste-toi

**Le portail Wi-Fi invités affiche une erreur de certificat sur tous les téléphones des visiteurs, mais pas sur les postes de l’entreprise. Pourquoi ?**

<details><summary>Voir le corrigé</summary>

Le portail utilise un certificat de la **CA interne**. Les postes de l’entreprise ont sa racine dans leur magasin de confiance ; les téléphones des visiteurs, non. Pour un service vu par des appareils non gérés, il faut un certificat d’une **CA publique**.

</details>

<!-- approfondir -->

## Distribuer la racine interne

| Plateforme | Méthode |
|---|---|
| Windows dans le domaine | automatique avec une CA intégrée à Active Directory, ou GPO |
| macOS, iOS, Android gérés | profil de configuration via le MDM |
| Linux | `/usr/local/share/ca-certificates/` puis `update-ca-certificates` |
| Applications à magasin propre (Java, Firefox, Python) | importer dans leur magasin, ou les configurer pour utiliser celui du système |

```bash
$ sudo cp Exemple-Racine.crt /usr/local/share/ca-certificates/
$ sudo update-ca-certificates
$ curl https://intranet.exemple.fr     # n'affiche plus d'erreur de certificat
```

## Bonnes pratiques

- Ne jamais demander aux utilisateurs d’« accepter le risque » face à une erreur de certificat : on leur apprend à ignorer les vraies attaques.
- Remplacer les certificats **auto-signés** des équipements (interfaces Web d’administration, contrôleurs) par des certificats de la CA interne.
- Superviser les **dates d’expiration** de tous les certificats, y compris des intermédiaires et des CRL.

## Exercice

**Un script Python qui appelle l’API interne échoue avec une erreur de certificat, alors que le navigateur du même poste fonctionne. Explication ?**

<details><summary>Voir le corrigé</summary>

Python (la bibliothèque `requests` avec `certifi`) utilise **son propre magasin** d’autorités, qui ne contient pas la racine interne. Le navigateur utilise le magasin du système. Indiquer le fichier de la racine (`REQUESTS_CA_BUNDLE` ou `verify=`), ou configurer Python pour utiliser le magasin système — mais jamais désactiver la vérification.

</details>
