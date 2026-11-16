---
titre: Automatisation
nom: Automatiser le réseau
idee: Automatiser, c’est décrire la configuration voulue dans des fichiers, puis laisser un outil l’appliquer à tous les équipements — de façon rapide, identique et vérifiable.
osi: "transversal"
duree: [9, 18]
cle: true
prerequis: [ssh, changement]
retenir:
  - "On sépare les **données** (VLAN, adresses, sites — dans des fichiers YAML ou une source de vérité) des **modèles** (templates)."
  - "Outils courants — **Ansible** (sans agent, via SSH ou API), **Python** (Netmiko, NAPALM, Nornir), **Terraform** pour le cloud."
  - "On commence par **lire** (inventaire, sauvegardes, vérifications), puis on **écrit**."
  - "Tout passe par **Git** — historique, relecture, retour arrière."
---

## Le problème : 200 switches à la main

Il faut ajouter le VLAN 140 sur 200 switches. À la main, cela prend une journée, et il y aura forcément des oublis ou des fautes de frappe sur quelques équipements. Six mois plus tard, personne ne sait plus quels switches ont réellement ce VLAN.

> [!IMPORTANT] L’idée en une phrase
> On écrit **une fois** ce qu’on veut obtenir, un outil l’applique **partout de la même façon**, et l’on peut vérifier à tout moment que la réalité correspond à ce qui est écrit.

## Comment ça marche

1. **L’inventaire** : la liste des équipements, regroupés (par site, par rôle).
2. **Les données** : ce que chaque équipement doit avoir (VLAN, adresses, serveurs NTP…), dans des fichiers lisibles.
3. **Les modèles** : comment ces données deviennent des lignes de configuration.
4. **L’outil** se connecte à chaque équipement, calcule la différence, applique, et vérifie.

```yaml
# donnees/vlans.yaml : la source de vérité
vlans:
  - vlan_id: 10
    name: UTILISATEURS
  - vlan_id: 20
    name: VOIX
  - vlan_id: 140
    name: CAMERAS
```

## Lire avant d’écrire

L’automatisation la plus utile et la moins risquée consiste d’abord à **lire** : sauvegarder toutes les configurations chaque nuit, produire un inventaire (modèles, versions, numéros de série), vérifier la conformité (NTP, SSH, bannière…). Écrire vient ensuite, quand on maîtrise l’outil.

```topologie
titre: La chaîne d’automatisation
ING utilisateur 0,0.7 "Ingénieur" "modifie les données"
GIT serveur 1.4,0.7 "Dépôt Git" "relecture"
CI boite 2.8,0.7 "Pipeline" "contrôles, simulation"
ANS serveur 4.2,0.7 "Ansible"
SW1 switch 5.4,0 "Switches"
SW2 routeur 5.4,1.4 "Routeurs"
ING -- GIT
GIT -- CI
CI -- ANS "validé"
ANS ++ SW1 "SSH / API"
ANS ++ SW2 "SSH / API"
```

## Les mots à connaître

- **Infrastructure as Code** — Description de l’infrastructure dans des fichiers versionnés, appliqués par des outils.
- **Ansible** — Outil d’automatisation sans agent, piloté par des fichiers YAML appelés playbooks.
- **Idempotence** — Propriété d’une action qui produit le même résultat qu’on l’exécute une ou dix fois.
- **Source de vérité** — Référentiel qui fait autorité sur l’état attendu du réseau (NetBox, fichiers Git).
- **Template** — Modèle de configuration à trous, rempli avec les données (Jinja2).

## Teste-toi

**Pourquoi l’idempotence est-elle importante ?**

<details><summary>Voir le corrigé</summary>

Parce qu’on peut relancer l’automatisation **sans danger** : si le VLAN existe déjà, l’outil ne fait rien ; s’il manque, il l’ajoute. On peut donc l’exécuter régulièrement pour **corriger les écarts**, sans craindre de casser ce qui est déjà correct.

</details>

<!-- approfondir -->

## Un playbook Ansible

```yaml
# playbooks/vlans.yml
- name: Déployer les VLAN standard sur les switches d'accès
  hosts: acces
  gather_facts: false
  vars_files:
    - ../donnees/vlans.yaml
  tasks:
    - name: Appliquer les VLAN
      cisco.ios.ios_vlans:
        config: "{{ vlans }}"
        state: merged

    - name: Sauvegarder la configuration
      cisco.ios.ios_config:
        save_when: modified
```

```bash
# Voir ce qui changerait, sans rien modifier
ansible-playbook playbooks/vlans.yml --check --diff --limit site-lyon
# Appliquer sur un site pilote, puis partout
ansible-playbook playbooks/vlans.yml --limit site-lyon
ansible-playbook playbooks/vlans.yml
```

## Avec Python

```python
# Sauvegarder la configuration de tous les équipements (Netmiko)
from netmiko import ConnectHandler
import yaml, pathlib

inventaire = yaml.safe_load(open("inventaire.yaml"))
for eq in inventaire["equipements"]:
    with ConnectHandler(device_type="cisco_ios", host=eq["ip"],
                        username=eq["user"], password=eq["mdp"]) as c:
        config = c.send_command("show running-config")
    pathlib.Path(f"sauvegardes/{eq['nom']}.cfg").write_text(config)
    print("ok", eq["nom"])
```

> [!WARNING]
> Ne jamais écrire de mot de passe dans un fichier versionné. Utiliser un **coffre** (Ansible Vault, variables d’environnement, gestionnaire de secrets).

## La chaîne complète

1. Un ingénieur modifie les **données** (ajout du VLAN 140) dans Git, sur une branche.
2. Un collègue **relit** la modification (merge request).
3. Une **pipeline** vérifie automatiquement : syntaxe, règles (« pas de VLAN 1 », « nom obligatoire »), simulation (`--check --diff`).
4. Après validation, l’outil **applique** — d’abord sur un site pilote.
5. Des **tests** confirment le résultat (le VLAN existe, les trunks le transportent).
6. Régulièrement, l’outil compare la réalité aux données et signale les **dérives**.

## Exercice

**Un collègue ajoute un VLAN à la main sur un switch, en urgence. La nuit suivante, l’automatisation qui applique l’état complet (mode « remplacer ») le supprime. Qui a raison, et comment éviter ce problème ?**

<details><summary>Voir le corrigé</summary>

L’automatisation fait ce qu’on lui demande : la **source de vérité** ne contient pas ce VLAN, donc il est retiré. La règle doit être claire : toute modification passe par les **données** (même en urgence, on met à jour les fichiers juste après), et les changements manuels sont détectés et signalés (rapport de dérive) **avant** d’être écrasés. Le mode « remplacer » ne s’active qu’une fois cette discipline acquise.

</details>
