---
titre: IPS
nom: Système de prévention d’intrusion
idee: Un IPS est placé sur le chemin du trafic ; il fait la même analyse qu’un IDS, mais peut bloquer immédiatement les paquets d’une attaque reconnue.
osi: "3 à 7"
duree: [5, 10]
prerequis: [ids]
retenir:
  - L’IPS est **en ligne** — tout le trafic le traverse, il peut **jeter** les paquets malveillants.
  - "Contrepartie — une **fausse détection** bloque du trafic légitime, et une panne de l’IPS peut couper le réseau."
  - Il est aujourd’hui le plus souvent **intégré au pare-feu** (NGFW).
  - On déploie en mode **détection** d’abord, puis on passe progressivement en **blocage**.
---

## Le problème

Un IDS alerte, mais une attaque automatique peut aboutir en quelques secondes, bien avant qu’un humain lise l’alerte. Il faut parfois **bloquer automatiquement**.

> [!IMPORTANT] L’idée en une phrase
> L’IPS est un IDS placé **sur le chemin** du trafic : quand il reconnaît une attaque, il jette les paquets au lieu de seulement prévenir.

## IDS ou IPS ?

| | IDS | IPS |
|---|---|---|
| Position | hors bande (copie du trafic) | **en ligne** |
| Action | alerte | alerte **et bloque** |
| Effet d’une fausse détection | une alerte inutile | **un service légitime coupé** |
| Effet d’une panne | on perd la visibilité | on peut perdre le **réseau** (sauf mode de secours) |
| Latence ajoutée | aucune | un peu |

```topologie
titre: IDS à côté, IPS sur le chemin
NET nuage 0,0 "Internet"
FW parefeu 1.5,0 "Pare-feu"
IPS boite 3,0 "IPS" "en coupure : peut bloquer"
SW switch 4.5,0 "Réseau interne"
IDS boite 4.5,1.2 "IDS" "copie du trafic : alerte seulement"
NET -- FW
FW -- IPS
IPS ++ SW
SW .. IDS "SPAN"
```

## Les mots à connaître

- **IPS** — *Intrusion Prevention System*, système qui détecte et bloque les attaques en ligne.
- **En ligne** — Placé sur le chemin du trafic, que tout paquet doit traverser.
- **Fail-open / fail-closed** — Comportement en cas de panne : laisser passer le trafic, ou tout bloquer.

## Teste-toi

**Après la mise à jour des signatures de l’IPS, une application métier cesse de fonctionner. Que s’est-il probablement passé ?**

<details><summary>Voir le corrigé</summary>

Une nouvelle signature produit un **faux positif** sur le trafic de l’application : l’IPS bloque des échanges légitimes. Les journaux de l’IPS indiquent la signature en cause ; on crée une exception ciblée (et l’on signale le faux positif à l’éditeur) plutôt que de désactiver tout l’IPS.

</details>

<!-- approfondir -->

## Déployer sans tout casser

1. **Mode détection** sur tout le trafic : observer les alertes pendant quelques semaines.
2. **Ajuster** : désactiver les signatures sans objet, créer des exceptions pour les faux positifs.
3. **Bloquer** d’abord les signatures fiables et graves (exploits critiques, logiciels malveillants connus).
4. Élargir progressivement, en surveillant les incidents.

## Disponibilité

- **Fail-open** (*bypass* matériel ou logiciel) : si l’IPS tombe, le trafic passe sans inspection. Priorité à la disponibilité.
- **Fail-closed** : si l’IPS tombe, plus rien ne passe. Priorité à la sécurité.
- En pratique, on met deux équipements en **haute disponibilité**, et l’on choisit le comportement selon la criticité de chaque lien.

## Exercice

**Pourquoi l’IPS est-il moins efficace sur le trafic Internet des postes que sur le trafic vers les serveurs publiés ?**

<details><summary>Voir le corrigé</summary>

Le trafic des postes vers Internet est presque entièrement **chiffré** (HTTPS) : sans inspection TLS, l’IPS ne voit pas les contenus. Pour les **serveurs publiés**, l’entreprise détient les certificats et peut faire inspecter le trafic déchiffré (sur le reverse proxy ou le pare-feu), ce qui permet de reconnaître les exploits.

</details>
