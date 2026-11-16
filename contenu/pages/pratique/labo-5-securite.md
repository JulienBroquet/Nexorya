---
titre: "Labo 5 — Sécuriser"
actif: pratique
chapeau: Le réseau du labo 4 fonctionne, mais n’importe qui peut s’y brancher et administrer les équipements. Tu vas le durcir.
---

> [!IMPORTANT] Objectif
> Remplacer Telnet par SSH avec des comptes nominatifs, filtrer l’administration, filtrer le trafic entre sites avec une ACL, et protéger les ports d’accès.

**Durée** : 1 heure. **Fiches utiles** : [SSH](../niveau-3/ssh.md), [ACL](../niveau-4/acl.md), [Protection des ports](../niveau-4/protection-ports.md), [Durcissement](../niveau-4/durcissement.md).

Repars de la topologie du [labo 4](labo-4-routage.md), en ajoutant un switch d’accès entre R-LYON et le PC de Lyon, et un **PC d’administration** au siège, dans le réseau `10.0.99.0/24`.

## Étape 1 — SSH et comptes

Sur chaque équipement :

```cisco
R-LYON(config)# hostname R-LYON
R-LYON(config)# ip domain-name lumen.local
R-LYON(config)# crypto key generate rsa modulus 2048
R-LYON(config)# ip ssh version 2
R-LYON(config)# username alice privilege 15 secret Un-Vrai-Mot-De-Passe
R-LYON(config)# enable secret Un-Autre-Secret
R-LYON(config)# service password-encryption
R-LYON(config)# line vty 0 4
R-LYON(config-line)# transport input ssh
R-LYON(config-line)# login local
R-LYON(config-line)# exec-timeout 10 0
```

Teste depuis le PC d’administration : `ssh -l alice 10.255.0.2`. Un `telnet` doit être refusé.

## Étape 2 — Limiter qui peut administrer

```cisco
R-LYON(config)# ip access-list standard ADMIN
R-LYON(config-std-nacl)# permit 10.0.99.0 0.0.0.255
R-LYON(config-std-nacl)# deny any log
R-LYON(config)# line vty 0 4
R-LYON(config-line)# access-class ADMIN in
```

Depuis le PC de Lyon, la connexion SSH au routeur doit maintenant être refusée.

> [!WARNING]
> Sur un vrai équipement à distance, applique d’abord `reload in 10` : une erreur dans cette ACL te coupe l’accès. Voir [Gestion du changement](../niveau-5/changement.md).

## Étape 3 — Filtrer entre sites

Règle à appliquer : les postes de Nantes peuvent joindre les serveurs du siège en HTTPS et DNS, mais pas les postes de Lyon.

```cisco
R-NANTES(config)# ip access-list extended NANTES-SORTIE
R-NANTES(config-ext-nacl)# permit udp 10.2.10.0 0.0.0.255 any eq 67
R-NANTES(config-ext-nacl)# permit tcp 10.2.10.0 0.0.0.255 10.0.0.0 0.0.0.255 eq 443
R-NANTES(config-ext-nacl)# permit udp 10.2.10.0 0.0.0.255 10.0.0.0 0.0.0.255 eq 53
R-NANTES(config-ext-nacl)# deny ip 10.2.10.0 0.0.0.255 10.1.10.0 0.0.0.255 log
R-NANTES(config-ext-nacl)# permit ip 10.2.10.0 0.0.0.255 any
R-NANTES(config)# interface Gi0/0
R-NANTES(config-if)# ip access-group NANTES-SORTIE in
```

```cisco
R-NANTES# show access-lists NANTES-SORTIE
```

## Étape 4 — Protéger les ports d’accès

```cisco
SW-LYON(config)# interface range Fa0/1 - 24
SW-LYON(config-if-range)# switchport mode access
SW-LYON(config-if-range)# switchport port-security
SW-LYON(config-if-range)# switchport port-security maximum 2
SW-LYON(config-if-range)# switchport port-security violation restrict
SW-LYON(config-if-range)# spanning-tree bpduguard enable
SW-LYON(config)# interface range Fa0/10 - 24
SW-LYON(config-if-range)# shutdown
```

Branche trois PC derrière un petit switch sur Fa0/1 : le troisième ne doit pas passer.

## Questions

**1.** Pourquoi la première ligne de l’ACL NANTES-SORTIE autorise-t-elle le port 67 ?

**2.** Pourquoi l’ACL est-elle appliquée en entrée sur l’interface des postes, et pas ailleurs ?

**3.** Quelle différence entre les modes de violation `shutdown`, `restrict` et `protect` ?

<details><summary>Voir le corrigé</summary>

**1.** Pour laisser passer les **demandes DHCP** des postes (vers le relais) : sans cette ligne, l’ACL les bloquerait et les postes n’obtiendraient plus d’adresse.

**2.** Une ACL étendue se place **au plus près de la source** : le trafic interdit est rejeté dès son entrée dans le réseau, sans traverser les liens WAN pour rien.

**3.** `shutdown` coupe le port (err-disabled) ; `restrict` jette le trafic des adresses en trop et **journalise** ; `protect` jette sans rien signaler. `restrict` est souvent le bon compromis : l’utilisateur légitime n’est pas coupé et l’incident est visible.

</details>

**Suite** : [Labo 6 — Chasse aux pannes](labo-6-pannes.md).
