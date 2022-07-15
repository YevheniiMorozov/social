from django import forms
from posts.models import Post, Comments, Tag


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