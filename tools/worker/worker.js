/**
 * iek-proxy — Cloudflare Worker для сайта иэк.бел.
 *
 * Маршруты:
 *   GET /img/{SKU}.jpg     → фото товара из lk.iek.ru (Basic-авторизация на сервере),
 *                            кэшируется на edge на 1 год (фото по артикулу не меняется).
 *   GET /api/stock?sku=A,B,C → ЖИВЫЕ остатки: ИЭК (lk.iek.ru) + все партнёрские фиды
 *                            из переменной PARTNER_FEEDS. Кэш 10 минут.
 *   GET /                  → статус.
 *
 * Секреты (wrangler secret put / dashboard → Settings → Variables):
 *   LK_LOGIN, LK_PASSWORD          — API-доступ личного кабинета ИЭК (Basic)
 *   PARTNER_FEEDS                  — JSON: [{"name":"avido","url":"https://..","headers":{"X-Api-Key":".."}}, ...]
 *   ALLOW_ORIGIN                   — CORS-домен сайта, напр. https://xn--h1ae0d.xn--90ais
 *
 * Подключение к сайту: в Cloudflare Dashboard → Workers Routes добавить маршрут
 *   иэк.бел/img/*  и  иэк.бел/api/*  → этот воркер. Тогда фронтенд обращается
 *   к same-origin /img/... и /api/stock — прокси работает прозрачно.
 */

const LK_BASE = "https://lk.iek.ru";
const STOCK_TTL = 600;      // кэш остатков, сек
const IMG_TTL = 31536000;   // кэш фото, сек (1 год)
const MAX_SKUS = 50;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Cache-Control": "no-store",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    try {
      if (url.pathname.startsWith("/img/")) return await handleImage(request, env, ctx, cors);
      // /thumb/ — миниатюры: локально ресайзит devserver; на проде воркер отдаёт
      // оригинал с edge-кэшем (опция апгрейда: Cloudflare Image Resizing)
      if (url.pathname.startsWith("/thumb/")) return await handleImage(request, env, ctx, cors);
      if (url.pathname.startsWith("/docs/")) return await handleDoc(request, env, ctx, cors);
      if (url.pathname === "/api/docs") return await handleDocsMeta(request, env, ctx, cors);
      if (url.pathname === "/api/stock") return await handleStock(request, env, ctx, cors);
      if (url.pathname === "/api/order" && request.method === "POST") return await handleOrder(request, env, ctx, cors);
      if (url.pathname === "/") return json(cors, { service: "iek-proxy", ok: true });
      return json(cors, { error: "not found" }, 404);
    } catch (e) {
      return json(cors, { error: String(e && e.message || e) }, 502);
    }
  },
};

function json(cors, obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...cors } });
}

function lkAuth(env) {
  return "Basic " + btoa(`${env.LK_LOGIN}:${env.LK_PASSWORD}`);
}

/* ---------------- фото ---------------- */

