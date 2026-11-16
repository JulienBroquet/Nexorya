---
titre: IDS
nom: Système de détection d’intrusion
idee: Un IDS observe une copie du trafic, la compare à des signatures d’attaques et à des comportements anormaux, et donne l’alerte ; il ne bloque rien lui-même.
osi: "3 à 7"
duree: [6, 12]
retenir:
  - L’IDS est **hors bande** — il reçoit une **copie** du trafic (SPAN, TAP) et ne peut pas le bloquer.
  - "Deux méthodes — **signatures** (attaques connues) et **anomalies** (écarts au comportement normal)."
  - Sa valeur dépend du **réglage** — trop d’alertes inutiles, et personne ne les lit.
  - "Exemples libres — **Suricata**, **Zeek**, Snort."
---

## Le problème : savoir qu’on est attaqué

Un attaquant qui a pénétré le réseau balaie les machines, tente des exploits, exfiltre des données. Sans outil pour **voir** ces comportements, l’entreprise ne découvre l’intrusion que des semaines plus tard, souvent quand les fichiers sont déjà chiffrés.

> [!IMPORTANT] L’idée en une phrase
> L’IDS est une caméra de surveillance du réseau : il regarde une copie du trafic et sonne l’alarme quand il reconnaît une attaque, mais il n’arrête pas l’intrus.

## Où le placer

```topologie
titre: Un IDS reçoit une copie du trafic
NET nuage 0,0 "Internet"
FW parefeu 1.5,0 "Pare-feu"
SW l3 3,0 "Cœur" "port miroir (SPAN)"
SRV serveur 4.5,0 "Serveurs"
IDS serveur 3,1 "IDS" "sonde"
SIEM serveur 4.5,1 "SIEM / SOC"
NET -- FW
FW -- SW
SW -- SRV
SW .. IDS "copie du trafic"
IDS -- SIEM "alertes"
```

Positions courantes : derrière le pare-feu Internet, devant les serveurs sensibles, entre les zones internes (pour voir les **mouvements latéraux**).

## Les mots à connaître

- **IDS** — *Intrusion Detection System*, système qui détecte les attaques et alerte sans bloquer.
- **Signature** — Motif caractéristique d’une attaque connue (une suite d’octets, une requête précise).
- **Faux positif** — Alerte déclenchée par un trafic légitime.
- **SOC** — Centre des opérations de sécurité, équipe qui traite les alertes.

## Teste-toi

**Un IDS a bien détecté une attaque contre un serveur, mais le serveur a quand même été compromis. Est-ce un dysfonctionnement ?**

<details><summary>Voir le corrigé</summary>

**Pas forcément.** Un IDS hors bande **n’a pas la capacité de bloquer** : il alerte. Si personne n’a réagi à l’alerte à temps, ou si aucune action automatique n’était prévue, l’attaque aboutit. Pour bloquer, il faut un **IPS** en ligne, ou une réaction rapide du SOC.

</details>

<!-- approfondir -->

## Signatures et comportements

| Méthode | Détecte bien | Limites |
|---|---|---|
| **Signatures** | exploits connus, logiciels malveillants connus, balayages | inefficace contre une attaque inédite ou un trafic chiffré |
| **Anomalies / comportement** | volumes inhabituels, nouveaux flux, machine qui parle à des centaines d’autres | plus de faux positifs, nécessite une période d’apprentissage |
| **Analyse de métadonnées** (Zeek) | journaux détaillés de chaque connexion, DNS, TLS (noms, certificats, empreintes JA3/JA4) | demande de l’analyse et du stockage |

## Une règle Suricata

```text
alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"Téléchargement d’un exécutable depuis une IP brute";
  flow:established,to_server; http.host; pcre:"/^\d{1,3}(\.\d{1,3}){3}$/";
  http.uri; content:".exe"; endswith; classtype:policy-violation; sid:1000001; rev:1;)
```

## Le trafic chiffré

La majorité du trafic est chiffrée (TLS) : l’IDS ne voit plus les contenus. Il reste efficace sur :

- les **métadonnées** : adresses, volumes, horaires, noms dans le SNI, certificats, empreintes de clients TLS ;
- le trafic **interne non chiffré** et les protocoles d’administration ;
- le trafic **déchiffré** par un proxy ou un pare-feu qui fait de l’inspection TLS.

## Réglage : la clé du succès

Un IDS installé avec toutes ses signatures produit des milliers d’alertes par jour, dont la plupart sans intérêt pour l’entreprise. Il faut : désactiver les règles qui ne concernent pas l’environnement, définir précisément les réseaux internes (`HOME_NET`), classer les alertes par gravité, et **mesurer** combien sont réellement traitées.

## Exercice

**Un IDS placé derrière le pare-feu Internet ne voit rien de l’attaque d’un poste interne contre un serveur du même site. Pourquoi, et que proposer ?**

<details><summary>Voir le corrigé</summary>

Le trafic entre le poste et le serveur **ne passe pas** par le lien observé (Internet ↔ pare-feu) : il reste dans le réseau interne. Ajouter une copie du trafic **interne** (SPAN sur le cœur, ou sonde entre zones), en priorité vers les serveurs sensibles, pour détecter les mouvements latéraux.

</details>
