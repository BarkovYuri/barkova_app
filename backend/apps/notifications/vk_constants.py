# backend/apps/notifications/vk_constants.py

VK_EVENT_CONFIRMATION = "confirmation"
VK_EVENT_MESSAGE_NEW = "message_new"
VK_EVENT_MESSAGE_EVENT = "message_event"

VK_CMD_CONNECT = "connect"
VK_CMD_CONFIRM = "confirm"
VK_CMD_CANCEL_REQUEST = "cancel_request"
VK_CMD_CANCEL_CONFIRM = "cancel_confirm"
VK_CMD_CANCEL_KEEP = "cancel_keep"
VK_CMD_CANCEL = "cancel"
VK_CMD_YES = "yes"
VK_CMD_NO = "no"
VK_CMD_DOCTOR = "doctor"

VK_STATE_IDLE = "idle"
VK_STATE_HAS_ACTIVE_APPOINTMENT = "has_active_appointment"
VK_STATE_CONFIRM_CANCEL = "confirm_cancel"

VK_MENU_KIND_NONE = "none"
VK_MENU_KIND_BOOKING = "booking"
VK_MENU_KIND_ACTIVE_APPOINTMENT = "active_appointment"
VK_MENU_KIND_CANCEL_CONFIRM = "cancel_confirm"