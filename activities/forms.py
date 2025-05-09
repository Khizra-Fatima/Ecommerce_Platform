from django import forms
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from .models import Message
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image as PilImage




class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['msg_content']
        widgets = {
            'msg_content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type Your Message...',
                'rows': 2,
            }),
        }
        labels = {
            'msg_content': 'Message',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['msg_content'].required = True
