---
titre: SSH
nom: Secure Shell
idee: SSH ouvre une session chiffrée vers un serveur ou un équipement réseau pour l’administrer à distance, en remplaçant Telnet qui faisait tout passer en clair.
osi: "7 (TCP 22)"
duree: [7, 16]
prerequis: [tcp]
retenir:
  - SSH chiffre la session **et** le mot de passe ; **Telnet** envoie tout en clair et doit être désactivé.
  - À la première connexion, le client mémorise **l’empreinte** du serveur — un changement inattendu doit alerter.
  - L’authentification par **clé** est plus sûre que par mot de passe.
  - "Sur un équipement réseau — SSH v2, accès limité aux réseaux d’administration, comptes nominatifs."
---

## Le problème : administrer à distance sans tout dévoiler

Un administrateur configure 200 switches répartis dans plusieurs bâtiments. Il ne va pas se brancher sur chacun avec un câble console. Il se connecte à distance… mais si la connexion est en clair, comme avec l’ancien **Telnet**, son mot de passe administrateur peut être capturé par n’importe qui sur le réseau.

> [!IMPORTANT] L’idée en une phrase
> SSH ouvre une ligne de commande à distance **chiffrée** : le mot de passe, les commandes et les réponses sont illisibles pour un observateur, et le client vérifie qu’il parle au bon serveur.

## Comment ça marche

1. Le client se connecte au port **22** du serveur.
2. Le serveur présente sa **clé d’hôte**. À la première connexion, le client affiche son **empreinte** et demande confirmation ; il la mémorise ensuite.
3. Les deux établissent une clé de chiffrement de session.
4. L’utilisateur s’authentifie : mot de passe, ou mieux, **clé personnelle**.
5. La session commence : tout est chiffré.

```text
$ ssh admin@sw-etage2.exemple.fr
The authenticity of host 'sw-etage2.exemple.fr (10.99.0.21)' can't be established.
ED25519 key fingerprint is SHA256:mT3k2bq1…
Are you sure you want to continue connecting (yes/no)? yes
admin@sw-etage2.exemple.fr's password:
SW-ETAGE2#
```

> [!WARNING]
> Si, lors d’une connexion ultérieure, SSH affiche « REMOTE HOST IDENTIFICATION HAS CHANGED », la clé du serveur a changé. C’est normal après une réinstallation de l’équipement… mais cela peut aussi être une **interception**. Vérifie avant d’accepter.

```sequence
titre: Ouvrir une session SSH sur un switch
Admin | Switch
Admin -> Switch : connexion TCP au port 22
Switch --> Admin : versions et algorithmes proposés
Admin -> Switch : échange de clés : un secret commun est établi
Switch --> Admin : clé publique du switch (empreinte)
note Admin : compare l’empreinte avec celle déjà connue : protection contre l’usurpation
Admin -> Switch : authentification (clé ou mot de passe), désormais chiffrée
Switch --> Admin : session ouverte : tout ce qui suit est chiffré
```

## Les mots à connaître

- **SSH** — *Secure Shell*, protocole d’accès à distance chiffré.
- **Telnet** — Ancien protocole d’accès à distance, sans chiffrement, à proscrire.
- **Clé d’hôte** — Clé qui identifie un serveur SSH ; son empreinte est mémorisée par les clients.
- **Authentification par clé** — Connexion prouvée par une clé privée détenue par l’utilisateur, plutôt que par un mot de passe.
- **Bastion** — Serveur intermédiaire par lequel passent obligatoirement les connexions d’administration.

## Teste-toi

**Pourquoi Telnet doit-il être désactivé même dans un réseau interne « de confiance » ?**

<details><summary>Voir le corrigé</summary>

Parce que tout y circule **en clair**, y compris les mots de passe administrateur. Un poste compromis, un port miroir mal placé ou une capture suffisent à les récupérer. Le réseau interne n’est pas un lieu sûr par principe.

</details>

<!-- approfondir -->

## Activer SSH sur un équipement Cisco

```cisco
hostname SW-ETAGE2
ip domain name exemple.fr
crypto key generate rsa modulus 3072
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
!
username admin privilege 15 algorithm-type scrypt secret Un-Mot-De-Passe-Long
!
ip access-list standard ADMIN-SEULEMENT
 permit 10.99.0.0 0.0.0.255
 deny any log
!
line vty 0 15
 transport input ssh
 login local
 access-class ADMIN-SEULEMENT in
 exec-timeout 10 0
```

- `transport input ssh` : refuse Telnet sur les lignes VTY.
- `access-class` : seules les machines du réseau d’administration peuvent se connecter.
- En production, l’authentification passe par un serveur **TACACS+** ou RADIUS (comptes nominatifs, traçabilité), avec un compte local de secours. Voir [AAA](../niveau-4/aaa.md).

> [!CAUTION]
> Appliquer `access-class` ou `transport input ssh` **à distance** peut te couper ton propre accès. Garde une session ouverte, prépare un accès console de secours, et utilise `reload in 10` avant les modifications risquées (le redémarrage programmé restaure la configuration sauvegardée si tu perds la main ; annule-le avec `reload cancel`).

## Authentification par clé

```bash
$ ssh-keygen -t ed25519 -C "alice@exemple.fr"
$ ssh-copy-id alice@srv-app01.exemple.fr
$ ssh alice@srv-app01.exemple.fr          # plus de mot de passe ; la clé privée peut être protégée par une phrase de passe
```

Bonnes pratiques côté serveurs Linux : désactiver la connexion directe de `root`, désactiver l’authentification par mot de passe une fois les clés déployées, et limiter les utilisateurs autorisés.

## Fonctions utiles

| Usage | Commande |
|---|---|
| Rebondir par un bastion | `ssh -J bastion.exemple.fr admin@10.99.0.21` |
| Copier un fichier | `scp sauvegarde.cfg admin@srv:/sauvegardes/` ou `sftp` |
| Tunnel local (atteindre un service interne) | `ssh -L 8443:intranet:443 bastion` puis `https://localhost:8443` |
| Diagnostiquer une connexion | `ssh -vvv admin@hôte` |

## Vérification côté Cisco

```cisco
SW1# show ip ssh
SSH Enabled - version 2.0
Authentication methods:publickey,keyboard-interactive,password
SW1# show ssh
Connection Version Mode Encryption  Hmac         State          Username
0          2.0     IN   aes256-ctr  hmac-sha2-256 Session started admin
```

## Exercices

**1.** Après avoir appliqué `access-class ADMIN-SEULEMENT in` sur les lignes VTY, l’administrateur, connecté depuis le Wi-Fi des employés, ne peut plus se reconnecter. Que s’est-il passé ?

<details><summary>Voir le corrigé</summary>

Son poste Wi-Fi n’est pas dans le réseau `10.99.0.0/24` autorisé par l’ACL : les nouvelles connexions sont refusées (sa session en cours peut continuer jusqu’à sa fermeture). Il faut se connecter depuis le réseau d’administration (bastion) ou par la console pour corriger.

</details>

**2.** Pourquoi faire passer les accès d’administration par un bastion plutôt que d’autoriser les postes des administrateurs ?

<details><summary>Voir le corrigé</summary>

Le bastion **centralise** les accès : une seule source autorisée dans les ACL des équipements, une authentification forte (MFA) au même endroit, et la **journalisation** (voire l’enregistrement) des sessions. Un poste d’administrateur compromis ne donne plus d’accès direct à tous les équipements.

</details>
