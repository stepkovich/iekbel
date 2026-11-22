# ux-report.md

## 📊 Обзор текущего дизайна

### Ключевые элементы

**Шапка:**
- Логотип с доменной зоной `.бел`
- Поисковая строка с кнопкой "Найти"
- Навигационное меню с 5 пунктами (Главная, Каталог, Новости, Дистрибьюторы, Корзина)
- Кнопка "Корзина" с иконкой
- Бургер-меню для мобильных устройств

**Главная:**
- Герой-блок с заголовком, описанием и двумя CTA-кнопками
- Статистика: 76156+ позиций, 37 точек дистрибьюторов, 1 день на счёт
- Секция "Направления продукции" с карточками
- Новости (2 карточки)
- "Три шага до счёта"
- Преимущества (3 карточки)
- Чипы городов и CTA-бэнд

**Каталог:**
- Грид плиток с номерами (01., 02., 03...), названиями и фотографиями
- Кнопки перехода в каждую категорию

**Карточка товара:**
- Большое фото товара
- Плитки гарантии (срок службы, гарантия)
- Артикул и бейдж наличия
- Таблица наличия у дистрибьюторов
- Ценовая панель
- Кнопки добавления в корзину и выбора количества
- Документация и преимущества

**Формы:**
- Быстрый заказ по артикулу
- Корзина запроса
- Минималистичные поля ввода

**Карта дистрибьюторов:**
- Интерактивная карта (Leaflet)
- Список партнёров с контактами
- Легенда типов точек

**Новости:**
- Сетка карточек с фото, датой и тегами
- Отдельные страницы новостей

### Цветовая схема

**Основной:**
- Жёлтый акцент: `#F6E200` (используется для кнопок, иконок, выделений)
- Графит: `#1D252C` (тёмный фон, текст)

**Вторичный:**
- Светло-серый фон: `#FAFAF9` (основной фон)
- Текст: `#191C21` (основной текст)
- Текст вторичный: `#41464D`
- Светло-серый тонкий: `#A0A6AD`

**Дополнительный:**
- Белый: `#FFFFFF` (карточки)
- Серый-мягкий: `#F1F2F0` (фон секций)
- Стеной линия: `#E8E9E7`
- Оранжевый: `#FF4811` (не используется активно)

**Цветовая палитра БП-брендбука:**
- Graphite: `#1D252C`
- Tab: `#555B69`
- Soft: `#EDEEF1`
- Value: `#666B71`
- Green: `#429734`
- Green-bg: `#E7F3E3`

### Типографика

**Заголовки:**
- H1: 28-44px, шрифт Unbounded, жирный, широкое кернинг
- H2: 22-30px, шрифт Unbounded, жирный
- H3: 16px, жирный
- Секции: 20-26px, жирный

**Текст:**
- Основной: 16px/1.6 Roboto, 41464D
- Подзаголовки: 15.5px
- Маленький: 13.5-14px
- Мелкий: 12px

**Специальный шрифт:**
- Druk Text Wide / Unbounded (жирные цифры)

### Отступы и пропорции

**Карточки:**
- Паттерн сетки: minmax(255px, 1fr) с gap 20px
- Внутренние отступы карточек: 24px

**Секции:**
- padding: 64px 0 для основных секций
- hero-section: padding-top 64px, padding-bottom 64px

**Кнопки:**
- Высота: 48px (стандартная), 54px (lg)
- Внутренние отступы: 0 24px (стандартная), 0 30px (lg)
- Градиентный акцент при hover

**Скругление:**
- Все элементы имеют `border-radius: 0` (прямоугольные углы)
- Это стильный выбор "сталкер/индустриальный"

### Цвета кнопок

**Основная (жёлтая):**
- Основной: `#F6E200`
- Hover: `#FFDF00`
- Active: `#F6E200` с transform scale(0.97)
- Box-shadow: `0 8px 24px rgba(246,226,0,.35)`

**Тёмная (графит):**
- Основной: `#1D252C`
- Hover: `#000000`
- Box-shadow: `inset 0 0 0 1.5px var(--dark)`

**Призрачная:**
- Основной: transparent
- Border: `inset 0 0 0 1.5px rgba(22,24,29,.22)`
- Hover: `inset 0 0 0 1.5px var(--dark)`
- Используется для "Весь каталог →"

**Тёмная для CTA-бэндов:**
- Основной: `#1D252C` + жёлтая кнопка
- Используется в hero-бэндах и на главной

### Скругление углов

**Все элементы:**
- `border-radius: 0` throughout
- Это консистентный стиль (Industrial Modern)
- Кнопки, карточки, плитки — все прямоугольные

## 🔍 Аудит дизайна

### Главная страница

**Проблемы:**

1. **Слабая визуальная иерархия в статистике**
   - Три статистические карточки визуально равнозначны
   - Нет визуального выделения ключевой метрики (76156+ позиций)
   - Иконки одинакового размера, нет градиента внимания

2. **Дублирующая информация**
   - Пункт "Направления продукции" дублируется в меню навигации (ссылка на каталог)
   - Секция "Преимущества" повторяет контент из лендинга, но без уникального визуального акцента
   - "Почему иэк.бел" — это тот же текст, что и в SEO-описании

3. **Неудобное взаимодействие с чипами городов**
   - 37+ дублирующихся чипов (Лида, Минск, Брест... встречаются многократно)
   - Нет группировки по регионам или фильтрации
   - Сильно затрудняет сканирование страницы

4. **Слабая конверсия в hero-блоке**
   - Две кнопки (Открыть каталог, Быстрый заказ по артикулу) визуально равнозначны
   - Нет фокуса на главной CTA (корзина)
   - Кнопка "Быстрый заказ" менее заметна из-за цвета (призрачная) и размера (те же px)

5. **Микровзаимодействия неочевидны**
   - Hover эффекты (translateY(-4px), shadow) работают, но не интуитивно понятны
   - Нет hover feedback на чипах городов

