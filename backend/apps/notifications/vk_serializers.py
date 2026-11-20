from rest_framework import serializers


class VKCallbackEnvelopeSerializer(serializers.Serializer):
    type = serializers.CharField()
    object = serializers.JSONField(required=False)
    group_id = serializers.IntegerField(required=False)
    event_id = serializers.CharField(required=False, allow_blank=True)
    secret = serializers.CharField(required=False, allow_blank=True)
