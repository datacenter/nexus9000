from django.db import models
from django.conf import settings
from utils import qaes
import binascii


class AESEncryptedField(models.CharField):
    '''http://www.tylerlesmann.com/2008/dec/19/encrypting-database-data-django/
    This is used to save password in DB as encrpyted.
    The reason of not using django.contrib.auth.models.AbstractBaseUser is because,
    its generates password with one-way hashing and therefore cannot be retreived. 
    '''
    def save_form_data(self, instance, data):
        setattr(instance, self.name,
            binascii.b2a_base64(qaes.encrypt(settings.AESKEY, data)))
    def value_from_object(self, obj):
        return qaes.decrypt(settings.AESKEY,
            binascii.a2b_base64(getattr(obj, self.attname)))
        
class HostNames(models.Model):
    '''
    This is a model for View seen by index.html Network Dashboard Table
    This model is updated by the LoginForm
    NOTE: Do not make primary_key a non-integer item: https://code.djangoproject.com/ticket/14881
    '''
    url = models.URLField(unique=True)
    username = models.CharField(unique=False, max_length=30)
    password = AESEncryptedField(unique=False, max_length=128)
    is_online = models.BooleanField(default=False)
    is_healthy = models.BooleanField(default=False)
    hostname = models.CharField(unique=True, max_length=100)                                    # This is simply hostname extraction from url using urlparse
    polling_interval = models.FloatField(default=settings.POLLING_INTERVAL_DEFAULT)
    polling_timestamp = models.FloatField(null=True)
    polling_method = models.CharField(max_length=30, default=settings.POLLING_METHOD_CLI)       # Can be: 'routercli', 'nxapi'
    os_type = models.CharField(null=True, max_length=30)
    error_online = models.CharField(null=True, max_length=1000)
    health_statuses = models.CharField(null=True, max_length=1000)
    
    def __unicode__(self):
        return self.url
    