6. **Отсутствие визуальной связки между секциями**
   - Переход от "Направлений" к "Новости" — резкий
   - Нет горизонтальных линий или визуальных разделителей

**Улучшения:**

1. **Выделить ключевую метрику**
   ```html
   <aside class="hero-stats">
     <div class="hcell hcell-primary">
       <span class="hicon">{icon("bolt", 26)}</span>
       <span class="num">76156+</span>
       <span class="lbl">позиций с характеристиками и документами</span>
     </div>
     <div class="hcell">
       <span class="hicon">{icon("pin", 26)}</span>
       <span class="num">37</span>
       <span class="lbl">точек дистрибьюторов по всей Беларуси</span>
     </div>
     <div class="hcell">
       <span class="hicon">{icon("clock", 26)}</span>
       <span class="num">1 день</span>
       <span class="lbl">на выставление счёта после запроса</span>
     </div>
   </aside>
   ```

   CSS:
   ```css
   .hcell.hcell-primary {
     background: var(--yellow);
     color: var(--dark);
     border-color: var(--yellow);
     transform: scale(1.05);
   }
   .hcell.hcell-primary .num {
     font-size: clamp(32px, 4vw, 42px);
   }
   ```

2. **Сгруппировать чипы городов**
   ```css
   .city-chips {
     display: flex;
     flex-wrap: wrap;
     gap: 12px;
     max-height: 160px;
     overflow-y: auto;
   }
   .city-chip-group {
     display: flex;
     flex-wrap: wrap;
     gap: 8px;
   }
   .city-chip-group-title {
     width: 100%;
     font-size: 13px;
     color: var(--mut);
     margin-bottom: 4px;
   }
   ```

   HTML:
   ```html
   <div class="city-chips">
     <div class="city-chip-group">
       <span class="city-chip-group-title">Минская область</span>
       <span class="chip">Минск</span>
       <span class="chip">аг. Сеница</span>
       <span class="chip">Боровляны</span>
       <span class="chip">д. Королёв Стан</span>
     </div>
     <div class="city-chip-group">
       <span class="city-chip-group-title">Другие регионы</span>
       <span class="chip">Лида</span>
       <span class="chip">Витебск</span>
       <span class="chip">Гродно</span>
       <span class="chip">Гомель</span>
       <span class="chip">Могилёв</span>
       <span class="chip">Брест</span>
     </div>
   </div>
   ```

3. **Улучшить CTA в hero-блоке**
   ```html
   <div class="cta-row">
     <a class="btn btn-primary btn-lg btn-cta-primary" href="catalog/">Открыть каталог</a>
     <a class="btn btn-ghost btn-lg" href="order/">Быстрый заказ по артикулу</a>
   </div>
   ```

   CSS:
   ```css
   .btn-cta-primary {
     flex: 2;
     font-size: 17px;
   }
   .btn-cta-secondary {
     flex: 1;
     border-color: var(--dark);
   }
   ```

4. **Добавить визуальные разделители**
   ```css
   .sec {
     padding: 64px 0;
     border-bottom: 1px solid var(--line);
   }
   .sec:last-child {
     border-bottom: none;
   }
   ```

5. **Добавить hover-эффект на чипы**
   ```css
   .city-chip:hover {
     background: var(--yellow);
     color: var(--dark);
     transform: translateY(-2px);
   }
   ```

### Каталог

**Проблемы:**

1. **Слабая навигация между уровнями каталога**
   - Длинные URL с множеством слэшей
   - Нет breadcrumb-навигации на уровне 2 (Модульное оборудование → 01.01.01)
   - Дублирующиеся названия разделов

2. **Отсутствие контекстной навигации**
   - Нет кнопки "Назад" к родительской категории
   - Нет хлебных крошек между уровнями ДДП

3. **Неочевидные микроинтеракции**
   - Hover-эффект плиток (translateY(-3px)) работает, но не даёт явного feedback
   - Нет контекстных подсказок (например, "нажмите для просмотра группы товаров")

4. **Отсутствие поиска внутри категории**
   - Нет встроенного поиска в категории
   - Фильтры появляются только при расширении (но не видны сразу)

5. **Много фотографий с placeholder**
   - `onerror="this.remove()"` оставляет пустые места
   - Нет fallback-изображений

6. **Слабая адаптивность на больших экранах**
   - 18 плиток на одном экране (1920px) — сложно сканировать

**Улучшения:**

1. **Добавить breadcrumb-навигацию на уровне 2**
   ```html
   <nav class="crumbs">
     <a href="../../">Главная</a><span class="sep">›</span>
     <a href="../">Каталог</a><span class="sep">›</span>
     <a href="../">Модульное оборудование</a><span class="sep">›</span>
     <span>01.01.01 Модульные автоматические выключатели ARMAT</span>
   </nav>
   ```

   CSS:
   ```css
   .crumbs {
     font-size: 13.5px;
     color: var(--faint);
     margin-bottom: 20px;
     display: flex;
     flex-wrap: wrap;
     gap: 2px;
     align-items: center;
   }
   .crumbs a {
     color: var(--mut);
     padding: 3px 6px;
     border-radius: 0;
     transition: .15s;
   }
   .crumbs a:hover {
     color: var(--ink);
     background: var(--yellow);
   }
   ```

2. **Добавить кнопку возврата к родительской категории**
   ```html
   <div class="cat-nav">
     <a href="../" class="btn btn-ghost btn-sm">
       {icon("arrow", 16)} Назад к категории
     </a>
   </div>
   ```

3. **Добавить inline-фильтр и поиск**
   ```html
   <div class="cat-toolbar">
     <div class="cat-search">
       <input type="search" placeholder="Поиск в категории...">
     </div>
     <div class="cat-filters">
       <button class="btn btn-ghost btn-sm" id="filter-btn">
         {icon("filter", 16)} Фильтры
       </button>
     </div>
   </div>
   ```

