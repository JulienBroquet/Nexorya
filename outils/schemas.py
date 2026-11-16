# -*- coding: utf-8 -*-
"""Mini-langages de schémas de Nexorya.

Deux blocs de code Markdown sont transformés en SVG lors de la génération du site :

```sequence
titre: Obtenir une adresse avec DHCP
PC | Serveur DHCP
PC -> Serveur DHCP : DISCOVER (broadcast)
Serveur DHCP --> PC : OFFER 192.168.1.20
PC -x Serveur DHCP : message perdu
note PC : texte d'une note
note PC, Serveur DHCP : note qui couvre deux acteurs
== Étape suivante ==
```

```topologie
titre: Trois switches en triangle
SW1 switch 1,0 "SW1" "racine"
SW2 switch 0,1 "SW2"
SW1 -- SW2 "coût 4"
SW2 -x- SW3 "bloqué"
zone "VLAN 10" 0,0 1,1
```
Liens : `--` normal, `++` chemin actif (vert), `==` agrégat, `-x-` bloqué, `..` logique / tunnel, `~~` sans fil.
Types : switch, l3, routeur, pc, portable, serveur, nuage, parefeu, ap, telephone, camera, utilisateur, imprimante, vm, boite.
"""
import html
import re
import shlex

CH = 7.3  # largeur moyenne d'un caractère à 14 px


def _e(s):
    return html.escape(str(s), quote=True)


def _wrap(texte, largeur_px, ch=CH):
    maxc = max(8, int(largeur_px / ch))
    mots, lignes, cur = texte.split(), [], ''
    for m in mots:
        if len(cur) + len(m) + (1 if cur else 0) <= maxc:
            cur = (cur + ' ' + m).strip()
        else:
            if cur:
                lignes.append(cur)
            cur = m
    if cur:
        lignes.append(cur)
    return lignes or ['']


