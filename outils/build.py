# -*- coding: utf-8 -*-
"""Génère le site statique Nexorya à partir du dossier contenu/.

    python3 outils/build.py            # produit docs/ (publiable tel quel sur GitHub Pages)
    python3 outils/build.py --verifier # génère puis contrôle liens internes et schémas

Dépendances : Python 3.9+, `markdown`, `pyyaml` (voir requirements.txt).
"""
import html, json, os, random, re, shutil, sys, unicodedata
import markdown
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schemas  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENU = os.path.join(RACINE, 'contenu')
THEME = os.path.join(RACINE, 'theme')
SORTIE = os.path.join(RACINE, 'docs')
VERSION = '1.0.0'
SLOGAN = 'Explore les réseaux. Maîtrise l’infrastructure.'

e = lambda s: html.escape(str(s), quote=True)


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# ======================================================================= Markdown
ALERTES = {'NOTE': ('note', 'Bon à savoir'), 'TIP': ('astuce', 'Astuce'), 'WARNING': ('piege', 'Piège à éviter'),
           'IMPORTANT': ('retenir', 'À retenir'), 'CAUTION': ('attention', 'Attention en production'),
           'EXAMPLE': ('exemple', 'Exemple')}


class Rendu:
    def __init__(self):
        self.schemas = []

    def pre(self, texte):
        # 1) schémas
        def remplace(m):
            genre, src = m.group(1), m.group(2)
            svg, titre = (schemas.sequence if genre == 'sequence' else schemas.topologie)(src)
            self.schemas.append((svg, titre))
            return f'\n\nSCHEMA{len(self.schemas)-1}FIN\n\n'
        texte = re.sub(r'```(sequence|topologie)\n(.*?)```', remplace, texte, flags=re.S)
        # 2) encadrés façon GitHub : > [!TIP] Titre facultatif
        lignes, out, i = texte.split('\n'), [], 0
        while i < len(lignes):
            m = re.match(r'^>\s*\[!(\w+)\]\s*(.*)$', lignes[i])
            if m and m.group(1).upper() in ALERTES:
                cls, defaut = ALERTES[m.group(1).upper()]
                titre = m.group(2).strip() or defaut
                corps = []
                i += 1
                while i < len(lignes) and lignes[i].startswith('>'):
                    corps.append(re.sub(r'^>\s?', '', lignes[i])); i += 1
                out += ['', f'<div class="encadre {cls}" markdown="1">', '', f'<p class="encadre-titre">{e(titre)}</p>', ''] + corps + ['', '</div>', '']
                continue
            out.append(lignes[i]); i += 1
        texte = '\n'.join(out)
        texte = texte.replace('<details>', '<details markdown="1">')
        return texte

    def html(self, texte):
        md = markdown.Markdown(extensions=['extra', 'sane_lists', 'toc'],
                               extension_configs={'toc': {'slugify': lambda v, sep: slug(v), 'toc_depth': '2-3'}},
                               output_format='html5')
        h = md.convert(self.pre(texte))
        # schémas
        def fig(m):
            svg, titre = self.schemas[int(m.group(1))]
            cap = f'<figcaption>{e(titre)}</figcaption>' if titre else ''
            return f'<figure class="schema">{svg}{cap}</figure>'
        h = re.sub(r'<p>SCHEMA(\d+)FIN</p>', fig, h)
        # liens .md -> .html
        h = re.sub(r'href="([^"#:]+?)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', h)
        # coloration minimale : commentaires et invites
        def code(m):
            lang, corps = m.group(1) or '', m.group(2)
            lignes = []
            for l in corps.split('\n'):
                if re.match(r'^\s*(!|#(?!\s*$)(?=\s)|//)', l) and lang in ('cisco', 'bash', 'shell', 'yaml', 'python', 'text', 'powershell', ''):
                    lignes.append(f'<span class="c">{l}</span>')
                else:
                    l = re.sub(r'^(\S+[#>$])(\s)', r'<span class="k">\1</span>\2', l) if lang in ('cisco', 'bash', 'shell', 'powershell', 'text') else l
                    lignes.append(l)
            return f'<pre><code class="language-{lang}">' + '\n'.join(lignes) + '</code></pre>'
        h = re.sub(r'<pre><code(?: class="language-([\w-]+)")?>(.*?)</code></pre>', code, h, flags=re.S)
        return h, md.toc_tokens


def lire_md(chemin):
    t = open(chemin, encoding='utf-8').read()
    meta = {}
    if t.startswith('---'):
        _, fm, t = t.split('---', 2)
        meta = yaml.safe_load(fm) or {}
    return meta, t.strip('\n')