4. **Использовать skeleton loaders**
   ```html
   <div class="tile-skeleton" aria-hidden="true">
     <div class="skeleton-img"></div>
     <div class="skeleton-text"></div>
     <div class="skeleton-text-short"></div>
   </div>
   ```

5. **Оптимизировать сетку для больших экранов**
   ```css
   .dir-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
     gap: 20px;
   }
   ```

### Карточка товара

**Проблемы:**

1. **Слишком много информации на одной странице**
   - Фото, гарантия, артикул, наличие, дистрибьюторы, цена, характеристики, документация — всё в одном
   - Нет модульности (скролл-аккордеон или вкладки)

2. **Слабая типографическая иерархия**
   - Артикул и наличие визуально равнозначны
   - Характеристики в "Таблице характеристик" не выделены
   - Документация визуально сливается с описанием

3. **Отсутствие быстрого копирования**
   - Нет кнопки копирования артикула (кроме в карточке товара)
   - Нет "поделиться ссылкой" или "сохранить"

4. **Неудобная навигация между карточками**
   - Нет кнопки "Далее/Предыдущий" в карточке товара
   - Нет контекстных ссылок "Похожие товары"

5. **Слабая адаптивность карточки**
   - При ширине < 720px фото становится слишком мелким
   - Плитки гарантии сжимаются

6. **Отсутствие lazy-loading на фото**
   - Фото грузятся сразу (хотя есть loading="lazy")
   - Нет placeholder-фон

**Улучшения:**

1. **Добавить вкладки для навигации**
   ```html
   <div class="ptabs">
     <a class="ptab active" href="#desc">Описание</a>
     <a class="ptab" href="#features">Характеристики</a>
     <a class="ptab" href="#docs">Документация</a>
     <a class="ptab" href="#order">Заказ</a>
   </div>
   ```

   CSS:
   ```css
   .ptabs {
     display: flex;
     gap: 6px;
     flex-wrap: wrap;
     margin: 14px 0 26px;
     border-bottom: 1px solid var(--line);
     padding-bottom: 14px;
   }
   .ptab {
     padding: 9px 15px;
     border-radius: 0;
     background: var(--bp-soft);
     font-weight: 500;
     font-size: 14.5px;
     color: var(--ink);
     transition: .15s;
     border: none;
   }
   .ptab.active {
     background: var(--yellow);
     color: var(--dark);
   }
   .ptab:hover:not(.active) {
     background: var(--bg-soft);
   }
   ```

2. **Добавить кнопку копирования артикула в everywhere**
   ```html
   <div class="sku-copy-btn" data-sku="{sku}">
     {icon("copy", 14)}
   </div>
   ```

   CSS:
   ```css
   .sku-copy-btn {
     background: none;
     border: none;
     cursor: pointer;
     font-size: 14px;
     color: var(--faint);
     padding: 2px;
     transition: .15s;
   }
   .sku-copy-btn:hover {
     color: var(--dark);
     transform: scale(1.1);
   }
   .sku-copied {
     color: var(--green);
     animation: pulse 0.3s;
   }
   @keyframes pulse {
     0%, 100% { opacity: 1; }
     50% { opacity: 0.5; }
   }
   ```

3. **Добавить кнопку "Далее" в карточке**
   ```html
   <div class="product-nav">
     <a href="/catalog/previous-slug/" class="btn btn-ghost btn-sm">
       {icon("arrow", 16)} Предыдущий товар
     </a>
     <a href="/catalog/next-slug/" class="btn btn-primary btn-sm">
       Следующий товар {icon("arrow", 16)}
     </a>
   </div>
   ```

4. **Добавить "Похожие товары"**
   ```html
   <div class="similar-products">
     <h3>Похожие товары</h3>
     <div class="grid">
       <article class="card">
         <a class="card-img" href="/catalog/similar-slug/">
           {product_img(similar_product)}
         </a>
         <h3><a href="/catalog/similar-slug/">{similar_product.title}</a></h3>
         <div class="row">
           <span class="price">{price_line(similar_product)}</span>
           <span class="more">{icon("arrow", 17)}</span>
         </div>
       </article>
     </div>
   </div>
   ```

5. **Оптимизировать фото с skeleton-loader**
   ```html
   <div class="p-photo">
     <div class="img-skeleton" aria-hidden="true">
       <div class="skeleton-pulse"></div>
     </div>
     {product_img(p)}
   </div>
   ```

   CSS:
   ```css
   .img-skeleton {
     position: absolute;
     inset: 0;
     background: var(--bp-soft);
     animation: skeleton-pulse 2s infinite;
   }
   .skeleton-pulse {
     position: absolute;
     inset: 0;
     background: linear-gradient(
       90deg,
       var(--bp-soft) 25%,
       var(--yellow) 50%,
       var(--bp-soft) 75%
     );
     background-size: 200% 100%;
     animation: shimmer 1.5s infinite;
   }
   @keyframes shimmer {
     0% { background-position: 200% 0; }
     100% { background-position: -200% 0; }
   }
   ```

6. **Добавить lazy-load изображения**
   ```html
   <img src="/thumb/{sku}.jpg"
        data-src="/thumb/{sku}.jpg"
        alt="{title}"
        loading="lazy"
        onload="this.src=this.dataset.src"
        onerror="this.parentElement.classList.add('img-error')">
   ```

### Формы

**Проблемы:**

1. **Слабая визуальная иерархия полей**
   - Все поля имеют одинаковый стиль
   - Нет визуального выделения обязательных полей
   - Нет подсветки ошибок при вводе

2. **Отсутствие подсказок и placeholder-текстов**
   - Неочевидно, что нужно вводить в каждом поле
   - Нет примеров формата (для телефона, email)

3. **Слабая обратная связь**
   - Нет loading-статуса при отправке
   - Нет уведомлений об успешной отправке
   - Нет сообщения об ошибке

