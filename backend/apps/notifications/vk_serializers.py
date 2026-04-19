# backend/apps/notifications/vk_serializers.py

from rest_framework import serializers
from .vk_constants import (
    VK_EVENT_CONFIRMATION,
    VK_EVENT_MESSAGE_NEW,
    VK_EVENT_MESSAGE_EVENT,
    VK_CMD_CONNECT,
    VK_CMD_CONFIRM,
    VK_CMD_CANCEL_REQUEST,
    VK_CMD_CANCEL_CONFIRM,
    VK_CMD_CANCEL_KEEP,
    VK_CMD_YES,
    VK_CMD_NO,
    VK_CMD_DOCTOR,
)

class VKCallbackEnvelopeSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=[VK_EVENT_CONFIRMATION, VK_EVENT_MESSAGE_NEW, VK_EVENT_MESSAGE_EVENT]
    )
    object = serializers.JSONField(required=False)
    group_id = serializers.IntegerField(required=False)
    event_id = serializers.CharField(required=False, allow_blank=True)
    secret = serializers.CharField(required=False, allow_blank=True)


class VKMessageNewObjectSerializer(serializers.Serializer):
    message = serializers.JSONField()
    client_info = serializers.JSONField(required=False)


class VKMessageEventPayloadSerializer(serializers.Serializer):
    cmd = serializers.ChoiceField(
        choices=[
            VK_CMD_CONNECT,
            VK_CMD_CONFIRM,
            VK_CMD_CANCEL_REQUEST,
            VK_CMD_CANCEL_CONFIRM,
            VK_CMD_CANCEL_KEEP,
            VK_CMD_YES,
            VK_CMD_NO,
            VK_CMD_DOCTOR,
        ]
    )
    appointment_id = serializers.IntegerField(required=False)
    token = serializers.CharField(required=False, allow_blank=True)


class VKMessageEventObjectSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    peer_id = serializers.IntegerField()
    event_id = serializers.CharField()
    payload = serializers.JSONField()
    conversation_message_id = serializers.IntegerField(required=False)