# ======================================================================= Modèle de données
def charger():
    plan = yaml.safe_load(open(os.path.join(CONTENU, 'plan.yaml'), encoding='utf-8'))
    fiches = {}
    ordre = []
    for niv in plan['niveaux']:
        niv['ids'] = []
        for k, ch in enumerate(niv['chapitres'], 1):
            ch['num'] = k
            ch['slug'] = f'chapitre-{k}'
            for fid in ch['fiches']:
                chemin = os.path.join(CONTENU, niv['dossier'], fid + '.md')
                if not os.path.exists(chemin):
                    meta, corps = {'titre': fid, 'nom': '', 'idee': 'Fiche en cours de rédaction.'}, '*Fiche en cours de rédaction.*'
                    meta['_absente'] = True
                else:
                    meta, corps = lire_md(chemin)
                meta.update(id=fid, niveau=niv, chapitre=ch, corps=corps,
                            url=f'{niv["dossier"]}/{fid}.html', source=f'{niv["dossier"]}/{fid}.md')
                fiches[(niv['dossier'], fid)] = meta
                niv['ids'].append(f'{niv["dossier"]}/{fid}')
                ordre.append(meta)
    return plan, fiches, ordre


# ======================================================================= Gabarits
def coquille(titre, corps, prof, actif='', ligne=None, extra_tete='', scripts='', desc=''):
    r = '../' * prof
    nav = [('demarrer/index.html', 'Je débute', 'demarrer'), ('index.html#plan', 'Les niveaux', 'niveaux'),
           ('pratique/index.html', 'Pratique', 'pratique'), ('lexique.html', 'Lexique', 'lexique'),
           ('progression.html', 'Ma progression', 'progression')]
    liens = ''.join(f'<a href="{r}{u}"{" aria-current=page" if k == actif else ""} class="{"secondaire-nav" if k in ("lexique","pratique") else ""}">{t}</a>' for u, t, k in nav)
    style = f' style="--ligne:{ligne}"' if ligne else ''
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(desc or SLOGAN)}">
<link rel="icon" href="{r}assets/img/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/css/nexorya.css">
<script>try{{var t=JSON.parse(localStorage.getItem('nexorya:v1')||'{{}}').theme;document.documentElement.setAttribute('data-theme',t||(matchMedia('(prefers-color-scheme: dark)').matches?'sombre':'clair'))}}catch(x){{}}</script>
{extra_tete}
</head>
<body data-racine="{r}"{style}>
<a class="saut" href="#principal">Aller au contenu</a>
<header class="barre"><div class="barre-int">
<a class="marque" href="{r}index.html"><img src="{r}assets/img/logo.svg" alt="">Nexorya</a>
<button class="bouton-icone" id="bascule-nav" type="button" aria-expanded="false" aria-controls="nav-principale"><svg width="18" height="18" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg> Menu</button>
<nav id="nav-principale" aria-label="Navigation principale">{liens}
<a href="{r}recherche.html" aria-label="Rechercher">⌕ Rechercher</a>
<button class="bouton-icone" id="bascule-theme" type="button" aria-label="Changer de thème"><svg width="18" height="18" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 2a8 8 0 0 1 0 16z" fill="currentColor"/></svg><span class="seul-mobile"> Changer de thème</span></button>
</nav></div></header>
<main id="principal">
{corps}
</main>
<footer class="pied"><span><strong>Nexorya</strong> — {SLOGAN}</span><span>Version {VERSION} · © 2026 Julien Broquet · Contenu sous licence <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr" rel="license">CC BY-NC-SA 4.0</a>, usage commercial sur autorisation · <a href="{r}credits.html">Crédits des images</a> · <a href="{r}a-propos.html">À propos</a></span></footer>
{scripts}
<script src="{r}assets/js/nexorya.js"></script>
</body>
</html>
'''


def couleur(niv):
    return f'var(--l{niv["num"]})'


# ----------------------------------------------------------------------- Fiche
def page_fiche(f, plan, ordre, idx):
    niv, ch = f['niveau'], f['chapitre']
    prof = 1
    corps = f['corps']
    parties = re.split(r'^<!--\s*approfondir\s*-->\s*$', corps, maxsplit=1, flags=re.M)
    rendus = []
    sommaires = []
    for p in parties:
        h, toc = Rendu().html(p)
        rendus.append(h)
        sommaires.append([(t['id'], t['name']) for t in toc])
    a_deux = len(parties) == 2
    # navigation latérale
    lat = [f'<a class="retour" href="index.html"><i>{niv["num"]}</i>{e(niv["titre"])}</a>']
    for c in niv['chapitres']:
        lat.append(f'<h3>{e(c["titre"])}</h3><ul>')
        for fid in c['fiches']:
            o = ORDRE_IDX[(niv['dossier'], fid)]
            cur = ' aria-current="page"' if fid == f['id'] else ''
            lat.append(f'<li><a href="{fid}.html" data-fiche="{niv["dossier"]}/{fid}"{cur}>{e(o["titre"])}</a></li>')
        lat.append('</ul>')
    # badges
    badges = []
    if f.get('osi'):
        badges.append(f'<span>Couche OSI {e(f["osi"])}</span>')
    d = f.get('duree') or []
    if d:
        badges.append(f'<span>Découvrir : {d[0]} min</span>')
        if a_deux and len(d) > 1:
            badges.append(f'<span>Approfondir : {d[1]} min</span>')
    if f.get('prerequis'):
        pre = []
        for p in f['prerequis']:
            cible = TROUVE.get(p)
            if cible:
                pre.append(f'<a href="../{cible["url"]}">{e(cible["titre"])}</a>')
        if pre:
            badges.append('<span>Avant : ' + ', '.join(pre) + '</span>')
    modes = ''
    if a_deux:
        modes = ('<div class="modes" role="tablist" aria-label="Niveau de lecture">'
                 f'<button role="tab" data-mode="decouvrir" aria-selected="true" aria-controls="partie-decouvrir">Découvrir<small>l’essentiel</small></button>'
                 f'<button role="tab" data-mode="approfondir" aria-selected="false" aria-controls="partie-approfondir">Approfondir<small>le détail technique</small></button></div>'
                 '<p class="mode-aide">Commence par « Découvrir ». Passe à « Approfondir » quand l’essentiel est clair.</p>')
    contenu = ''
    noms = ['decouvrir', 'approfondir']
    for k, h in enumerate(rendus):
        contenu += f'<section class="prose" id="partie-{noms[k]}" data-partie="{noms[k]}" role="tabpanel"{" hidden" if k else ""}>{h}</section>'
    som = ''.join(f'<div data-sommaire="{noms[k]}"{" hidden" if k else ""}><p>Sur cette page</p>' + ''.join(f'<a href="#{i}">{e(n)}</a>' for i, n in s) + '</div>' for k, s in enumerate(sommaires) if s)
    prec = ordre[idx - 1] if idx > 0 else None
    suiv = ordre[idx + 1] if idx + 1 < len(ordre) else None
    suite = '<nav class="suite" aria-label="Fiches voisines">'
    if prec:
        suite += f'<a href="../{prec["url"]}"><small>Fiche précédente</small><strong>{e(prec["titre"])}</strong></a>'
    if suiv:
        suite += f'<a class="apres" href="../{suiv["url"]}"><small>Fiche suivante{"" if suiv["niveau"] is niv else " · " + e(suiv["niveau"]["titre"])}</small><strong>{e(suiv["titre"])}</strong></a>'
    suite += '</nav>'
    html_ = f'''<div class="lecture">
