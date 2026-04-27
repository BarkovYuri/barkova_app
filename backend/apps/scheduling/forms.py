"""
Форма wizard'а для удобной массовой генерации слотов.

Используется в админке: одна форма позволяет сразу выбрать диапазон дат,
несколько дней недели, диапазон времени и длительность слота — а затем
одной кнопкой создать все слоты.
"""

from datetime import date, timedelta

from django import forms

from .models import WEEKDAY_CHOICES


PRESET_RANGE_CHOICES = [
    ("", "Свой диапазон дат"),
    ("month_1", "Следующий месяц"),
    ("month_2", "Следующие 2 месяца"),
    ("month_3", "Следующие 3 месяца"),
]


class SlotGenerationForm(forms.Form):
    """Форма генерации слотов на несколько дней недели сразу."""

    preset_range = forms.ChoiceField(
        label="Период",
        choices=PRESET_RANGE_CHOICES,
        required=False,
        initial="month_1",
        help_text="Выберите готовый период или укажите даты вручную ниже.",
    )

    start_date = forms.DateField(
        label="Дата начала",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "vDateField"}
        ),
        help_text="Игнорируется, если выбран готовый период.",
    )
    end_date = forms.DateField(
        label="Дата окончания",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "vDateField"}
        ),
    )

    weekdays = forms.TypedMultipleChoiceField(
        label="Дни недели",
        choices=WEEKDAY_CHOICES,
        coerce=int,
        widget=forms.CheckboxSelectMultiple,
        help_text="Отметьте все дни недели, в которые ведёте приём.",
    )

    start_time = forms.TimeField(
        label="Время начала приёма",
        widget=forms.TimeInput(attrs={"type": "time"}),
        initial="09:00",
    )
    end_time = forms.TimeField(
        label="Время окончания приёма",
        widget=forms.TimeInput(attrs={"type": "time"}),
        initial="18:00",
    )

    slot_duration = forms.IntegerField(
        label="Длительность слота, минут",
        min_value=10,
        max_value=240,
        initial=30,
        help_text="Каждый слот будет такой длины. Например, 30 минут.",
    )

    create_rule = forms.BooleanField(
        label="Сохранить как правило расписания",
        required=False,
        initial=True,
        help_text="Если отметить — будет создано «Правило расписания», "
        "и в будущем можно будет повторно сгенерировать слоты по нему.",
    )

    def clean(self):
        cleaned = super().clean()
        preset = cleaned.get("preset_range")
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        # Готовые диапазоны
        today = date.today()
        if preset == "month_1":
            start = today
            end = today + timedelta(days=30)
        elif preset == "month_2":
            start = today
            end = today + timedelta(days=60)
        elif preset == "month_3":
            start = today
            end = today + timedelta(days=90)

        if not start or not end:
            raise forms.ValidationError(
                "Укажите даты начала и окончания, либо выберите готовый период."
            )

        if start > end:
            raise forms.ValidationError(
                "Дата окончания не может быть раньше даты начала."
            )

        if cleaned.get("start_time") and cleaned.get("end_time"):
            if cleaned["start_time"] >= cleaned["end_time"]:
                raise forms.ValidationError(
                    "Время окончания должно быть позже времени начала."
                )

        cleaned["start_date"] = start
        cleaned["end_date"] = end
        return cleaned
