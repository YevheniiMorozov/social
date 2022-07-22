from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import Account, Image
from PIL import Image as im


class UserLoginForm(AuthenticationForm):
    password = forms.CharField(label="password", widget=forms.PasswordInput(attrs={"class": "form-control"}))


class AccountRegisterForm(UserCreationForm):
    email = forms.EmailField(label="email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(label="password", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="repeat password", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = ["email"]
        exclude = ["username"]


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

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 4mb )")
            # Cloudinary can download pdf file without that condition. Also now we can create post without image
            elif image.size < 10 * 1024 * 1024:
                try:
                    im.open(image)
                except IOError:
                    raise ValidationError("File is not image")
            return image
