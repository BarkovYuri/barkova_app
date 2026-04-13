from django.contrib import admin, messages

from .models import AvailabilityRule, TimeSlot
from .services import generate_slots_for_rule, generate_slots_for_rules


@admin.action(description="Сгенерировать слоты по выбранным правилам")
def generate_slots_action(modeladmin, request, queryset):
    selected_count = queryset.count()
    active_rules = queryset.filter(is_active=True)
    active_count = active_rules.count()

    created_slots = generate_slots_for_rules(active_rules)

    if selected_count == 0:
        modeladmin.message_user(
            request,
            "Не выбрано ни одного правила.",
            level=messages.WARNING,
        )
        return

    if active_count == 0:
        modeladmin.message_user(
            request,
            "Среди выбранных правил нет активных.",
            level=messages.WARNING,
        )
        return

    modeladmin.message_user(
        request,
        (
            f"Выбрано правил: {selected_count}. "
            f"Активных правил: {active_count}. "
            f"Создано новых слотов: {len(created_slots)}."
        ),
        level=messages.SUCCESS,
    )


@admin.action(description="Сделать выбранные слоты недоступными")
def deactivate_slots(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f"Недоступными отмечено слотов: {updated}",
        level=messages.SUCCESS,
    )


@admin.action(description="Сделать выбранные слоты доступными")
def activate_slots(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f"Доступными отмечено слотов: {updated}",
        level=messages.SUCCESS,
    )


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "weekday_display",
        "start_date",
        "end_date",
        "start_time",
        "end_time",
        "slot_duration",
        "is_active",
    )
    list_filter = ("weekday", "is_active")
    actions = [generate_slots_action]

    def weekday_display(self, obj):
        return obj.get_weekday_display()

    weekday_display.short_description = "День недели"

    @admin.action(description="Сгенерировать слоты по выбранным правилам")
    def generate_slots_action(self, request, queryset):
        selected_count = queryset.count()
        active_rules = queryset.filter(is_active=True)
        active_count = active_rules.count()

        created_slots = generate_slots_for_rules(active_rules)

        if selected_count == 0:
            self.message_user(
                request,
                "Не выбрано ни одного правила.",
                level=messages.WARNING,
            )
            return

        if active_count == 0:
            self.message_user(
                request,
                "Среди выбранных правил нет активных.",
                level=messages.WARNING,
            )
            return

        self.message_user(
            request,
            (
                f"Выбрано правил: {selected_count}. "
                f"Активных правил: {active_count}. "
                f"Создано новых слотов: {len(created_slots)}."
            ),
            level=messages.SUCCESS,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if "_generate_slots" in request.POST and obj.is_active:
            created_slots = generate_slots_for_rule(obj)
            self.message_user(
                request,
                f"По правилу создано новых слотов: {len(created_slots)}",
                level=messages.SUCCESS,
            )

    fieldsets = (
        (
            "Параметры расписания",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "weekday",
                    "start_time",
                    "end_time",
                    "slot_duration",
                    "is_active",
                )
            },
        ),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "start_time",
        "end_time",
        "is_booked",
        "is_active",
        "created_at",
    )
    list_filter = ("date", "is_booked", "is_active")
    search_fields = ("date",)
    actions = [deactivate_slots, activate_slots]