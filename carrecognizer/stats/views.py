import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.utils.datetime_safe import datetime

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from stats.models import ApiUsage
from stats.serializers import ApiUsageSerializer

logger = logging.getLogger(__name__)


class ApiUsageList(generics.ListCreateAPIView):
    model = ApiUsage
    serializer_class = ApiUsageSerializer
    permission_classes = (IsAuthenticated,)
    paginate_by = 1000 # as an upper limit

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous or not user.is_staff:
            logger.warning('Permission required to get api usage')
            return []
        tz = timezone.get_fixed_timezone(60)
        now = datetime.now().replace(tzinfo=tz)
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))
        day = int(self.request.GET.get('day', now.day))
        hour = int(self.request.GET.get('hour', now.hour))
        minutes = int(self.request.GET.get('min', now.minute))
        seconds = int(self.request.GET.get('sec', now.second))
        start_date = datetime(year=year, month=month, day=day, hour=hour, minute=minutes, second=seconds).replace(tzinfo=tz)

        logger.info('%s requesting api usage after %d-%d-%d %d:%d:%d' % (user.username, year, month, day, hour, minutes, seconds))
        cursor = connection.cursor()
        raw_sql = '''SELECT * FROM stats_apiusage where time >= '%s-%s-%s %s:%s:%s+01' '''
        usage = ApiUsage.objects.raw(raw_sql, params=[year, month, day, hour, minutes, seconds])
        logger.info('%d api usage found' % len(usage))
        return usage

    def get_context_data(self, **kwargs):
        context = super(ApiUsage, self).get_context_data(**kwargs)
        now = datetime.now()
        context['year'] = self.request.GET.get('year', now.year)
        context['month'] = self.request.GET.get('month', now.month)
        context['day'] = self.request.GET.get('day', now.day)
        context['hour'] = self.request.GET.get('hour', now.hour)
        context['minutes'] = self.request.GET.get('min', now.minute)
        context['seconds'] = int(self.request.GET.get('sec', now.second))

        return context