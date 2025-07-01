from django import forms
from .models import OrderCheckoutUserInfo, DELIVERY_CHOICES
from django.core.validators import RegexValidator
from products.models import Color


class OrderCheckoutForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number (9-15 digits).")
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    delivery_method = forms.ChoiceField(
        choices=DELIVERY_CHOICES, 
        widget=forms.Select(attrs={
            'class': 'form-control'
        }))
    
    color = forms.ModelChoiceField(
        queryset=Color.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = OrderCheckoutUserInfo
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'color', 'delivery_method']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if product:
            self.fields['color'].queryset = Color.objects.filter(products=product)





class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderCheckoutUserInfo
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }