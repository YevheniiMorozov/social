from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Account, Image


class UserLoginForm(AuthenticationForm):
    password = forms.CharField(label="password", widget=forms.PasswordInput(attrs={"class": "form-control"}))


class AccountRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="email", widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = Account
        fields = ["email"]


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "username", "password", "bio"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ChangeUserInfoForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "bio"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]
