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
      '<label>Тип клиента<select name="client_type"><option>Юридическое лицо</option><option>ИП</option><option>Частное лицо</option></select></label>' +
      '<label>Организация / УНП<input name="org" placeholder="ООО «Ромашка», УНП 190000000"></label>' +
      '<label>Полные банковские реквизиты (для выставления счёта)<textarea name="requisites" rows="3" placeholder="Наименование, адрес, банк, IBAN/BIC…"></textarea></label>' +
      '<label>Город / доставка<input name="city"></label>' +
      '<label>Комментарий<textarea name="comment" rows="2"></textarea></label>' +
      '<p class="note">Реквизиты прикрепляются к заказу — дистрибьютор выставит счёт на них. Отправляя запрос, вы соглашаетесь на передачу данных выбранным дистрибьюторам.</p>' +
      '<button class="cta big" type="submit">Отправить запрос дистрибьютору</button>' +
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
    var finish = function (names) {
      var choice = document.getElementById("dist-choice");
      if (!choice) return;
      if (!names || !names.length) { choice.innerHTML = '<p class="note">Список дистрибьюторов недоступен — запрос уйдёт представительству.</p>'; return; }
      choice.innerHTML = names.map(function (n, i) {
        return '<label class="radio"><input type="radio" name="distributor" value="' + esc(n) + '"' + (i === 0 ? " checked" : "") + '> ' + esc(n) + '</label>';
      }).join("") +
      '<label class="radio all"><input type="radio" name="distributor" value="__ALL__"> Отправить всем дистрибьюторам — соберу их предложения</label>';
    };
    if (window.IEK_DISTRIBUTORS) { finish(window.IEK_DISTRIBUTORS); return; }
    fetch("/distributors/index.html").then(function (r) { return r.text(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var names = [];
      doc.querySelectorAll(".dist h3").forEach(function (h) {
        names.push((h.childNodes[0] ? h.childNodes[0].textContent : h.textContent).trim());
      });
      finish(names);
    }).catch(function () { finish(null); });
  }

  function bindSubmit(items) {
    var form = document.getElementById("order-form");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var fd = new FormData(form);
      var payload = {
        created: new Date().toISOString(),
        distributor: fd.get("distributor") || "__ALL__",
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
            var whom = payload.distributor === "__ALL__" ? "всем дистрибьюторам" : ("«" + payload.distributor + "»");
            out.innerHTML = '<div class="order-ok"><h3>✓ Запрос направлен ' + esc(whom) + '</h3>' +
              '<p>Дистрибьютор свяжется с вами и выставит счёт по указанным реквизитам. Остальные партнёры тоже видят запрос и могут предложить свои условия.</p>' +
              '<p class="note">Номер запроса: ' + esc(res.j.orderId || "—") + '</p></div>';
            localStorage.removeItem(KEY);
            updateCount();
            form.reset();
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
