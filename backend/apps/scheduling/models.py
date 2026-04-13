from django.db import models


class AvailabilityRule(models.Model):
    WEEKDAY_CHOICES = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")

    weekday = models.IntegerField("День недели", choices=WEEKDAY_CHOICES)

    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время окончания")

    slot_duration = models.PositiveIntegerField("Длительность слота, мин", default=30)

    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Правило расписания"
        verbose_name_plural = "Правила расписания"
        ordering = ["start_date", "weekday", "start_time"]

    def __str__(self):
        return (
            f"{self.get_weekday_display()}: "
            f"{self.start_date} — {self.end_date}, "
            f"{self.start_time}–{self.end_time}"
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