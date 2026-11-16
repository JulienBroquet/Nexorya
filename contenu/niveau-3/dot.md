---
titre: DoT
nom: DNS over TLS
idee: DoT chiffre les requêtes DNS dans une connexion TLS dédiée, sur le port 853 ; personne sur le chemin ne peut lire ni modifier les noms demandés.
osi: "7 (TCP 853)"
duree: [5, 10]
prerequis: [dns, tls]
retenir:
  - DoT chiffre les requêtes DNS sur un **port dédié, 853** — facile à identifier et à filtrer.
  - Il protège la **confidentialité** des requêtes ; DNSSEC protège l’**authenticité** des réponses — les deux sont complémentaires.
  - En entreprise, on l’utilise surtout **entre le résolveur interne et Internet**, pas depuis chaque poste.
---

## Le problème

Le DNS classique circule **en clair**. Sur un Wi-Fi public, chez un fournisseur d’accès ou sur n’importe quel lien, on peut lire tous les noms que tu demandes — c’est-à-dire tous les sites que tu visites — et même falsifier les réponses.

> [!IMPORTANT] L’idée en une phrase
> DoT envoie les questions DNS dans une connexion TLS vers un résolveur de confiance : le contenu devient illisible pour les intermédiaires.

## DoT ou DoH ?

| | DoT | DoH |
|---|---|---|
| Transport | TLS sur TCP **853** | HTTPS sur **443** |
| Visibilité pour l’administrateur | on voit qu’il y a du DNS chiffré, on peut l’autoriser ou le bloquer | se mélange au trafic Web ordinaire |
| Utilisation typique | systèmes (Android « DNS privé »), résolveurs vers l’extérieur | navigateurs |

## Les mots à connaître

- **DoT** — *DNS over TLS*, requêtes DNS chiffrées par TLS sur le port 853.
- **Résolveur de confiance** — Serveur DNS auquel on confie ses requêtes et dont on vérifie l’identité par son certificat.

## Teste-toi

**DoT empêche-t-il un fournisseur d’accès de savoir quels sites tu consultes ?**

<details><summary>Voir le corrigé</summary>

**En partie seulement.** Les requêtes DNS deviennent illisibles, mais le fournisseur voit toujours les **adresses IP** contactées et, souvent, le nom du site dans le **SNI** de la connexion TLS (sauf avec Encrypted Client Hello).

</details>

<!-- approfondir -->

## Configurer un résolveur d’entreprise en DoT vers l’extérieur (Unbound)

```text
server:
    tls-cert-bundle: /etc/ssl/certs/ca-certificates.crt
forward-zone:
    name: "."
    forward-tls-upstream: yes
    forward-addr: 9.9.9.9@853#dns.quad9.net
    forward-addr: 149.112.112.112@853#dns.quad9.net
```

Le nom après `#` sert à vérifier le certificat du résolveur distant.

## Vérifier

```bash
$ kdig -d @9.9.9.9 +tls-ca +tls-host=dns.quad9.net exemple.fr
;; TLS session (TLS1.3)-(ECDHE-X25519)-(ECDSA-SECP256R1-SHA256)-(AES-256-GCM)
```

## Politique d’entreprise

- Autoriser le TCP 853 sortant **uniquement** depuis les résolveurs internes.
- Bloquer le TCP 853 depuis les postes, pour qu’ils utilisent le résolveur interne (filtrage, journaux, noms internes).
- Sur les téléphones gérés, configurer le « DNS privé » vers un résolveur de l’entreprise si le télétravail l’exige.

## Exercice

**Un téléphone Android en mode « DNS privé automatique » se connecte au Wi-Fi de l’entreprise. Le pare-feu bloque le TCP 853. Que se passe-t-il ?**

<details><summary>Voir le corrigé</summary>

En mode **automatique**, Android tente DoT vers le résolveur fourni par le réseau ; en cas d’échec, il **revient au DNS classique** : tout fonctionne. En mode **strict** (nom d’hôte imposé), il n’y a pas de repli : la résolution échoue tant que le 853 est bloqué.

</details>
