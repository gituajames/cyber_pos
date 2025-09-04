from django.db import models
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name



class Sale(models.Model):
    items = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.items