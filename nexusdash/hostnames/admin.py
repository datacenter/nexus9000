from django.contrib import admin
from .models import HostNames
# TODO: Display time in different format
# import datetime
# class HostNamesModelAdmin(admin.ModelAdmin):
#     # https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
# 
#     def display_polling_timestamp(self, obj):
#         tfloat = str(obj.polling_timestamp)
#         if tfloat.replace('.', '').isdigit():
#             timestamp = datetime.datetime.fromtimestamp(float(tfloat)).strftime("%H:%M:%S %m-%d-%Y")
#         else:
#             timestamp = tfloat
#         return timestamp
#     display_polling_timestamp.short_description = 'Timestamp when device polled'
#     
# admin.site.register(HostNames, HostNamesModelAdmin)
admin.site.register(HostNames)