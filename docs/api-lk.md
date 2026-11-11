# API личного кабинета ИЭК (lk.iek.ru) — справочник

Источник: официальные доки ЛК (Анкрон) + проверено практикой. Авторизация: Basic.
Креды: `.env` (LK_API_LOGIN / LK_API_PASSWORD). Лимит: 500 позиций/страница.

## Сервисы

| Сервис | URL | Что даёт | Статус у нас |
|---|---|---|---|
| products | /api/products | все товары ГК IEK: цены, описания, фото, сертификаты, ETIM и др. | ✅ импортёр |
| ddp | /api/ddp | дерево каталога ДДП (section/kind/group/groupId) | ✅ импортёр |
| residues | /api/residues/json/ | остатки по складам (GUID → кол-во), поле zakaz, assembly + daysToComplete | ✅ импортёр |
| planresidues | /api/planresidues/json/ | план приходов: sku → склад → [{dateBegan, dateEnd, amount}] | ✅ доки, не интегрировано |
| etim | /api/etim | ETIM-характеристики всех товаров (Attribute/value/unit/class_name) | ✅ выгрузка фоном |
| services | /api/services | сервисные центры (город, адрес, тип) | 📋 доки |
| videos | /api/videos | видео | 📋 доки |
| seriesspecifications | /api/seriesspecifications | спецификации серий (xlsx) | 📋 доки |

## products — параметры
- Пагинация: `page`, `pageSize` (≤500). Без groupId → dict {totalElements, items}; с groupId → массив
- Фильтры: `groupId` (любая вложенность: 01, 01.01, 01.01.01), `TM` (IEK/ITK/ONI/IEK серия Home/GENERICA), `art`, `updatedAtFrom`/`updatedAtTo` (инкрементальные обновления!)
- `format` = json / jsonp / xml

## products — сущности (entity=…)
### База (всегда)
art, TM, groupId, name, price (₽), saleprice, vat, vat_included, createdAt, updatedAt

### Коммерция
- `roc` — рекомендованная оптовая, `rrc` — рекомендованная розничная, `rrc_control` — управляемость РРЦ
- `PriceIndividualPre` / `PriceIndividualPost` — цены партнёра: предоплата / отсрочка
- `min_ship` — минимальная отгрузка, `order_multiplicity` — кратность заказа, `spr` — коэф. транспортной упаковки
- `DeliveryTimeInDays` — типовой срок поставки, `custom_item` — признак заказной

### Контент
- `Description` (ru/en/es), `Advantages`, `DesignFeature` (преимущества-картинки)
- `ImgPng`/`ImgJpeg`, `Models3d`, `Video`, `Lists` (листовки), `Brochure`
- `InstallationProduct` (руководства), `Passport` (паспорт), `WiringDiagram` (схемы), `DimensionDrawing` (габариты)
- `Certificates` (ТР ТС/ТР ПБ: certNumber, validFrom/To), `CertificatesFsa` (NEW: ссылка на реестр pub.fsa.gov.ru)

### Классификация
- `ArtEtim` — ETIM-фичи прямо в products (может быть пустым) / отдельный `etim`-сервис (полный, пагинация)
  - Feature: {Attribute, value, unit, class_code, class_name, FEATUREID, VALUEID}
- `Feacn` — ТН ВЭД, `Okpd2` — ОКПД 2, `RegistryEntry` — номер реестровой записи
- `ChestnyZnakGtin` / `ChestnyZnakProductGroup` / `ChestnyZnakLabel` — «Честный знак»
- `CountryOfOrigin` — страна происхождения, `Divisibility` — делится ли товар
- `SubjectToDeclaration` / `SubjectToCertification` — подлежит декларированию/сертификации

### Прочее
- `Analog` — внутренние аналоги ({analog, ord, view: «одно/двухсторонний», desc})
- `LeftPeriod` — гарантия/срок службы (структура: warrantyYears, serviceLife, serviceLifeUnit)
- `LogisticParameters` — individual/group/transport/pallet: quantity, barcode, grossWeight, volume, l/b/h
- `Constructor`, `Complects`, `Configurators`, `EquipmentForSAPR`, `Software`, `Comments` (отзывы), `ServicesCenter`, `CompetitiveAdvantages`, `SafeWorkload`, `IndPacking`, `ImgPlanoGramm`
- `ArtUrl` — ссылка на артикул на ресурсах IEK (qr.iek.group)
- `custom_item` — признак заказной продукции

### Файлы
file_ref: {md5, name, size, uri}. uri → `lk.iek.ru/api/store/{name}` — требует Basic-авторизацию
(на сайте отдаём через прокси: воркер `/img/{SKU}`, `/docs/{file}`; dev-сервер — то же)

## Остатки (residues)
- 4 склада в выгрузке нашего ЛК (Щ Щербинка, БЛБ Балабаново, Кув Кувекино, Я Ясногорский) — состав зависит от ЛК
- shopItems: {sku, zakaz (под заказ), residues {GUID: qty}, assembly {GUID: qty}, daysToComplete {GUID: days}}
- assembly — товар, требующий сборки комплекта (дни в daysToComplete)
- фильтр: ?sku=A,B,C

## План приходов (planresidues)
- {sku, plan {GUID: [{dateBegan, dateEnd, amount}]}} — когда и сколько придёт на склад
- фильтр: ?sku=

## ETIM (детали)
- Полный пул пагинацией (500/стр); поля: Code (артикул), TM, groupId, name, Features[]
- Feature: Attribute («Номинальный ток»), value («63.0»), unit («А»), class_code/class_name (ETIM-класс)
- Атрибуты бывают с суффиксами _Name/_Code: _Code содержит ETIM-код значения (EV…), _Name — человекочитаемое

## Инкрементальные обновления (правильный механизм)
`products?updatedAtFrom=2026-01-01&entity=…` — только изменённые с даты. Это вместо полной перекачки:
ежедневный job тянет delta и обновляет локальные данные.

## Известные особенности / грабли
- С groupId фильтром API возвращает массив без totalElements → пагинация по «len(items)<500»
- На части групп пагинация может игнорироваться → защита: лимит страниц, детект повторной первой страницы
- file_ref.uri требует авторизацию → для сайта только через прокси (воркер/dev-сервер)
- apiVersion в выгрузках (semver) — сверять при обновлениях механизма
- E-mail интеграции: platform@iek.ru (BP API), platforma@iek.ru