# ----------------------------------------------------------------- séquence
def sequence(src):
    titre, acteurs, etapes = None, None, []
    for brut in src.strip().splitlines():
        l = brut.strip()
        if not l or l.startswith('#'):
            continue
        if l.lower().startswith('titre:'):
            titre = l.split(':', 1)[1].strip(); continue
        if acteurs is None and '|' in l:
            acteurs = [a.strip() for a in l.split('|')]; continue
        if l.startswith('==') and l.endswith('=='):
            etapes.append(('sep', l.strip('= ').strip())); continue
        if l.lower().startswith('note '):
            qui, txt = re.split(r'\s:\s|:\s', l[5:], maxsplit=1)
            etapes.append(('note', [q.strip() for q in qui.split(',')], txt.strip())); continue
        m = re.match(r'^(.+?)\s*(-->|-x|->)\s*(.+?)(?:\s+:\s+(.*))?$', l)
        if not m:
            raise ValueError('Ligne de séquence non comprise : ' + l)
        genre = {'-->': 'rep', '-x': 'perdu', '->': 'msg'}[m.group(2)]
        etapes.append((genre, m.group(1).strip(), m.group(3).strip(), (m.group(4) or '').strip()))
    n = len(acteurs)
    W, m = 760, 85
    pas = (W - 2 * m) / max(1, n - 1) if n > 1 else 0
    X = {a: (m + i * pas if n > 1 else W / 2) for i, a in enumerate(acteurs)}
    for et in etapes:
        for qui in ([et[1], et[2]] if et[0] in ('msg', 'rep', 'perdu') else (et[1] if et[0] == 'note' else [])):
            if qui not in X:
                raise ValueError('Acteur inconnu dans la séquence : ' + qui)
    out, y, num = [], 74, 0
    corps = []
    for et in etapes:
        if et[0] == 'sep':
            y += 8
            corps.append(f'<g class="sq-sep"><line x1="20" y1="{y}" x2="{W-20}" y2="{y}"/>'
                         f'<text x="{W/2}" y="{y-6}" text-anchor="middle">{_e(et[1])}</text></g>')
            y += 30
        elif et[0] == 'note':
            xs = [X[q] for q in et[1]]
            x1, x2 = min(xs), max(xs)
            larg = max(200, x2 - x1 + 150)
            cx = (x1 + x2) / 2
            lignes = _wrap(et[2], larg - 20, 7.0)
            h = 14 + 18 * len(lignes)
            gx = max(6, min(W - larg - 6, cx - larg / 2))
            t = ''.join(f'<text x="{gx + larg/2}" y="{y + 19 + 18*i}" text-anchor="middle">{_e(li)}</text>' for i, li in enumerate(lignes))
            corps.append(f'<g class="sq-note"><rect x="{gx}" y="{y}" width="{larg}" height="{h}" rx="6"/>{t}</g>')
            y += h + 34
        else:
            genre, a, b, txt = et
            num += 1
            xa, xb = X[a], X[b]
            if a == b:
                lignes = _wrap(f'{num}. {txt}', 230)
                ty = y
                t = ''.join(f'<text x="{xa+44}" y="{ty + 18*i + 4}">{_e(li)}</text>' for i, li in enumerate(lignes))
                corps.append(f'<g class="sq-msg"><path d="M{xa} {y} h30 v22 h-24" fill="none" stroke="currentColor" class="sq-boucle"/>'
                             f'<line x1="{xa+30}" y1="{y}" x2="{xa+30}" y2="{y}"/>{t}'
                             f'<polygon class="sq-pointe" points="{xa},{y+22} {xa+9},{y+17} {xa+9},{y+27}"/></g>')
                y += max(44, 18 * len(lignes) + 26)
                continue
            sens = 1 if xb > xa else -1
            span = abs(xb - xa)
            lignes = _wrap(f'{num}. {txt}' if txt else f'{num}.', max(span - 16, 150))
            ly = y + 18 * (len(lignes) - 1)
            cx = (xa + xb) / 2
            t = ''.join(f'<text x="{cx}" y="{y - 8 + 18*i}" text-anchor="middle">{_e(li)}</text>' for i, li in enumerate(lignes))
            fin = xb - sens * 2
            if genre == 'perdu':
                xf = xa + sens * span * 0.62
                corps.append(f'<g class="sq-msg perdu">{t}<line x1="{xa}" y1="{ly+4}" x2="{xf}" y2="{ly+4}"/>'
                             f'<path class="sq-croix" d="M{xf-8} {ly-4} l16 16 M{xf+8} {ly-4} l-16 16"/></g>')
            else:
                pts = f'{fin},{ly+4} {fin - sens*12},{ly-2} {fin - sens*12},{ly+10}'
                corps.append(f'<g class="sq-msg {"rep" if genre == "rep" else ""}">{t}'
                             f'<line x1="{xa}" y1="{ly+4}" x2="{fin - sens*10}" y2="{ly+4}"/>'
                             f'<polygon class="sq-pointe" points="{pts}"/></g>')
            y = ly + 50
    H = y + 6
    tete = []
    for a in acteurs:
        lignes = _wrap(a, min(150, max(pas - 14, 90)) if n > 1 else 200, 7.6)
        larg = min(max(len(max(lignes, key=len)) * 8.2 + 26, 80), 170)
        hb = 14 + 17 * len(lignes)
        t = ''.join(f'<text x="{X[a]}" y="{12 + 21 + 17*i}" text-anchor="middle">{_e(li)}</text>' for i, li in enumerate(lignes))
        tete.append(f'<line class="sq-vie" x1="{X[a]}" y1="{12+hb}" x2="{X[a]}" y2="{H}"/>'
                    f'<g class="sq-acteur"><rect x="{X[a]-larg/2}" y="12" width="{larg}" height="{hb}" rx="8"/>{t}</g>')
    svg = (f'<svg viewBox="0 0 {W} {H}" width="{W}" role="img" aria-label="{_e(titre or "Diagramme de séquence")}" xmlns="http://www.w3.org/2000/svg">'
           + ''.join(tete) + ''.join(corps) + '</svg>')
    return svg, titre


# ----------------------------------------------------------------- topologie
COLW, ROWH, MX, MY = 122, 140, 110, 50


