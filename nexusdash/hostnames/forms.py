from django import forms
from .models import HostNames
from urlparse import urlparse
from django.core import validators
from django.utils.translation import ugettext_lazy as _
import re


class MyURLValidator(validators.URLValidator):
    '''
    Override URLValidator to:
    * allow ssh and telnet as protocols
    * allow domain without dots
    '''
    # Copy of regex from validators.URLValidator
    regex = re.compile(
        r'^(?:http|https|ssh|telnet)://'        ## r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'[\w\-]+|'                           ## r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    message = _('Enter a valid URL.')
    
class MyURLField(forms.URLField):
    '''
    Override URLField to modify the validation
    The validation is modified to allow ssh and telnet as protocols
    '''
    default_validators = [MyURLValidator()]

class LoginForm(forms.ModelForm):
    """
    Form for login.
    """
    url = MyURLField(required=True, min_length=5, max_length=30)
    username = forms.RegexField(label='Username', required=True, min_length=3, max_length=30, regex = re.compile(r'^[\\\w]+$'),
                                error_messages = {'invalid': "Enter valid username. Allowed only letters, numbers and characters _ \\"})
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True, min_length=3, max_length=30)

    class Meta:
        model = HostNames
        fields = ['url', 'username', 'password']    # Fields to be used for creating form

    def save(self, commit=True):
        '''Overriding save to allow 
        '''
        user = super(LoginForm, self).save(commit=False)
        if commit:
            # Adding hostname to the db
            user.hostname = str(urlparse(user.url).hostname)
            user.save()
        return user
    