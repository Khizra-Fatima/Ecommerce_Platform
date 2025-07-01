from django import forms

class CustomSelectWithPlaceholder(forms.Select):
    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop('placeholder', '')
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        
        if self.placeholder and not value:
            option['label'] = self.placeholder
            option['attrs']['disabled'] = 'disabled'
            option['attrs']['hidden'] = 'hidden'
        return option