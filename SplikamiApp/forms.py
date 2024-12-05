# forms.py
from django import forms
from .models import Contact, Document
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'company', 'email', 'phone_number', 'subject', 'message']
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title']

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Validate email format
        try:
            validate_email(username)
        except ValidationError:
            raise forms.ValidationError(_("Voer een geldig e-mailadres in."))

        # Check for unique username (email)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Dit e-mailadres is al geregistreerd.")
        
        return username