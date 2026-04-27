from django.contrib.postgres.fields import ArrayField
from django.db import models


WEEKDAY_CHOICES = [
    (0, "Понедельник"),
    (1, "Вторник"),
    (2, "Среда"),
    (3, "Четверг"),
    (4, "Пятница"),
    (5, "Суббота"),
    (6, "Воскресенье"),
]

WEEKDAY_SHORT = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}


class AvailabilityRule(models.Model):
    """
    Правило расписания: «по понедельникам и средам с 09:00 до 18:00,
    слоты по 30 минут, действует с 1 апреля по 30 июня».

    Раньше поле `weekday` хранило один день недели — теперь добавлено
    `weekdays` (ArrayField) с несколькими днями. Старое поле оставлено
    для обратной совместимости (миграции данных) и при пустом `weekdays`
    система использует его.
    """

    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")

    weekday = models.IntegerField(
        "День недели (legacy)",
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text="Устаревшее поле. Используйте «Дни недели».",
    )

    weekdays = ArrayField(
        models.IntegerField(choices=WEEKDAY_CHOICES),
        verbose_name="Дни недели",
        size=7,
        default=list,
        blank=True,
        help_text="Выберите один или несколько дней недели, в которые "
        "действует это правило.",
    )

    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время окончания")

    slot_duration = models.PositiveIntegerField(
        "Длительность слота, мин", default=30
    )

    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Правило расписания"
        verbose_name_plural = "Правила расписания"
        ordering = ["start_date", "start_time"]

    @property
    def effective_weekdays(self) -> list[int]:
        """Возвращает список дней недели, которые действительно используются."""
        if self.weekdays:
            return list(self.weekdays)
        if self.weekday is not None:
            return [self.weekday]
        return []

    def __str__(self):
        days = self.effective_weekdays
        if days:
            days_str = ", ".join(WEEKDAY_SHORT[d] for d in sorted(days))
        else:
            days_str = "—"
        return (
            f"{days_str}: "
            f"{self.start_date} — {self.end_date}, "
            f"{self.start_time:%H:%M}–{self.end_time:%H:%M}"
        )


class DayException(models.Model):
    """
    Точечный нерабочий день (или часть дня).

    Используется когда врач не работает в обычно рабочий день
    (отпуск, больничный, конференция, личное).

    Если is_full_day=True — закрыт весь день. Иначе закрыт диапазон
    от start_time до end_time.
    """

    date = models.DateField("Дата", unique=True)
    is_full_day = models.BooleanField("Весь день", default=True)
    start_time = models.TimeField(
        "Начало (если не весь день)",
        null=True,
        blank=True,
    )
    end_time = models.TimeField(
        "Окончание (если не весь день)",
        null=True,
        blank=True,
    )
    reason = models.CharField(
        "Причина / комментарий",
        max_length=255,
        blank=True,
        help_text="Видно только в админке. На сайте слоты просто исчезают.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Выходной день / исключение"
        verbose_name_plural = "Выходные дни / исключения"
        ordering = ["-date"]

    def __str__(self):
        if self.is_full_day:
            return f"{self.date} — весь день"
        return (
            f"{self.date} — "
            f"{self.start_time:%H:%M}-{self.end_time:%H:%M}"
            if self.start_time and self.end_time
            else f"{self.date}"
        )


class TimeSlot(models.Model):
    date = models.DateField("Дата")
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Окончание")

    is_booked = models.BooleanField("Занят", default=False)
    is_active = models.BooleanField("Доступен", default=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Слот времени"
        verbose_name_plural = "Слоты времени"
        unique_together = ("date", "start_time")
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.date} {self.start_time.strftime('%H:%M')}"
