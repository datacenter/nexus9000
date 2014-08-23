'''
Created on May 8, 2014

@author: admin
@see: To allow access of constants in templates: http://stackoverflow.com/a/433209/558397
'''

from django.conf import settings # import the settings file

def site_name(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'SITE_NAME': settings.SITE_NAME}