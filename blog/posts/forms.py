from django import forms
from django.core.exceptions import ValidationError

from .models import Group, Post


class GroupForm(forms.ModelForm):
    def clean_slug(self):
        cleaned_slug = self.cleaned_data["slug"].lower()
        if cleaned_slug == "new":
            raise ValidationError("A slug may not be a 'new'")
        return cleaned_slug

    class Meta:
        model = Group
        fields = ("title", "slug", "description")

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

        labels = {
            'text': 'Текст',
            'group': 'Группа'
        }

        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }