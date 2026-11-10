# iek-proxy — динамический слой иэк.бел (Cloudflare Worker)

Статика (каталог, описания, РРЦ, SEO) живёт в `site/` на Cloudflare Pages.
Воркер добавляет два динамиеских маршрута на том же домене:

| Маршрут | Что делает | Кэш |
|---|---|---|
| `GET /img/{SKU}.jpg` | Фото товара из lk.iek.ru (Basic-авторизация на сервере, ключ не светится) | 1 год (immutable) |
| `GET /api/stock?sku=A,B,C` (≤50 SKU) | Живые остатки: склады ИЭК + все партнёрские фиды одним JSON | 10 минут |
| `POST /api/order` | **RFQ-маршрутизация**: заказ клиента → вебхук выбранного дистрибьютора (`DISTRIBUTOR_INTAKES`) или всем при `distributor="__ALL__"`; email-копия через Resend (`RESEND_API_KEY` + `ORDER_FROM` + `ORDER_EMAIL`) | без кэша |

Секреты для /api/order (добавить к остальным):
- `DISTRIBUTOR_INTAKES` — JSON `[{"name":"ЭЛОС","url":"https://элос.by/api/rfq","headers":{...}}]`
- `RESEND_API_KEY`, `ORDER_FROM`, `ORDER_EMAIL` — email-фолбэк (письмо представительству)
- Пока переменные не заданы, POST вернёт `{ok:true, routed:[]}` — заказ принимается, но не маршрутизируется; фронт покажет предупреждение только при ошибке сети.

Фронтенд (`site/assets/js/live.js`) обращается к same-origin `/api/stock`,
обновляет бейджи «в наличии/под заказ» и блок наличия на карточке товара.
Если воркер не подключён — страницы показывают статический фолбэк из
последней выгрузки (`data/lk-catalog.json`), ничего не ломается.

## Деплой (10 минут)

1. В Cloudflare Dashboard → **Workers & Pages → Create Worker** → вставить `worker.js`
   (или через wrangler: `npm i -g wrangler && wrangler deploy` из этой папки).
2. Прописать секреты (Workers → Settings → Variables):
   - `LK_LOGIN`, `LK_PASSWORD` — API-доступ личного кабинета ИЭК (значение из `.env`)
   - `ALLOW_ORIGIN` = `https://xn--h1ae0d.xn--90ais`
   - `PARTNER_FEEDS` — JSON-массив фидов дистрибьюторов (см. ниже), можно добавить позже
3. Workers Routes → добавить маршруты:
   - `иэк.бел/img/*` → iek-proxy
   - `иэк.бел/api/*` → iek-proxy
4. Проверка: `https://иэк.бел/api/stock?sku=MVA20-1-006-C` → JSON с остатками.

## Формат партнёрского фида (остатки дистрибьютора)

```json
{
  "partner": "АВИДО",
  "updated": "2026-11-05T12:00:00",
  "items": { "MVA20-1-006-C": 120, "MVA20-1-010-C": 55 }
}
```

`PARTNER_FEEDS` (секрет воркера):
```json
[
  {"name": "АВИДО", "url": "https://avido.by/iek-stock.json"},
  {"name": "Электровектор", "url": "https://electrovector.by/api/iek", "headers": {"X-Api-Key": "..."}}
]
```

Воркер опрашивает все фиды параллельно и отдаёт клиенту единый ответ:
```json
{"updated": "...", "items": {"MVA20-1-006-C": {
  "iek": {"total": 11703, "stores": {"Щ": 300, "Кув": 11403}},
  "partners": [{"name": "АВИДО", "qty": 120}]}}}
```

Если партнёр отдаёт данные в своём формате — добавляется лёгкий маппер
в `worker.js` (функция transform на фид), контракт остаётся прежним.

## Статический фолбэк фидов

Те же данные в формате выше можно класть в `data/stock/{партнёр}.json` —
`build.py` вшьёт их в статические страницы (блок «Наличие у
дистрибьюторов-партнёров» в карточке товара). Для партнёров без API.
