from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

class MessageForm(forms.Form):
    message = forms.CharField(label='Your Question', widget=forms.Textarea(attrs={'required':'true', 'placeholder': 'Enter your Question'}))