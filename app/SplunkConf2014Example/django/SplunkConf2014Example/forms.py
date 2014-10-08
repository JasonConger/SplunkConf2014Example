# NOTE: Using django.forms directly instead of splunkdj.setup.forms
from django import forms
import os.path
import splunklib.client as client
import subprocess
import sys

class SetupForm(forms.Form):

    username = forms.CharField(
        label="Username",
        max_length=100)
    
    password = forms.CharField(
        label="Password",
        max_length=100,
        widget=forms.PasswordInput(render_value=True))
    
    @classmethod
    def load(cls, request):
        """Loads this form's persisted state, returning a new Form."""
        
        service = request.service
        
        # Locate the storage/passwords entity that contains the
        # credentials, if available.
        passwords_endpoint = client.Collection(service, 'storage/passwords')
        passwords = passwords_endpoint.list()
        first_password = passwords[0] if len(passwords) > 0 else None
        
        settings = {}
        
        # Read credentials from the password entity.
        # NOTE: Reading from 'password' setting just gives a bunch of asterisks,
        #       so we need to read from the 'clear_password' setting instead.
        # NOTE: Reading from 'name' setting gives back a string in the form
        #       '<realm>:<username>', when we only want the username.
        #       So we need to read from the 'username' setting instead.
        settings['password'] = first_password['clear_password'].split(':')[0] if first_password else ''
        settings['username'] = first_password['username'] if first_password else ''
        
        # Create a SetupForm with the settings
        return cls(settings)
    
    def clean(self):
        """Perform validations that require multiple fields."""
        
        cleaned_data = super(SetupForm, self).clean()
        
        # Verify that the credentials are valid
        credentials = [
            cleaned_data.get('password', None),
            cleaned_data.get('username', None),
        ]
        if None in credentials:
            # One of the credential fields didn't pass validation,
            # so don't even try connecting to Twitter.
            pass

        return cleaned_data
    
    def save(self, request):
        """Saves this form's persisted state."""
        
        service = request.service
        settings = self.cleaned_data
        
        first_password_settings = {
            'name': settings['username'],
            'password': settings['password']
        }
        
        # Replace old password entity with new one
        passwords_endpoint = client.Collection(service, 'storage/passwords')
        passwords = passwords_endpoint.list()
        if len(passwords) > 0:
            first_password = passwords[0]
            first_password.delete()
        first_password = passwords_endpoint.create(**first_password_settings)