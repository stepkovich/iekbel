/* cart.js — корзина RFQ-агрегатора иэк.бел.
 *
 * Модель: клиент собирает корзину (localStorage, без регистрации),
 * на странице /cart/ выбирает дистрибьютора (или «отправить всем»),
 * прикрепляет реквизиты — заказ уходит через прокси /api/order
 * выбранному дистрибьютору (+ опционально остальным, они могут
 * выставить свой счёт). На статике без воркера — демо-режим.
 */
(function () {
  "use strict";

  var KEY = "iekbel_cart_v1";
  var ORDER_ENDPOINT = "/api/order";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch (e) { return []; }
  }
  function save(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
    updateCount();
  }
  function add(sku, title, qty) {
    var items = load();
    var found = items.find(function (i) { return i.sku === sku; });
    if (found) found.qty += qty || 1;
    else items.push({ sku: sku, title: title, qty: qty || 1 });
    save(items);
  }
  function updateCount() {
    var n = load().reduce(function (a, i) { return a + i.qty; }, 0);
    document.querySelectorAll(".cart-count").forEach(function (el) {
      el.textContent = n || "";
      el.style.display = n ? "inline-block" : "none";
    });
  }

  /* -------- кнопки «В корзину» -------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".add-to-cart");
    if (!btn) return;
    add(btn.getAttribute("data-sku"), btn.getAttribute("data-title") || "", 1);
    var old = btn.textContent;
    btn.textContent = "✓ Добавлено";
    btn.disabled = true;
    setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1200);
  });


  /* -------- степпер количества на карточке товара -------- */
  document.addEventListener("click", function (e) {
    var box = e.target.closest(".qty-stepper");
    if (!box) return;
    var inp = box.querySelector(".qty-val");
    var v = Math.max(1, (+inp.value || 1) + (e.target.classList.contains("qs-plus") ? 1 : -1));
    inp.value = v;
  });

  /* -------- «Добавить в корзину» с количеством -------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".add-to-cart-qty");
    if (!btn) return;
    var box = btn.closest(".qty-box");
    var inp = box ? box.querySelector(".qty-val") : null;
    var qty = Math.max(1, +((inp && inp.value) || 1));
    add(btn.getAttribute("data-sku"), btn.getAttribute("data-title") || "", qty);
    var old = btn.textContent;
    btn.textContent = "✓ Добавлено ×" + qty;
    btn.disabled = true;
    setTimeout(function () { btn.textContent = old; btn.disabled = false; }, 1300);
  });

  /* -------- очистка корзины -------- */
  var clearBtn = document.getElementById("cart-clear");
  if (clearBtn) clearBtn.addEventListener("click", function () {
    if (confirm("Очистить корзину?")) { save([]); renderCart(root); }
  });

  /* -------- мобильное меню -------- */
  document.querySelectorAll(".burger").forEach(function (b) {
    b.addEventListener("click", function () {
      var m = document.getElementById("mnav");
      if (!m) return;
      var open = m.classList.toggle("open");
      b.setAttribute("aria-expanded", open ? "true" : "false");
      b.textContent = open ? "✕" : "☰";
    });
  });

  /* -------- копирование артикула -------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".sku-copy");
    if (!btn) return;
    var v = btn.getAttribute("data-copy") || "";
    if (navigator.clipboard) navigator.clipboard.writeText(v);
    var old = btn.textContent;
    btn.textContent = "✓";
    setTimeout(function () { btn.textContent = old; }, 900);
  });

  /* -------- страница корзины -------- */
  var root = document.getElementById("cart-root");
  if (root) renderCart(root);

  function renderCart(root) {
    var items = load();
    if (!items.length) {
      root.innerHTML = '<p class="empty">Корзина пуста. Откройте <a href="/catalog/">каталог</a> и добавьте позиции.</p>';
      return;
    }
    var rows = items.map(function (i, idx) {
      return '<tr><td class="sku">' + esc(i.sku) + '</td><td>' + esc(i.title) + '</td>' +
        '<td><input type="number" min="1" value="' + i.qty + '" data-idx="' + idx + '" class="qty"></td>' +
        '<td><button class="rm" data-idx="' + idx + '" title="Удалить">✕</button></td></tr>';
    }).join("");

    root.innerHTML =
      '<h2>1. Позиции заказа</h2>' +
      '<table class="cart-table"><thead><tr><th>Артикул</th><th>Наименование</th><th>Кол-во</th><th></th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>' +
      '<form id="order-form" class="order-form">' +
      '<h2>2. Кому отправить запрос</h2>' +
      '<div class="dist-choice" id="dist-choice"><p class="note">Загружаю список дистрибьюторов…</p></div>' +
      '<h2>3. Реквизиты и контакты</h2>' +
      '<label>Контактное лицо (ФИО)<input name="name" required></label>' +
      '<label>Телефон<input name="phone" type="tel" required></label>' +
      '<label>Email<input name="email" type="email" required></label>' +
      '<label>Организация / УНП<input name="org" placeholder="ООО «Ромашка», УНП 190000000"></label>' +
      '<label>Полные банковские реквизиты (для выставления счёта)<textarea name="requisites" rows="3" placeholder="Наименование, адрес, банк, IBAN/BIC…"></textarea></label>' +
      '<label>Город / доставка<input name="city"></label>' +
      '<label>Комментарий<textarea name="comment" rows="2"></textarea></label>' +
      '<p class="note">Реквизиты прикрепляются к заказу — дистрибьютор выставит счёт на них. Отправляя запрос, вы соглашаетесь на передачу данных выбранным дистрибьюторам.</p>' +
      '<button class="btn btn-primary btn-lg" type="submit">Отправить запрос дистрибьютору</button>' +
      '<div id="order-result"></div>' +
      '</form>';

    bindTable();
    renderDistChoice();
    bindSubmit(items);
  }

  function bindTable() {
    root.querySelectorAll(".qty").forEach(function (inp) {
      inp.addEventListener("change", function () {
        var items = load();
        var idx = +inp.getAttribute("data-idx");
        items[idx].qty = Math.max(1, +inp.value || 1);
        save(items);
      });
    });
    root.querySelectorAll(".rm").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var items = load();
        items.splice(+btn.getAttribute("data-idx"), 1);
        save(items);
        renderCart(root);
      });
    });
  }

  function renderDistChoice() {
    var finish = function (list) {
      var choice = document.getElementById("dist-choice");
      if (!choice) return;
      if (!list || !list.length) { choice.innerHTML = '<p class="note">Список дистрибьюторов недоступен — запрос уйдёт представительству.</p>'; return; }
      // list: [{name, retail}]; retail — работает с частными лицами
      var TYPES = ["Юридическое лицо", "ИП", "Частное лицо"];
      var state = { type: "Юридическое лицо" };

      choice.innerHTML =
        '<div class="seg-head">Тип клиента:</div>' +
        '<div class="chips-row seg-row">' +
        TYPES.map(function (t) {
          var lbl = t === "Юридическое лицо" ? "Юрлицо" : t === "Частное лицо" ? "Частное лицо" : "ИП";
          return '<label class="pchip-toggle seg"><input type="radio" name="client_type" value="' + t + '"' +
            (state.type === t ? " checked" : "") + '><span class="pchip">' + lbl + '</span></label>';
        }).join("") +
        '</div>' +
        '<div class="dist-partners" id="dist-partners"></div>' +
        '<p class="note dist-hint">Юрлицам и ИП доступны все партнёры сети; частным лицам — розничные. Можно выбрать нескольких партнёров — каждый получит ваш список позиций и выставит счёт по своим условиям.</p>';

      var wrap = choice.querySelector("#dist-partners");

      function renderPartners() {
        var visible = list.filter(function (p) { return state.type !== "Частное лицо" || p.retail; });
        if (!visible.length) { wrap.innerHTML = '<p class="note">Нет партнёров для выбранного типа клиента.</p>'; return; }
        wrap.innerHTML =
          '<div class="chips-row">' +
          '<label class="pchip-toggle all"><input type="checkbox" id="dist-all" checked>' +
          '<span class="pchip">Отправить всем — ' + visible.length + ' партнёрам</span></label>' +
          visible.map(function (p) {
            return '<label class="pchip-toggle"><input type="checkbox" class="dist-one" value="' + esc(p.name) + '" checked>' +
              '<span class="pchip">' + esc(p.name) + '</span></label>';
          }).join("") +
          '</div>';

        var all = wrap.querySelector("#dist-all");
        all.addEventListener("change", function () {
          wrap.querySelectorAll(".dist-one").forEach(function (c) { c.checked = all.checked; });
          sync();
        });
        wrap.querySelectorAll(".dist-one").forEach(function (c) {
          c.addEventListener("change", sync);
        });
        sync();
      }

      function sync() {
        var total = wrap.querySelectorAll(".dist-one").length;
        var n = wrap.querySelectorAll(".dist-one:checked").length;
        var all = wrap.querySelector("#dist-all");
        if (all) all.checked = total > 0 && n === total;
        var btn = document.querySelector("#order-form button[type=submit]");
        if (btn) { btn.textContent = n ? "Отправить запрос " + n + " партнёрам" : "Выберите партнёров"; btn.disabled = !n; }
        choice._ones = function () { return [...wrap.querySelectorAll(".dist-one:checked")].map(function (c) { return c.value; }); };
      }

      choice.querySelectorAll("input[name=client_type]").forEach(function (r) {
        r.addEventListener("change", function () { state.type = r.value; renderPartners(); });
      });

      renderPartners();
      choice._sync = sync;
    };
    if (window.IEK_DISTRIBUTORS) { finish(window.IEK_DISTRIBUTORS); return; }
    fetch("/distributors/index.html").then(function (r) { return r.text(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var list = [];
      doc.querySelectorAll(".dist h3").forEach(function (h) {
        var n = (h.childNodes[0] ? h.childNodes[0].textContent : h.textContent).trim();
        if (n && !/МЭТЗ/.test(n)) list.push({ name: n, retail: true });
      });
      finish(list);
    }).catch(function () { finish(null); });
  }

  function bindSubmit(items) {
    var form = document.getElementById("order-form");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var fd = new FormData(form);
      var choice = document.getElementById("dist-choice");
      var allBox = document.getElementById("dist-all");
      var selected = (choice && choice._ones ? choice._ones() : []);
      var toAll = !selected.length || (allBox && allBox.checked);
      var whomNames = toAll ? null : selected;
      var payload = {
        created: new Date().toISOString(),
        distributor: toAll ? "__ALL__" : selected.join(", "),
        distributors: toAll ? ["__ALL__"] : selected,
        client: {
          name: fd.get("name"), phone: fd.get("phone"), email: fd.get("email"),
          type: fd.get("client_type"), org: fd.get("org") || null,
          requisites: fd.get("requisites") || null, city: fd.get("city") || null,
        },
        comment: fd.get("comment") || null,
        items: load(),
      };
      var out = document.getElementById("order-result");
      out.innerHTML = '<p class="note">Отправляю…</p>';
      fetch(ORDER_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok) {
            var whom = toAll ? "всем дистрибьюторам"
              : (whomNames.length === 1 ? "«" + whomNames[0] + "»" : whomNames.length + " партнёрам: " + whomNames.join(", "));
            out.innerHTML = '<div class="order-ok"><h3>✓ Запрос направлен ' + esc(whom) + '</h3>' +
              '<p>Каждый выбранный партнёр получит ваш список позиций, свяжется с вами и выставит счёт по указанным реквизитам.</p>' +
              '<p class="note">Номер запроса: ' + esc(res.j.orderId || "—") + '</p></div>';
            localStorage.removeItem(KEY);
            updateCount();
            form.reset();
            if (choice._sync) choice._sync();
          } else {
            out.innerHTML = '<p class="note">Не удалось отправить: ' + esc((res.j && res.j.error) || "ошибка") + '. Позвоните или напишите нам — контакты на странице «Дистрибьюторы».</p>';
          }
        })
        .catch(function () {
          out.innerHTML = '<p class="note">Сервис приёма заказов временно недоступен. Отправьте позиции на email — контакты на странице «Дистрибьюторы».</p>';
        });
    });
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  updateCount();
})();
