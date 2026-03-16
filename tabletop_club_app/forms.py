from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import BoardGame

class MemberCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

class BoardGameCreationForm(forms.ModelForm):
    class Meta:
        model = BoardGame
        fields = ['title', 'category', 'min_players', 'max_players', 'playtime_minutes', 'quantity']

class MemberEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]