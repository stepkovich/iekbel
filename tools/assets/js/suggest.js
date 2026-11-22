/* suggest.js — живые подсказки в поиске хедера (все страницы).
 *
 * Ленивая загрузка компактного индекса suggest-index.json.gz при первом
 * вводе (DecompressionStream; фолбэк — несжатый suggest-index.json).
 * Поиск устойчив к смешанной кириллице/латинице: «2Р» = «2P»,
 * «25А» = «25A» — в данных SKU/названий алфавиты смешаны.
 */
(function () {
  "use strict";

  var XLAT = {p: "р", a: "а", c: "с", e: "е", o: "о", x: "х", k: "к", m: "м", t: "т", y: "у", h: "н"};
  function norm(s) {
    return (s || "").toLowerCase().replace(/[a-z]/g, function (ch) { return XLAT[ch] || ch; });
  }

  var IDX = null, LOADING = false, WAIT = [];
  function ensureIndex(cb) {
    if (IDX) { cb(); return; }
    WAIT.push(cb);
    if (LOADING) return;
    LOADING = true;
    var done = function (body) { IDX = body; WAIT.forEach(function (f) { f(); }); WAIT = []; };
    // путь берём от action формы поиска (учитывает глубину страницы)
    var form = document.querySelector("form.searchbox");
    var root = (form && form.getAttribute("action") || "/search/").replace(/search\/$/, "");
    fetch(root + "suggest-index.json.gz")
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        if (!window.DecompressionStream) return r.arrayBuffer().then(function (b) { return new TextDecoder("utf-8").decode(b); });
        return new Response(r.body.pipeThrough(new DecompressionStream("gzip"))).text();
      })
      .then(function (t) { done(JSON.parse(t)); })
      .catch(function () {
        fetch(root + "suggest-index.json")
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (j) { done(j || []); })
          .catch(function () { done([]); });
      });
  }

  function search(q) {
    var tokens = norm(q).trim().split(/\s+/).filter(Boolean);
    if (!tokens.length || !IDX) return [];
    var hits = [];
    for (var i = 0; i < IDX.length && hits.length < 8; i++) {
      var it = IDX[i];
      var hay = norm(it.s + " " + it.n);
      var ok = true;
      for (var j = 0; j < tokens.length; j++) {
        if (hay.indexOf(tokens[j]) === -1) { ok = false; break; }
      }
      if (ok) hits.push(it);
    }
    return hits;
  }

  document.querySelectorAll("form.searchbox").forEach(function (form) {
    var input = form.querySelector("input[name=q]");
    if (!input) return;
    var box = document.createElement("div");
    box.className = "suggest";
    box.hidden = true;
    form.appendChild(box);

    function render() {
      var q = input.value;
      if (q.trim().length < 2) { box.hidden = true; return; }
      ensureIndex(function () {
        var hits = search(q);
        if (!hits.length) { box.hidden = true; return; }
        box.innerHTML = hits.map(function (h) {
          return '<a href="' + h.u + '"><b>' + h.s + '</b><span>' + h.n + '</span></a>';
        }).join("");
        box.hidden = false;
      });
    }

    input.addEventListener("input", render);
    input.addEventListener("focus", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") box.hidden = true;
    });
    // mousedown — раньше blur, чтобы клик по подсказке успел сработать
    box.addEventListener("mousedown", function (e) {
      var a = e.target.closest("a");
      if (a) { e.preventDefault(); location.href = a.getAttribute("href"); }
    });
    document.addEventListener("click", function (e) {
      if (!form.contains(e.target)) box.hidden = true;
    });
  });
})();
