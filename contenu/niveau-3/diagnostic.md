---
titre: Démontrer une panne
nom: Les outils de diagnostic Windows et Linux
idee: Pour dépanner vite, on remonte les couches avec une poignée d’outils — adresse, voisin, route, nom, port, application — et l’on garde la preuve de chaque étape.
osi: "1 à 7"
duree: [10, 20]
cle: true
prerequis: [commandes, osi]
retenir:
  - "L’ordre — **adresse** (ipconfig / ip a) → **voisin** (arp / ip neigh) → **route** (route print / ip route) → **nom** (nslookup / dig) → **port** (Test-NetConnection / nc) → **application** (curl)."
  - Toujours comparer avec **un poste qui fonctionne**.
  - "Une **capture** (Wireshark, tcpdump) tranche les débats — elle montre ce qui part et ce qui revient."
  - Noter la **preuve** de chaque étape — sortie de commande, heure, poste, destination.
---

## Le problème : « ça ne marche pas »

Un utilisateur appelle : « l’application de facturation ne fonctionne plus ». Redémarrer le poste, puis le switch, puis le serveur, au hasard, fait perdre du temps et ne prouve rien. Un professionnel **localise** la panne avec une méthode, et **démontre** où elle se trouve.

> [!IMPORTANT] L’idée en une phrase
> On vérifie les étapes dans l’ordre où une connexion se construit, chacune avec un outil précis ; la première étape qui échoue désigne la zone à corriger.

## La méthode en six questions

| Question | Windows | Linux / macOS | Si ça échoue… |
|---|---|---|---|
| 1. Ai-je une adresse correcte ? | `ipconfig /all` | `ip a` / `ifconfig` | câble, Wi-Fi, VLAN, DHCP |
| 2. Je joins ma passerelle ? | `ping <passerelle>`, `arp -a` | `ping`, `ip neigh` | réseau local : port, VLAN, switch |
| 3. Ai-je une route vers la destination ? | `route print`, `tracert` | `ip route get <ip>`, `traceroute` | routage, VPN, pare-feu en chemin |
| 4. Le nom est-il traduit ? | `nslookup`, `Resolve-DnsName` | `dig`, `getent hosts` | DNS |
| 5. Le port du service est-il ouvert ? | `Test-NetConnection -Port` | `nc -zv`, `curl -v telnet://h:p` | pare-feu, service arrêté |
| 6. L’application répond-elle bien ? | navigateur, `curl.exe -v` | `curl -v` | application, certificat, droits |

> [!TIP]
> Teste la même chose **depuis un poste qui fonctionne**. Si l’autre poste réussit à l’étape 5 et pas celui de l’utilisateur, le problème est lié à ce poste (pare-feu local, proxy, VLAN, droits), pas au serveur.

## Exemple complet : l’application de facturation

```powershell
PS> Resolve-DnsName facturation.exemple.fr
Name                      Type   TTL   IPAddress
facturation.exemple.fr    A      3600  10.20.0.40          # étape 4 : OK

PS> Test-NetConnection facturation.exemple.fr -Port 443
ComputerName     : facturation.exemple.fr
RemoteAddress    : 10.20.0.40
PingSucceeded    : True                                    # étapes 1 à 3 : OK
TcpTestSucceeded : False                                   # étape 5 : ÉCHEC
```

Le nom est traduit, le serveur répond au ping, mais le **port 443 n’est pas joignable**. On a localisé la panne : soit le service Web est arrêté sur le serveur, soit un pare-feu bloque le port. On le vérifie depuis un poste du même réseau que le serveur : si le port y est ouvert, c’est un pare-feu sur le chemin.

## Les mots à connaître

- **Diagnostic par couches** — Méthode qui vérifie les couches réseau dans l’ordre pour localiser une panne.
- **Capture réseau** — Enregistrement des paquets qui passent sur une interface, pour les analyser.
- **Wireshark** — Logiciel graphique de capture et d’analyse de paquets ; tcpdump est son équivalent en ligne de commande.

## Teste-toi

**`Test-NetConnection srv -Port 445` renvoie `PingSucceeded: False` et `TcpTestSucceeded: True`. Le serveur est-il joignable ?**

<details><summary>Voir le corrigé</summary>

**Oui** : la connexion TCP au port 445 réussit. Le ping échoue seulement parce que le serveur (ou un pare-feu) **bloque l’ICMP**. Un ping qui échoue n’est jamais une preuve suffisante.

</details>

<!-- approfondir -->

## La boîte à outils détaillée

### Windows (PowerShell)

