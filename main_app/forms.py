from django import forms
from products.models import Category, Size, Material, Color




class ProductFilterForm(forms.Form):
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('in stock', 'In Stock'),
            ('out of stock', 'Out of Stock')
        ],
        required=False,
        label="Stock Status"
    )

    sale = forms.BooleanField(
        required=False,
        label="Sale Product"
    )

    price_range = forms.MultipleChoiceField(
        choices=[
            ('0-200', '$0-$200'),
            ('200-400', '$200-$400'),
            ('400-600', '$400-$600'),
            ('600-800', '$600-$800'),
            ('800-10000', '$800-$10000'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Filter by Price"
    )

    size = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

