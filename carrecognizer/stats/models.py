import datetime

from django.db import models


class ApiUsage(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100,null=True)
    last_login = models.DateTimeField(null=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=100)
    referer = models.CharField(max_length=100, null=True)
    user_agent = models.CharField(max_length=255, null=True)
    query_string = models.CharField(max_length=255, null=True)
    origin = models.CharField(max_length=100, null=True)
    host = models.CharField(max_length=100, null=True)
    content_type = models.CharField(max_length=100, null=True)
    remote_address = models.CharField(max_length=100, null=True)
    scheme = models.CharField(max_length=20, null=True)
    response_code = models.IntegerField()

    def save(self, *args, **kwargs):
        self.time = datetime.datetime.now().replace(tzinfo=None)
        super(ApiUsage, self).save(*args, **kwargs)