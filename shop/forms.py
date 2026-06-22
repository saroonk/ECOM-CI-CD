from django import forms
from .models import CartItem,Contact


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }





class contactform(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(str(phone)) < 10:
            raise forms.ValidationError("phone number should be min 10")
        return phone