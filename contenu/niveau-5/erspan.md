---
titre: ERSPAN
nom: Port miroir à distance par tunnel
idee: ERSPAN encapsule la copie du trafic dans un tunnel GRE et l’envoie, à travers le réseau routé, vers un analyseur situé n’importe où.
osi: "2 copié, transporté dans GRE sur IP"
duree: [5, 10]
prerequis: [span]
retenir:
  - La copie est **encapsulée dans GRE** et envoyée vers une **adresse IP** de destination.
  - On peut analyser une agence depuis le **siège** ou le SOC, sans se déplacer.
  - "Attention à la **bande passante** — la copie traverse le WAN et peut le saturer."
---

## Le problème

Un incident a lieu dans une agence à 500 km. L’analyseur et l’équipe du SOC sont au siège. Un SPAN local exigerait d’envoyer quelqu’un sur place avec un PC.

> [!IMPORTANT] L’idée en une phrase
> ERSPAN fait du port miroir à distance : la copie du trafic est mise dans un tunnel et routée jusqu’à l’analyseur, où qu’il soit.

## Comment ça marche

1. Sur le switch de l’agence, on définit la **source** (un port, un VLAN) et la **destination IP** (l’analyseur ou une sonde au siège).
2. Chaque copie est encapsulée dans un en-tête **GRE** avec un identifiant de session.
3. Les paquets traversent le réseau routé.
4. L’analyseur reçoit les paquets GRE ; Wireshark sait les ouvrir et afficher le trafic d’origine.

## Les mots à connaître

- **ERSPAN** — *Encapsulated Remote SPAN*, port miroir transporté dans un tunnel GRE.
- **GRE** — *Generic Routing Encapsulation*, encapsulation simple d’un paquet dans un autre.

## Teste-toi

**Pourquoi faut-il filtrer finement la source d’une session ERSPAN qui traverse un lien WAN de 50 Mb/s ?**

<details><summary>Voir le corrigé</summary>

Parce que la **copie** du trafic s’ajoute au trafic normal sur le lien WAN : copier un port très chargé peut saturer le lien et **dégrader** le service qu’on essaie justement de diagnostiquer. On copie un seul port, un seul sens, ou l’on filtre par ACL.

</details>

<!-- approfondir -->

## Configuration (Cisco IOS-XE)

```cisco
monitor session 10 type erspan-source
 source interface GigabitEthernet1/0/10 rx
 filter ip access-group ERSPAN-FILTRE
 no shutdown
 destination
  erspan-id 10
  ip address 10.99.0.70
  origin ip address 10.50.255.1
!
ip access-list extended ERSPAN-FILTRE
 permit tcp host 10.50.0.25 host 10.20.0.40 eq 443
```

Côté analyseur, Wireshark décode l’ERSPAN automatiquement (filtre `erspan`) ; on peut aussi utiliser une sonde qui reçoit directement le flux.

## Exercice

**L’analyseur au siège ne reçoit aucun paquet ERSPAN, alors que la session est active. Que vérifier ?**

<details><summary>Voir le corrigé</summary>

La **joignabilité** de l’adresse destination depuis l’adresse d’origine de la session (route, VRF de gestion), le **filtrage** du protocole GRE (IP 47) par les pare-feu sur le chemin, et le filtre de la session (une ACL trop restrictive ne copie rien). Une capture sur l’interface de l’analyseur confirme si les paquets GRE arrivent.

</details>
