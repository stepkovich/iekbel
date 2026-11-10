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
