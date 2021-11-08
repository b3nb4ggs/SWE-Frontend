from django import forms
from django.forms import widgets
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from datetime import date


INTEGER_CHOICES = [tuple([x, x]) for x in range(1, 10)]
# DATE_FORMAT
ROOM_TYPES = ((1, "Standard"), (2, "Queen"), (3, "King"))
AMENITIES = (
    (1, "Pool"),
    (2, "Gym"),
    (3, "Business Office"),
    (4, "Wifi"),
    (5, "Room Service"),
    (6, "Spa"),
)
PRICE_RANGE = (
    (1, "Less than $50"),
    (2, "$50 to $100"),
    (3, "$100 to $200"),
    (4, "$200 to $300"),
    (5, "Greater than $300"),
)


class Protoform(forms.Form):
    my_date_field = forms.DateField()


class FindRoomMaxPrice(forms.Form):
    price = forms.CharField(label="Price", max_length=200)


class dateinput(forms.DateInput):
    input_type = "date"


class Search(forms.Form):
    check_in = forms.DateField(widget=dateinput)
    check_out = forms.DateField(widget=dateinput, initial=date.today())
    # checkin = forms.CharField(label="Check-In")
    # checkout = forms.CharField(label="Check-Out")
    numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
    numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)

    class Meta(forms.Form):
        widgets = {"check_in": dateinput()}
