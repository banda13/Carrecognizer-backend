from rest_framework import serializers

from stats.models import ApiUsage


class ApiUsageSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = ApiUsage
        fields = ('username', 'time', 'method', 'method', 'path', 'remote_address', 'response_code')