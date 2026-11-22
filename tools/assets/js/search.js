/* search.js — клиентский поиск по каталогу иэк.бел (search-index.json). */
(function () {
  "use strict";

  // латиница → похожая кириллица при сравнении: в данных «4P C 6А» и «2Р 25А»
  // сосуществуют (P латинская рядом с А кириллической), запрос клиента может
  // быть в любом алфавите
  var XLAT = {p: "р", a: "а", c: "с", e: "е", o: "о", x: "х", k: "к", m: "м", t: "т", y: "у", h: "н"};
  function norm(s) {
    return (s || "").toLowerCase().replace(/[a-z]/g, function (ch) { return XLAT[ch] || ch; });
  }

  var input = document.getElementById("q");
  var out = document.getElementById("results");
  if (!input || !out) return;

  var INDEX = null;

  fetch("../search-index.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (idx) {
      INDEX = idx;
      var q = new URLSearchParams(location.search).get("q") || "";
      if (q) { input.value = q; }
      render(input.value);
    })
    .catch(function () {
      out.innerHTML = '<p class="note">Индекс поиска недоступен. Используйте каталог или <a href="/order/">быстрый заказ по артикулу</a>.</p>';
    });

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { render(input.value); }, 150);
  });

  function render(q) {
    q = (q || "").trim().toLowerCase();
    if (q.replace(/\s+/g, "").length < 2) {
      out.innerHTML = '<p class="note">Введите минимум 2 символа. В каталоге 76 000+ позиций ИЭК.</p>';
      if (q) { out.innerHTML = ""; }
      history.replaceState(null, "", q ? "?q=" + encodeURIComponent(q) : location.pathname);
      return;
    }
    history.replaceState(null, "", "?q=" + encodeURIComponent(q));
    var tokens = norm(q).trim().split(/\s+/).filter(Boolean);
    var hits = [];
    for (var i = 0; i < INDEX.length && hits.length < 60; i++) {
      var it = INDEX[i];
      var hay = norm(it.s + " " + it.n);
      var ok = tokens.every(function (t) { return hay.indexOf(t) !== -1; });
      if (ok) hits.push(it);
    }
    if (!hits.length) {
      out.innerHTML = '<p>Ничего не найдено. Проверьте артикул или отправьте <a href="/order/">быстрый запрос по артикулу</a> — дистрибьютор подберёт позицию.</p>';
      return;
    }
    var rows = hits.map(function (h) {
      return '<article class="card"><div class="sku">' + esc(h.s) + '</div>' +
        '<h3><a href="/' + h.u + '">' + esc(h.n) + '</a></h3>' +
        '<p class="note">' + esc(h.c) + '</p></article>';
    }).join("");
    out.innerHTML = '<p class="note">Найдено: ' + hits.length + (hits.length === 60 ? "+ (уточните запрос)" : "") + '</p>' +
      '<div class="grid">' + rows + '</div>';
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
})();