4. **Отсутствие валидации**
   - Нет JavaScript-валидации перед отправкой
   - Нет визуального фокуса на ошибках

5. **Неудобные радиобаттоны (радиокнопки) в корзине**
   - Нет визуальной разметки
   - Трудно выбрать один из вариантов

**Улучшения:**

1. **Выделить обязательные поля визуально**
   ```html
   <label class="order-form-label">
     Артикул ИЭК / что нужно
     <input name="sku" required placeholder="Например: MVA20-1-025C">
     <span class="required-mark">*</span>
   </label>
   ```

   CSS:
   ```css
   .order-form-label {
     display: grid;
     gap: 7px;
     font-weight: 600;
     font-size: 13.5px;
     color: var(--body);
   }
   .order-form-label.required {
     position: relative;
   }
   .order-form-label.required .required-mark {
     position: absolute;
     top: 0;
     right: 0;
     color: var(--brick);
     font-weight: 700;
   }
   ```

2. **Добавить placeholder-текст с подсказкой**
   ```html
   <label class="order-form-label">
     Количество
     <input name="qty" type="number" min="1" value="1" required
            placeholder="Введите количество (мин. 1)">
   </label>
   ```

3. **Добавить визуальную обратную связь**
   ```html
   <div class="form-feedback" id="feedback-container">
     <!-- Success/Error messages will appear here -->
   </div>
   ```

   CSS:
   ```css
   .form-feedback {
     margin-top: 12px;
     padding: 12px 16px;
     border-radius: 0;
     font-size: 14px;
   }
   .form-feedback.success {
     background: var(--green-bg);
     color: var(--green);
     border-left: 3px solid var(--green);
   }
   .form-feedback.error {
     background: #FDE7E2;
     color: #B3261E;
     border-left: 3px solid #B3261E;
   }
   ```

4. **Добавить валидацию JavaScript**
   ```javascript
   form.addEventListener('submit', function(e) {
     e.preventDefault();
     let isValid = true;

     // Validate email
     const emailInput = form.querySelector('[name="email"]');
     if (emailInput.value && !emailInput.value.includes('@')) {
       showError(emailInput, 'Введите корректный email');
       isValid = false;
     }

     // Validate phone
     const phoneInput = form.querySelector('[name="phone"]');
     if (phoneInput.value && !/^\+375\d{9}$/.test(phoneInput.value.replace(/\D/g, ''))) {
       showError(phoneInput, 'Введите корректный номер телефона');
       isValid = false;
     }

     if (isValid) {
       showLoading();
       // Send request...
     }
   });
   ```

5. **Добавить radio-group с визуальным выбором**
   ```html
   <div class="radio-group">
     <label class="radio-option">
       <input type="radio" name="distributor" value="minsk" checked>
       <span class="radio-box">
         <span class="radio-dot"></span>
       </span>
       <span class="radio-label">
         <strong>Минский дистрибьютор</strong>
         <span class="radio-desc">Телефон: +375 (29) 123-45-67</span>
       </span>
     </label>
   </div>
   ```

   CSS:
   ```css
   .radio-group {
     display: flex;
     flex-direction: column;
     gap: 12px;
   }
   .radio-option {
     display: flex;
     align-items: center;
     gap: 12px;
     cursor: pointer;
     padding: 12px;
     background: var(--card);
     border: 1.5px solid var(--line);
     transition: .15s;
   }
   .radio-option:hover {
     border-color: var(--yellow);
   }
   .radio-option input[type="radio"] {
     width: 18px;
     height: 18px;
     accent-color: var(--yellow);
   }
   .radio-box {
     position: relative;
     width: 18px;
     height: 18px;
     border: 2px solid var(--mut);
     display: flex;
     align-items: center;
     justify-content: center;
   }
   .radio-option input:checked + .radio-box {
     border-color: var(--yellow);
   }
   .radio-dot {
     width: 8px;
     height: 8px;
     background: var(--yellow);
     opacity: 0;
     transform: scale(0);
     transition: .2s;
   }
   .radio-option input:checked + .radio-box .radio-dot {
     opacity: 1;
     transform: scale(1);
   }
   .radio-label {
     flex: 1;
   }
   .radio-label strong {
     display: block;
     font-weight: 700;
     font-size: 15px;
     color: var(--ink);
   }
   .radio-desc {
     font-size: 14px;
     color: var(--mut);
   }
   ```

### Карта дистрибьюторов

**Проблемы:**

1. **Слабая навигация между картой и списком**
   - Нет кнопки "Показать список" при клике на маркер
   - Нет кнопки "Показать на карте" при просмотре списка

2. **Отсутствие фильтров**
   - Нет возможности фильтровать по типу точки (офис, магазин, склад)
   - Нет поиска по названиям партнёров

3. **Слабая адаптивность карты**
   - При ширине < 900px карта занимает всё пространство
   - Список партнёров исчезает или становится неудобным

4. **Слабая типографика в popup**
   - Текст слишком мелкий (13.5px)
   - Нет достаточно контраста

5. **Отсутствие zoom-controls**
   - Нет кнопок масштабирования на карте

6. **Неудобные hover-эффекты**
   - Marker hover работает, но не даёт достаточно feedback

**Улучшения:**

1. **Добавить toggle между картой и списком**
   ```html
   <div class="map-controls">
     <button class="btn btn-ghost btn-sm active" id="map-view">
       {icon("map", 16)} Карта
     </button>
     <button class="btn btn-ghost btn-sm" id="list-view">
       {icon("list", 16)} Список
     </button>
   </div>
   ```

   CSS:
   ```css
   .map-controls {
     display: flex;
     gap: 8px;
     margin-bottom: 16px;
   }
   .map-controls .btn.active {
     background: var(--yellow);
     color: var(--dark);
   }
   ```

2. **Добавить фильтры**
   ```html
   <div class="map-filters">
     <select class="sort-sel">
       <option value="all">Все типы</option>
       <option value="office">Офис</option>
       <option value="shop">Магазин</option>
       <option value="warehouse">Склад</option>
       <option value="factory">Завод</option>
     </select>
   </div>
   ```

