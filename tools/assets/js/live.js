/* live.js — живые остатки для иэк.бел.
 *
 * Работает через same-origin прокси (Cloudflare Worker, маршрут /api/*).
 * На статике без воркера тихо отключается — на страницах остаётся
 * статический фолбэк из последней выгрузки.
 *
 * Разметка, которую обновляет:
 *   .live-badge[data-sku]            — бейдж на карточке (в наличии / под заказ / партнёр N шт)
 *   [data-live-stock="SKU"]          — блок на странице товара (детали по складам и партнёрам)
 */
(function () {
  "use strict";

  var nodes = document.querySelectorAll(".live-badge[data-sku], [data-live-stock]");
  var docsNodes = document.querySelectorAll("[data-docs-sku]");
  if (!nodes.length && !docsNodes.length) return;

  if (docsNodes.length) loadDocs(docsNodes);
  if (!nodes.length) return;

  var skus = [];
  var seen = {};
  nodes.forEach(function (n) {
    var sku = n.getAttribute("data-sku") || n.getAttribute("data-live-stock");
    if (sku && !seen[sku]) { seen[sku] = 1; skus.push(sku); }
  });
  if (!skus.length) return;

  var url = "/api/stock?sku=" + encodeURIComponent(skus.slice(0, 50).join(","));
  fetch(url, { headers: { Accept: "application/json" } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) { render(data.items || {}); })
    .catch(function () { /* прокси не подключён — оставляем статический фолбэк */ });

  function totalFor(item) {
    if (!item) return 0;
    var t = (item.iek && item.iek.total) || 0;
    (item.partners || []).forEach(function (p) { t += p.qty || 0; });
    return t;
  }

  function render(items) {
    nodes.forEach(function (n) {
      var sku = (n.getAttribute("data-sku") || n.getAttribute("data-live-stock") || "").toUpperCase();
      var item = items[sku];
      if (!item) return;

      if (n.classList.contains("live-badge")) {
        var t = totalFor(item);
        var partners = (item.partners || []).filter(function (p) { return p.qty > 0; });
        if (t > 0) {
          n.textContent = partners.length && !(item.iek && item.iek.total)
            ? "у партнёра: " + partners[0].qty + " шт"
            : "В наличии · " + t.toLocaleString("ru-RU") + " шт";
          n.classList.add("ok");
        } else {
          n.textContent = "под заказ";
          n.classList.remove("ok");
        }
        return;
      }

      // детальный блок: таблица наличия (карточка) или текст (order-box)
      if (n.classList.contains("stock-tbl-wrap")) {
        n.innerHTML = stockTableHTML(item, data.updated);
        return;
      }
      var html = "";
      if (item.iek && item.iek.total) {
        var stores = Object.keys(item.iek.stores || {}).map(function (k) { return k + " " + item.iek.stores[k]; }).join(", ");
        html += "<p class=\"stock\">Наличие на складах ИЭК: <strong>" + item.iek.total + " шт</strong>" +
                (stores ? " <span class=\"note\">(" + stores + ")</span>" : "") + "</p>";
      }
      (item.partners || []).forEach(function (p) {
        if (p.qty > 0) html += "<p class=\"stock\">Наличие у партнёра «" + p.name + "»: <strong>" + p.qty + " шт</strong></p>";
      });
      if (!html) html = "<p class=\"stock\">Под заказ — срок уточнит дистрибьютор.</p>";
      html += "<p class=\"note\">Обновлено онлайн: " + new Date(data.updated || Date.now()).toLocaleString("ru-RU") + "</p>";
      n.innerHTML = html;
    });
  }
  function esc2(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var STORE_RU = {"Щ": "Щёлково", "Кув": "Кувекино", "Я": "Ярославль",
                  "БЛБ": "БЛБ", "др.": "Другие склады"};
  function fmtQty(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " шт";
  }
  function stockTableHTML(item, updated) {
    var rows = "";
    var partners = {};
    (item.partners || []).forEach(function (p) {
      if (p.qty > 0) partners[p.name] = (partners[p.name] || 0) + p.qty;
    });
    if (Object.keys(partners).length) {
      rows += '<tr class="grp"><td colspan="2">У дистрибьюторов</td></tr>';
      Object.keys(partners).forEach(function (name) {
        rows += "<tr><td>" + esc2(name) + "</td><td>" + fmtQty(partners[name]) + "</td></tr>";
      });
    }
    var st = (item.iek && item.iek.stores) || {};
    if (Object.keys(st).length) {
      rows += '<tr class="grp"><td colspan="2">Склады ИЭК (РФ)</td></tr>';
      Object.keys(st).forEach(function (k) {
        if (st[k] > 0) rows += "<tr><td>" + esc2(STORE_RU[k] || k) + "</td><td>" + fmtQty(st[k]) + "</td></tr>";
      });
      if (item.iek.total) rows += '<tr class="sum"><td>Итого на складах ИЭК</td><td>' + fmtQty(item.iek.total) + "</td></tr>";
    }
    if (!rows) return '<p class="stock">Под заказ — срок уточнит дистрибьютор.</p>';
    return '<h4>Наличие</h4><table class="stock-tbl">' + rows + "</table>" +
           (updated ? '<p class="note">Обновлено онлайн: ' + new Date(updated).toLocaleString("ru-RU") + "</p>" : "");
  }

  /* -------- документы и сертификаты: живьём из API ИЭК -------- */
  function loadDocs(nodes) {
    nodes.forEach(function (sec) {
      var sku = sec.getAttribute("data-docs-sku");
      fetch("/api/docs?sku=" + encodeURIComponent(sku))
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (j) {
          var docs = j.docs || [];
          var body = sec.querySelector(".docs-body");
          if (!body) return;
          if (!docs.length) { sec.style.display = "none"; return; }
          body.innerHTML = "<ul class='docs'>" + docs.map(function (d) {
            return "<li><a href='" + d.url + "' target='_blank' rel='noopener'>" + esc2(d.name) + "</a>" +
                   " <span class='note'>" + esc2(d.type) + "</span></li>";
          }).join("") + "</ul>" +
          "<p class='note'>Актуальный список — напрямую из базы ИЭК на момент открытия страницы.</p>";
        })
        .catch(function () { sec.style.display = "none"; });
    });
  }
})();
