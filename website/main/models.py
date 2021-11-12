from django.db import models

# Create your models here.

class Property(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=200)
	numStandard=models.IntegerField(default=0)
	numQueen=models.IntegerField(default=0)
	numKing=models.IntegerField(default=0)
	priceStandard=models.IntegerField(default=0)
	priceQueen=models.IntegerField(default=0)
	priceKing=models.IntegerField(default=0)
	weekendDiff=models.IntegerField(default=0)
	amenities=models.CharField(max_length=200)
	
	def __str__(self):
		return self.name


class User(models.Model):
	first = models.CharField(max_length=200)
	last = models.CharField(max_length=200)
	type = models.CharField(max_length=200)
	username = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	phone = models.CharField(max_length=200)

	def __str__(self):
		return self.username

class Reservation(models.Model):
	id = models.IntegerField(primary_key=True)
	active = models.BooleanField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	property = models.ForeignKey(Property, on_delete=models.CASCADE)
	checkin =  models.CharField(max_length=200)
	checkout =models.CharField(max_length=200)
	roomType = models.CharField(max_length=200)
	numNights = models.IntegerField(default=0)
	totalPrice = models.CharField(max_length=200)

	def __str__(self):
            return self.id

