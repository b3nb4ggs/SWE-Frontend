from django import forms


class FindRoomMaxPrice(forms.Form):
    price = forms.CharField(label="Price", max_length=200)