<aside class="lateral" aria-label="Fiches du niveau">{"".join(lat)}</aside>
<article class="contenu" data-fiche-id="{niv["dossier"]}/{f["id"]}">
<p class="fil"><a href="index.html">{e(niv["titre"])}</a> › <a href="index.html#{ch["slug"]}">{e(ch["titre"])}</a> <button class="bouton-icone menu-mobile" id="menu-mobile" aria-expanded="false" type="button">☰ Fiches du niveau</button></p>
<header class="contenu-tete"><h1>{e(f["titre"])}</h1>{f'<p class="nom-complet">{e(f["nom"])}</p>' if f.get("nom") else ""}
<p class="idee">{e(f.get("idee",""))}</p><div class="badges">{"".join(badges)}</div></header>
{modes}
{contenu}
<footer class="fin-fiche"><div class="marquer"><button class="bouton" id="bouton-lu" type="button" aria-pressed="false">Marquer cette fiche comme lue</button>
<span class="mode-aide">Ta progression reste sur cet appareil.</span></div>{suite}</footer>
</article>
<aside class="sommaire" aria-label="Sur cette page">{som}</aside>
</div>'''
    return coquille(f'{f["titre"]} — {f.get("nom") or niv["titre"]} | Nexorya', html_, prof, 'demarrer' if niv['num'] == 0 else 'niveaux', couleur(niv), desc=f.get('idee', ''))


# ----------------------------------------------------------------------- Niveau
def page_niveau(niv, plan):
    rendu_intro = Rendu().html(niv.get('intro', ''))[0] if niv.get('intro') else ''
    chap = []
    for c in niv['chapitres']:
        ids = [f'{niv["dossier"]}/{x}' for x in c['fiches']]
        items = ''
        for fid in c['fiches']:
            f = ORDRE_IDX[(niv['dossier'], fid)]
            cle = '<span class="cle">Notion clé</span>' if f.get('cle') else ''
            items += (f'<li><a class="fiche-lien" href="{fid}.html" data-fiche="{niv["dossier"]}/{fid}">'
                      f'<strong>{e(f["titre"])}</strong><span class="etat" aria-hidden="true"></span>{cle}<span class="nom">{e(f.get("idee",""))}</span></a></li>')
        chap.append(f'<section class="chapitre" id="{c["slug"]}" data-chapitre="{",".join(ids)}"><span class="arret">{c["num"]}</span>'
                    f'<div class="chapitre-corps"><h2>{e(c["titre"])}</h2><p>{e(c.get("but",""))}</p><ul class="fiches">{items}</ul></div></section>')
    actions = ''
    if niv['num'] > 0:
        actions = (f'<a class="bouton" href="{niv["chapitres"][0]["fiches"][0]}.html">Commencer le niveau</a>'
                   f'<a class="bouton secondaire" href="revision.html">Réviser en 10 minutes</a>'
                   f'<a class="bouton secondaire" href="../qcm/niveau-{niv["num"]}.html">Passer le QCM</a>')
    else:
        actions = (f'<a class="bouton" href="{niv["chapitres"][0]["fiches"][0]}.html">Commencer ici</a>'
                   f'<a class="bouton secondaire" href="../qcm/niveau-0.html">Faire le quiz du débutant</a>')
    tete = f'''<header class="niveau-tete"><p class="fil"><a href="../index.html">Accueil</a> › {e(niv["titre"])}</p>
