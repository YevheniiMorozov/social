from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Post, Comments, Account, Tag, Image


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


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["body"]
        widgets = {
            "body": forms.TextInput(attrs={"class": "form-control"}),
        }