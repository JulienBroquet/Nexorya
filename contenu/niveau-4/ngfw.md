---
titre: NGFW
nom: Pare-feu de nouvelle génération
idee: Un pare-feu suit chaque connexion pour n’autoriser que les flux voulus et leurs réponses ; un NGFW reconnaît en plus les applications, les utilisateurs et les menaces.
osi: "3 à 7"
duree: [9, 18]
prerequis: [acl, tcp]
retenir:
  - "Un pare-feu **à états** mémorise les connexions — les **réponses** sont autorisées automatiquement."
  - "Un **NGFW** ajoute — identification des **applications**, des **utilisateurs**, IPS, filtrage d’URL, inspection TLS."
  - Les règles sont lues **dans l’ordre** ; la dernière est **tout refuser**.
  - Une bonne politique est **minimale**, **documentée** et **revue** régulièrement.
---

## Le problème : les ports ne disent plus tout

Une ACL autorise ou refuse selon les adresses et les ports. Mais aujourd’hui, presque tout passe par le port 443 : la messagerie, la visioconférence, un réseau social, un outil de prise de contrôle à distance, un logiciel malveillant. Autoriser « le 443 » revient à presque tout autoriser.

> [!IMPORTANT] L’idée en une phrase
> Un NGFW ne se contente pas de regarder les ports : il reconnaît **l’application**, **l’utilisateur** et les **menaces**, et applique des règles du type « le service comptable peut utiliser Teams, mais pas les outils de partage de fichiers personnels ».

## Pare-feu à états : la base

Contrairement à une ACL, un pare-feu à états garde une **table des connexions**. Quand un poste ouvre une connexion autorisée vers un serveur, le pare-feu enregistre la session et laisse passer les **réponses** sans règle supplémentaire. Une réponse qui ne correspond à aucune session connue est rejetée.

## Ce qu’ajoute un NGFW

| Fonction | Exemple de règle |
|---|---|
| **Identification d’application** | autoriser « Microsoft Teams », bloquer « BitTorrent », quel que soit le port |
| **Identité de l’utilisateur** (annuaire, 802.1X, VPN) | autoriser le groupe Compta vers l’ERP |
| **IPS intégré** | bloquer les exploits connus vers les serveurs |
| **Filtrage d’URL / de catégories** | bloquer les sites de jeux d’argent, les domaines malveillants |
| **Analyse de fichiers** | examiner les téléchargements dans un bac à sable |
| **Inspection TLS** | déchiffrer pour inspecter, selon une politique |

## Les mots à connaître

- **Pare-feu à états** — Pare-feu qui suit les connexions et autorise automatiquement leurs réponses ; *stateful*.
- **NGFW** — *Next-Generation Firewall*, pare-feu qui identifie applications, utilisateurs et menaces.
- **Politique de sécurité** — Ensemble ordonné des règles d’un pare-feu.
- **DMZ** — Zone intermédiaire qui héberge les serveurs accessibles depuis Internet.

## Teste-toi

**Pourquoi, avec un pare-feu à états, n’a-t-on pas besoin d’écrire une règle pour autoriser les réponses des sites Web ?**

<details><summary>Voir le corrigé</summary>

Parce que le pare-feu a **enregistré** la connexion sortante autorisée ; les paquets de réponse correspondent à cette session et sont acceptés automatiquement. Une ACL sans état, elle, aurait besoin d’une règle explicite pour le retour.

</details>

<!-- approfondir -->

## Écrire une politique lisible

| N° | Source | Destination | Application / service | Action | Journal |
|---|---|---|---|---|---|
| 10 | Admins (groupe AD) | Réseau d’administration | SSH, HTTPS | autoriser | oui |
| 20 | Postes | Serveurs AD | Kerberos, LDAP(S), DNS, SMB | autoriser | non |
| 30 | Postes | ERP | HTTPS (application ERP) | autoriser | non |
| 40 | Postes | Internet | Web, Teams, applications approuvées | autoriser + IPS + filtrage URL | oui |
| 50 | Invités | Internet | Web | autoriser | oui |
| 99 | toute | toute | toute | **refuser** | **oui** |

Principes :

- **Moindre privilège** : chaque règle autorise le strict nécessaire, avec un propriétaire et une justification.
- **Ordre** : les règles précises avant les règles générales.
- **Journaliser** les refus pour comprendre ce qui est bloqué.
- **Objets nommés** (groupes d’adresses, d’applications) plutôt que des adresses écrites en dur.
- **Revue** régulière : supprimer les règles inutilisées (compteurs à zéro depuis des mois) et les règles trop larges (`any` vers `any`).

## Dépannage

1. Le flux arrive-t-il au pare-feu ? (capture, compteurs d’interface, routage)
2. Quelle règle s’applique ? La plupart des pare-feu ont un outil de **simulation** (*packet tracer*) qui indique la règle retenue pour un flux donné.
3. La session est-elle créée ? (table des sessions)
4. La réponse revient-elle **par le même pare-feu** ? Un retour par un autre chemin (routage asymétrique) est rejeté faute de session.

```text
# Exemple Cisco ASA / FTD : simuler un flux
packet-tracer input inside tcp 10.10.0.57 51544 10.20.0.40 443 detailed
...
Phase: 4  Type: ACCESS-LIST  Result: DROP
  access-group INSIDE in interface inside
  access-list INSIDE extended deny ip any any log
```

## Exercices

**1.** Un serveur répond aux requêtes, mais ses réponses repartent par un autre routeur qui ne passe pas par le pare-feu. Les utilisateurs n’obtiennent rien. Pourquoi ?

<details><summary>Voir le corrigé</summary>

**Routage asymétrique** : le pare-feu a vu passer la demande, mais pas la réponse. Côté utilisateurs, si la réponse passe par un autre pare-feu à états, celui-ci la rejette (aucune session connue). Il faut que l’aller et le retour traversent le **même** pare-feu (routage symétrique, ou synchronisation des sessions dans un cluster).

</details>

**2.** Une règle « Postes → Internet → TCP 443 → autoriser » existe depuis des années. Pourquoi est-elle insuffisante aujourd’hui ?

<details><summary>Voir le corrigé</summary>

Presque toutes les applications utilisent le 443 : cette règle autorise aussi les outils de prise de main à distance non approuvés, les tunnels, les services de partage personnels et les communications de logiciels malveillants. Avec un NGFW, on autorise des **applications** et des **catégories**, et l’on applique IPS et filtrage d’URL.

</details>