<span class="numero">{niv["num"]}</span><h1>{e(niv["titre"])}</h1><p class="chapeau">{e(niv["chapeau"])}</p>
<div class="prose">{rendu_intro}</div>
<div class="niveau-actions">{actions}</div>
<div class="jauge" data-jauge="{",".join(niv["ids"])}"><i></i></div><p class="jauge-texte" data-jauge-texte></p></header>'''
    return coquille(f'{niv["titre"]} | Nexorya', tete + f'<div class="parcours">{"".join(chap)}</div>', 1,
                    'demarrer' if niv['num'] == 0 else 'niveaux', couleur(niv), desc=niv['chapeau'])


def page_revision(niv):
    blocs = []
    for c in niv['chapitres']:
        blocs.append(f'<h2 id="{c["slug"]}">{e(c["titre"])}</h2>')
        for fid in c['fiches']:
            f = ORDRE_IDX[(niv['dossier'], fid)]
            ret = ''.join(f'<li>{Rendu().html(x)[0][3:-4]}</li>' for x in (f.get('retenir') or []))
            blocs.append(f'<h3><a href="{fid}.html">{e(f["titre"])}</a>{" — " + e(f["nom"]) if f.get("nom") else ""}</h3><p>{e(f.get("idee",""))}</p><ul>{ret}</ul>')
    corps = (f'<div class="page"><p class="fil"><a href="../index.html">Accueil</a> › <a href="index.html">{e(niv["titre"])}</a> › Révision</p>'
             f'<h1>Réviser le niveau {niv["num"]}</h1><p class="chapeau">L’idée et les points à retenir de chaque fiche, sur une seule page. Si une ligne ne te dit plus rien, rouvre la fiche.</p>'
             f'<div class="prose">{"".join(blocs)}</div><p><a class="bouton" href="../qcm/niveau-{niv["num"]}.html">Je me teste avec le QCM</a></p></div>')
    return coquille(f'Révision — {niv["titre"]} | Nexorya', corps, 1, 'niveaux', couleur(niv))


# ----------------------------------------------------------------------- Accueil
def plan_svg(plan):
    lignes = plan['niveaux']
    W, x0, x1, H0 = 1240, 330, 1160, 132
    H = H0 * len(lignes) + 10
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="plan-titre" xmlns="http://www.w3.org/2000/svg"><title id="plan-titre">Plan des niveaux de Nexorya</title>']
    for k, niv in enumerate(lignes):
        y = 44 + k * H0
        col = f'var(--l{niv["num"]})'
        n = len(niv['chapitres'])
        xs = [x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
        s.append(f'<a href="{niv["dossier"]}/index.html" class="terminus"><circle cx="34" cy="{y}" r="24" fill="{col}"/>'
                 f'<text x="34" y="{y+6}" text-anchor="middle" fill="#fff">{niv["num"]}</text>')
        tl = schemas._wrap(niv['titre'], 200, 9)
        for i, t in enumerate(tl):
            s.append(f'<text x="70" y="{y - 4 + i*20 - (len(tl)-1)*10}" fill="var(--encre)">{e(t)}</text>')
        s.append('</a>')
        s.append(f'<line x1="{xs[0]-30}" y1="{y}" x2="{xs[-1]+20}" y2="{y}" stroke="{col}" stroke-width="10" stroke-linecap="round"/>')
        for i, c in enumerate(niv['chapitres']):
            ids = ','.join(f'{niv["dossier"]}/{x}' for x in c['fiches'])
            tl = schemas._wrap(c['titre'], 128, 7.1)
            txt = ''.join(f'<text x="{xs[i]}" y="{y + 34 + j*16}" text-anchor="middle">{e(t)}</text>' for j, t in enumerate(tl))
            s.append(f'<g class="station" data-ids="{ids}"><a href="{niv["dossier"]}/index.html#{c["slug"]}">'
                     f'<circle class="rond" cx="{xs[i]}" cy="{y}" r="11" stroke="{col}"/>{txt}</a></g>')
    s.append('</svg>')
    return ''.join(s)


def page_accueil(plan, ordre):
    nb = len([f for f in ordre if f['niveau']['num'] > 0])
    liste = ''.join(f'<li><a href="{n["dossier"]}/index.html" style="--ligne:var(--l{n["num"]})"><span class="numero" style="width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--l{n["num"]});color:#fff;font:800 17px var(--titre)">{n["num"]}</span><span><strong>{e(n["titre"])}</strong><small>{len(n["ids"])} fiches</small></span></a></li>' for n in plan['niveaux'])
    corps = f'''<section class="accueil-tete">