def _icone(t):
    if t == 'switch' or t == 'l3':
        ports = ''.join(f'<rect class="tp-ico-plein" x="{-22 + i*9}" y="-3" width="5" height="5" rx="1"/>' for i in range(5))
        extra = '<path class="tp-ico-trait" d="M-10 -20 h20 m-6 -4 l6 4 l-6 4"/>' if t == 'l3' else ''
        return f'<rect class="tp-ico" x="-30" y="-13" width="60" height="26" rx="5"/>{ports}{extra}'
    if t == 'routeur':
        return ('<circle class="tp-ico" r="19"/><path class="tp-ico-trait" d="M-11 0 h22 M0 -11 v22 '
                'M7 -4 l4 4 l-4 4 M-7 -4 l-4 4 l4 4 M-4 -7 l4 -4 l4 4 M-4 7 l4 4 l4 -4"/>')
    if t in ('pc', 'portable'):
        if t == 'portable':
            return '<rect class="tp-ico" x="-18" y="-15" width="36" height="22" rx="3"/><path class="tp-ico" d="M-25 9 h50 l-4 6 h-42 z"/>'
        return '<rect class="tp-ico" x="-21" y="-18" width="42" height="28" rx="3"/><path class="tp-ico-trait" d="M0 10 v6 M-10 17 h20"/>'
    if t == 'serveur':
        return ('<rect class="tp-ico" x="-15" y="-22" width="30" height="44" rx="4"/>'
                '<path class="tp-ico-trait" d="M-8 -12 h16 M-8 -4 h16 M-8 4 h16"/><circle class="tp-ico-plein" cx="0" cy="14" r="2.5"/>')
    if t == 'nuage':
        return '<path class="tp-ico" d="M-24 12 a11 11 0 0 1 2 -21 a14 14 0 0 1 26 -5 a11 11 0 0 1 20 9 a9 9 0 0 1 -2 17 z"/>'
    if t == 'parefeu':
        return ('<rect class="tp-ico" x="-26" y="-16" width="52" height="32" rx="3"/>'
                '<path class="tp-ico-trait" d="M-26 -5 h52 M-26 6 h52 M-9 -16 v11 M9 -16 v11 M0 -5 v11 M-17 -5 v11 M17 -5 v11 M-9 6 v10 M9 6 v10"/>')
    if t == 'ap':
        return ('<rect class="tp-ico" x="-18" y="2" width="36" height="12" rx="6"/>'
                '<path class="tp-ico-trait" d="M-9 -4 a13 13 0 0 1 18 0 M-15 -10 a21 21 0 0 1 30 0"/>')
    if t == 'telephone':
        return '<rect class="tp-ico" x="-13" y="-20" width="26" height="40" rx="5"/><rect class="tp-ico-plein" x="-8" y="-14" width="16" height="12" rx="2" opacity=".35"/>'
    if t == 'camera':
        return '<rect class="tp-ico" x="-22" y="-12" width="34" height="24" rx="4"/><path class="tp-ico" d="M12 -6 l12 -6 v24 l-12 -6 z"/><circle class="tp-ico-plein" cx="-5" cy="0" r="5" opacity=".4"/>'
    if t == 'utilisateur':
        return '<circle class="tp-ico" cy="-10" r="9"/><path class="tp-ico" d="M-17 18 a17 15 0 0 1 34 0 z"/>'
    if t == 'imprimante':
        return '<rect class="tp-ico" x="-22" y="-8" width="44" height="20" rx="3"/><rect class="tp-ico" x="-13" y="-19" width="26" height="11"/><rect class="tp-ico" x="-13" y="8" width="26" height="10"/>'
    if t == 'vm':
        return '<rect class="tp-ico" x="-20" y="-15" width="40" height="30" rx="4" stroke-dasharray="4 3"/><path class="tp-ico-trait" d="M-9 -2 h18 M-9 5 h12"/>'
    return '<rect class="tp-ico" x="-24" y="-15" width="48" height="30" rx="6"/>'


