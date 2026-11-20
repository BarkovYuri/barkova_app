from rest_framework.throttling import AnonRateThrottle


class AppointmentCreateThrottle(AnonRateThrottle):
    """
    Не более 10 записей в час с одного IP. IP клиента берётся из
    X-Forwarded-For с учётом NUM_PROXIES=1 (за nginx), поэтому подделка
    заголовка лимит не обходит.
    """

    scope = "appointment_create"
