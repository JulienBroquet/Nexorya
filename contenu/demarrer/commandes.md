---
titre: Les commandes de base
nom: ipconfig, ping, tracert, nslookup
idee: Quatre commandes, disponibles sur tous les ordinateurs, suffisent à savoir où une connexion échoue.
duree: [12]
retenir:
  - "`ipconfig /all` (Windows) ou `ip a` (Linux) — ai-je une adresse, une passerelle et un DNS ?"
  - "`ping` — est-ce que j’atteins cette machine ?"
  - "`tracert` / `traceroute` — par où passe le chemin, et où s’arrête-t-il ?"
  - "`nslookup` — le nom est-il traduit en adresse IP ?"
---

## Le problème : « Internet ne marche pas »

Plutôt que de redémarrer au hasard, un professionnel **pose des questions dans l’ordre** et y répond avec des commandes. Bonne nouvelle : quatre commandes suffisent pour commencer, et elles existent sur tous les ordinateurs.

Pour les essayer :

- **Windows** : touche Windows, tape `cmd`, puis Entrée.
- **macOS** : ouvre l’application Terminal.
- **Linux** : ouvre un terminal.

## 1. Ai-je une adresse ? — `ipconfig` ou `ip a`

```powershell
C:\> ipconfig /all

Carte Ethernet Ethernet :
   Adresse physique . . . . . . . . . . . : 3C-22-FB-1A-09-7E
   DHCP activé. . . . . . . . . . . . . . : Oui
   Adresse IPv4. . . . . . . . . . . . . .: 192.168.1.20
   Masque de sous-réseau. . . . . . . . . : 255.255.255.0
   Passerelle par défaut. . . . . . . . . : 192.168.1.1
   Serveurs DNS. . . . . . . . . . . . . .: 192.168.1.1
```

Ce que tu dois vérifier :

- **Adresse IPv4** : elle existe et ne commence pas par `169.254` (sinon, le DHCP n’a pas répondu).
- **Passerelle par défaut** : elle est renseignée (sinon, impossible de sortir du réseau local).
- **Serveurs DNS** : au moins un (sinon, les noms ne seront pas traduits).
- **Adresse physique** : c’est l’adresse MAC de la carte réseau.

Sous Linux, `ip a` affiche les adresses et `ip route` la passerelle (ligne `default via …`). Sous macOS, `ifconfig` et `netstat -nr`.

## 2. Est-ce que j’atteins cette machine ? — `ping`

`ping` envoie un petit message et attend une réponse. On teste en partant du plus proche :

```powershell
C:\> ping 192.168.1.1

Réponse de 192.168.1.1 : octets=32 temps=2 ms TTL=64
Réponse de 192.168.1.1 : octets=32 temps=1 ms TTL=64
Réponse de 192.168.1.1 : octets=32 temps=1 ms TTL=64
Réponse de 192.168.1.1 : octets=32 temps=2 ms TTL=64
Paquets : envoyés = 4, reçus = 4, perdus = 0 (perte 0%)
```

- **Réponse** et **temps** en millisecondes : la machine est joignable, et l’on voit le délai aller-retour.
- **Délai d’attente de la demande dépassé** : pas de réponse. La machine est éteinte, injoignable… ou elle bloque volontairement le ping (beaucoup de pare-feu le font).

> [!TIP] La méthode de l’escalier
> Fais `ping` dans cet ordre : **ta passerelle** (la box), puis **une adresse sur Internet** (par exemple `1.1.1.1`), puis **un nom** (`ping www.exemple.fr`). La première marche qui échoue t’indique où chercher. Si `ping 1.1.1.1` fonctionne mais pas `ping www.exemple.fr`, le problème vient du DNS.

## 3. Par où passe le chemin ? — `tracert` ou `traceroute`

```powershell
C:\> tracert 1.1.1.1

  1     1 ms     1 ms     1 ms  192.168.1.1
  2     6 ms     5 ms     6 ms  10.142.0.1
  3     8 ms     7 ms     8 ms  198.51.100.33
  4     9 ms     9 ms     9 ms  1.1.1.1
Itinéraire déterminé.
```

Chaque ligne est un **routeur** traversé, avec le délai pour l’atteindre. Si la liste s’arrête à la ligne 1 et affiche ensuite des astérisques `* * *`, ta box ne parvient pas à joindre ton fournisseur d’accès. Sous Linux et macOS, la commande s’appelle `traceroute`.

## 4. Le nom est-il traduit ? — `nslookup`

```powershell
C:\> nslookup www.exemple.fr

Serveur :   box.home
Address:    192.168.1.1

Réponse ne faisant pas autorité :
Nom :       www.exemple.fr
Address:    203.0.113.10
```

Si tu obtiens une adresse, le DNS fonctionne. Si tu obtiens une erreur (« Non-existent domain », « timeout »), le problème vient du nom ou du serveur DNS.

## La méthode complète

| Question | Commande | Si ça échoue, regarder… |
|---|---|---|
| Ai-je une adresse ? | `ipconfig /all` | Câble, Wi-Fi, service DHCP |
| J’atteins ma passerelle ? | `ping 192.168.1.1` | Réseau local : câble, Wi-Fi, switch |
| J’atteins Internet ? | `ping 1.1.1.1` | Box, fournisseur d’accès |
| Les noms sont-ils traduits ? | `nslookup www.exemple.fr` | Serveur DNS |
| Le site répond-il ? | le navigateur | Le site lui-même |

## Les mots à connaître

- **ping** — Commande qui envoie un petit message (ICMP) à une machine et mesure le temps de réponse.
- **traceroute** — Commande qui affiche la liste des routeurs traversés jusqu’à une destination (`tracert` sous Windows).
- **nslookup** — Commande qui interroge un serveur DNS pour traduire un nom en adresse IP.
- **Latence** — Temps mis par un message pour faire l’aller-retour, en millisecondes.

## Teste-toi

**1.** `ping 192.168.1.1` fonctionne, `ping 1.1.1.1` fonctionne, mais `ping www.exemple.fr` répond « hôte inconnu ». Où est le problème ?

<details><summary>Voir la réponse</summary>

**Le DNS.** Le réseau local et l’accès à Internet fonctionnent (les deux premiers ping). Seule la traduction du nom échoue. Vérifie les serveurs DNS dans `ipconfig /all` et teste avec `nslookup`.

</details>

**2.** `ipconfig` montre l’adresse `169.254.88.3` et aucune passerelle. Que fais-tu en premier ?

<details><summary>Voir la réponse</summary>

L’ordinateur n’a pas reçu de réponse DHCP. Vérifie d’abord la **connexion physique** : câble branché et voyant allumé, ou connexion au bon réseau Wi-Fi. Puis, si tout est correct, vérifie que la box (ou le serveur DHCP de l’entreprise) fonctionne. Sous Windows, `ipconfig /renew` redemande une adresse.

</details>

**3.** Tu es prêt pour la suite ?

<details><summary>Voir la réponse</summary>

Si tu as lu les huit fiches de « Je débute », tu as tout ce qu’il faut pour commencer le [niveau 1](../niveau-1/index.html). Tu y découvriras en détail les câbles, les switches et les VLAN. Garde le [lexique](../lexique.html) à portée de main.

</details>
