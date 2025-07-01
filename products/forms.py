from django import forms
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from .models import Product, Category, Color, Size, WeightUnit, Material, DimensionUnit, Tag
from .widgets import CustomSelectWithPlaceholder
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image as PilImage


def validate_greater_than_zero(value, field_name="Value"):
    if value is None:
        return None
    
    if value <= 0:
        raise ValidationError(f'{field_name} must be greater than zero.')
    return value



# Product Form (Related to Creation)
class ProductForm(forms.ModelForm):     
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'description', 'stock', 'stock_status', 
                  'colors', 'features', 'size', 'weight', 'weight_unit', 'materials', 
                  'height', 'width', 'depth', 'dimension_unit', 'featured_image', 
                  'product_video', 'price', 'sale_price', 'delivery_charges', 'tags']
        

    product_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Your Product Name',
            'class': 'form-control'
        })
    )


    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter the description of your product',
            'class': 'form-control',
            'rows': "6",
        })
    )


    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=CustomSelectWithPlaceholder(placeholder='Choose a category')
    )


    stock = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the stock',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The stock field must only contain numbers.',
            'required': 'The stock field is required.'
        }
    )

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        return validate_greater_than_zero(stock, 'Stock')


    stock_status = forms.ChoiceField(
        choices=[('in stock', 'In Stock'), ('out of stock', 'Out of Stock')],
        widget=CustomSelectWithPlaceholder(placeholder='Choose Stock status'),
        initial='in stock',
    )


    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label="Choose Your Product Colors:",
        required=False
    )


    features = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter Features of your product',
            'class': 'form-control',
            'rows': "4",
        })
    )


    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        widget=CustomSelectWithPlaceholder(placeholder='Choose Your Product Size')
    )


    weight = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Product Weight',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The weight field must only contain numbers.',
            'required': 'The weight field is required.'
        }
    )

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        return validate_greater_than_zero(weight, 'Weight')


    weight_unit = forms.ModelChoiceField(
        queryset=WeightUnit.objects.all(),
        widget=CustomSelectWithPlaceholder(placeholder='Choose Weight Unit')
    )


    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label="Choose Your Product Materials:",
        required=False
    )


    height = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Height',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The height field must only contain numbers.',
            'required': 'The height field is required.'
        }
    )

    def clean_height(self):
        height = self.cleaned_data.get('height')
        return validate_greater_than_zero(height, 'Height')


    width = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Width',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The width field must only contain numbers.',
            'required': 'The width field is required.'
        }
    )

    def clean_width(self):
        width = self.cleaned_data.get('width')
        return validate_greater_than_zero(width, 'Width')


    depth = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Depth',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The depth field must only contain numbers.',
            'required': 'The depth field is required.'
        }
    )

    def clean_depth(self):
        depth = self.cleaned_data.get('depth')
        return validate_greater_than_zero(depth, 'Depth')


    dimension_unit = forms.ModelChoiceField(
        queryset=DimensionUnit.objects.all(),
        widget=CustomSelectWithPlaceholder(placeholder='Dimension Unit')
    )



    '''def validate_image_dimensions(featured_image):
        #Validate the dimensions of the image (max 1920x1080).
        img = PilImage.open(featured_image)
        if img.height > 1080 or img.width > 1920:
            raise ValidationError(_('Image dimensions too large ( > 1920x1080 )'))'''

    '''def validate_image_size(featured_image):
        max_size_img = 4
        if featured_image.size > max_size_img * 1024 * 1024:
            raise ValidationError(f"Image file size should not exceed {max_size_img}MB.")'''

    featured_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        }),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            #validate_image_size,
            #validate_image_dimensions
        ]
    )


    def validate_video_size(value):
        max_size = 26 * 1024 * 1024
        if value.size > max_size:
            raise ValidationError('The video size cannot exceed 26MB.')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_video'].required = False

    product_video = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        }),
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']),
            validate_video_size]
    )

    price = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Price',
            'class': 'form-control'
        }),
        error_messages={
            'invalid': 'The price field must only contain numbers.',
            'required': 'The price field is required.'
        }
    )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        return validate_greater_than_zero(price, 'Price')


    sale_price = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Sale Price',
            'class': 'form-control'
        }),

        required=False, 

        error_messages={
            'invalid': 'The sale price field must only contain numbers.',
        }
    )

    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        return validate_greater_than_zero(sale_price, 'Sale Price')


    delivery_charges = forms.DecimalField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Product Delivery Charges',
            'class': 'form-control'
        }),

        required=False, 

        error_messages={
            'invalid': 'The delivery charges field must only contain numbers.',
        }
    )

    def clean_delivery_charges(self):
        delivery_charges = self.cleaned_data.get('delivery_charges')
        return validate_greater_than_zero(delivery_charges, 'Delivery Charges')
    

    
    tags = forms.CharField(
        required=False, 
        help_text="Enter tags separated by commas."
    )

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tag_names]
        return tags
