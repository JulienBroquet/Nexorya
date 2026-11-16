/* Nexorya — comportements de l'interface (aucune dépendance, fonctionne hors ligne) */
(function () {
  'use strict';
  var CLE = 'nexorya:v1';
  var doc = document.documentElement;

  /* ---------- Stockage local ---------- */
  function lire() {
    try { return JSON.parse(localStorage.getItem(CLE)) || {}; } catch (e) { return {}; }
  }
  function ecrire(d) {
    try { localStorage.setItem(CLE, JSON.stringify(d)); return true; } catch (e) { return false; }
  }
  var etat = lire();
  etat.lu = etat.lu || {}; etat.qcm = etat.qcm || {};
  function sauver() { return ecrire(etat); }
  window.Nexorya = { etat: etat, sauver: sauver };

  /* ---------- Thème clair / sombre ---------- */
  var themeChoisi = etat.theme || (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'sombre' : 'clair');
  doc.setAttribute('data-theme', themeChoisi);
  document.addEventListener('DOMContentLoaded', function () {
    var bt = document.getElementById('bascule-theme');
    function libelle() { if (bt) bt.setAttribute('aria-label', doc.getAttribute('data-theme') === 'sombre' ? 'Passer en thème clair' : 'Passer en thème sombre'); }
    libelle();
    if (bt) bt.addEventListener('click', function () {
      var t = doc.getAttribute('data-theme') === 'sombre' ? 'clair' : 'sombre';
      doc.setAttribute('data-theme', t); etat.theme = t; sauver(); libelle();
    });
    var bn = document.getElementById('bascule-nav'), barre = document.querySelector('.barre');
    if (bn && barre) bn.addEventListener('click', function () {
      var o = barre.classList.toggle('ouverte'); bn.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
    var menu = document.getElementById('menu-mobile'), lat = document.querySelector('.lateral');
    if (menu && lat) menu.addEventListener('click', function () {
      var o = lat.classList.toggle('ouvert'); menu.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
    marquerLus();
    pageFiche();
    pageNiveau();
    pagePlan();
    pageRecherche();
    pageQcm();
    pageProgression();
    sommaireActif();
  });

  /* ---------- Repères « lu » dans les listes ---------- */
  function marquerLus() {
    document.querySelectorAll('[data-fiche]').forEach(function (a) {
      if (etat.lu[a.getAttribute('data-fiche')]) a.classList.add('lu');
    });
  }

  /* ---------- Fiche : modes Découvrir / Approfondir, lecture ---------- */
  function pageFiche() {
    var fiche = document.querySelector('[data-fiche-id]');
    if (!fiche) return;
    var id = fiche.getAttribute('data-fiche-id');
    var onglets = document.querySelectorAll('.modes button');
    var parties = document.querySelectorAll('[data-partie]');
    function montrer(mode, focus) {
      if (!document.querySelector('[data-partie="' + mode + '"]')) mode = 'decouvrir';
      onglets.forEach(function (b) { b.setAttribute('aria-selected', b.dataset.mode === mode ? 'true' : 'false'); b.tabIndex = b.dataset.mode === mode ? 0 : -1; });
      parties.forEach(function (p) { p.hidden = p.getAttribute('data-partie') !== mode; });
      document.querySelectorAll('[data-sommaire]').forEach(function (s) { s.hidden = s.getAttribute('data-sommaire') !== mode; });
      if (focus) { var b = document.querySelector('.modes button[data-mode="' + mode + '"]'); if (b) b.focus(); }
    }
    var initial = location.hash === '#approfondir' ? 'approfondir' : (location.hash === '#decouvrir' ? 'decouvrir' : (etat.mode || 'decouvrir'));
    if (location.hash && location.hash.length > 1 && !/^#(approfondir|decouvrir)$/.test(location.hash)) {
      var cible = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (cible) { var p = cible.closest('[data-partie]'); if (p) initial = p.getAttribute('data-partie'); }
    }
    montrer(initial);
    onglets.forEach(function (b, i) {
      b.addEventListener('click', function () { etat.mode = b.dataset.mode; sauver(); montrer(b.dataset.mode); history.replaceState(null, '', '#' + b.dataset.mode); });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          var n = onglets[(i + (e.key === 'ArrowRight' ? 1 : onglets.length - 1)) % onglets.length];
          etat.mode = n.dataset.mode; sauver(); montrer(n.dataset.mode, true);
        }
      });
    });
    var bt = document.getElementById('bouton-lu');
    function maj() {
      var lu = !!etat.lu[id];
      if (!bt) return;
      bt.classList.toggle('lu', lu);
      bt.textContent = lu ? '✓ Fiche marquée comme lue' : 'Marquer cette fiche comme lue';
      bt.setAttribute('aria-pressed', lu ? 'true' : 'false');
    }
    if (bt) bt.addEventListener('click', function () { if (etat.lu[id]) delete etat.lu[id]; else etat.lu[id] = Date.now(); sauver(); maj(); marquerLus(); });
    maj();
  }

  function sommaireActif() {
    var liens = document.querySelectorAll('.sommaire a');
    if (!liens.length || !('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          liens.forEach(function (a) { a.classList.toggle('actif', a.getAttribute('href') === '#' + e.target.id); });
        }
      });
    }, { rootMargin: '0px 0px -70% 0px' });
    document.querySelectorAll('.prose h2[id]').forEach(function (h) { obs.observe(h); });
  }

  /* ---------- Niveau : progression ---------- */
  function compter(ids) { return ids.filter(function (i) { return etat.lu[i]; }).length; }
  function pageNiveau() {
    document.querySelectorAll('[data-chapitre]').forEach(function (c) {
      var ids = c.getAttribute('data-chapitre').split(',');
      var arret = c.querySelector('.arret');
      if (arret && ids.length && compter(ids) === ids.length) arret.classList.add('fait');
    });
    var j = document.querySelector('[data-jauge]');
    if (j) {
      var ids = j.getAttribute('data-jauge').split(',');
      var n = compter(ids);
      j.querySelector('i').style.width = Math.round(100 * n / ids.length) + '%';
      var t = document.querySelector('[data-jauge-texte]');
      if (t) t.textContent = n + ' fiche' + (n > 1 ? 's' : '') + ' lue' + (n > 1 ? 's' : '') + ' sur ' + ids.length;
    }
  }

  /* ---------- Plan des lignes (accueil) ---------- */
  function pagePlan() {
    document.querySelectorAll('.station[data-ids]').forEach(function (s) {
      var ids = s.getAttribute('data-ids').split(',');
      if (ids.length && compter(ids) === ids.length) s.classList.add('fait');
    });
  }

  /* ---------- Recherche ---------- */
  function normaliser(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function pageRecherche() {
    var champ = document.getElementById('champ-recherche');
    var liste = document.getElementById('resultats');
    if (!champ || !liste || !window.NX_INDEX) return;
    var racine = document.body.getAttribute('data-racine') || '';
    var idx = window.NX_INDEX.map(function (e) { e._t = normaliser(e.t); e._s = normaliser(e.s + ' ' + e.c); return e; });
    function chercher() {
      var q = normaliser(champ.value.trim());
      liste.innerHTML = '';
      if (q.length < 2) return;
      var mots = q.split(/\s+/);
      var res = idx.map(function (e) {
        var score = 0;
        for (var i = 0; i < mots.length; i++) {
          var m = mots[i];
          if (e._t === m) score += 50; else if (e._t.indexOf(m) >= 0) score += 20;
          if (e._s.indexOf(m) >= 0) score += 5; else if (e._t.indexOf(m) < 0) return 0;
        }
        return score ? { e: e, s: score } : null;
      }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 30);
      if (!res.length) { liste.innerHTML = '<li>Aucun résultat pour « ' + echapper(champ.value) + ' ». Essaie un sigle (OSPF) ou un mot simple (adresse, boucle, câble).</li>'; return; }
      liste.innerHTML = res.map(function (r) {
        return '<li><small>' + echapper(r.e.n) + '</small><a href="' + racine + r.e.u + '">' + echapper(r.e.t) + '</a><p>' + echapper(r.e.s) + '</p></li>';
      }).join('');
    }
    champ.addEventListener('input', chercher);
    var q = new URLSearchParams(location.search).get('q');
    if (q) { champ.value = q; chercher(); }
  }
  function echapper(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ---------- QCM : une question à la fois, correction immédiate ---------- */
  function pageQcm() {
    var zone = document.getElementById('qcm');
    var src = document.getElementById('qcm-donnees');
    if (!zone || !src) return;
    var data = JSON.parse(src.textContent);
    var niveau = data.niveau, Q = data.questions, i = 0, points = 0, reponses = [];
    var racine = document.body.getAttribute('data-racine') || '';
    var lettres = 'ABCD';
    var etatTxt = document.getElementById('qcm-avancement'), jauge = document.getElementById('qcm-jauge');
    function classe(n) { return normaliser(n); }
    function afficher() {
      var q = Q[i];
      etatTxt.textContent = 'Question ' + (i + 1) + ' sur ' + Q.length + ' · ' + points + ' bonne' + (points > 1 ? 's' : '') + ' réponse' + (points > 1 ? 's' : '');
      jauge.style.width = Math.round(100 * i / Q.length) + '%';
      zone.innerHTML = '<article class="question" aria-live="polite"><span class="etiquette ' + classe(q.niveau) + '">' + echapper(q.niveau) + '</span>' +
        '<p class="situation">' + echapper(q.situation) + '</p><h2 id="q-titre">' + echapper(q.question) + '</h2>' +
        '<div class="choix" role="group" aria-labelledby="q-titre">' + q.choix.map(function (c, j) {
          return '<button type="button" data-j="' + j + '"><b>' + lettres[j] + '</b><span>' + echapper(c) + '</span></button>';
        }).join('') + '</div><div id="q-verdict"></div></article>' +
        '<div class="qcm-nav"><span></span><button class="bouton" id="q-suivant" hidden>' + (i + 1 < Q.length ? 'Question suivante' : 'Voir mon résultat') + '</button></div>';
      zone.querySelectorAll('.choix button').forEach(function (b) { b.addEventListener('click', function () { repondre(+b.dataset.j); }); });
      var premier = zone.querySelector('.choix button'); if (premier && i > 0) premier.focus();
    }
    function repondre(j) {
      var q = Q[i], ok = j === q.bonne;
      if (ok) points++;
      reponses.push({ q: i, j: j, ok: ok });
      zone.querySelectorAll('.choix button').forEach(function (b) {
        var k = +b.dataset.j; b.disabled = true;
        if (k === q.bonne) b.classList.add('juste');
        if (k === j && !ok) b.classList.add('faux');
        if (k !== q.bonne) b.insertAdjacentHTML('beforeend', '<span class="pourquoi">' + echapper(q.pourquoi[k]) + '</span>');
      });
      var v = document.getElementById('q-verdict');
      v.innerHTML = '<div class="verdict ' + (ok ? 'ok' : 'ko') + '"><h3>' + (ok ? 'Bonne réponse' : 'Pas tout à fait : la bonne réponse est ' + lettres[q.bonne]) + '</h3>' +
        '<p>' + echapper(q.pourquoi[q.bonne]) + '</p><p><strong>À retenir :</strong> ' + echapper(q.retenir) + '</p>' +
        (q.fiche ? '<p><a href="' + racine + q.fiche + '">Relire la fiche ' + echapper(q.fiche_titre || '') + '</a></p>' : '') + '</div>';
      var s = document.getElementById('q-suivant'); s.hidden = false; s.focus();
      s.addEventListener('click', function () { i++; if (i < Q.length) afficher(); else fin(); });
    }
    function fin() {
      jauge.style.width = '100%';
      var seuil = Math.ceil(Q.length * 0.8), reussi = points >= seuil;
      var ancien = etat.qcm[niveau] || {};
      etat.qcm[niveau] = { meilleur: Math.max(points, ancien.meilleur || 0), total: Q.length, dernier: points, date: new Date().toISOString(), essais: (ancien.essais || 0) + 1 };
      var garde = sauver();
      var rates = reponses.filter(function (r) { return !r.ok; });
      etatTxt.textContent = 'Terminé';
      zone.innerHTML = '<div class="resultat"><p>Ton score</p><p class="score">' + points + ' / ' + Q.length + '</p>' +
        '<p>' + (reussi ? 'Niveau validé : tu as atteint le seuil de ' + seuil + ' bonnes réponses (80 %).' : 'Il faut ' + seuil + ' bonnes réponses (80 %) pour valider ce niveau. Relis les fiches ci-dessous, puis réessaie.') + '</p>' +
        (garde ? '' : '<p class="mode-aide">Ton navigateur bloque l’enregistrement local : le score ne sera pas conservé.</p>') +
        '<p><button class="bouton" onclick="location.reload()">Recommencer</button> <a class="bouton secondaire" href="' + racine + 'progression.html">Voir ma progression</a></p>' +
        (rates.length ? '<div class="revoir prose"><h3>À revoir</h3><ul>' + rates.map(function (r) {
          var q = Q[r.q]; return '<li><strong>' + echapper(q.question) + '</strong><br>' + echapper(q.retenir) + (q.fiche ? ' · <a href="' + racine + q.fiche + '">relire la fiche</a>' : '') + '</li>';
        }).join('') + '</ul></div>' : '') + '</div>';
    }
    document.getElementById('qcm-demarrer').addEventListener('click', function () {
      document.getElementById('qcm-accueil').hidden = true; document.getElementById('qcm-zone').hidden = false; afficher();
    });
  }

  /* ---------- Progression et attestation ---------- */
  function pageProgression() {
    var z = document.getElementById('progression');
    if (!z || !window.NX_NIVEAUX) return;
    var tous = true;
    z.innerHTML = window.NX_NIVEAUX.map(function (n) {
      var lus = compter(n.ids), q = etat.qcm[n.num] || null, seuil = Math.ceil(n.total_qcm * 0.8);
      var valide = q && q.total === n.total_qcm && q.meilleur >= seuil;
      if (n.num > 0 && !valide) tous = false;
      return '<div class="ligne-prog" style="--ligne:' + n.couleur + '"><span class="numero" style="background:' + n.couleur + '">' + n.num + '</span>' +
        '<div><strong>' + echapper(n.titre) + '</strong><small>' + lus + ' fiche' + (lus > 1 ? 's' : '') + ' lue' + (lus > 1 ? 's' : '') + ' sur ' + n.ids.length + '</small><div class="jauge"><i style="width:' + Math.round(100 * lus / n.ids.length) + '%"></i></div></div>' +
        (n.total_qcm ? '<div><small>QCM</small><strong>' + (q ? q.meilleur + ' / ' + n.total_qcm : 'pas encore passé') + '</strong></div><div>' + (valide ? '<strong style="color:var(--ok)">Validé</strong>' : '<a href="' + n.qcm + '">' + (q ? 'Réessayer' : 'Passer le QCM') + '</a>') + '</div>' : '<div></div><div></div>') + '</div>';
    }).join('');
    var att = document.getElementById('attestation-etat'), form = document.getElementById('attestation-form');
    if (att) att.textContent = tous ? 'Les cinq QCM sont validés : tu peux éditer ton attestation.' : 'L’attestation se débloque quand chacun des cinq QCM atteint 80 %.';
    if (form) form.hidden = !tous;
    var bt = document.getElementById('attestation-generer');
    if (bt) bt.addEventListener('click', function () {
      var nom = document.getElementById('attestation-nom').value.trim().replace(/\s+/g, ' ');
      if (nom.length < 3) { document.getElementById('attestation-nom').focus(); return; }
      document.getElementById('cert-nom').textContent = nom;
      document.getElementById('cert-date').textContent = new Date().toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' });
      document.getElementById('cert-scores').textContent = window.NX_NIVEAUX.filter(function (n) { return n.num > 0; }).map(function (n) { return 'Niveau ' + n.num + ' : ' + etat.qcm[n.num].meilleur + '/' + n.total_qcm; }).join(' · ');
      document.getElementById('certificat').classList.add('visible');
      setTimeout(function () { window.print(); }, 200);
    });
    var ex = document.getElementById('export'), im = document.getElementById('import');
    if (ex) ex.addEventListener('click', function () {
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([JSON.stringify(etat, null, 2)], { type: 'application/json' }));
      a.download = 'nexorya-progression.json'; a.click();
    });
    if (im) im.addEventListener('change', function () {
      var f = im.files[0]; if (!f) return;
      f.text().then(function (t) { try { var d = JSON.parse(t); etat.lu = d.lu || {}; etat.qcm = d.qcm || {}; sauver(); location.reload(); } catch (e) { alert('Ce fichier n’est pas une sauvegarde Nexorya valide.'); } });
    });
    var rz = document.getElementById('reinit');
    if (rz) rz.addEventListener('click', function () { if (confirm('Effacer toute ta progression sur ce navigateur ?')) { etat.lu = {}; etat.qcm = {}; sauver(); location.reload(); } });
  }
})();
