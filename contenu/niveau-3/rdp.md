---
titre: RDP
nom: Remote Desktop Protocol
idee: RDP affiche à distance le bureau d’un ordinateur Windows et transmet clavier et souris ; c’est l’outil courant du support et de l’administration des serveurs Windows.
osi: "7 (TCP et UDP 3389)"
duree: [5, 10]
prerequis: [tcp]
retenir:
  - RDP utilise le **port 3389** (TCP, et UDP pour de meilleures performances).
  - Il ne faut **jamais** exposer RDP directement sur Internet — passer par un **VPN** ou une **passerelle RD** avec MFA.
  - "**NLA** exige l’authentification avant d’ouvrir la session graphique."
---

## Le problème

Le support informatique doit voir l’écran d’un utilisateur, ou un administrateur doit gérer un serveur Windows situé dans un datacenter. Il faut transmettre l’image d’un bureau, et en retour le clavier et la souris.

> [!IMPORTANT] L’idée en une phrase
> RDP transmet le bureau d’un ordinateur Windows à un autre, de façon chiffrée, comme si l’on était assis devant.

## Le risque n°1 : RDP ouvert sur Internet

Les attaquants balaient en permanence Internet à la recherche du port 3389. Un serveur RDP exposé subit des milliers de tentatives de connexion par jour ; c’est l’une des premières portes d’entrée des **rançongiciels**.

| À éviter | À faire |
|---|---|
| Redirection du port 3389 sur la box ou le pare-feu | accès par **VPN** avec MFA, ou par **passerelle Bureau à distance** (HTTPS 443) avec MFA |
| Comptes administrateurs avec mot de passe simple | comptes nominatifs, mots de passe forts, verrouillage après échecs |
| NLA désactivé | **NLA** activé |

```topologie
titre: Accéder à un poste à distance sans l’exposer à Internet
U portable 0,0 "Utilisateur" "à domicile"
INT nuage 1.4,0 "Internet"
GW parefeu 2.8,0 "Passerelle RDP" "HTTPS 443 + MFA"
SRV serveur 4.2,0 "Poste ou serveur" "TCP 3389, réseau interne"
U -- INT
INT ++ GW "TLS"
GW -- SRV "RDP"
```

## Les mots à connaître

- **RDP** — Protocole de bureau à distance de Microsoft.
- **NLA** — *Network Level Authentication*, authentification exigée avant l’ouverture de la session graphique.
- **Passerelle RD** — Serveur qui encapsule RDP dans HTTPS pour un accès distant contrôlé.

## Teste-toi

**Une PME a redirigé le port 3389 de sa box vers son serveur pour que le gérant travaille de chez lui. Quel est le risque, et que proposer ?**

<details><summary>Voir le corrigé</summary>

Le serveur est **exposé à tout Internet** : attaques par force brute en continu, exploitation de vulnérabilités, risque élevé de rançongiciel. Proposer un **VPN** avec authentification forte (ou une passerelle RD avec MFA), et fermer la redirection.

</details>

<!-- approfondir -->

## Diagnostiquer une connexion RDP

```powershell
PS> Test-NetConnection srv-app01 -Port 3389
TcpTestSucceeded : True
PS> Get-NetTCPConnection -LocalPort 3389 -State Established
PS> Get-WinEvent -LogName "Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational" -MaxEvents 20
```

| Symptôme | Piste |
|---|---|
| Port 3389 fermé | service « Services Bureau à distance » arrêté, pare-feu Windows, pare-feu réseau |
| Connexion acceptée puis refusée | l’utilisateur n’est pas dans le groupe « Utilisateurs du Bureau à distance », NLA et compte expiré |
| Image saccadée | latence et pertes : RDP utilise UDP 3389 si possible ; vérifier qu’il n’est pas bloqué |
| Erreur de certificat | certificat auto-signé du serveur : déployer un certificat de l’autorité interne |

## Journaliser et surveiller

Les ouvertures de session à distance apparaissent dans le journal de sécurité Windows (événement **4624**, type de connexion **10**). Les échecs (4625) en rafale signalent une tentative de force brute : à remonter au SIEM.

## Exercice

**Un utilisateur se plaint que sa session RDP vers un serveur distant est saccadée. Le TCP 3389 fonctionne, mais l’UDP 3389 est bloqué par le pare-feu. Quel est l’effet ?**

<details><summary>Voir le corrigé</summary>

RDP **revient à TCP seul** : la session fonctionne, mais chaque perte provoque des retransmissions et des ralentissements visibles, surtout sur un lien lointain ou chargé. Autoriser l’UDP 3389 (dans le VPN ou via la passerelle) améliore nettement la fluidité.

</details>
