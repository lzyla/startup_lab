from django import forms
from .models import Character, Message

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'header_description', 'greeting', 'description', 'avatar', 'avatar_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'header_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'greeting': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'avatar_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        labels = {'content': '',}
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Napisz wiadomość...'
            }),
        }