<div><h1>Explore les réseaux. <span>Maîtrise l’infrastructure.</span></h1>
<p class="chapeau">Un parcours gratuit et progressif, du premier câble branché jusqu’au datacenter. Chaque notion s’explique d’abord simplement, puis en détail, avec des schémas, des cas réels et des exercices corrigés.</p></div>
<div class="departs"><p>Par où commencer ?</p>
<a class="depart" href="demarrer/index.html" style="--ligne:var(--l0)"><span class="pastille">0</span><span><strong>Je n’y connais rien</strong><small>Huit repères pour comprendre ce qu’est un réseau, sans prérequis.</small></span><span class="fleche" aria-hidden="true">›</span></a>
<a class="depart" href="niveau-1/index.html" style="--ligne:var(--l1)"><span class="pastille">1</span><span><strong>J’ai quelques bases</strong><small>Commencer le niveau 1 : câbles, switches, VLAN et Wi-Fi.</small></span><span class="fleche" aria-hidden="true">›</span></a>
<a class="depart" href="qcm/niveau-1.html" style="--ligne:var(--l5)"><span class="pastille">✓</span><span><strong>Je travaille déjà dans le réseau</strong><small>Mesurer mon niveau avec les QCM, puis combler les manques.</small></span><span class="fleche" aria-hidden="true">›</span></a>
</div></section>
<section class="plan" id="plan" aria-label="Plan des niveaux"><div class="plan-carte">{plan_svg(plan)}
<div class="plan-legende"><span><i></i>Chapitre à découvrir</span><span><i class="fait"></i>Chapitre terminé : toutes ses fiches sont lues</span><span>{nb} fiches, un quiz pour débuter, 5 QCM, 1 attestation</span></div></div>
<ul class="plan-liste">{liste}</ul></section>
<section class="methode"><h2>Comment on apprend ici</h2><ol>
<li><strong>Découvrir</strong><p>Le problème à résoudre, l’idée en une phrase, un exemple concret. Aucun jargon sans explication.</p></li>
<li><strong>Approfondir</strong><p>Le fonctionnement exact, les commandes, les sorties à interpréter et les pièges qu’on rencontre en entreprise.</p></li>
<li><strong>Se tester</strong><p>Des exercices corrigés dans chaque fiche, puis un QCM par niveau qui explique chaque mauvaise réponse.</p></li></ol></section>
<section class="vitrine" aria-label="Pour aller plus loin">
<a href="pratique/index.html"><strong>Laboratoires et projet</strong><span>Monter un réseau d’entreprise pas à pas, provoquer des pannes et les résoudre.</span></a>
<a href="outils/cidr.html"><strong>Calculateur de sous-réseaux</strong><span>Voir le masque bit par bit et vérifier tes calculs.</span></a>
<a href="lexique.html"><strong>Lexique</strong><span>Tous les termes expliqués simplement, avec la fiche où ils apparaissent.</span></a>
</section>'''
    return coquille(f'Nexorya — {SLOGAN}', corps, 0, '')


# ----------------------------------------------------------------------- QCM
def page_qcm(num, plan):
    niv = next(n for n in plan['niveaux'] if n['num'] == num)
    chemin = os.path.join(CONTENU, 'qcm', f'niveau-{num}.yaml')
    d = yaml.safe_load(open(chemin, encoding='utf-8'))
    rng = random.Random(1000 + num)
    qs = d['questions']
    pos = [i % 4 for i in range(len(qs))]
    rng.shuffle(pos)
    sortie = []
    for i, q in enumerate(qs):
        fausses = list(q['fausses']); rng.shuffle(fausses)
        choix, pq = [], []
        for p in range(4):
            if p == pos[i]:
                choix.append(q['bonne'][0]); pq.append(q['bonne'][1])
            else:
                t, w = fausses.pop(); choix.append(t); pq.append(w)
        fiche = TROUVE.get(q.get('fiche'))
        sortie.append(dict(niveau=q['niveau'], situation=q['situation'].strip(), question=q['question'].strip(), choix=choix,
                           bonne=pos[i], pourquoi=pq, retenir=q['retenir'], fiche=fiche['url'] if fiche else '',
                           fiche_titre=fiche['titre'] if fiche else ''))
    donnees = json.dumps(dict(niveau=num, questions=sortie), ensure_ascii=False).replace('</', '<\\/')
    n = len(sortie)
    corps = f'''<div class="qcm"><p class="fil"><a href="../index.html">Accueil</a> › <a href="../{niv["dossier"]}/index.html">{e(niv["titre"])}</a> › QCM</p>
