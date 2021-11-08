from django import forms
import datetime
import re
from django.forms import widgets


INTEGER_CHOICES=[tuple([x,x]) for x in range(1,10)]
#DATE_FORMAT 
ROOM_TYPES = ( (1, "Standard"), 
		(2, "Queen"), 
		(3, "King")
)
AMENITIES = ((1, "Pool"), (2, "Gym"), (3, "Business Office"), (4, "Wifi"), (5, "Room Service"), (6, "Spa"))
PRICE_RANGE = ( (1, "Less than $50"), (2,"$50 to $100"), (3,"$100 to $200"), (4, "$200 to $300"), (5, "Greater than $300")) 

class CreateAccount(forms.Form):
	first = forms.CharField(label="First Name", max_length=200)
	last = forms.CharField(label="Last Name", max_length=200)
	phone = forms.CharField(label="Phone Number", max_length=200)
	email = forms.EmailField(label="Email Address", max_length=200)
	username = forms.CharField(label="User Name", max_length=200)
	password = forms.CharField(label="Password", max_length=200)


#class CreateReservation(forms.Form):	
	
class Login(forms.Form):
	username = forms.CharField(label="Username", max_length=200)	
	password = forms.CharField(label="Password", max_length=200)   

class Search(forms.Form):
	#checkin = forms.DateField(label="Check-In", widget=widgets.SelectDateWidget())
	#checkout = forms.DateField(label="Check-Out", widget=widgets.SelectDateWidget())
	checkin = forms.CharField(label="Check-In")
	checkout =  forms.CharField(label="Check-Out")
	numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
	numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)

class Filter(forms.Form):
        #checkin = forms.DateField(label="Check-In", widget=widgets.SelectDateWidget())
        #checkout = forms.DateField(label="Check-Out", widget=widgets.SelectDateWidget())
	checkin = forms.CharField(label="Check-In")
	checkout =  forms.CharField(label="Check-Out")
	numRooms = forms.ChoiceField(label="Rooms", choices=INTEGER_CHOICES)
	numGuests = forms.ChoiceField(label="Guests", choices=INTEGER_CHOICES)
	roomType = forms.ChoiceField(label="Room Type", choices=ROOM_TYPES)
	amenities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=AMENITIES)
	priceRange = forms.MultipleChoiceField(label="Your Budget",widget=forms.CheckboxSelectMultiple,choices=PRICE_RANGE)
	#priceRange = forms.IntegerField(label="Price Range", widget=forms.NumberInput(attrs={'type':'range', 'step': '5', 'min': '0', 'max': '500'}), required=False)


