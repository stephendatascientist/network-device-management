from rest_framework import serializers


class LoopbackConfigSerializer(serializers.Serializer):
    loopback_number = serializers.IntegerField()
    ip_address = serializers.IPAddressField()
    subnet_mask = serializers.IPAddressField()


class LoopbackDeleteSerializer(serializers.Serializer):
    device_name = serializers.CharField(max_length=100)
    loopback_id = serializers.IntegerField()
