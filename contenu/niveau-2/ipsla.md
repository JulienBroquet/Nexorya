---
titre: IP SLA et suivi
nom: Sondes, tracking et bascule intelligente
idee: IP SLA fait envoyer par un routeur des sondes régulières vers une destination lointaine ; si elles échouent, le suivi (track) retire une route ou baisse une priorité pour basculer sur le secours.
osi: "3 et 4"
duree: [8, 16]
cle: true
prerequis: [routage-statique, hsrp]
retenir:
  - "Un lien **physiquement actif** ne prouve pas que le **chemin** fonctionne."
  - "**IP SLA** = une sonde (ping, TCP, HTTP…) envoyée régulièrement ; **track** = un objet qui vaut « up » ou « down » selon la sonde."
  - On attache le track à une **route statique**, une **priorité HSRP/VRRP**, ou une politique de routage.
  - IP SLA mesure aussi **latence, gigue et pertes** pour superviser la qualité d’un lien.
---

## Le problème : la box allumée qui ne mène nulle part

Une agence a deux accès : une fibre principale et une 4G de secours. Un matin, la fibre ne transporte plus rien chez l’opérateur, mais la box reste allumée : l’interface du routeur reste **active**. La route par défaut vers la fibre reste en place, la 4G n’est jamais utilisée, et l’agence est coupée.

> [!IMPORTANT] L’idée en une phrase
> Le routeur vérifie lui-même, en permanence, qu’il atteint vraiment Internet à travers la fibre. Si les vérifications échouent, il retire la route principale et la route de secours prend le relais.

## Comment ça marche

```topologie
titre: Une sonde décide de la route par défaut
R routeur 0,0.5 "Routeur d’agence"
FIB routeur 2,0 "Box fibre"
LTE routeur 2,1 "Routeur 4G"
NET nuage 4,0.5 "Internet" "cible de sonde : 198.51.100.1"
R ++ FIB "route principale (track 10)"
R -- LTE "route de secours (AD 200)"
FIB -x- NET "coupure chez l’opérateur"
LTE -- NET
```

1. **La sonde** : toutes les 5 secondes, le routeur envoie un ping vers une adresse sur Internet, **en sortant par la fibre**.
2. **Le suivi** : un objet `track` passe à « down » si la sonde échoue plusieurs fois de suite.
3. **L’action** : la route par défaut principale est liée au track. Quand il passe à down, la route est retirée, et la route de secours (distance administrative plus élevée) apparaît.
4. **Le retour** : quand la sonde réussit à nouveau, la route principale revient.

## Les mots à connaître

- **IP SLA** — Fonction Cisco qui envoie des sondes régulières et mesure leur résultat (joignabilité, délai, gigue, pertes).
- **Sonde** — Test automatique envoyé vers une cible : ping, connexion TCP, requête HTTP ou DNS.
- **Track (objet de suivi)** — Objet dont l’état up/down dépend d’une sonde ou d’une interface, et auquel on rattache des actions.

## Teste-toi

**Pourquoi choisir une cible de sonde sur Internet plutôt que l’adresse de la box fibre elle-même ?**

<details><summary>Voir le corrigé</summary>

Parce que la box répond tant qu’elle est allumée, même si la fibre derrière elle ne transporte plus rien. Une cible **au-delà** de l’opérateur prouve que **le chemin complet** fonctionne. On en choisit idéalement deux, fiables, pour ne pas basculer à tort si une seule cible tombe.

</details>

<!-- approfondir -->

## Configuration complète (Cisco IOS)

```cisco
! 1. La sonde : ping vers une cible fiable, en sortant par la fibre
ip sla 10
 icmp-echo 198.51.100.1 source-interface GigabitEthernet0/0/0
 frequency 5
 threshold 1000
 timeout 1000
ip sla schedule 10 life forever start-time now
!
! 2. L'objet de suivi, avec un délai anti-oscillation
track 10 ip sla 10 reachability
 delay down 10 up 60
!
! 3. Les routes : principale suivie, secours flottant
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 10
ip route 0.0.0.0 0.0.0.0 192.0.2.1 200
!
! 4. La cible de la sonde doit toujours sortir par la fibre
ip route 198.51.100.1 255.255.255.255 203.0.113.1
```

> [!WARNING]
> L’étape 4 est indispensable. Sans elle, quand la route principale est retirée, la sonde vers `198.51.100.1` part… par la 4G, **réussit**, remet le track à up, la route principale revient, la sonde repart par la fibre et échoue : la route **oscille** sans fin. La route d’hôte force la sonde à toujours tester la fibre.

`delay down 10 up 60` : on déclare la panne après 10 s d’échec, et le retour seulement après 60 s de succès continus. Un lien instable ne fait pas basculer le trafic toutes les secondes.

## Combiner plusieurs sondes

```cisco
track 11 ip sla 11 reachability       ! seconde cible
track 20 list boolean or
 object 10
 object 11
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 20
```

Avec `boolean or`, la route reste tant qu’**une** des deux cibles répond : la panne d’un seul serveur distant ne provoque pas de bascule inutile.

## Suivi et passerelle redondante

```cisco
interface Vlan10
 standby 10 track 10 decrement 30
```

Si la sonde du routeur actif échoue, sa priorité HSRP baisse et l’autre routeur devient la passerelle des postes. Voir [HSRP](hsrp.md).

## Mesurer la qualité d’un lien

IP SLA sait aussi mesurer la qualité, pas seulement la joignabilité :

```cisco
ip sla 30
 udp-jitter 10.20.0.1 16384 codec g711alaw
 frequency 60
ip sla schedule 30 life forever start-time now
!
R1# show ip sla statistics 30
Round Trip Time (RTT) for       Index 30
        Latest RTT: 24 milliseconds
Voice Scores:
        ICPIF: 1        MOS Score: 4.34
Jitter Time:
        Source to Destination Jitter Min/Avg/Max: 0/2/9 milliseconds
Packet Loss Values:
        Loss Source to Destination: 0
```

La sonde `udp-jitter` simule un appel vocal et calcule un **score MOS** (qualité perçue, de 1 à 5). Le routeur distant doit avoir `ip sla responder`.

## Vérification

```cisco
R1# show ip sla summary
ID           Type        Destination       Stats       Return      Last
                                           (ms)        Code        Run
-----------------------------------------------------------------------
*10          icmp-echo   198.51.100.1      RTT=12      OK          3 seconds ago

R1# show track 10
Track 10
  IP SLA 10 reachability
  Reachability is Up
    3 changes, last change 2d04h
  Delay up 60 secs, down 10 secs
  Tracked by:
    Static IP Routing 0
```

## Exercices

**1.** Après la mise en place d’une sonde, la route par défaut alterne toutes les quelques secondes entre la fibre et la 4G pendant une panne de la fibre. Que manque-t-il ?

<details><summary>Voir le corrigé</summary>

La **route d’hôte** qui force la sonde à sortir par la fibre. Sans elle, la sonde réussit par la 4G une fois la route principale retirée, ce qui la fait revenir, etc. Ajouter `ip route <cible> 255.255.255.255 <prochain saut fibre>` et un délai `up` sur le track.

</details>

**2.** On veut que le routeur HSRP actif cède sa place si l’accès Internet de l’agence ne fonctionne plus, même si son uplink reste up. Comment ?

<details><summary>Voir le corrigé</summary>

Créer une sonde IP SLA vers une cible sur Internet, un `track` basé sur cette sonde, et `standby 10 track <n> decrement <valeur>` avec une valeur qui fait passer la priorité sous celle du second routeur (qui doit avoir `preempt`).

</details>
