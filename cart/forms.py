from django import forms
from .models import ShoppingCart
from products.models import Color

class AddToCartForm(forms.ModelForm):
    color = forms.ModelChoiceField(queryset=Color.objects.none(), required=True)

    class Meta:
        model = ShoppingCart
        fields = ['color', 'quantity']

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

        if product:
            self.fields['color'].queryset = product.colors.all()
