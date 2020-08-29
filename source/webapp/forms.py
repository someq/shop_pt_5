from django import forms
from webapp.models import Product, Cart, Order


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label="Найти")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = []


class CartAddForm(forms.ModelForm):
    class Meta:
        model = Cart
        # fields = []
        fields = ['qty']  # бонус


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['products']