async function handleImage(request, env, ctx, cors) {
  const sku = new URL(request.url).pathname.replace(/^\/img\//, "").replace(/\.jpg$/i, "").toUpperCase();
  if (!/^[A-Z0-9._-]{3,64}$/.test(sku)) return new Response("bad sku", { status: 400 });

  const cache = caches.default;
  let res = await cache.match(request);
  if (res) return res;

  // 1. ищем URI фото по артикулу
  const meta = await fetch(`${LK_BASE}/api/products?art=${encodeURIComponent(sku)}&entity=ImgPng,ImgJpeg&format=json`,
    { headers: { Authorization: lkAuth(env) } });
  if (!meta.ok) return new Response("meta fail", { status: 502 });
  const items = await meta.json();
  const item = Array.isArray(items) ? items[0] : (items.items || [])[0];
  let uri = null;
  for (const ent of ["ImgPng", "ImgJpeg"]) {
    const arr = item && item[ent];
    if (Array.isArray(arr) && arr[0] && arr[0].file_ref && arr[0].file_ref.uri) { uri = arr[0].file_ref.uri; break; }
  }
  if (!uri) return new Response("no image", { status: 404 });

  // 2. качаем файл и отдаём с годовым кэшем
  const img = await fetch(uri, { headers: { Authorization: lkAuth(env) } });
  if (!img.ok) return new Response("img fail", { status: 502 });
  const buf = await img.arrayBuffer();
  res = new Response(buf, {
    headers: {
      "Content-Type": img.headers.get("Content-Type") || "image/jpeg",
      "Cache-Control": `public, max-age=${IMG_TTL}, immutable`,
      ...cors,
    },
  });
  ctx.waitUntil(cache.put(request, res.clone()));
  return res;
}

/* ---------------- документы (сертификаты, паспорта, схемы) ---------------- */

const DOCS_TTL = 21600; // метаданные документов кэшируются 6 часов — «а вдруг изменится»

async function handleDocsMeta(request, env, ctx, cors) {
  const sku = (new URL(request.url).searchParams.get("sku") || "").trim().toUpperCase();
  if (!/^[A-Z0-9._-]{3,64}$/.test(sku)) return json(cors, { error: "sku required" }, 400);

  const url = new URL(request.url);
  const cacheKey = new Request(url.toString(), { method: "GET" });
  const cache = caches.default;
  let res = await cache.match(cacheKey);
  if (res) return res;

  const r = await fetch(`${LK_BASE}/api/products?art=${encodeURIComponent(sku)}&entity=Certificates,Passport,WiringDiagram,InstallationProduct&format=json`,
    { headers: { Authorization: lkAuth(env) } });
  if (!r.ok) return json(cors, { error: "lk fail" }, 502);
  const items = await r.json();
  const item = Array.isArray(items) ? items[0] : (items.items || [])[0];

  const docs = [];
  for (const [ent, label] of [["Certificates", "сертификат"], ["Passport", "паспорт"],
      ["WiringDiagram", "схема подключения"], ["InstallationProduct", "руководство"]]) {
    for (const d of (item && item[ent]) || []) {
      const fr = d.file_ref || {};
      if (!fr.name) continue;
      docs.push({ name: (d.pubName || d.name || label).slice(0, 120), type: label, url: `/docs/${fr.name}` });
    }
  }
  res = json(cors, { sku, docs }, 200);
  res.headers.set("Cache-Control", `public, max-age=${DOCS_TTL}`);
  ctx.waitUntil(cache.put(cacheKey, res.clone()));
  return res;
}

async function handleDoc(request, env, ctx, cors) {
  const file = decodeURIComponent(new URL(request.url).pathname.replace(/^\/docs\//, ""));
  if (!/^[A-Za-z0-9._-]{8,100}$/.test(file)) return new Response("bad file", { status: 400 });

  const cache = caches.default;
  let res = await cache.match(request);
  if (res) return res;

  const r = await fetch(`${LK_BASE}/api/store/${file}`, { headers: { Authorization: lkAuth(env) } });
  if (!r.ok) return new Response("doc fail", { status: 502 });
  const buf = await r.arrayBuffer();
  res = new Response(buf, {
    headers: {
      "Content-Type": r.headers.get("Content-Type") || "application/octet-stream",
      "Content-Disposition": `inline; filename="${file}"`,
      "Cache-Control": `public, max-age=${IMG_TTL}, immutable`,
      ...cors,
    },
  });
  ctx.waitUntil(cache.put(request, res.clone()));
  return res;
}

/* ---------------- заказы (RFQ) ---------------- */

function orderText(order) {
  const items = (order.items || []).map(i => `• ${i.sku} — ${i.title} × ${i.qty}`).join("\n");
  const c = order.client || {};
  const toAll = order.distributor === "__ALL__";
  return [
    `ЗАПРОС СЧЁТА ${order.orderId || ""} (иэк.бел)`,
    `Адресат: ${toAll ? "ВСЕ дистрибьюторы" : order.distributor}`,
    "",
    "ПОЗИЦИИ:", items,
    "",
    "КЛИЕНТ:",
    `Контакт: ${c.name || "—"}`,
    `Тел.: ${c.phone || "—"} · Email: ${c.email || "—"}`,
    `Тип: ${c.type || "—"}`,
    c.org ? `Организация: ${c.org}` : "",
    c.requisites ? `Реквизиты: ${c.requisites}` : "",
    c.city ? `Город: ${c.city}` : "",
    order.comment ? `Комментарий: ${order.comment}` : "",
  ].filter(Boolean).join("\n");
}

async function handleOrder(request, env, ctx, cors) {
  let order;
  try { order = await request.json(); } catch (e) { return json(cors, { error: "bad json" }, 400); }
  if (!Array.isArray(order.items) || !order.items.length) return json(cors, { error: "items required" }, 400);
  if (!order.client || !order.client.name || !order.client.phone || !order.client.email)
    return json(cors, { error: "client contact required" }, 400);

  order.orderId = `IEK-${new Date().toISOString().slice(2, 10).replace(/-/g, "")}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`;
  const routed = [];

  // 1. вебхуки дистрибьюторов: DISTRIBUTOR_INTAKES=[{"name":"ЭЛОС","url":"https://...","headers":{}}]
  let intakes = [];
  try { intakes = env.DISTRIBUTOR_INTAKES ? JSON.parse(env.DISTRIBUTOR_INTAKES) : []; } catch (e) {}
  const toAll = order.distributor === "__ALL__";
  const targets = toAll ? intakes
    : intakes.filter(i => (order.distributor || "").includes(i.name));
  for (const intake of targets) {
    try {
      const r = await fetch(intake.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(intake.headers || {}) },
        body: JSON.stringify(order),
      });
      routed.push({ target: intake.name, ok: r.ok });
    } catch (e) { routed.push({ target: intake.name, ok: false }); }
  }

  // 2. email-фолбэк (Resend): ORDER_FROM="иэк.бел <orders@домен>", ORDER_EMAIL="куда слать"
  if (env.RESEND_API_KEY && env.ORDER_EMAIL && env.ORDER_FROM) {
    try {
      const r = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          from: env.ORDER_FROM, to: [env.ORDER_EMAIL],
          subject: `Запрос счёта ${order.orderId} — ${toAll ? "все дистрибьюторы" : order.distributor || "представительство"}`,
          text: orderText(order),
        }),
      });
      routed.push({ target: "email", ok: r.ok });
    } catch (e) { routed.push({ target: "email", ok: false }); }
  }

  return json(cors, { ok: true, orderId: order.orderId, routed }, 200);
}