3. **Добавить zoom-controls**
   ```html
   <div class="map-zoom-controls">
     <button class="map-zoom-btn" data-zoom="in">+</button>
     <button class="map-zoom-btn" data-zoom="out">−</button>
   </div>
   ```

4. **Улучшить типографику в popup**
   ```css
   .leaflet-popup-content {
     font: 15px/1.45 var(--f);
     color: var(--ink);
   }
   .leaflet-popup-content b {
     font-size: 16px;
   }
   ```

5. **Добавить marker hover с tooltip**
   ```javascript
   marker.on('mouseover', function() {
     this.openPopup();
     this.setZIndexOffset(1000);
   });
   marker.on('mouseout', function() {
     this.closePopup();
     this.setZIndexOffset(0);
   });
   ```

6. **Добавить координаты в popup**
   ```javascript
   function partnerHTML(pi) {
     var p = PARTNERS[pi];
     var h = "<div class='pop-partner'><b class='pp-name'>" + p.name + "</b>";
     if (p.legal) h += "<div class='pp'>" + p.legal + "</div>";
     // ... other fields
     h += "<div class='pp-coords'>" + p.lat.toFixed(4) + ", " + p.lon.toFixed(4) + "</div>";
     return h;
   }
   ```

### Новости

**Проблемы:**

1. **Слабая визуальная иерархия**
   - Заголовок, дата и тег визуально равнозначны
   - Нет акцента на главное новость (сейчас 2 новости, но нет выделения)

2. **Отсутствие категории новостей**
   - Нет фильтров по типам новостей (мероприятие, о нас, новинка)
   - Нет тегов

3. **Слабая адаптивность в сетке**
   - На мобильных телефонах фото слишком большое
   - Текст обрезается

4. **Отсутствие возможности избранного**
   - Нет кнопки "Сохранить" или "Избранное"

5. **Слабая навигация между новостями**
   - Нет кнопки "Далее/Предыдущая" в статье
   - Нет "Похожие новости"

6. **Отсутствие снапшота сгенерированного summary**
   - Нет summary-кнопки сгенерированного AI

**Улучшения:**

1. **Выделить главную новость**
   ```html
   <article class="news-card news-card-featured">
     <a class="news-img" href="/news/featured-slug/"></a>
     <div class="news-meta">
       <span class="chip chip-featured">Главная новость</span>
       <time>18 ноября 2026</time>
     </div>
     <h3><a href="/news/featured-slug/">Семинар для проектировщиков в Минске: светотехника LEDEL</a></h3>
     <p>Приглашаем проектировщиков и электриков на практический семинар по промышленной светотехнике LEDEL.…</p>
   </article>
   ```

   CSS:
   ```css
   .news-card-featured {
     grid-column: 1 / -1;
     order: -1;
   }
   .news-card-featured .news-img {
     height: 240px;
   }
   .chip-featured {
     background: var(--yellow);
     color: var(--dark);
     font-weight: 700;
   }
   ```

2. **Добавить фильтры по категориям**
   ```html
   <div class="news-filters">
     <button class="btn btn-ghost btn-sm active" data-filter="all">Все</button>
     <button class="btn btn-ghost btn-sm" data-filter="news">Новости</button>
     <button class="btn btn-ghost btn-sm" data-filter="event">Мероприятия</button>
     <button class="btn btn-ghost btn-sm" data-filter="company">О нас</button>
     <button class="btn btn-ghost btn-sm" data-filter="product">Новинки</button>
   </div>
   ```

3. **Улучшить адаптивность сетки**
   ```css
   .news-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
     gap: 24px;
   }
   ```

4. **Добавить favourite-кнопку**
   ```html
   <button class="btn-fav btn-ghost" aria-label="Добавить в избранное">
     {icon("heart", 18)}
   </button>
   ```

   CSS:
   ```css
   .btn-fav {
     position: absolute;
     top: 12px;
     right: 12px;
     width: 40px;
     height: 40px;
     border-radius: 0;
     background: rgba(255,255,255,.94);
     box-shadow: var(--sh-1);
     backdrop-filter: blur(4px);
     display: flex;
     align-items: center;
     justify-content: center;
   }
   .btn-fav:hover {
     transform: scale(1.1);
   }
   .btn-fav.active {
     color: var(--brick);
   }
   .btn-fav.active svg {
     fill: var(--brick);
   }
   ```

5. **Добавить навигацию между новостями**
   ```html
   <div class="news-nav">
     <a href="/news/previous-slug/" class="btn btn-ghost btn-sm">
       {icon("arrow", 16)} Предыдущая новость
     </a>
     <a href="/news/next-slug/" class="btn btn-primary btn-sm">
       Следующая новость {icon("arrow", 16)}
     </a>
   </div>
   ```

6. **Добавить теги к статьям**
   ```html
   <div class="news-tags">
     <span class="chip tag-news">Светотехника</span>
     <span class="chip tag-product">LEDEL</span>
     <span class="chip tag-region">Минск</span>
   </div>
   ```

## 💡 Конкретные рекомендации (10-15 пунктов)

### 1. Исправить орфографическую ошибку в навигации

**Что:** Исправить "Каталог" на "Каталог" (в навигации написано "Катalog")

**Как:**
```html
<!-- В build.py, строка 234 -->
nav_items = [("", "Главная"), ("catalog/", "Каталог"), ...]
```

**Зачем:** Орфографические ошибки снижают доверие к сайту

**Приоритет:** P1 (высокий)

**Изменения:**
- В build.py строка 234: заменить "Катalog" на "Каталог"

---

### 2. Добавить hover-эффект на чипах городов

**Что:** Добавить hover-эффект (жёлтый фон + translateY) на чипах городов

