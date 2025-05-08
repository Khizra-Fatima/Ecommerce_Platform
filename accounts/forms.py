from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, Store, Profile
from django.core.validators import MaxLengthValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from .widgets import CustomSelectWithPlaceholder
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from django.utils.translation import gettext_lazy as _



class CustomUserCreationForm(UserCreationForm):

    ROLE_CHOICES = [
        #('admin', 'Admin'),
        #('coadmin', 'Coadmin'),
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]
    
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': '@gmail.com', 'autocomplete': 'email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': '@gmail.com', 'autocomplete': 'email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'current-password'})
    )

    def __init__(self, *args, **kwargs):
        # Pop the request from kwargs
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            # Use email for authentication
            user = authenticate(request=self.request, email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password")
        return self.cleaned_data



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio', 'phone_number', 'address', 'instagram', 'facebook', 'twitter']

        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            try:
                # Open the image using PIL
                img = Image.open(image)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    # Save the resized image back to memory
                    buffer = io.BytesIO()
                    img.save(buffer, format=img.format)
                    buffer.seek(0)

                    # Replace the uploaded image with the resized one
                    image = InMemoryUploadedFile(
                        buffer,
                        'ImageField',
                        image.name,
                        image.content_type,
                        buffer.tell(),
                        None
                    )
            except Exception as e:
                raise forms.ValidationError(f"Error processing image: {e}")

        return image



class UserUpdateForm(forms.ModelForm):
    new_email = forms.EmailField(label='New Email', required=False)
    password_form = PasswordChangeForm

    class Meta:
        model = CustomUser
        fields = ['email']


    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if new_email and CustomUser.objects.filter(email=new_email).exists():
            raise forms.ValidationError("This email is already used for an account.")
        return new_email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('new_email'):
            user.email = self.cleaned_data['new_email']
        if commit:
            user.save()
        return user
    


# Store Form (Related to Editing)
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name', 'description', 'store_number', 'store_location', 
            'featured_image', 'banner_image', 'opening_hours', 
            'closing_hours', 'return_policy', 'shipping_policy'
        ]
    
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your store name',
            'class': 'form-control'
        }),
        label="Store Name"
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter a description for your store: max length (150)',
            'class': 'form-control',
            'rows': 4,
        }),
        label="Description",
        required=False
    )

    store_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact number for your store'
        }),
        label="Store Contact Number",
        required=False
    )

    store_location = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter the location of your store'
        }),
        label="Store Location",
        required=False
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
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            # validate_image_size,
            # validate_image_dimensions
        ],
        label="Featured Image"
    )

    banner_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            # validate_image_size,
            # validate_image_dimensions
        ],
        label="Banner Image"
    )

    opening_hours = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Opening Hours",
        required=False
    )

    closing_hours = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Closing Hours",
        required=False
    )

    return_policy = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Enter your return policy...'
        }),
        label="Return Policy",
        required=False,
        help_text="Specify the return policy for your store."
    )

    shipping_policy = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Enter your shipping policy...'
        }),
        label="Shipping Policy",
        required=False,
        help_text="Specify the shipping policy for your store."
    )

    # Additional validation for opening and closing hours
    def clean(self):
        cleaned_data = super().clean()
        opening_hours = cleaned_data.get("opening_hours")
        closing_hours = cleaned_data.get("closing_hours")

        if opening_hours and closing_hours and opening_hours >= closing_hours:
            self.add_error('closing_hours', "Closing hours must be after opening hours.")

        return cleaned_data