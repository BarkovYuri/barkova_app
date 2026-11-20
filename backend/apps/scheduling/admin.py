from django.contrib import admin, messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .admin_forms import AvailabilityRuleAdminForm
from .forms import SlotGenerationForm
from .models import (
    WEEKDAY_SHORT,
    AvailabilityRule,
    DayException,
    TimeSlot,
)
from .services import (
    apply_day_exception,
    close_day_slots,
    generate_slots_bulk,
    generate_slots_for_rule,
    generate_slots_for_rules,
)


def _invalidate_dates_cache(dates) -> None:
    """queryset.update() не вызывает сигналы, поэтому кэш свободных слотов
    сбрасываем вручную."""
    cache.delete("scheduling:available_dates")
    for d in set(dates):
        cache.delete(f"scheduling:available_slots:{d}")


def _warn_about_appointments(model_admin, request, dates) -> None:
    from apps.appointments.models import ACTIVE_STATUSES, Appointment

    booked = (
        Appointment.objects.select_related("slot")
        .filter(slot__date__in=list(dates), status__in=ACTIVE_STATUSES)
        .order_by("slot__date", "slot__start_time")
    )
    if booked:
        lines = ", ".join(f"{a.slot.date:%d.%m} {a.slot.start_time:%H:%M} {a.name}" for a in booked[:10])
        model_admin.message_user(
            request,
            f"Внимание: на эти дни уже есть записи пациентов ({lines}). "
            "Их слоты не закрыты. Отмените или перенесите записи вручную, "
            "пациент получит сообщение об отмене.",
            level=messages.WARNING,
        )