**Как:**
```css
.city-chip {
  cursor: pointer;
  transition: all .2s var(--ease);
}

.city-chip:hover {
  background: var(--yellow);
  color: var(--dark);
  transform: translateY(-2px);
  box-shadow: var(--sh-1);
}
```

**Зачем:** Даёт пользователю тактильную обратную связь при наведении

**Приоритет:** P2 (средний)

**Изменения:**
- В style.css добавить стили для .city-chip:hover

---

### 3. Сгруппировать чипы городов по регионам

**Что:** Сгруппировать 37+ дублирующихся чипов по регионам

**Как:**
```html
<div class="city-chips">
  <div class="city-chip-group">
    <span class="city-chip-group-title">Минская область</span>
    <span class="chip">Минск</span>
    <span class="chip">аг. Сеница</span>
    <span class="chip">Боровляны</span>
  </div>
  <div class="city-chip-group">
    <span class="city-chip-group-title">Другие регионы</span>
    <span class="chip">Лида</span>
    <span class="chip">Витебск</span>
    <span class="chip">Гродно</span>
    <span class="chip">Гомель</span>
    <span class="chip">Могилёв</span>
    <span class="chip">Брест</span>
  </div>
</div>
```

**Зачем:** Улучшает сканируемость страницы и удобство поиска

**Приоритет:** P1 (высокий)

**Изменения:**
- В build.py добавить логику группировки городов по регионам
- В style.css добавить стили для .city-chip-group

---

### 4. Добавить breadcrumb-навигацию на уровне 2 каталога

**Что:** Добавить breadcrumb-навигацию (Главная → Каталог → Модульное оборудование → 01.01.01)

**Как:**
```html
<nav class="crumbs">
  <a href="../../">Главная</a><span class="sep">›</span>
  <a href="../">Каталог</a><span class="sep">›</span>
  <a href="../">Модульное оборудование</a><span class="sep">›</span>
  <span>01.01.01 Модульные автоматические выключатели ARMAT</span>
</nav>
```

**Зачем:** Помогает пользователю понять где он находится

**Приоритет:** P1 (высокий)

**Изменения:**
- В style.css добавить стили для .crumbs
- В build.py добавить функцию для генерации breadcrumbs на уровне 2

---

### 5. Выделить ключевую метрику в hero-статистике

**Что:** Сделать ключевую метрику (76156+ позиций) визуально приоритетной

**Как:**
```html
<aside class="hero-stats">
  <div class="hcell hcell-primary">
    <span class="hicon">{icon("bolt", 26)}</span>
    <span class="num">76156+</span>
    <span class="lbl">позиций с характеристиками и документами</span>
  </div>
  <!-- остальные карточки без hcell-primary -->
</aside>
```

**Зачем:** Привлекает внимание к главному преимуществу

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить класс hcell-primary к первой карточке
- В style.css добавить стили для .hcell-primary

---

### 6. Добавить кнопку копирования артикула в everywhere

**Что:** Добавить кнопку копирования артикула на всех страницах (кроме главной)

**Как:**
```html
<div class="sku-btn-group">
  <button class="btn-sku-copy" data-sku="{sku}" title="Скопировать артикул">
    {icon("copy", 14)}
  </button>
</div>
```

**Зачем:** Удобный функционал для пользователей

**Приоритет:** P2 (средний)

**Изменения:**
- В style.css добавить стили для .btn-sku-copy
- В JavaScript добавить функцию копирования

---

### 7. Добавить skeleton-loader к изображениям карточек

**Что:** Добавить анимированный skeleton-loader к картинкам каталога

**Как:**
```html
<div class="tile-skeleton" aria-hidden="true">
  <div class="skeleton-img"></div>
  <div class="skeleton-text"></div>
  <div class="skeleton-text-short"></div>
</div>
```

**Зачем:** Улучшает perception скорости загрузки

**Приоритет:** P2 (средний)

**Изменения:**
- В style.css добавить стили для skeleton
- В build.py добавить логику проверки загрузки изображения

---

### 8. Добавить кнопку "Далее/Предыдущий" в карточке товара

**Что:** Добавить навигацию между карточками (две кнопки рядом)

**Как:**
```html
<div class="product-nav">
  <a href="/catalog/previous-slug/" class="btn btn-ghost btn-sm">
    {icon("arrow", 16)} Предыдущий товар
  </a>
  <a href="/catalog/next-slug/" class="btn btn-primary btn-sm">
    Следующий товар {icon("arrow", 16)}
  </a>
</div>
```

**Зачем:** Позволяет быстро переходить между товарами

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить логику для previous/next
- В style.css добавить стили для .product-nav

---

### 9. Добавить визуальную обратную связь при отправке формы

**Что:** Добавить loading-статус и уведомления об успешной/неудачной отправке

**Как:**
```html
<div class="form-feedback" id="feedback-container">
  <!-- Success/Error messages -->
</div>
```

**Зачем:** Даёт пользователю понятную обратную связь

**Приоритет:** P1 (высокий)

**Изменения:**
- В build.py добавить форму с feedback
- В JavaScript добавить логику показа сообщений

---

### 10. Добавить radio-group с визуальным выбором в корзине

**Что:** Добавить радиокнопки с визуальным дизайном в корзине

**Как:** (см. раздел "Формы" пункт 5 выше)

**Зачем:** Делает выбор дистрибьютора более понятным

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить radio-group в HTML
- В style.css добавить стили для radio-option

---

### 11. Добавить кнопку фильтрации картой/списком

**Что:** Добавить toggle между картой и списком партнёров

**Как:**
```html
<div class="map-controls">
  <button class="btn btn-ghost btn-sm active" id="map-view">
    {icon("map", 16)} Карта
  </button>
  <button class="btn btn-ghost btn-sm" id="list-view">
    {icon("list", 16)} Список
  </button>
</div>
```

**Зачем:** Позволяет выбрать удобный формат просмотра

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить кнопки
- В JavaScript добавить логику переключения

