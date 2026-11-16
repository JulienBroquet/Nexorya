# Historique des versions

## 1.0.0 — Novembre 2026

Première version publique sous le nom **Nexorya**, entièrement réécrite à partir de la « Formation Réseaux » V4.4.

### Contenu
- Toutes les fiches réécrites selon une même structure en deux lectures : **Découvrir** (le problème, l’idée en une phrase, un exemple, les mots à connaître, un test corrigé) et **Approfondir** (fonctionnement, commandes commentées, sorties annotées, dépannage, exercices corrigés).
- Nouveau parcours **Je débute** (8 fiches sans prérequis) et son quiz.
- 134 fiches réparties en 6 niveaux et 33 chapitres, chacune avec ses prérequis et ses points à retenir.
- QCM réécrits : 158 questions en situation, classées Découverte, Pratique et Expert ; chaque proposition est expliquée.
- Section **Pratique** : le voyage d’un clic, 6 laboratoires progressifs, le projet fil rouge « Lumen ».
- Calculateur de sous-réseaux avec vue binaire et exercices aléatoires.
- Lexique généré automatiquement (plus de 500 termes).
- Pages de révision par niveau.

### Interface
- Nouvelle identité : logo, palette, typographies Bricolage Grotesque, Atkinson Hyperlegible et JetBrains Mono, hébergées localement.
- Accueil en forme de plan de réseau de transport : chaque niveau est une ligne, chaque chapitre une station qui se remplit à la lecture.
- Lecture en trois colonnes : parcours du niveau, fiche, sommaire de la page ; bascule Découvrir / Approfondir.
- Schémas (séquences et topologies) générés en SVG à partir de texte, lisibles en thème clair et sombre.
- Thème sombre, recherche instantanée, progression et attestation stockées dans le navigateur, export et import JSON.
- Mise en page adaptée aux mobiles et à l’impression.

### Technique
- Générateur statique en Python (`outils/build.py`) avec vérification des liens internes.
- Publication directe sur GitHub Pages depuis le dossier `docs/`.
- Licences : contenu CC BY-NC-SA 4.0, code PolyForm Noncommercial 1.0.0, nom et logo réservés.

### Images
- Illustrations de matériel reprises de la V4.4 et recadrées (modules SFP, câble DAC, fibre LC, RJ45, façade de switch, baies), avec légende détaillée et crédit sous chaque image.
- Page « Crédits des images » générée automatiquement.

### Retiré
- Les anciens volumes PDF de la V4.4, remplacés par les fiches et les schémas générés.
