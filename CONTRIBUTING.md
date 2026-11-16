# Contribuer à Nexorya

Merci de vouloir améliorer Nexorya ! Ce guide explique comment écrire une fiche, un schéma ou une question de QCM, et comment vérifier ton travail.

## Avant de proposer une modification

```bash
python3 -m pip install -r requirements.txt
python3 outils/build.py --verifier
```

La commande régénère `docs/` et doit se terminer par **« 0 lien(s) cassé(s). »**. Ouvre ensuite la page modifiée dans un navigateur pour vérifier le rendu, en thème clair et sombre.

## Le ton

- On **tutoie** le lecteur, on écrit des phrases courtes, à la voix active.
- On part toujours du **problème** avant la solution.
- Aucun sigle ni terme technique sans explication au moment où il apparaît.
- Les chiffres (débits, temporisateurs, valeurs par défaut) sont vérifiés dans la norme ou la documentation du constructeur.
- Typographie française : espace avant `:`, `;`, `?`, `!` ; apostrophe typographique `’` ; guillemets « ».

## Écrire une fiche

Une fiche est un fichier Markdown dans `contenu/demarrer/` ou `contenu/niveau-N/`, déclaré dans `contenu/plan.yaml` (son nom de fichier, sans `.md`).

```markdown
---
titre: STP
nom: Spanning Tree Protocol
idee: Une phrase qui résume toute la fiche.
osi: "2"
duree: [8, 15]            # minutes de lecture : Découvrir, Approfondir
prerequis: [switch, vlan] # identifiants de fiches, sans dossier
cle: true                 # facultatif : « notion clé »
retenir:
  - "Trois à cinq phrases, **les mots importants en gras**."
---

## Le problème : …

> [!IMPORTANT] L’idée en une phrase
> …

## Comment ça marche
## Les mots à connaître

- **Terme** — Définition courte (reprise automatiquement dans le lexique).

## Teste-toi

**Question ?**

<details><summary>Voir le corrigé</summary>

Réponse expliquée.

</details>

<!-- approfondir -->

## Fonctionnement détaillé, commandes, dépannage, exercices…
```

La ligne `<!-- approfondir -->` sépare les deux lectures. Les valeurs YAML contenant `:` doivent être entre guillemets.

### Encadrés

```markdown
> [!IMPORTANT] Titre facultatif
> Texte.
```

Types : `IMPORTANT` (l’idée clé), `TIP` (astuce, analogie), `NOTE`, `WARNING` (piège), `CAUTION` (danger), `EXAMPLE`.

### Liens

Liens relatifs vers le fichier Markdown : `[OSPF](ospf.md)` dans le même niveau, `[OSPF](../niveau-2/ospf.md)` depuis un autre dossier. Le générateur les transforme en liens HTML et signale ceux qui sont cassés.

### Code

Utilise la langue du bloc pour la coloration : `cisco`, `text`, `bash`, `python`, `yaml`, `json`. Commente les lignes importantes avec `!` (Cisco) ou `#`.

## Dessiner un schéma

Les schémas sont décrits en texte dans un bloc de code ; le générateur les transforme en SVG accessibles, adaptés au thème clair et sombre.

### Diagramme de séquence

````markdown
```sequence
titre: Obtenir une adresse
PC | Serveur DHCP
== Découverte ==
PC -> Serveur DHCP : DISCOVER (broadcast)
Serveur DHCP --> PC : OFFER 192.168.1.20
PC -x Serveur DHCP : message perdu
note PC, Serveur DHCP : texte d’explication
```
````

- La première ligne d’acteurs liste les colonnes, séparées par `|`.
- `->` message, `-->` réponse, `-x` message perdu ; le texte suit **` : `** (espace, deux-points, espace).
- `== Titre ==` ouvre une section ; `note A, B : texte` ajoute une note.

### Topologie

````markdown
```topologie
titre: Deux VLAN
zone "Bâtiment A" 0,0 1,1
SW switch 0,0 "SW1" "cœur"
PC pc 1,1 "PC" "VLAN 10"
SW -- PC "Gi1/0/5"
```
````

- Nœud : `IDENTIFIANT type colonne,ligne "Libellé" "sous-libellé"` (coordonnées positives, décimales permises).
- Types : `switch`, `l3`, `routeur`, `pc`, `portable`, `serveur`, `nuage`, `parefeu`, `ap`, `telephone`, `camera`, `utilisateur`, `imprimante`, `vm`, `boite`.
- Liens : `--` normal, `==` agrégat ou trunk, `++` lien mis en évidence (chemin actif, tunnel), `..` flux logique, `~~` sans fil, `-x-` lien bloqué ou coupé ; libellé facultatif entre guillemets.
- Zone : `zone "Libellé" c1,r1 c2,r2` entoure les nœuds compris entre ces deux coins.

## Écrire une question de QCM

Les questions sont dans `contenu/qcm/niveau-N.yaml` (`niveau-0.yaml` pour le quiz « Je débute »). **Toutes les valeurs sont entre guillemets doubles.** La bonne réponse est écrite en premier ; le générateur mélange les propositions.

```yaml
- niveau: "Pratique"              # Découverte, Pratique ou Expert
  situation: "Le contexte concret, en une ou deux phrases."
  question: "La question posée ?"
  bonne: ["La bonne réponse", "Pourquoi elle est juste."]
  fausses:
    - ["Une erreur plausible", "Pourquoi elle est fausse."]
    - ["Une autre erreur plausible", "Pourquoi elle est fausse."]
    - ["Une troisième erreur plausible", "Pourquoi elle est fausse."]
  retenir: "La règle à retenir, en une ligne."
  fiche: "stp"                    # identifiant de la fiche à relire
```

Une bonne question part d’une situation réelle, a des distracteurs crédibles (des erreurs que font vraiment les apprenants), et explique **chaque** proposition.

## Pages libres

`contenu/pages/` contient les pages hors parcours. Un fichier `.md` est rendu comme une fiche (sans les deux lectures). Un fichier `.html` est inséré tel quel dans la mise en page ; son front matter peut lister des scripts de `theme/js/` à charger (`scripts: [mon-outil.js]`).
