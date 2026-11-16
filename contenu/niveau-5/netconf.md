---
titre: NETCONF et YANG
nom: Configuration par API structurée
idee: Au lieu d’envoyer des lignes de commande et de lire du texte, NETCONF et RESTCONF échangent des données structurées décrites par des modèles YANG — les programmes comprennent alors parfaitement ce qu’ils lisent et écrivent.
osi: "7"
duree: [7, 14]
prerequis: [automatisation]
retenir:
  - "**YANG** décrit la structure des données (interfaces, VLAN, routes) ; **NETCONF** (SSH, port 830) et **RESTCONF** (HTTPS) les transportent."
  - "Avantages — données structurées, **transactions** (tout ou rien), validation avant application."
  - "Modèles **standard** (IETF, OpenConfig) ou **propriétaires** (Cisco, Juniper…)."
  - "**gNMI** sert surtout à la télémétrie en streaming."
---

## Le problème : parler à une machine comme à un humain

Un script qui automatise un switch en ligne de commande envoie du texte et lit du texte : il doit **deviner** où se trouve l’information dans la sortie de `show interfaces`, et la moindre différence de version casse le script. Et si une commande échoue au milieu de vingt, l’équipement reste dans un état à moitié configuré.

> [!IMPORTANT] L’idée en une phrase
> NETCONF et RESTCONF sont des **API** : on lit et l’on écrit la configuration sous forme de données structurées, décrites par des modèles YANG, avec des transactions qui s’appliquent entièrement ou pas du tout.

## La différence

| Ligne de commande (CLI) | API (NETCONF / RESTCONF) |
|---|---|
| texte libre, différent selon les versions | données structurées (XML, JSON) selon un modèle |
| il faut analyser la sortie | les champs sont nommés et typés |
| commande par commande | transaction complète, validée avant application |
| erreur au milieu = état partiel | erreur = rien n’est appliqué |

```sequence
titre: Modifier une configuration en NETCONF, en une transaction
Script | Switch
Script -> Switch : session SSH, port 830 : hello (capacités, modèles YANG)
Script -> Switch : edit-config sur la configuration candidate
Script -> Switch : validate
Switch --> Script : ok : la configuration est cohérente
Script -> Switch : commit
Switch --> Script : ok : appliqué en une seule fois
note Script, Switch : en cas d’erreur à n’importe quelle étape, rien n’est appliqué
```

## Les mots à connaître

- **YANG** — Langage de modélisation qui décrit la structure des données de configuration et d’état.
- **NETCONF** — Protocole de configuration par API, sur SSH (port 830), avec des données XML.
- **RESTCONF** — API HTTP(S) exposant les mêmes modèles YANG, en JSON ou XML.
- **OpenConfig** — Ensemble de modèles YANG communs à plusieurs constructeurs.
- **gNMI** — Protocole basé sur gRPC pour la configuration et surtout la télémétrie en streaming.

## Teste-toi

**Pourquoi la notion de transaction est-elle précieuse pour l’automatisation ?**

<details><summary>Voir le corrigé</summary>

Parce qu’en cas d’erreur, **rien** n’est appliqué : l’équipement ne reste jamais dans un état à moitié configuré. Avec la CLI, si la commande 12 sur 20 échoue, les 11 premières restent en place et il faut nettoyer à la main.

</details>

<!-- approfondir -->

## Lire une interface en RESTCONF

```bash
curl -sk -u admin:****** \
  -H "Accept: application/yang-data+json" \
  https://10.99.0.21/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F1
```

```json
{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet1/0/1",
    "description": "Bureau 214",
    "type": "iana-if-type:ethernetCsmacd",
    "enabled": true
  }
}
```

Le programme lit directement `enabled: true`, sans analyser de texte.

## Modifier en NETCONF (Python, ncclient)

```python
from ncclient import manager

config = """
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>GigabitEthernet1/0/1</name>
      <description>Bureau 214 - imprimante</description>
    </interface>
  </interfaces>
</config>"""

with manager.connect(host="10.99.0.21", port=830, username="admin",
                     password="******", hostkey_verify=False) as m:
    m.edit_config(target="candidate", config=config)
    m.validate(source="candidate")
    m.commit()
```

Le flux **candidate → validate → commit** : on prépare une configuration candidate, l’équipement la vérifie, puis l’applique en une fois.

## Activer les API (Cisco IOS-XE)

```cisco
netconf-yang
restconf
ip http secure-server
```

> [!WARNING]
> Une API d’administration est un accès complet à l’équipement : la limiter au **réseau de gestion** (ACL), utiliser HTTPS avec un certificat valide et des comptes nominatifs avec droits adaptés (AAA).

## Exercice

**Un script CLI qui lit le nombre d’erreurs CRC fonctionne sur les switches en version 16 mais renvoie des valeurs absurdes sur ceux en version 17. Pourquoi une API YANG éviterait-elle ce problème ?**

<details><summary>Voir le corrigé</summary>

Le script analyse un **texte** dont la mise en forme a changé entre les versions (colonne déplacée, libellé modifié). Avec une API, la valeur est un **champ nommé** d’un modèle YANG (par exemple `in-errors` dans `ietf-interfaces`), indépendant de la présentation : le script lit le même champ quelle que soit la version.

</details>