```powershell
Get-NetIPConfiguration -Detailed                    # adresses, passerelle, DNS, profil
Get-NetNeighbor -State Reachable,Stale              # cache ARP / NDP
Find-NetRoute -RemoteIPAddress 10.20.0.40           # route et interface choisies
Resolve-DnsName facturation.exemple.fr -Server 10.99.0.53 -DnsOnly
Test-NetConnection 10.20.0.40 -Port 443 -InformationLevel Detailed
Test-NetConnection 10.20.0.40 -TraceRoute
Get-NetTCPConnection -RemotePort 443 -State Established
netsh winhttp show proxy                            # proxy système
pathping 10.20.0.40                                 # pertes par saut
pktmon start --capture --comp nics -f C:\cap.etl    # capture intégrée à Windows
```

### Linux

```bash
ip -br a                         # adresses, résumé
ip route get 10.20.0.40          # route et adresse source utilisées
ip neigh                         # voisins
resolvectl query facturation.exemple.fr    # ou dig, selon le système
nc -zv 10.20.0.40 443            # test de port TCP
curl -v https://facturation.exemple.fr/
mtr -rwc 50 10.20.0.40           # latence et pertes par saut
ss -tanp                         # connexions et processus
sudo tcpdump -ni eth0 host 10.20.0.40 and port 443 -w cap.pcap
```

## Lire une capture pour trancher

On capture **sur le poste**, puis si possible **côté serveur**, pendant que l’on reproduit le problème.

| Ce que montre la capture du poste | Interprétation |
|---|---|
| SYN envoyés, aucune réponse | les paquets sont perdus ou filtrés en route, ou la réponse ne revient pas |
| SYN envoyé, **RST** reçu | le serveur (ou un pare-feu) refuse explicitement : port fermé |
| SYN, SYN-ACK, ACK, puis **TLS Alert** | problème de certificat ou de version TLS |
| Connexion établie, requête HTTP, réponse **4xx / 5xx** | l’application répond : problème applicatif |
| Requêtes DNS sans réponse | résolveur injoignable ou UDP 53 filtré |

Si la capture **côté serveur** montre les SYN arrivant et les SYN-ACK repartant, mais que le poste ne les reçoit jamais : le **chemin retour** est en cause (route asymétrique, pare-feu qui ne voit qu’un sens).

## Documenter la preuve

Un bon ticket d’incident contient, pour chaque étape testée : la **commande**, sa **sortie**, l’**heure**, la **machine source** et la **destination**. C’est ce qui permet de transmettre le dossier à l’équipe suivante (système, sécurité, opérateur) sans qu’elle recommence tout, et d’éviter les « chez nous tout va bien ».

```text
2026-11-15 09:41 — Poste PC-COMPTA-12 (10.10.0.57) → facturation.exemple.fr (10.20.0.40)
- DNS : OK (Resolve-DnsName → 10.20.0.40)
- ICMP : OK (4/4, 1 ms)
- TCP 443 : ÉCHEC (Test-NetConnection : TcpTestSucceeded False)
- Depuis SRV-ADMIN-01 (10.20.0.5, même VLAN que le serveur) : TCP 443 OK
- Capture poste : SYN ×3 sans réponse
→ Conclusion : filtrage entre 10.10.0.0/24 et 10.20.0.40:443. Transmis à l’équipe pare-feu.
```

## Exercices

**1.** Un poste obtient une adresse, joint sa passerelle et Internet par IP, mais « aucun site ne fonctionne ». `nslookup www.exemple.fr` répond par délai d’attente. Quelle est l’étape en échec, et quelles sont les deux causes les plus probables ?

<details><summary>Voir le corrigé</summary>

L’étape 4 (**DNS**). Causes probables : le poste utilise un **serveur DNS injoignable ou arrêté** (mauvaise option DHCP, serveur en panne), ou le **trafic DNS est filtré** (UDP/TCP 53). Tester avec `nslookup www.exemple.fr <autre résolveur>` pour distinguer les deux.

</details>

**2.** La capture côté serveur montre les SYN du client et les SYN-ACK du serveur. La capture côté client ne montre que les SYN. Où chercher ?

<details><summary>Voir le corrigé</summary>

Sur le **chemin retour** : la réponse du serveur part, mais n’arrive jamais. Typiquement, le serveur a une passerelle ou une route différente de celle par laquelle la requête est arrivée (**routage asymétrique**), et un pare-feu à états jette la réponse qu’il n’a pas vue partir, ou elle prend un chemin qui ne mène pas au client.

</details>
