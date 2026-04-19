from celery import shared_task

@shared_task
def process_vk_callback_event(event_data: dict):
    event_type = event_data.get("type")

    if event_type == "message_new":
        from vk_bot import handle_new_message_event
        handle_new_message_event(event_data)
        return

    if event_type == "message_event":
        from vk_bot import handle_callback_event
        handle_callback_event(event_data)
        return