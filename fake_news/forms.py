from django import forms
from .models import News, Auth 


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ('title', 'text',)

class AuthForm(forms.ModelForm):
    class Meta:
        model = Auth
        fields = ('username', 'password',)