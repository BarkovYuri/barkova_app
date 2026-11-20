from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.notifications.messages import doctor as doctor_msg
from apps.notifications.notifiers import alert_doctor
from apps.notifications.transports import vk as vk_transport


class Command(BaseCommand):
    help = "Проверяет канал алертов врачу и отправляет тестовое сообщение в VK (резерв — email)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Только показать, может ли сообщество писать получателям, без отправки сообщения.",
        )

    def handle(self, *args, **options):
        recipients = settings.VK_DOCTOR_USER_IDS
        if not recipients and not settings.DOCTOR_ALERT_EMAILS:
            raise CommandError("Не заданы ни VK_DOCTOR_USER_IDS, ни DOCTOR_ALERT_EMAILS.")

        if recipients and not vk_transport.is_configured():
            self.stdout.write(self.style.WARNING("VK_GROUP_TOKEN или VK_GROUP_ID не заданы: VK-алерты не уйдут."))

        reachable = 0
        for user_id in recipients:
            allowed, error = vk_transport.is_messages_allowed(user_id)
            reachable += int(allowed)
            if allowed:
                self.stdout.write(self.style.SUCCESS(f"VK {user_id}: сообщество может писать"))
            else:
                self.stdout.write(
                    self.style.ERROR(f"VK {user_id}: сообщество НЕ может писать ({error or 'нет разрешения'})")
                )
                self.stdout.write("  Этот аккаунт должен один раз написать сообществу или разрешить сообщения от него.")
        if settings.DOCTOR_ALERT_EMAILS:
            self.stdout.write(f"Резервный email: {', '.join(settings.DOCTOR_ALERT_EMAILS)}")

        if options["check"]:
            if recipients and not reachable and not settings.DOCTOR_ALERT_EMAILS:
                raise CommandError("Ни одному получателю нельзя доставить алерт.")
            return

        if alert_doctor(doctor_msg.test_alert(), notification_type="daily_digest"):
            self.stdout.write(self.style.SUCCESS("Тестовый алерт доставлен."))
        else:
            raise CommandError("Алерт не доставлен ни в один канал. Подробности в «Логи уведомлений».")
