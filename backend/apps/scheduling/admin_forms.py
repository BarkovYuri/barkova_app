"""
Кастомные ModelForm'ы для админки scheduling.
"""
from django import forms

from .models import AvailabilityRule, WEEKDAY_CHOICES


class AvailabilityRuleAdminForm(forms.ModelForm):
    """
    Поле `weekdays` — это PostgreSQL ArrayField. По умолчанию админка
    рендерит его как обычное текстовое поле, в которое надо писать что-то
    вроде «0,1,2». Это неудобно. Заменяем на чекбоксы.
    """

    weekdays = forms.TypedMultipleChoiceField(
        label="Дни недели",
        choices=WEEKDAY_CHOICES,
        coerce=int,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Отметьте все дни недели, в которые вы ведёте приём.",
    )

    class Meta:
        model = AvailabilityRule
        fields = "__all__"
