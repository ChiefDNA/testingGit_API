from django.db import models
from companies.models import Company

# Create your models here.

class Accounts(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    username = models.CharField(unique=True,max_length=255)
    contact = models.CharField(unique=True,max_length=30)
    address = models.CharField(max_length=200)
    dateOfBirth = models.DateField(max_length=20)
    password = models.CharField(max_length=255)
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('foreman','Foreman'),
        ('worker','Worker'),
        ('manager','Manager'),
        ('supervisor','Supervisor'),
        ('client','Client'),
        ('guest','Guest'),
        ('superUser','SuperUser'),
        ('subcontractor','Subcontractor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')

    def __str__(self):
        return self.username