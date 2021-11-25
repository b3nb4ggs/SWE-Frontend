from django import forms
import datetime
import re
from django.forms import widgets
from django.forms.fields import DateField
from datetime import date
from main import database as db
from django_filters.widgets import RangeWidget
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm

INTEGER_CHOICES = [tuple([x, x]) for x in range(1, 10)]
# DATE_FORMAT
ROOM_TYPES = (("Standard", "Standard"), ("Queen", "Queen"), ("King", "King"))

AMENITIES = (
    ("Pool", "Pool"),
    ("Gym", "Gym"),
    ("Business Office", "Business Office"),
    ("Wifi", "Wifi"),
    ("Room Service", "Room Service"),
    ("Spa", "Spa"),
)

PRICE_RANGE = (
    (1, "Less than $50"),
    (2, "$50 to $100"),
    (3, "$100 to $200"),
    (4, "$200 to $300"),
    (5, "Greater than $300"),
)


class CreateAccount(forms.Form):
    first = forms.CharField(label="First Name", max_length=200)
    last = forms.CharField(label="Last Name", max_length=200)
    phone = forms.CharField(label="Phone Number", max_length=200)
    email = forms.EmailField(label="Email Address", max_length=200)
    username = forms.CharField(label="User Name", max_length=200)
    password = forms.CharField(label="Password", max_length=200)

class ViewAccount(UserChangeForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=True, help_text="Phone number")
    first = forms.CharField(max_length=20, required=True, help_text="First name")
    last = forms.CharField(max_length=20, required=True, help_text="Last name")

    class Meta:
        model = User
        fields = [
            "first",
            "last",
            "phone",
            "email",
            "username",
        ]


class dateinput(forms.DateInput):
    input_type = "date"


class Login(forms.Form):
    username = forms.CharField(label="Username", max_length=200)
    password = forms.CharField(label="Password", max_length=200)


class Search(forms.Form):
    checkin = forms.DateField(widget=dateinput, initial=datetime.today())
    checkout = forms.DateField(widget=dateinput, initial=datetime.today() + timedelta(days=1))
    numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
    numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)



class Filter(forms.Form):
    checkin = forms.DateField(widget=dateinput, required=True, initial=datetime.today())
    checkout = forms.DateField(widget=dateinput, required=True, initial=datetime.today() + timedelta(days=1))
    numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES, required=True)
    numGuests = forms.ChoiceField(
        label="Guests", choices=INTEGER_CHOICES, required=True
    )
    roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES, required=True)
    amenities = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=AMENITIES, required=False
    )



class Reserve(forms.Form):
    checkin = forms.DateField(widget=dateinput)
    checkout = forms.DateField(widget=dateinput)
    numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
    numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)
    roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES)

    class Meta(forms.Form):
        widgets = {
            "checkin": forms.HiddenInput(),
            "checkout": forms.HiddenInput(),
            "numRooms": forms.HiddenInput(),
            "numGuests": forms.HiddenInput(),
            "roomType": forms.HiddenInput,
        }


class ReadOnlyWidget(widgets.Widget):
    def render(self, _, value, attrs=None):
        return value


class EditReservation(forms.Form):
    checkin = forms.DateField(widget=dateinput, required=True)
    checkout = forms.DateField(widget=dateinput, required=True)
    numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES, required=True)
    numGuests = forms.ChoiceField(
        label="Guests", choices=INTEGER_CHOICES, required=True
    )
    roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES, required=True)

class AddProperty(forms.Form):
    name = forms.CharField(label="Property Name", max_length=200)
    amenities = forms.MultipleChoiceField(label="Amenities",
        widget=forms.CheckboxSelectMultiple, choices=AMENITIES, required=True
    )
    numStandard = forms.IntegerField(label="Number of Standard Rooms", required=True)
    priceStandard = forms.FloatField(label="Standard Rate", required=True)
    numQueen = forms.IntegerField(label="Number of Queen Rooms", required=True)
    priceQueen = forms.FloatField(label="Queen Rate", required=True)
    numKing = forms.IntegerField(label="Number of King Rooms", required=True)
    priceKing = forms.FloatField(label="King Rate", required=True)
    weekendDiff = forms.IntegerField(label="Weekend Differential", required=True)


