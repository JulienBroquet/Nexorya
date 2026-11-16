---
titre: DoH
nom: DNS over HTTPS
idee: DoH envoie les requêtes DNS dans du HTTPS ordinaire ; c’est excellent pour la vie privée sur un réseau public, mais en entreprise, cela peut contourner le DNS interne et ses protections.
osi: "7 (HTTPS 443)"
duree: [5, 10]
prerequis: [dns, https]
retenir:
  - DoH utilise le **port 443**, comme le Web — il est difficile à distinguer et à bloquer.
  - Un navigateur en DoH vers un service public **contourne** le résolveur de l’entreprise (filtrage, journaux, noms internes).
  - "En entreprise — **politique** des navigateurs, domaine canari, blocage des résolveurs DoH publics connus."
---

## Le problème

L’entreprise s’appuie sur son résolveur DNS interne pour **bloquer** les domaines malveillants, **journaliser** les requêtes (indispensable pour enquêter) et résoudre les **noms internes**. Si un navigateur envoie ses requêtes DNS, chiffrées, directement à un service public, tout cela disparaît pour ce navigateur.

> [!IMPORTANT] L’idée en une phrase
> DoH cache les requêtes DNS dans le trafic Web chiffré ; il protège l’utilisateur d’un réseau espion, mais prive l’entreprise de sa visibilité si elle ne le maîtrise pas.

```topologie
titre: Trois façons d’envoyer une question DNS
PC pc 0,1 "Poste"
R1 serveur 3,0 "DNS classique" "UDP 53, lisible par tous"
R2 serveur 3,1 "DoT" "TCP 853, chiffré, port reconnaissable"
R3 serveur 3,2 "DoH" "HTTPS 443, chiffré, mêlé au trafic Web"
PC -- R1
PC ++ R2
PC ++ R3
```

## Les mots à connaître

- **DoH** — *DNS over HTTPS*, requêtes DNS transportées dans HTTPS.
- **Domaine canari** — Nom (`use-application-dns.net`) qu’un réseau peut bloquer pour demander à Firefox de ne pas activer DoH automatiquement.

## Teste-toi

**Un poste de l’entreprise contourne le filtrage DNS. Les journaux du résolveur interne ne montrent presque aucune requête de ce poste, alors qu’il navigue. Quelle hypothèse ?**

<details><summary>Voir le corrigé</summary>

Le navigateur (ou un logiciel) utilise **DoH** vers un résolveur public : ses requêtes DNS passent dans HTTPS, sans toucher le résolveur interne.

</details>

<!-- approfondir -->

## Maîtriser DoH en entreprise

| Mesure | Effet |
|---|---|
| Politiques des navigateurs (GPO, MDM) | désactiver DoH, ou le pointer vers un résolveur DoH **de l’entreprise** |
| Domaine canari | Firefox renonce à l’activation automatique de DoH |
| Blocage des résolveurs DoH publics connus (liste d’adresses ou catégorie NGFW) | empêche le contournement par la plupart des logiciels |
| Interdire le DNS sortant direct (53, 853) | oblige à passer par le résolveur interne |
| Détection | repérer les connexions vers des résolveurs DoH, les volumes anormaux |

Les logiciels malveillants utilisent aussi DoH pour dissimuler leurs communications : une politique claire sur les résolveurs autorisés est donc un point de sécurité, pas seulement de confort.

## Exercice

**Pourquoi proposer un résolveur DoH interne plutôt que d’interdire totalement DoH ?**

<details><summary>Voir le corrigé</summary>

Pour garder les **avantages** de DoH (requêtes chiffrées, notamment pour les postes nomades sur des réseaux publics) **sans perdre** le filtrage, les journaux et la résolution des noms internes. Les navigateurs gérés sont configurés pour utiliser ce résolveur, et les autres sont bloqués.

</details>
