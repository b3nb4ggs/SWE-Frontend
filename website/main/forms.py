from django import forms
import datetime
import re
from django.forms import widgets
from django.forms.fields import DateField
from datetime import date 

INTEGER_CHOICES=[tuple([x,x]) for x in range(1,10)]
#DATE_FORMAT 
ROOM_TYPES = ( ("Standard", "Standard"),
		("Queen", "Queen"),
		("King", "King")
)
AMENITIES = (
    ("Pool", "Pool"),
    ("Gym", "Gym"),
    ("Business Office", "Business Office"),
    ("Wifi", "Wifi"),
    ("Room Service", "Room Service"),
    ("Spa", "Spa"),
)
PRICE_RANGE = ( (1, "Less than $50"), (2,"$50 to $100"), (3,"$100 to $200"), (4, "$200 to $300"), (5, "Greater than $300")) 

class CreateAccount(forms.Form):
	first = forms.CharField(label="First Name", max_length=200)
	last = forms.CharField(label="Last Name", max_length=200)
	phone = forms.CharField(label="Phone Number", max_length=200)
	email = forms.EmailField(label="Email Address", max_length=200)
	username = forms.CharField(label="User Name", max_length=200)
	password = forms.CharField(label="Password", max_length=200)

class dateinput(forms.DateInput):
        input_type = "date"
	
class Login(forms.Form):
	username = forms.CharField(label="Username", max_length=200)	
	password = forms.CharField(label="Password", max_length=200)   

class Search(forms.Form):
	checkin = forms.DateField(widget=dateinput, initial=date.today())
	checkout = forms.DateField(widget=dateinput, initial=date.today())
	numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
	numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)


class Filter(forms.Form):
	checkin = forms.DateField(widget=dateinput, required=True)
	checkout = forms.DateField(widget=dateinput, required=True)
	numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES, required=True)
	numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES, required=True)
	roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES, required=True)
	amenities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=AMENITIES, required=False)
	priceRange = forms.MultipleChoiceField(label="Your Budget",widget=forms.CheckboxSelectMultiple,choices=PRICE_RANGE, required=False)
	class Meta(forms.Form):
		widgets = {"checkin": dateinput()}

class Reserve(forms.Form):
	checkin = forms.DateField(widget=dateinput)
	checkout = forms.DateField(widget=dateinput)
	numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
	numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)
	roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES)

	class Meta(forms.Form):
		widgets = {'checkin': forms.HiddenInput(), 'checkout': forms.HiddenInput(), 'numRooms': forms.HiddenInput(), 'numGuests': forms.HiddenInput(), 'roomType': forms.HiddenInput  }