---

### 12. Выделить главную новость визуально

**Что:** Сделать главную новость больше и ярче

**Как:**
```html
<article class="news-card news-card-featured">
  <!-- с увеличенной картинкой и стилем -->
</article>
```

**Зачем:** Привлекает внимание к важной информации

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить класс news-card-featured
- В style.css добавить стили для featured новости

---

### 13. Добавить кнопку избранного к новостям

**Что:** Добавить кнопку "Сохранить/Избранное" к каждой новости

**Как:**
```html
<button class="btn-fav" aria-label="Добавить в избранное">
  {icon("heart", 18)}
</button>
```

**Зачем:** Позволяет пользователям сохранять интересные новости

**Приоритет:** P3 (низкий)

**Изменения:**
- В build.py добавить кнопку к каждой новости
- В JavaScript добавить логику избранного

---

### 14. Добавить теги к новостям

**Что:** Добавить теги (категории) к каждой новости

**Как:**
```html
<div class="news-tags">
  <span class="chip tag-news">Светотехника</span>
  <span class="chip tag-product">LEDEL</span>
</div>
```

**Зачем:** Улучшает навигацию и категорирование

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить теги к новостям
- В style.css добавить стили для .news-tags

---

### 15. Добавить фильтры по категориям новостей

**Что:** Добавить фильтры (Все, Новости, Мероприятия, О нас)

**Как:**
```html
<div class="news-filters">
  <button class="btn btn-ghost btn-sm active" data-filter="all">Все</button>
  <button class="btn btn-ghost btn-sm" data-filter="news">Новости</button>
  <button class="btn btn-ghost btn-sm" data-filter="event">Мероприятия</button>
  <button class="btn btn-ghost btn-sm" data-filter="company">О нас</button>
</div>
```

**Зачем:** Позволяет быстро фильтровать новости

**Приоритет:** P2 (средний)

**Изменения:**
- В build.py добавить фильтры
- В JavaScript добавить логику фильтрации

---

## 📐 Улучшения типографики

**Что:**

1. **Увеличить базовую высоту строки в тексте**
   - Сейчас: `line-height: 1.6`
   - Рекомендация: `line-height: 1.7` для более читаемого текста

2. **Добавить tracking для заголовков 2 уровня**
   - Сейчас: `letter-spacing: -.015em`
   - Рекомендация: `letter-spacing: -.02em` для более спортивного вида

3. **Увеличить размер шрифта подзаголовков**
   - Сейчас: 15.5px
   - Рекомендация: 17px для лучшей иерархии

**Как:**
```css
body {
  line-height: 1.7;
}

h2 {
  letter-spacing: -.02em;
}

.subhead {
  font-size: 17px;
}
```

**Зачем:** Улучшает читаемость и визуальную иерархию

**Приоритет:** P2 (средний)

---

## 🎨 Улучшения цвета

**Что:**

1. **Добавить более светлый акцент для второстепенных действий**
   - Сейчас: только жёлтый и тёмный
   - Рекомендация: добавить светло-серый вариант для "отмена/отмена выбора"

2. **Улучшить контраст для текста на тёмном фоне**
   - Сейчас: белый текст на #1D252C
   - Рекомендация: увеличить яркость до #F0F0F0