<h1>{'Le quiz du débutant' if num == 0 else f'QCM du niveau {num}'}</h1>
<div id="qcm-accueil"><p class="qcm-intro">{n} questions{' pour vérifier que les repères du parcours « Je débute » sont en place' if num == 0 else ', de la découverte à l’expertise'}. Chacune part d’une situation réelle. Après chaque réponse, tu vois pourquoi la bonne réponse est juste et pourquoi chaque autre proposition est fausse.</p>
<p class="qcm-intro">Seuil de validation : <strong>{-(-n*8//10)} bonnes réponses</strong> (80 %). Tu peux recommencer autant de fois que tu veux : seul ton meilleur score est gardé.</p>
<p><button class="bouton" id="qcm-demarrer" type="button">Commencer</button> <a class="bouton secondaire" href="../{niv["dossier"]}/revision.html">Réviser d’abord</a></p></div>
<div id="qcm-zone" hidden><div class="qcm-etat"><span id="qcm-avancement"></span><div class="jauge"><i id="qcm-jauge"></i></div></div><div id="qcm"></div></div></div>
<script type="application/json" id="qcm-donnees">{donnees}</script>'''
    return coquille(f'QCM niveau {num} — {niv["titre"]} | Nexorya', corps, 1, 'demarrer' if num == 0 else 'niveaux', couleur(niv)), n


# ----------------------------------------------------------------------- Pages diverses
def page_simple(titre, corps_html, prof, actif='', chapeau='', fil=''):
    c = f'<div class="page">{fil}<h1>{e(titre)}</h1>{f"<p class=chapeau>{e(chapeau)}</p>" if chapeau else ""}{corps_html}</div>'
    return coquille(f'{titre} | Nexorya', c, prof, actif)


def page_lexique(ordre):
    termes = {}
    for f in ordre:
        corps = re.split(r'^<!--\s*approfondir\s*-->', f['corps'], flags=re.M)[0]
        m = re.search(r'^## Les mots à connaître\s*\n(.*?)(?=^## |\Z)', corps, flags=re.M | re.S)
        if not m:
            continue
        for t, d in re.findall(r'^- \*\*(.+?)\*\*\s*[—–-]\s*(.+)$', m.group(1), flags=re.M):
            k = slug(t)
            if k not in termes:
                termes[k] = [t, d, []]
            termes[k][2].append(f)
    tri = sorted(termes.values(), key=lambda x: slug(x[0]))
    lettres, blocs, courant = [], [], None
    for t, d, fs in tri:
        L = slug(t)[:1].upper() or '#'
        if L.isdigit():
            L = '0-9'
        if L != courant:
            if courant:
                blocs.append('</dl>')
            blocs.append(f'<h2 id="lettre-{L}">{L}</h2><dl>')
            lettres.append(L); courant = L
        sources = ', '.join(f'<a href="{x["url"]}">{e(x["titre"])}</a>' for x in fs[:4])
        dd = Rendu().html(re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', d))[0]
        dd = re.sub(r'^<p>|</p>$', '', dd)
        blocs.append(f'<dt id="{slug(t)}">{e(t)}</dt><dd>{dd} <a href="{fs[0]["url"]}">Voir : {e(fs[0]["titre"])}</a>{" · aussi " + sources.split(", ",1)[1] if len(fs) > 1 else ""}</dd>')
    if courant:
        blocs.append('</dl>')
    nav = '<nav class="lettres" aria-label="Lettres">' + ''.join(f'<a href="#lettre-{L}">{L}</a>' for L in lettres) + '</nav>'
    return page_simple('Lexique', nav + '<div class="lexique">' + ''.join(blocs) + '</div>', 0, 'lexique',
                       f'{len(tri)} termes expliqués simplement. Chaque définition renvoie à la fiche où le terme est présenté.'), len(tri)


def index_recherche(ordre):
    idx = []
    for f in ordre:
        titres = re.findall(r'^#{2,3} (.+)$', f['corps'], flags=re.M)
        ret = ' '.join(f.get('retenir') or [])
        idx.append(dict(t=f['titre'] + (f' — {f["nom"]}' if f.get('nom') else ''), s=f.get('idee', ''),
                        c=' '.join(titres) + ' ' + ret, u=f['url'], n=f['niveau']['titre']))
    return 'window.NX_INDEX=' + json.dumps(idx, ensure_ascii=False) + ';'


def page_progression(plan, totaux):
    data = [dict(num=n['num'], titre=n['titre'], couleur=f'var(--l{n["num"]})', ids=n['ids'],
                 total_qcm=totaux.get(n['num'], 0), qcm=f'qcm/niveau-{n["num"]}.html') for n in plan['niveaux']]
    corps = f'''<div id="progression" class="progression-niveaux"></div>
<section class="attestation-zone"><h2>Attestation de réussite</h2><p id="attestation-etat"></p>
<div id="attestation-form" hidden><label for="attestation-nom">Ton nom tel qu’il doit apparaître</label><br>
<input id="attestation-nom" autocomplete="name"> <button class="bouton" id="attestation-generer" type="button">Créer et imprimer l’attestation</button></div>
<p class="mode-aide">Attestation non officielle : elle reconnaît une autoévaluation, sans surveillance d’examen ni valeur de certification.</p></section>
<section style="margin-top:28px"><h2>Sauvegarder ma progression</h2><p>Ta progression est enregistrée dans ce navigateur. Pour la transférer sur un autre appareil, exporte-la puis importe le fichier.</p>
<p><button class="bouton secondaire" id="export" type="button">Exporter (.json)</button> <label class="bouton secondaire" style="cursor:pointer">Importer<input type="file" id="import" accept="application/json" hidden></label> <button class="bouton secondaire" id="reinit" type="button">Tout effacer</button></p></section>
<div class="certificat" id="certificat"><img src="assets/img/logo.svg" alt=""><p>Nexorya</p><h2>Attestation de réussite</h2><p>Cette attestation reconnaît que</p><div class="personne" id="cert-nom"></div>
<p>a obtenu au moins 80 % aux cinq QCM du parcours Nexorya :<br><strong>Ethernet et switching · IP et routage · Services · Sécurité · WAN et datacenter</strong></p><p id="cert-scores"></p><p>Le <span id="cert-date"></span></p>
<p class="mention">Attestation non officielle fondée sur une autoévaluation, sans surveillance ni authentification. Elle n’a pas valeur de certification professionnelle ou académique.</p></div>
<script>window.NX_NIVEAUX={json.dumps(data, ensure_ascii=False)};</script>'''
    return page_simple('Ma progression', corps, 0, 'progression', 'Les fiches que tu as lues, tes meilleurs scores aux QCM et ton attestation.')


# ======================================================================= Programme
ORDRE_IDX, TROUVE = {}, {}


def construire():
    plan, fiches, ordre = charger()
    ORDRE_IDX.update(fiches)
    for f in ordre:
        TROUVE.setdefault(f['id'], f)
        TROUVE[f['niveau']['dossier'] + '/' + f['id']] = f
    if os.path.exists(SORTIE):
        shutil.rmtree(SORTIE)
    os.makedirs(SORTIE)
    shutil.copytree(THEME, os.path.join(SORTIE, 'assets'), ignore=shutil.ignore_patterns('outils'))
    ecrire = lambda chemin, t: (os.makedirs(os.path.dirname(os.path.join(SORTIE, chemin)), exist_ok=True),
                                open(os.path.join(SORTIE, chemin), 'w', encoding='utf-8').write(t))
    for i, f in enumerate(ordre):
        ecrire(f['url'], page_fiche(f, plan, ordre, i))
    for niv in plan['niveaux']:
        ecrire(f'{niv["dossier"]}/index.html', page_niveau(niv, plan))
        ecrire(f'{niv["dossier"]}/revision.html', page_revision(niv))
    totaux = {}
    for num in range(0, 6):
        if os.path.exists(os.path.join(CONTENU, 'qcm', f'niveau-{num}.yaml')):
            h, n = page_qcm(num, plan)
            totaux[num] = n
            ecrire(f'qcm/niveau-{num}.html', h)
        else:
            totaux[num] = 0
            ecrire(f'qcm/niveau-{num}.html', page_simple(f'QCM du niveau {num}', '<p>Ce QCM est en cours de rédaction.</p>', 1, 'niveaux'))
    ecrire('index.html', page_accueil(plan, ordre))
    lex, nlex = page_lexique(ordre)
    ecrire('lexique.html', lex)
    ecrire('assets/js/index-recherche.js', index_recherche(ordre))
    ecrire('recherche.html', page_simple('Rechercher', '<label class="visuellement-cache" for="champ-recherche">Mot à rechercher</label><input class="recherche-champ" id="champ-recherche" type="search" placeholder="Ex. VLAN, adresse IP, boucle, Wi-Fi…" autofocus><ul class="resultats" id="resultats"></ul>', 0, '', 'Cherche une technologie, un sigle ou une idée dans toutes les fiches.').replace('<script src="assets/js/nexorya.js">', '<script src="assets/js/index-recherche.js"></script><script src="assets/js/nexorya.js">'))
    ecrire('progression.html', page_progression(plan, totaux))
    # pages libres (pratique, outils, à propos)
    for dossier in ('pratique', 'outils', ''):
        base = os.path.join(CONTENU, 'pages', dossier) if dossier else os.path.join(CONTENU, 'pages')
        if not os.path.isdir(base):
            continue
        for nom in sorted(os.listdir(base)):
            if not (nom.endswith('.md') or nom.endswith('.html')):
                continue
            prof = 1 if dossier else 0
            chemin_sortie = (dossier + '/' if dossier else '') + nom.rsplit('.', 1)[0] + '.html'
            if nom.endswith('.md'):
                meta, corps = lire_md(os.path.join(base, nom))
                h = Rendu().html(corps)[0]
                fil = f'<p class="fil"><a href="{"../" * prof}index.html">Accueil</a>{" › <a href=index.html>Pratique</a>" if dossier == "pratique" and nom != "index.md" else ""}</p>'
                ecrire(chemin_sortie, page_simple(meta.get('titre', nom), f'<div class="prose">{h}</div>', prof, meta.get('actif', dossier), meta.get('chapeau', ''), fil))
            else:
                meta, corps = lire_md(os.path.join(base, nom))
                ecrire(chemin_sortie, page_simple(meta.get('titre', nom), corps, prof, meta.get('actif', dossier), meta.get('chapeau', '')).replace(
                    '<script src="' + '../' * prof + 'assets/js/nexorya.js">', ''.join(f'<script src="{"../" * prof}assets/js/{s}"></script>' for s in meta.get('scripts', [])) + '<script src="' + '../' * prof + 'assets/js/nexorya.js">'))
    open(os.path.join(SORTIE, '.nojekyll'), 'w').close()
    absentes = [f['source'] for f in ordre if f.get('_absente')]
    print(f'Nexorya {VERSION} : {len(ordre)} fiches ({len(absentes)} à rédiger), {sum(totaux.values())} questions de QCM, {nlex} termes au lexique.')
    return ordre


def verifier():
    casses = []
    for d, _, fichiers in os.walk(SORTIE):
        for nom in fichiers:
            if not nom.endswith('.html'):
                continue
            p = os.path.join(d, nom)
            h = open(p, encoding='utf-8').read()
            for u in re.findall(r'(?:href|src)="([^"#?]+)', h):
                if u.startswith(('http:', 'https:', 'mailto:', 'data:')) or u.startswith('{'):
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(d, u))):
                    casses.append((os.path.relpath(p, SORTIE), u))
    for p, u in casses:
        print('Lien cassé :', p, '→', u)
    print(f'{len(casses)} lien(s) cassé(s).')
    return casses


if __name__ == '__main__':
    construire()
    if '--verifier' in sys.argv and verifier():
        sys.exit(1)
