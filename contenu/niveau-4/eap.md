---
titre: EAP
nom: Extensible Authentication Protocol
idee: EAP est une enveloppe qui transporte différentes méthodes d’authentification (mot de passe protégé, certificat…) entre un appareil et le serveur, sans que le switch ou la borne ait besoin de les comprendre.
osi: "2 (transporté par EAPoL puis RADIUS)"
duree: [7, 14]
prerequis: [802-1x]
retenir:
  - EAP n’est pas une méthode, c’est un **cadre** qui transporte des méthodes.
  - "**PEAP / EAP-TTLS** — un tunnel TLS protège un échange par mot de passe ; **EAP-TLS** — certificats des deux côtés."
  - Dans tous les cas, le client doit **vérifier le certificat du serveur**, sinon un faux serveur peut récupérer les identifiants.
---

## Le problème

Il existe de nombreuses façons de s’authentifier : mot de passe, certificat, carte à puce, code à usage unique. Si le switch et la borne devaient toutes les comprendre, il faudrait les mettre à jour à chaque nouvelle méthode.

> [!IMPORTANT] L’idée en une phrase
> EAP est une **enveloppe standard** : le switch ou la borne la transmettent sans l’ouvrir, et seuls le poste et le serveur se mettent d’accord sur la méthode utilisée à l’intérieur.

## Les méthodes courantes

| Méthode | Ce que prouve le client | Sécurité | Remarque |
|---|---|---|---|
| **EAP-TLS** | un **certificat** | excellente | nécessite une PKI pour les postes ; voir [EAP-TLS](eap-tls.md) |
| **PEAP** (MSCHAPv2) | identifiant + mot de passe, dans un tunnel TLS | bonne si le certificat du serveur est vérifié | très répandue avec Active Directory ; en recul (Credential Guard) |
| **EAP-TTLS** | mot de passe (ou autre), dans un tunnel TLS | bonne si le certificat du serveur est vérifié | courante hors Windows |
| EAP-FAST, TEAP | variantes avec tunnel | bonnes | TEAP permet machine + utilisateur |
| EAP-MD5 | mot de passe haché | **faible** | à proscrire |

## Les mots à connaître

- **EAP** — Cadre de transport des méthodes d’authentification, utilisé par 802.1X.
- **Méthode EAP** — Façon précise de s’authentifier dans EAP (EAP-TLS, PEAP…).
- **PEAP** — Méthode qui protège un échange par mot de passe dans un tunnel TLS.

## Teste-toi

**Un poste configuré en PEAP ne vérifie pas le certificat du serveur. Un attaquant installe une fausse borne avec le même nom de réseau. Que risque l’utilisateur ?**

<details><summary>Voir le corrigé</summary>

Le poste ouvre le tunnel avec le **faux serveur** de l’attaquant et lui envoie l’échange MSCHAPv2, que l’attaquant peut tenter de casser pour retrouver le **mot de passe**. La vérification du certificat du serveur (nom et autorité) est indispensable.

</details>

<!-- approfondir -->

## Le trajet d’un échange EAP

```sequence
titre: PEAP, du poste au serveur
Poste | Switch ou borne | Serveur RADIUS
Switch ou borne -> Poste : EAP-Request/Identity
Poste --> Switch ou borne : EAP-Response/Identity : « anonymous@exemple.fr »
Switch ou borne -> Serveur RADIUS : Access-Request (EAP encapsulé)
Serveur RADIUS --> Poste : début de PEAP : certificat du serveur (via Access-Challenge)
note Poste : vérifie le certificat : nom attendu, autorité de confiance
Poste -> Serveur RADIUS : tunnel TLS établi, identité réelle et MSCHAPv2 à l’intérieur
Serveur RADIUS --> Switch ou borne : Access-Accept + clés de session (Wi-Fi) + VLAN
Switch ou borne --> Poste : EAP-Success
```

L’identité **extérieure** (`anonymous@exemple.fr`) circule en clair ; la vraie identité ne circule que dans le tunnel. C’est la protection de la vie privée des méthodes à tunnel.

## Configurer correctement le poste

La vérification du serveur ne doit pas être laissée à l’utilisateur (qui clique sur « Se connecter » face à n’importe quel certificat). On la **déploie par stratégie** (GPO, MDM) :

- autorités de confiance : uniquement l’autorité interne qui a signé le certificat du serveur RADIUS ;
- nom du serveur attendu : `radius.exemple.fr` ;
- ne pas permettre à l’utilisateur d’accepter un nouveau serveur.

## PEAP-MSCHAPv2 et Windows Credential Guard

Sur les versions récentes de Windows, **Credential Guard** est activé par défaut et **empêche** l’utilisation des identifiants de session pour PEAP-MSCHAPv2. Les entreprises migrent vers **EAP-TLS** (certificats) ou vers des méthodes compatibles. C’est un changement de fond à planifier.

## Exercice

**Pourquoi l’identité extérieure « anonymous@exemple.fr » garde-t-elle le nom de domaine ?**

<details><summary>Voir le corrigé</summary>

Le **domaine** (le *realm*) permet aux serveurs RADIUS de **router** la demande vers le bon serveur (par exemple dans des réseaux fédérés comme eduroam, où l’utilisateur d’une université se connecte dans une autre). Seule la partie utilisateur est anonymisée.

</details>
