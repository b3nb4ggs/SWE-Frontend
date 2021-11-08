from django.contrib import admin
from .models import User, Reservation, Property 

# Register your models here.
admin.site.register(User)
admin.site.register(Reservation)
admin.site.register(Property)