/* ---------------- остатки ---------------- */

async function handleStock(request, env, ctx, cors) {
  const url = new URL(request.url);
  const skus = (url.searchParams.get("sku") || "")
    .split(",").map(s => s.trim().toUpperCase()).filter(Boolean).slice(0, MAX_SKUS);
  if (!skus.length) return json(cors, { error: "sku= required" }, 400);

  const cache = caches.default;
  const cacheKey = new Request(url.toString(), { method: "GET" });
  let res = await cache.match(cacheKey);
  if (res) return res;

  const out = { updated: new Date().toISOString(), items: {}, partners: [] };

  // 1. остатки ИЭК (lk.iek.ru поддерживает ?sku=a,b,c)
  try {
    const r = await fetch(`${LK_BASE}/api/residues/json/?sku=${skus.map(encodeURIComponent).join(",")}`,
      { headers: { Authorization: lkAuth(env) } });
    if (r.ok) {
      const data = await r.json();
      const abbr = {};
      for (const [guid, s] of Object.entries(data.stores || {})) abbr[guid] = s.abbr || s.name || guid;
      for (const it of data.shopItems || []) {
        const sku = (it.sku || "").toUpperCase();
        if (!skus.includes(sku)) continue;
        const stores = {};
        for (const [guid, q] of Object.entries(it.residues || {})) {
          if (q) stores[abbr[guid] || guid] = (stores[abbr[guid] || guid] || 0) + q;
        }
        out.items[sku] = {
          iek: { total: Object.values(stores).reduce((a, b) => a + b, 0), stores, assembly: it.assembly || null },
          partners: [],
        };
      }
    }
  } catch (e) { out.iekError = String(e && e.message || e); }

  // 2. партнёрские фиды (каждый дистрибьютор отдаёт {"items": {"SKU": qty}})
  let feeds = [];
  try { feeds = env.PARTNER_FEEDS ? JSON.parse(env.PARTNER_FEEDS) : []; } catch (e) { out.feedsError = "bad PARTNER_FEEDS JSON"; }
  await Promise.all(feeds.map(async (f) => {
    try {
      const r = await fetch(f.url, { headers: f.headers || {} });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const items = data.items || {};
      out.partners.push({ name: f.name, updated: data.updated || null });
      for (const sku of skus) {
        const q = items[sku] ?? items[sku.toLowerCase()];
        if (q == null) continue;
        out.items[sku] = out.items[sku] || { iek: null, partners: [] };
        out.items[sku].partners.push({ name: f.name, qty: q });
      }
    } catch (e) {
      out.partners.push({ name: f.name, error: String(e && e.message || e) });
    }
  }));

  res = json(cors, out, 200);
  res.headers.set("Cache-Control", `public, max-age=${STOCK_TTL}`);
  ctx.waitUntil(cache.put(cacheKey, res.clone()));
  return res;
}