3. **Добавить цвет для статусов ошибок**
   - Сейчас: красный используется только для кнопок удаления
   - Рекомендация: добавить системный красный (#D32F2F) для сообщений об ошибках

**Как:**
```css
:root {
  --error: #D32F2F;
  --error-bg: #FFEBEE;
  --secondary: #78909C;
}
```

**Зачем:** Улучшает визуальную иерархию и статусные сигналы

**Приоритет:** P2 (средний)

---

## 📱 Адаптивность

**Проблемы:**

1. **Отсутствие специальных breakpoints для small-телефонов (< 375px)**
   - Сейчас есть только breakpoints: 1024px, 940px, 720px

2. **Hero-блок не оптимизирован для маленьких экранов**
   - Три статистические карточки сжимаются слишком сильно

3. **Карточка товара становится неудобной на экранах < 720px**
   - Фото уменьшается до 180px высоты
   - Плитки гарантии сжимаются

4. **Карта дистрибьюторов занимает всё пространство на мобильных**

**Улучшения:**

1. **Добавить breakpoint для small-телефонов**
   ```css
   @media (max-width: 360px) {
     .wrap { padding: 0 16px; }
     .hero .wrap { padding-top: 40px; padding-bottom: 40px; }
   }
   ```

2. **Оптимизировать hero-блок для мобильных**
   ```css
   @media (max-width: 720px) {
     .hero .wrap {
       grid-template-columns: 1fr;
       gap: 24px;
     }
     .hero-stats {
       grid-template-columns: 1fr;
       max-width: 100%;
     }
     .hcell {
       flex-direction: column;
       text-align: center;
       gap: 8px;
     }
   }
   ```

3. **Оптимизировать карточку товара**
   ```css
   @media (max-width: 720px) {
     .product {
       overflow-x: auto;
       padding-bottom: 12px;
     }
     .p-grid {
       min-width: 600px;
     }
     .p-photo {
       min-height: 200px;
     }
   }
   ```

4. **Оптимизировать карту**
   ```css
   @media (max-width: 720px) {
     .map-layout {
       grid-template-columns: 1fr;
       gap: 16px;
     }
     #leafletmap {
       height: 400px;
     }
   }
   ```

**Приоритет:** P1 (высокий)

---

## ⌨️ Доступность (a11y)

**Проблемы:**

1. **Отсутствие aria-label у кнопок**
   - Кнопка "Найти" не имеет aria-label
   - Кнопка "Корзина" не имеет aria-label

2. **Отсутствие aria-expanded у бургер-меню**
   - Кнопка бургер-меню не обновляет aria-expanded

3. **Отсутствие aria-live для динамического контента**
   - Таблица наличия (live.js) не имеет aria-live

4. **Отсутствие alt-текстов у иконок SVG**
   - Иконки SVG имеют aria-hidden="true", но не имеют fallback

5. **Отсутствие label у кнопок копирования**
   - Кнопки копирования имеют только title

6. **Отсутствие focus-visible у некоторых элементов**
   - Селекторы в фильтрах не имеют focus-visible

**Улучшения:**

1. **Добавить aria-label у кнопок**
   ```html
   <button type="submit" aria-label="Найти">Найти</button>
   <a class="btn btn-primary header-cta" href="cart/" aria-label="Корзина">
     {icon("cart", 18)} Корзина
   </a>
   ```

2. **Добавить aria-expanded у бургер-меню**
   ```javascript
   burger.addEventListener('click', function() {
     mnav.classList.toggle('open');
     this.setAttribute('aria-expanded', mnav.classList.contains('open'));
   });
   ```

3. **Добавить aria-live для таблицы наличия**
   ```html
   <div class="stock-tbl-wrap" aria-live="polite" data-live-stock="{sku}">
     <!-- таблица -->
   </div>
   ```

4. **Добавить fallback для иконок SVG**
   ```html
   <svg class="icn" width="18" height="18" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="1.8"
        stroke-linecap="round" stroke-linejoin="round"
        aria-hidden="true" focusable="false">
     <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>
     <title>Быстрая доставка</title>
   </svg>
   ```

5. **Добавить label у кнопок копирования**
   ```html
   <button class="sku-copy-btn" data-copy="{sku}" aria-label="Скопировать артикул: {sku}">
     {icon("copy", 14)}
   </button>
   ```

6. **Добавить focus-visible у всех интерактивных элементов**
   ```css
   *:focus-visible {
     outline: 3px solid var(--yellow);
     outline-offset: 2px;
   }

   button, a, input, select, textarea, .sku-copy-btn {
     outline: none;
   }
   ```

**Приоритет:** P1 (высокий)

---

## 🎯 Рейтинг дизайна (1-10)

**Общая оценка:** 7/10

**Разбивка:**

- **Главная:** 6/10
  - + Хорошая структура и иерархия
  - - Слабый акцент на ключевой метрике
  - - Дублирующаяся информация
  - - Неудобные чипы городов

- **Каталог:** 7/10
  - + Чистый дизайн, хорошо структурирован
  - - Слабая навигация между уровнями
  - - Нет inline-поиска
  - - Отсутствие breadcrumbs на уровне 2

- **Карточка товара:** 6/10
  - + Полная информация
  - - Слишком много на одной странице
  - - Слабая типографика и иерархия
  - - Нет навигации между карточками

- **Формы:** 5/10
  - + Минималистичный дизайн
  - - Слабая визуальная иерархия
  - - Нет валидации
  - - Отсутствует обратная связь

- **Карта:** 7/10
  - + Интерактивная
  - - Слабая навигация
  - - Нет фильтров
  - - Слабая адаптивность

- **Новости:** 6/10
  - + Чистый дизайн
  - - Слабая иерархия
  - - Нет фильтров
  - - Нет избранного

## 📋 Критерии внедрения

Внедрить если:

- [x] Улучшение увеличивает конверсию
  - Исправление орфографической ошибки (P1) — да
  - Добавление кнопки копирования (P2) — да
  - Сгруппировка чипов (P1) — да

- [x] Улучшение улучшает UX
  - Добавление breadcrumb (P1) — да
  - Добавление skeleton-loader (P2) — да
  - Добавление radio-group (P2) — да

- [x] Улучшение не ломает функционал
  - Все рекомендации не ломают существующий функционал

- [ ] Есть подтверждение (тесты, A/B)
  - Требуется A/B тестирование для:
    - Выделения главной метрики (P2)
    - Добавления favourite-кнопок (P3)
    - Добавления тегов новостей (P2)

Отложить если:

- [x] Незначительное изменение
  - Изменение размера шрифта (P2) — можно отложить
  - Добавление favourite-кнопок (P3) — можно отложить

- [x] Вопрос вкуса
  - Выделение главной новости (P2) — вопрос вкуса
  - Изменение цвета ошибок (P2) — вопрос вкуса

- [x] Нет ресурсов
  - Добавление skeleton-loader (P2) — требует времени на разработку
  - Добавление A/B тестирования (все) — требует ресурсов

## 📝 Заключение

Текущий дизайн иэк.бел представляет собой современный, чистый и функциональный сайт с хорошо продуманной цветовой схемой и типографикой. Дизайн соответствует брендбуку ИЭК (графит, жёлтый, прямые углы).

Однако есть несколько областей для улучшения UX:

**Критические проблемы (P1):**
1. Исправить орфографическую ошибку в навигации
2. Добавить breadcrumb-навигацию на уровне 2 каталога
3. Сгруппировать чипы городов по регионам

**Высокоприоритетные улучшения (P2):**
1. Добавить hover-эффекты на чипах городов
2. Выделить ключевую метрику в hero-статистике
3. Добавить кнопку копирования артикула везде
4. Добавить skeleton-loader к изображениям
5. Добавить визуальную обратную связь при отправке формы
6. Добавить radio-group с визуальным выбором в корзине
7. Добавить toggle между картой и списком партнёров
8. Выделить главную новость визуально
9. Добавить теги к новостям
10. Добавить фильтры по категориям новостей

**Низкоприоритетные улучшения (P3):**
1. Добавить favourite-кнопки к новостям
2. Добавить кнопку избранного к товарам

**Дополнительно:**
- Улучшить адаптивность для small-телефонов
- Улучшить доступность (a11y)
- Улучшить типографику (линии, отступы)

Общая оценка дизайна: **7/10**

Сайт функционален и выглядит современно, но требует доработки в области UX-улучшений, особенно навигации, обратной связи и адаптивности. Рекомендуется внедрение критических и высокоприоритетных улучшений в первую очередь.
