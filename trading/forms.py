from django import forms

class OrderForm(forms.Form):
    """
    This class defines a blank order form for placing an order
    """
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity (50kg bags)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Enter quantity'
        })
    )