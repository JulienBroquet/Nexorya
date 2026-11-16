<p align="center"><img src="theme/img/logo.svg" width="96" alt="Logo Nexorya"></p>

<h1 align="center">Nexorya</h1>
<p align="center"><strong>Explore les réseaux. Maîtrise l’infrastructure.</strong></p>

Nexorya est une formation libre et gratuite aux réseaux informatiques, en français, du grand débutant à l’ingénieur. Chaque notion part du problème qu’elle résout, s’explique d’abord simplement, puis en détail, avec des schémas, des configurations commentées et des exercices corrigés.

## Ce que contient la version 1.0

| | |
|---|---|
| **Je débute** | 8 fiches sans aucun prérequis, et un quiz de démarrage |
| **5 niveaux** | 126 fiches : Ethernet et Wi-Fi, IP et routage, services, sécurité, WAN et datacenter |
| **QCM** | 158 questions en situation ; chaque mauvaise réponse est expliquée |
| **Pratique** | 6 laboratoires progressifs, un projet fil rouge, « le voyage d’un clic » |
| **Outils** | calculateur de sous-réseaux avec vue binaire et exercices aléatoires |
| **Lexique** | plus de 500 termes, reliés à leur fiche |
| **Progression** | fiches lues, scores, attestation imprimable — stockés uniquement dans le navigateur |

Chaque fiche a deux lectures : **Découvrir** (le problème, l’idée en une phrase, un exemple, les mots à connaître, un test) et **Approfondir** (le fonctionnement précis, les commandes, les pièges, des exercices).

## Consulter le site

Le site est entièrement statique : ouvre `docs/index.html` dans un navigateur, ou publie-le.

### Publier sur GitHub Pages

1. Pousse le dépôt sur GitHub.
2. *Settings → Pages → Build and deployment* : source **Deploy from a branch**, branche `main`, dossier **`/docs`**.
3. Le site est en ligne quelques minutes plus tard à l’adresse `https://<compte>.github.io/<depot>/`.

Le dossier `docs/` est **généré** : ne le modifie pas à la main, régénère-le (voir ci-dessous) et commite-le avec tes modifications de contenu.

## Modifier le contenu

```bash
python3 -m pip install -r requirements.txt
python3 outils/build.py --verifier   # régénère docs/ et contrôle tous les liens internes
```

| Dossier | Contenu |
|---|---|
| `contenu/plan.yaml` | l’ordre des niveaux, chapitres et fiches |
| `contenu/demarrer/`, `contenu/niveau-N/` | les fiches, en Markdown |
| `contenu/qcm/` | les questions de QCM, en YAML |
| `contenu/pages/` | pages libres : pratique, outils, à propos |
| `theme/` | feuille de style, script, logo, polices |
| `outils/` | le générateur (`build.py`) et le moteur de schémas (`schemas.py`) |
| `docs/` | le site généré, publié tel quel |

Le guide complet d’écriture (fiche, schéma, question de QCM) est dans [CONTRIBUTING.md](CONTRIBUTING.md).

## Respect de la vie privée

Aucun compte, aucun traceur, aucune requête vers un service tiers : les polices sont hébergées avec le site, et la progression reste dans le stockage local du navigateur (exportable en JSON).

## Licence

- Les polices (Bricolage Grotesque, Atkinson Hyperlegible, JetBrains Mono) sont sous licence SIL Open Font License ; les textes de licence sont dans `theme/fonts/`.
- Licence du contenu et du code : à préciser par l’auteur dans un fichier `LICENSE` (par exemple CC BY-SA 4.0 pour les textes et MIT pour le code).

Les noms de produits et de marques cités appartiennent à leurs propriétaires. Nexorya n’est affiliée à aucun constructeur.
