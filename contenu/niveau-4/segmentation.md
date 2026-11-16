---
titre: Segmenter le réseau
nom: Entreprise, invités, objets connectés et zones sensibles
idee: Segmenter, c’est découper le réseau en zones selon le niveau de confiance et n’autoriser entre elles que les flux nécessaires ; une compromission reste alors contenue dans sa zone.
osi: "2 à 4"
duree: [10, 20]
cle: true
prerequis: [vlan, acl]
retenir:
  - "On groupe par **niveau de confiance et usage** — postes, serveurs, administration, invités, objets connectés, systèmes industriels."
  - Entre les zones, une **matrice de flux** — qui a besoin de joindre quoi, sur quel port.
  - Le filtrage se fait sur la **passerelle** (ACL) ou mieux, sur un **pare-feu** à états entre les zones sensibles.
  - "Le **réseau d’administration** des équipements est une zone à part, très restreinte."
---

## Le problème : un réseau « à plat »

Dans beaucoup de PME, tout est dans le même réseau : postes, serveurs, imprimantes, caméras, invités. Un seul poste compromis par un rançongiciel peut alors joindre **tous** les serveurs et toutes les sauvegardes. Une caméra mal sécurisée devient une porte d’entrée vers la comptabilité.

> [!IMPORTANT] L’idée en une phrase
> On découpe le réseau en zones de confiance, et l’on n’autorise entre elles que les échanges strictement nécessaires : un incident dans une zone ne se propage pas aux autres.

> [!TIP] L’analogie du navire
> Un navire est divisé en compartiments étanches. Si la coque est percée à un endroit, seul ce compartiment se remplit d’eau : le navire continue de flotter.

## Un découpage type

```topologie
titre: Zones de confiance d’une PME
FW parefeu 2,1 "Pare-feu interne"
POS pc 0,0 "Postes" "VLAN 10"
INV portable 0,1 "Invités" "VLAN 30"
IOT camera 0,2 "Objets connectés" "VLAN 50"
SRV serveur 4,0 "Serveurs" "VLAN 20"
SAV serveur 4,1 "Sauvegardes" "VLAN 25"
ADM l3 4,2 "Administration" "VLAN 99"
NET nuage 2,0 "Internet"
POS -- FW
INV -- FW
IOT -- FW
FW -- SRV
FW -- SAV
FW -- ADM
FW -- NET
```

## La matrice de flux

Avant de configurer quoi que ce soit, on écrit **qui a besoin de joindre quoi** :

| Depuis ↓ / Vers → | Serveurs | Sauvegardes | Administration | Internet |
|---|---|---|---|---|
| **Postes** | applications (443), fichiers (445), AD | non | non | oui (via proxy) |
| **Invités** | non | non | non | oui |
| **Objets connectés** | enregistreur vidéo seulement | non | non | mises à jour du fabricant seulement |
| **Serveurs** | — | oui (agent de sauvegarde) | non | mises à jour |
| **Administration** | SSH, RDP, consoles | oui | — | non |

Tout ce qui n’est pas dans la matrice est **refusé**.

## Les mots à connaître

- **Segmentation** — Découpage du réseau en zones séparées, avec un contrôle des flux entre elles.
- **Zone de confiance** — Ensemble de machines qui ont le même niveau de sensibilité et les mêmes besoins.
- **Matrice de flux** — Tableau des échanges autorisés entre zones (source, destination, protocole, port).
- **Mouvement latéral** — Déplacement d’un attaquant d’une machine compromise vers d’autres machines du réseau.

## Teste-toi

**Un rançongiciel infecte un poste du VLAN 10. Avec la matrice ci-dessus, peut-il chiffrer les sauvegardes ?**

<details><summary>Voir le corrigé</summary>

**Non, pas directement** : les postes n’ont aucun flux autorisé vers la zone des sauvegardes. C’est précisément l’objectif : protéger le dernier recours de l’entreprise. (Il faut aussi que les comptes utilisés pour les sauvegardes ne soient pas accessibles depuis les postes.)

</details>

<!-- approfondir -->

## ACL sur la passerelle ou pare-feu ?

| Critère | ACL sur switch L3 | Pare-feu interne |
|---|---|---|
| Suivi des connexions | non (sans état) | oui |
| Débit | vitesse du switch | dépend du modèle |
| Journalisation | limitée | complète |
| Filtrage applicatif, IPS | non | oui |
| Usage typique | séparations simples, à fort débit (postes ↔ imprimantes) | zones sensibles (serveurs, sauvegardes, administration, industriel) |

En pratique, on combine : routage et ACL simples sur le cœur pour les zones peu sensibles, et pare-feu pour les frontières importantes (souvent avec des **VRF** pour forcer le passage par le pare-feu, voir [VRF](../niveau-5/vrf.md)).

## Le réseau d’administration

- Interfaces de gestion des équipements (SVI de gestion, ports de gestion dédiés) dans un VLAN ou une VRF **dédiés**.
- Seul le **bastion** (et les outils de supervision et de sauvegarde) y a accès.
- Les ACL des lignes VTY et de SNMP n’autorisent que ce réseau.

## Segmenter un réseau existant sans tout casser

1. **Inventorier** : qui parle à qui aujourd’hui ? (NetFlow, journaux du pare-feu en mode observation, outils de découverte.)
2. **Concevoir** les zones et la matrice cible.
3. Créer les nouveaux VLAN et y **migrer** les machines par lots, en gardant d’abord des règles larges qui journalisent.
4. **Resserrer** progressivement, en s’appuyant sur les journaux pour ne pas casser d’application.
5. **Documenter** et revoir la matrice régulièrement.

## Exercices

**1.** Une caméra IP du VLAN 50 doit envoyer son flux à l’enregistreur `10.20.0.60` (RTSP, TCP 554) et ne doit rien joindre d’autre en interne. Écris la logique de filtrage.

<details><summary>Voir le corrigé</summary>

Sur la passerelle du VLAN 50, en entrée : autoriser `10.50.0.0/24` → `host 10.20.0.60` en TCP 554 (et éventuellement le DNS et le NTP internes), **refuser** `10.50.0.0/24` → réseaux internes (`10.0.0.0/8`), puis, selon la politique, autoriser ou non Internet (souvent seulement vers les serveurs de mise à jour du fabricant). Le reste tombe dans le refus implicite.

</details>

**2.** Pourquoi placer le réseau d’administration dans une zone séparée, même si « seuls les administrateurs connaissent les adresses » ?

<details><summary>Voir le corrigé</summary>

Parce que la sécurité ne peut pas reposer sur le **secret des adresses** (un balayage les révèle en quelques secondes). Un attaquant présent sur un poste chercherait justement à atteindre les interfaces d’administration pour prendre le contrôle du réseau. Seule une séparation filtrée l’en empêche.

</details>
