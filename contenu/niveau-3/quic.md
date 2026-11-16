---
titre: QUIC
nom: Le transport moderne de HTTP/3
idee: QUIC réunit en un seul protocole, au-dessus d’UDP, ce que faisaient TCP et TLS — connexion fiable, chiffrement, flux multiples — avec des connexions plus rapides à établir.
osi: "4 (sur UDP 443)"
duree: [6, 14]
prerequis: [tcp, tls, udp]
retenir:
  - QUIC fonctionne sur **UDP 443** et chiffre **presque tout**, y compris ses en-têtes de contrôle.
  - Plusieurs flux indépendants — une perte ne bloque que le flux concerné.
  - Une connexion survit à un **changement de réseau** (Wi-Fi → 4G).
  - Si UDP 443 est bloqué, les navigateurs **reviennent à TCP** — c’est pourquoi certains réseaux le bloquent volontairement.
---

## Le problème : TCP + TLS, c’est lent à démarrer

Pour charger une page en HTTPS classique, il faut d’abord la poignée de main TCP, puis la négociation TLS : plusieurs allers-retours avant la première donnée. Et avec HTTP/2, toutes les requêtes passent dans **une seule** connexion TCP : un seul paquet perdu bloque tout le monde jusqu’à sa retransmission.

> [!IMPORTANT] L’idée en une phrase
> QUIC refait TCP et TLS ensemble, au-dessus d’UDP : la connexion s’ouvre en un aller-retour, chaque requête a son propre flux, et une perte n’arrête que le flux touché.

## Ce que QUIC apporte

| Problème avec TCP + TLS | Réponse de QUIC |
|---|---|
| 2 à 3 allers-retours avant la première donnée | 1 aller-retour (0 en reprise de session) |
| Une perte bloque tous les flux HTTP/2 | flux indépendants |
| Changer de réseau casse la connexion (l’adresse IP change) | identifiant de connexion indépendant de l’adresse |
| En-têtes TCP visibles et modifiables par les équipements intermédiaires | en-têtes chiffrés : le protocole peut évoluer sans être cassé par le réseau |

## Les mots à connaître

- **QUIC** — Protocole de transport chiffré et fiable construit sur UDP, utilisé par HTTP/3.
- **HTTP/3** — Version de HTTP transportée par QUIC.
- **Blocage en tête de file** — Situation où une donnée perdue retarde toutes les suivantes ; *head-of-line blocking*.

## Teste-toi

**Un pare-feu d’entreprise bloque UDP 443. Les utilisateurs peuvent-ils encore consulter les sites qui proposent HTTP/3 ?**

<details><summary>Voir le corrigé</summary>

**Oui.** Les navigateurs tentent QUIC, constatent l’échec, et reviennent à **HTTP/2 sur TCP 443**. Certaines entreprises bloquent volontairement QUIC pour que tout le trafic Web passe par leur proxy ou leur inspection TLS, qui ne gèrent pas toujours QUIC.

</details>

<!-- approfondir -->

## Comment un navigateur découvre HTTP/3

La première visite se fait en HTTP/2 sur TCP. Le serveur annonce dans sa réponse qu’il propose aussi HTTP/3 (en-tête `Alt-Svc: h3=":443"`, ou enregistrement DNS **HTTPS**). Les connexions suivantes tentent QUIC.

```bash
$ curl -sI https://www.exemple.fr | grep -i alt-svc
alt-svc: h3=":443"; ma=86400
$ curl --http3 -sI https://www.exemple.fr | head -1     # nécessite un curl compilé avec HTTP/3
HTTP/3 200
```

## Conséquences pour l’exploitation

- **Visibilité réduite** : un pare-feu ne voit plus l’état de la connexion (pas de SYN, de FIN) et ne peut lire que peu d’informations. Les outils qui reposaient sur l’observation de TCP (mesure de latence passive, détection de retransmissions) perdent leur source.
- **Filtrage** : les NGFW récents savent identifier QUIC et parfois l’inspecter ; sinon, la politique est souvent de le bloquer pour forcer le repli en TCP.
- **Équilibrage de charge** : l’identifiant de connexion permet de router un client vers le même serveur même si son adresse change ; les répartiteurs doivent le comprendre.
- **Performances** : QUIC est traité dans l’application (en espace utilisateur), ce qui coûte plus de processeur que TCP traité par le noyau et les cartes réseau.

## Exercice

**Un utilisateur sur son téléphone passe du Wi-Fi du bureau à la 4G en plein appel vidéo dans le navigateur. Avec QUIC, que se passe-t-il pour la connexion, et pourquoi ?**

<details><summary>Voir le corrigé</summary>

La connexion **continue** : QUIC identifie la connexion par un **identifiant** propre, et non par le couple adresses/ports. Quand l’adresse change, le client poursuit avec le même identifiant, après une validation du nouveau chemin. Avec TCP, la connexion aurait été coupée, puis rouverte.

</details>
