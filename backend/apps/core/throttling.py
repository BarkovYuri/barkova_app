from rest_framework.throttling import AnonRateThrottle


class AppointmentCreateThrottle(AnonRateThrottle):
    """
    Ограничение на создание записей: не более 10 в час с одного IP.
    Защищает от флуда заявками на /api/appointments/ и /api/appointments/quick/.
    """
    scope = "appointment_create"


class PrelinkThrottle(AnonRateThrottle):
    """
    Ограничение на создание prelink-токенов: не более 30 в час с одного IP.
    Защищает /api/appointments/telegram/prelink/, /api/appointments/vk/prelink/,
    /api/appointments/vk/pending-link/.
    """
    scope = "prelink"
