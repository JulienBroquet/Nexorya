---
titre: Pratiquer
actif: pratique
chapeau: On comprend vraiment un réseau en le construisant, en le cassant et en le réparant. Voici des laboratoires guidés, un projet qui traverse tous les niveaux, et une synthèse pour relier toutes les notions.
---

## Pour commencer : le voyage d’un clic

Avant de te lancer dans les labos, lis [Le voyage d’un clic](voyage-d-un-clic.md) : on suit pas à pas tout ce qui se passe entre le moment où tu tapes une adresse et l’affichage de la page. C’est la meilleure façon de voir comment les notions des différents niveaux s’emboîtent.

## Les laboratoires

Chaque labo part d’un objectif concret, donne la topologie, les étapes, les commandes de vérification, et un corrigé. Fais-les dans l’ordre : chacun réutilise le précédent.

| Labo | Ce que tu construis | Niveau |
|---|---|---|
| [1. Mon premier réseau](labo-1-premier-reseau.md) | deux PC, un switch, des adresses, un ping | Je débute → 1 |
| [2. Des VLAN qui se parlent](labo-2-vlan.md) | trois VLAN, un trunk, un routage inter-VLAN | 1 → 2 |
| [3. Redondance sans boucle](labo-3-redondance.md) | spanning tree observé et réglé, agrégat LACP | 1 |
| [4. Plusieurs sites routés](labo-4-routage.md) | OSPF entre trois routeurs, relais DHCP, NAT vers Internet | 2 → 3 |
| [5. Sécuriser](labo-5-securite.md) | SSH, comptes, ACL, sécurité des ports | 4 |
| [6. Chasse aux pannes](labo-6-pannes.md) | dix pannes à trouver avec une méthode | tous |

## Le projet fil rouge

[Le réseau de l’entreprise Lumen](projet-lumen.md) : une PME qui grandit, de 15 salariés dans un bureau à trois sites avec un datacenter et du cloud. À chaque niveau, tu conçois la nouvelle étape et tu produis les documents d’un vrai ingénieur réseau : plan d’adressage, schémas, configurations, plan de changement.

## De quoi as-tu besoin ?

Tu n’as pas besoin de matériel. Un simulateur ou un émulateur suffit :

| Outil | Pour qui | Remarques |
|---|---|---|
| **Cisco Packet Tracer** | débutants, labos 1 à 6 | gratuit avec un compte Cisco Networking Academy ; simulation simple et visuelle |
| **GNS3** ou **EVE-NG** (édition communautaire) | niveaux 2 à 5 | émulent de vrais systèmes ; il faut fournir les images des équipements |
| **containerlab** | niveaux 3 à 5, automatisation | réseaux décrits dans un fichier, équipements en conteneurs (FRRouting, Nokia SR Linux, Arista cEOS…) |
| **Wireshark** | tous | indispensable pour voir les paquets |

> [!TIP] Conseil
> Garde un **carnet de labo** : pour chaque exercice, note ce que tu attendais, ce que tu as observé et ce que tu en as compris. C’est ce qui transforme une manipulation en compétence — et c’est exactement ce qu’on fait en entreprise après un incident.

Les commandes des labos sont écrites pour Cisco IOS (celui de Packet Tracer). Les concepts sont les mêmes sur les autres systèmes ; seule la syntaxe change.
