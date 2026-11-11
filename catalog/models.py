from django.db import models

# Модели каталога появятся в Уроке 3.

from django.db import models


class Distributor(models.Model):
    """Официальный дистрибьютор ИЭК в РБ."""
    STATUS_CHOICES = [
        ("confirmed", "Дистрибьютор IEK подтверждён"),
        ("declared", "IEK заявлен в ассортименте/партнёрах"),
        ("unconfirmed", "Статус IEK публично не подтверждён"),
        ("none", "Завод-производитель"),
    ]
    name = models.CharField("Название", max_length=120)
    legal_name = models.CharField("Юридическое название / УНП", max_length=160, blank=True)
    site = models.URLField("Сайт", blank=True)
    email = models.EmailField("E-mail", blank=True)
    specialization = models.TextField("Специализация", blank=True)
    iek_status = models.CharField("Статус IEK", max_length=16, choices=STATUS_CHOICES, default="declared")
    iek_evidence = models.URLField("Подтверждение статуса (ссылка)", blank=True)
    notes = models.TextField("Заметки", blank=True)
    updated = models.DateField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "дистрибьютор"
        verbose_name_plural = "Дистрибьюторы"

    def __str__(self):
        return self.name


class Location(models.Model):
    """Точка: офис, склад, магазин, пункт выдачи, производство."""
    TYPE_CHOICES = [
        ("офис", "Офис"), ("склад", "Склад"), ("магазин", "Магазин"),
        ("пункт выдачи", "Пункт выдачи"), ("производство", "Производство"),
        ("завод", "Завод"), ("юр.адрес", "Юридический адрес"),
    ]
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE,
                                    related_name="locations", verbose_name="Дистрибьютор")
    city = models.CharField("Город", max_length=80)
    address = models.CharField("Адрес", max_length=200)
    type = models.CharField("Тип точки", max_length=30, choices=TYPE_CHOICES, default="офис")
    phone = models.CharField("Телефон", max_length=120, blank=True)
    hours = models.CharField("Режим работы", max_length=120, blank=True)
    email = models.EmailField("E-mail точки", blank=True)
    lat = models.FloatField("Широта", null=True, blank=True)
    lon = models.FloatField("Долгота", null=True, blank=True)
    approx = models.BooleanField("Координаты приблизительные", default=False)

    class Meta:
        verbose_name = "точка"
        verbose_name_plural = "Точки (адреса, склады, магазины)"

    def __str__(self):
        return f"{self.city}, {self.address} — {self.distributor.name}"


class DdpNode(models.Model):
    """Узел дерева каталога ДДП: уровень 1 (01), 2 (01.01), 3 (01.01.01)."""
    ddp_id = models.CharField("Код ДДП", max_length=12, unique=True)
    level = models.PositiveSmallIntegerField("Уровень")
    title = models.CharField("Название", max_length=220)
    kind = models.CharField("Направление", max_length=120, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE,
                               related_name="children", verbose_name="Родитель")
    icon = models.CharField("Иконка", max_length=30, blank=True)
    products_count = models.PositiveIntegerField("Товаров (прямых)", default=0)

    class Meta:
        verbose_name = "узел ДДП"
        verbose_name_plural = "Дерево ДДП (каталог)"
        ordering = ["ddp_id"]

    def __str__(self):
        return f"{self.ddp_id} {self.title}"


class Product(models.Model):
    """Товар ГК IEK."""
    sku = models.CharField("Артикул", max_length=64, unique=True, db_index=True)
    name = models.CharField("Название", max_length=250)
    ddp = models.ForeignKey(DdpNode, null=True, blank=True, on_delete=models.SET_NULL,
                            related_name="products", verbose_name="Группа ДДП")
    tm = models.CharField("Торговая марка", max_length=40, blank=True)
    desc = models.TextField("Описание", blank=True)
    advantages = models.TextField("Преимущества", blank=True)
    price = models.FloatField("Базовая цена, ₽", null=True, blank=True)
    rrc = models.FloatField("РРЦ, ₽", null=True, blank=True)
    roc = models.FloatField("РОЦ, ₽", null=True, blank=True)
    stock_total = models.PositiveIntegerField("Остаток ИЭК, шт", default=0)
    stock_stores = models.JSONField("Остатки по складам", default=dict, blank=True)
    features = models.JSONField("Характеристики (ETIM)", default=list, blank=True)
    docs = models.JSONField("Документы", default=list, blank=True)
    analogs = models.JSONField("Аналоги", default=list, blank=True)
    updated_in_iek = models.DateTimeField("Обновлено в ИЭК", null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} — {self.name}"
