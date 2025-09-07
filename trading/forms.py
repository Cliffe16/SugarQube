from django import forms

class OrderForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity (50kg bags)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'})
    )