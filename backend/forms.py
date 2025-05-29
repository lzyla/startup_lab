from django import forms
from .models import Character, Message

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'header_description', 'description', 'avatar_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'header_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
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