# ============================================================================
# Bulk-генерация слотов через кастомный wizard-view
# ============================================================================


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(ModelAdmin):
    """
    Правила расписания. Поддерживают несколько дней недели сразу
    и сохраняются как шаблон, по которому можно потом перегенерировать слоты.
    """

    change_list_template = "admin/scheduling/availabilityrule/change_list.html"
    form = AvailabilityRuleAdminForm

    list_display = (
        "id",
        "weekdays_display",
        "start_date",
        "end_date",
        "time_range_display",
        "slot_duration",
        "is_active",
    )
    list_filter = ("is_active",)
    list_display_links = ("id", "weekdays_display")
    fieldsets = (
        (
            "Период",
            {"fields": ("start_date", "end_date")},
        ),
        (
            "Расписание",
            {
                "fields": (
                    "weekdays",
                    "start_time",
                    "end_time",
                    "slot_duration",
                ),
                "description": (
                    "Отметьте дни недели, в которые работаете. "
                    "Время начала и окончания приёма задают границы дня. "
                    "Длительность слота — длина одной записи."
                ),
            },
        ),
        ("Управление", {"fields": ("is_active",)}),
    )
    actions_on_top = True
    actions_on_bottom = False

    @admin.display(description="Дни недели", ordering="weekdays")
    def weekdays_display(self, obj):
        days = obj.effective_weekdays
        if not days:
            return "—"
        return ", ".join(WEEKDAY_SHORT[d] for d in sorted(days))

    @admin.display(description="Время")
    def time_range_display(self, obj):
        return f"{obj.start_time:%H:%M} – {obj.end_time:%H:%M}"

    # ------------------------------------------------------------------
    # Custom URL: wizard для генерации слотов
    # ------------------------------------------------------------------

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "wizard/",
                self.admin_site.admin_view(self.slot_wizard_view),
                name="scheduling_availabilityrule_wizard",
            ),
        ]
        return custom + urls

    def slot_wizard_view(self, request):
        """
        Wizard «Сгенерировать слоты»:
        — выбор диапазона дат (готовый или произвольный);
        — несколько дней недели чекбоксами;
        — время начала / окончания приёма;
        — длительность слота;
        — опция «Сохранить как правило».
        """

        if request.method == "POST":
            form = SlotGenerationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                # 1) Создаём слоты сразу через bulk
                created = generate_slots_bulk(
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    weekdays=data["weekdays"],
                    start_time=data["start_time"],
                    end_time=data["end_time"],
                    slot_duration_min=data["slot_duration"],
                )

                # 2) Опционально сохраняем как правило
                rule_id = None
                if data.get("create_rule"):
                    rule = AvailabilityRule.objects.create(
                        start_date=data["start_date"],
                        end_date=data["end_date"],
                        weekdays=data["weekdays"],
                        start_time=data["start_time"],
                        end_time=data["end_time"],
                        slot_duration=data["slot_duration"],
                        is_active=True,
                    )
                    rule_id = rule.id

                self.message_user(
                    request,
                    format_html(
                        "Создано слотов: <b>{}</b>. "
                        "Период: {} – {}. {}",
                        len(created),
                        data["start_date"],
                        data["end_date"],
                        f"Сохранено правило #{rule_id}." if rule_id else "",
                    ),
                    level=messages.SUCCESS,
                )

                return HttpResponseRedirect(
                    reverse("admin:scheduling_timeslot_changelist")
                )
        else:
            form = SlotGenerationForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Сгенерировать слоты",
            "form": form,
            "opts": self.model._meta,
            "has_view_permission": True,
        }
        return render(
            request,
            "admin/scheduling/availabilityrule/wizard.html",
            context,
        )

    # ------------------------------------------------------------------
    # Action: перегенерировать слоты по выбранным правилам
    # ------------------------------------------------------------------

    @admin.action(description="Сгенерировать слоты по выбранным правилам")
    def generate_slots_action(self, request, queryset):
        active_rules = queryset.filter(is_active=True)
        created = generate_slots_for_rules(active_rules)
        self.message_user(
            request,
            f"Создано новых слотов: {len(created)} "
            f"(по {active_rules.count()} активным правилам).",
            level=messages.SUCCESS,
        )

    actions = ["generate_slots_action"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Кнопка «сохранить и сразу сгенерировать»: можно нажать чекбокс
        # «is_active» и потом запустить action — это самый явный путь.
        if "_generate_slots" in request.POST and obj.is_active:
            created = generate_slots_for_rule(obj)
            self.message_user(
                request,
                f"По правилу создано новых слотов: {len(created)}",
                level=messages.SUCCESS,
            )


# ============================================================================
# Слоты времени
# ============================================================================


@admin.register(TimeSlot)
class TimeSlotAdmin(ModelAdmin):
    list_display = (
        "id",
        "date",
        "time_range",
        "is_booked",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_booked",
        "is_active",
        ("date", admin.DateFieldListFilter),
    )
    search_fields = ("date",)
    list_per_page = 50
    actions = ["deactivate_slots", "activate_slots"]

    @admin.display(description="Время")
    def time_range(self, obj):
        return f"{obj.start_time:%H:%M} – {obj.end_time:%H:%M}"

    @admin.action(description="Сделать выбранные слоты недоступными")
    def deactivate_slots(self, request, queryset):
        dates = list(queryset.values_list("date", flat=True))
        updated = queryset.update(is_active=False)
        _invalidate_dates_cache(dates)
        self.message_user(
            request,
            f"Недоступными отмечено слотов: {updated}",
            level=messages.SUCCESS,
        )

    @admin.action(description="Сделать выбранные слоты доступными")
    def activate_slots(self, request, queryset):
        dates = list(queryset.values_list("date", flat=True))
        updated = queryset.update(is_active=True)
        _invalidate_dates_cache(dates)
        self.message_user(
            request,
            f"Доступными отмечено слотов: {updated}",
            level=messages.SUCCESS,
        )


# ============================================================================
# Выходные дни / исключения
# ============================================================================


@admin.register(DayException)
class DayExceptionAdmin(ModelAdmin):
    list_display = ("date", "is_full_day", "time_range_display", "reason")
    list_filter = ("is_full_day",)
    search_fields = ("date", "reason")
    fieldsets = (
        (
            None,
            {
                "fields": ("date", "reason"),
                "description": (
                    "Создайте запись на день, в который вы не работаете. "
                    "Слоты этого дня автоматически станут недоступными "
                    "для записи."
                ),
            },
        ),
        (
            "Только часть дня (не обязательно)",
            {
                "fields": ("is_full_day", "start_time", "end_time"),
                "description": (
                    "Если работаете только часть дня — снимите галочку "
                    "«Весь день» и укажите начало/окончание перерыва."
                ),
            },
        ),
    )

    @admin.display(description="Время")
    def time_range_display(self, obj):
        if obj.is_full_day:
            return "—"
        if obj.start_time and obj.end_time:
            return f"{obj.start_time:%H:%M} – {obj.end_time:%H:%M}"
        return "—"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        affected = apply_day_exception(obj)
        _invalidate_dates_cache([obj.date])
        _warn_about_appointments(self, request, [obj.date])
        if affected:
            self.message_user(
                request,
                f"Сделано недоступными слотов в этот день: {affected}",
                level=messages.SUCCESS,
            )

    @admin.action(description="Закрыть выбранные дни (отключить слоты)")
    def close_days(self, request, queryset):
        total = 0
        for exc in queryset:
            total += apply_day_exception(exc)
        dates = [exc.date for exc in queryset]
        _invalidate_dates_cache(dates)
        _warn_about_appointments(self, request, dates)
        self.message_user(
            request,
            f"Сделано недоступными слотов: {total}",
            level=messages.SUCCESS,
        )

    actions = ["close_days"]


# Удобные admin-actions, доступные из закладок (на будущее)


def close_specific_day(date):
    """Helper для будущих интеграций."""
    return close_day_slots(date)