def topologie(src):
    titre, noeuds, liens, zones = None, {}, [], []
    ops = ['-x-', '++', '--', '==', '..', '~~']
    for brut in src.strip().splitlines():
        l = brut.strip()
        if not l or l.startswith('#'):
            continue
        if l.lower().startswith('titre:'):
            titre = l.split(':', 1)[1].strip(); continue
        tok = shlex.split(l)
        if tok[0] == 'zone':
            c1, r1 = map(float, tok[2].split(',')); c2, r2 = map(float, tok[3].split(','))
            zones.append((tok[1], c1, r1, c2, r2)); continue
        if len(tok) >= 3 and tok[1] in ops:
            liens.append((tok[0], tok[1], tok[2], tok[3:])); continue
        nid, typ, pos = tok[0], tok[1], tok[2]
        c, r = map(float, pos.split(','))
        lib = tok[3] if len(tok) > 3 else nid
        sous = tok[4] if len(tok) > 4 else ''
        noeuds[nid] = (typ, c, r, lib, sous)
    maxc = max(v[1] for v in noeuds.values()); maxr = max(v[2] for v in noeuds.values())
    W = max(440, 2 * MX + maxc * COLW)
    H = 2 * MY + maxr * ROWH + 46

    def P(c, r):
        return MX + c * COLW + (W - 2 * MX - maxc * COLW) / 2, MY + r * ROWH
    out = []
    for lib, c1, r1, c2, r2 in zones:
        x1, y1 = P(c1, r1); x2, y2 = P(c2, r2)
        out.append(f'<rect class="tp-zone" x="{x1-62}" y="{y1-40}" width="{x2-x1+124}" height="{y2-y1+96}" rx="14"/>'
                   f'<text class="tp-zone-lib" x="{x1-52}" y="{y1-24}">{_e(lib)}</text>')
    for a, op, b, labels in liens:
        if a not in noeuds or b not in noeuds:
            raise ValueError(f'Lien vers un nœud inconnu : {a} {op} {b}')
        xa, ya = P(*noeuds[a][1:3]); xb, yb = P(*noeuds[b][1:3])
        cls = {'--': '', '++': 'actif', '==': 'double', '-x-': 'bloque', '..': 'logique', '~~': 'sansfil'}[op]
        out.append(f'<line class="tp-lien {cls}" x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}"/>')
        if op == '==':
            out.append(f'<line class="tp-lien-int" x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="var(--surface)" stroke-width="3"/>')
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        if op == '-x-':
            out.append(f'<path class="sq-croix" d="M{mx-7} {my-7} l14 14 M{mx+7} {my-7} l-14 14"/>')
        if labels and labels[0]:
            L = ((xb - xa) ** 2 + (yb - ya) ** 2) ** .5 or 1
            ux, uy = (xb - xa) / L, (yb - ya) / L
            nx, ny = -uy, ux
            if abs(ny) > 0.3 and ny > 0 or (abs(ny) <= 0.3 and nx < 0):
                nx, ny = -nx, -ny
            if abs(uy) > 0.9:          # lien presque vertical : texte à droite
                nx, ny = 1, 0
            off = 12
            tx, ty = mx + nx * off, my + ny * off + (4 if abs(ny) < 0.3 else 0)
            anc = 'middle' if abs(nx) < 0.35 else ('start' if nx > 0 else 'end')
            out.append(f'<text class="tp-etiq{" ko" if op == "-x-" else ""}" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}">{_e(labels[0])}</text>')
        for k, extremite in ((1, 'a'), (2, 'b')):
            if len(labels) > k and labels[k]:
                (x0, y0), (x1, y1) = ((xa, ya), (xb, yb)) if extremite == 'a' else ((xb, yb), (xa, ya))
                d = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 or 1
                px, py = x0 + (x1 - x0) / d * 46, y0 + (y1 - y0) / d * 46
                out.append(f'<text class="tp-etiq" x="{px + (8 if abs(x1-x0) < 5 else 0)}" y="{py - (8 if abs(y1-y0) < 5 else 0)}" text-anchor="{"start" if abs(x1-x0) < 5 else "middle"}" font-size="12">{_e(labels[k])}</text>')
    for nid, (typ, c, r, lib, sous) in noeuds.items():
        x, y = P(c, r)
        s = f'<g transform="translate({x} {y})">{_icone(typ)}</g>'
        s += f'<text class="tp-lib" x="{x}" y="{y+40}" text-anchor="middle">{_e(lib)}</text>'
        if sous:
            s += f'<text class="tp-sous" x="{x}" y="{y+56}" text-anchor="middle">{_e(sous)}</text>'
        out.append(s)
    svg = (f'<svg viewBox="0 0 {W} {H}" width="{W}" role="img" aria-label="{_e(titre or "Schéma de topologie")}" xmlns="http://www.w3.org/2000/svg">'
           + ''.join(out) + '</svg>')
    return svg, titre
