from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Customer

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Customer
        fields = ('phone_number', 'first_name', 'last_name', 'location', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Customer.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone_number']  # Use phone number as username
        if commit:
            user.save()
        return user

class CustomerLoginForm(forms.Form):
    phone_number = forms.CharField(
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        try:
            Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            raise forms.ValidationError('No account found with this phone number.')
        return phone_number
