---
titre: WAN
nom: Relier des sites éloignés
idee: Le WAN relie les sites d’une entreprise répartis dans une région, un pays ou le monde, à travers des réseaux d’opérateurs ou Internet.
osi: "1 à 3"
duree: [7, 14]
prerequis: [man]
retenir:
  - "Supports — **MPLS VPN** d’opérateur, **Internet** (fibre, xDSL, 4G/5G, satellite) avec VPN, liaisons louées."
  - Les liens WAN sont **plus lents, plus chers et plus lointains** que le LAN — latence et capacité deviennent des contraintes.
  - On combine souvent plusieurs accès (MPLS + Internet, fibre + 4G) pour la **redondance**, piloté aujourd’hui par le **SD-WAN**.
---

## Le problème

Une chaîne de magasins a un siège et 120 boutiques dans tout le pays. Chaque boutique doit joindre les applications du siège (caisse, stocks), Internet et le cloud. On ne tire pas de fibre privée sur 800 km : on utilise des réseaux d’opérateurs.

> [!IMPORTANT] L’idée en une phrase
> Le WAN relie des sites lointains en s’appuyant sur des réseaux d’opérateurs ; il faut y composer avec une capacité limitée, une latence plus élevée et des pannes qu’on ne maîtrise pas directement.

## Les options

| Option | Principe | Avantages | Limites |
|---|---|---|---|
| **MPLS VPN** (L3VPN) | l’opérateur route les sites de l’entreprise dans un réseau privé virtuel | qualité de service garantie, contrat | coût, délais de mise en service |
| **Internet + VPN** (IPsec) | chaque site a un accès Internet et des tunnels chiffrés | coût faible, disponibilité partout | qualité non garantie |
| **4G/5G** | accès mobile | rapide à installer, secours | débit variable, volume |
| **Liaison louée / Ethernet point à point** | lien dédié entre deux sites | prévisible | coût, rigidité |
| **Satellite** (orbite basse) | accès partout | sites isolés | latence et météo (selon la technologie) |

## Topologies

- **Étoile** (*hub and spoke*) : chaque site est relié au siège. Simple, mais le trafic entre deux agences passe par le siège.
- **Maillage complet** : chaque site est relié à tous les autres. Direct, mais le nombre de tunnels explose (n × (n − 1) / 2).
- **Maillage dynamique** : étoile pour le contrôle, tunnels directs créés à la demande entre agences (DMVPN, SD-WAN).

```topologie
titre: Un WAN d’entreprise typique
SIEGE l3 1.5,0 "Siège" "datacenter"
MPLS nuage 0.5,1.3 "VPN MPLS" "opérateur"
INT nuage 2.5,1.3 "Internet"
A1 routeur 0,2.6 "Agence 1"
A2 routeur 1.5,2.6 "Agence 2"
A3 routeur 3,2.6 "Agence 3" "Internet seul"
SIEGE -- MPLS
SIEGE -- INT
MPLS -- A1
MPLS -- A2
INT .. A2 "secours"
INT ++ A3 "VPN IPsec"
```

## Les mots à connaître

- **WAN** — *Wide Area Network*, réseau qui relie des sites éloignés.
- **Hub and spoke** — Topologie en étoile, avec un site central (hub) et des sites périphériques (spokes).
- **Multihoming** — Raccordement d’un site à plusieurs accès ou opérateurs.

## Teste-toi

**Pourquoi un appel vidéo entre deux agences d’un WAN en étoile est-il parfois de mauvaise qualité, alors que chaque agence a un bon accès ?**

<details><summary>Voir le corrigé</summary>

Le flux passe par le **siège** : il traverse deux liens WAN au lieu d’un, ce qui double la latence et consomme la capacité du siège. Un maillage dynamique (tunnels directs entre agences) règle ce problème.

</details>

<!-- approfondir -->

## Dimensionner un lien WAN

1. **Mesurer** le trafic actuel (NetFlow, supervision) aux heures de pointe, pas en moyenne.
2. **Lister** les flux critiques et leurs besoins : voix (débit et gigue), applications métier (latence), sauvegardes (volume, plage horaire).
3. **Ajouter** la croissance et les usages cloud (visioconférence, SaaS).
4. **Prévoir la QoS** : sur un lien WAN, la congestion est normale ; c’est la QoS qui décide qui passe d’abord. Voir [QoS](qos.md).

## Ce que la distance change

Latence aller-retour typique : Paris–Lyon ≈ 10 ms, Paris–New York ≈ 75 ms, Paris–Singapour ≈ 160 ms. Les applications bavardes (beaucoup d’allers-retours, comme SMB ou certains clients lourds) deviennent lentes au-delà de quelques dizaines de millisecondes, quel que soit le débit. Solutions : publier l’application en mode Web ou bureau à distance, mettre des caches locaux, rapprocher les données.

## Exercice

**Une entreprise de 40 agences veut relier toutes ses agences entre elles en maillage complet avec IPsec statique. Combien de tunnels faut-il, et quelle alternative ?**

<details><summary>Voir le corrigé</summary>

40 × 39 / 2 = **780 tunnels** à configurer et maintenir. Alternative : une architecture en étoile avec tunnels directs **dynamiques** (DMVPN) ou un **SD-WAN** qui crée et gère ces tunnels automatiquement.

</details>
