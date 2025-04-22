from django import forms
from .models import Product

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 60px;',
        })
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product = self.product
        if quantity > product.stock:
            raise forms.ValidationError(
                f"Only {product.stock} items available in stock."
            )
        return quantity

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if self.product:
            self.fields['quantity'].max_value = self.product.stock 