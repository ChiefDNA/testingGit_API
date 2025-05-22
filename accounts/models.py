from django.db import models

# Create your models here.

class Accounts(models.Model):
    username = models.CharField(unique=True,max_length=255)
    contact = models.CharField(unique=True,max_length=30)
    address = models.CharField(max_length=200)
    dateOfBirth = models.DateField(max_length=20)
    password = models.CharField(max_length=255)
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('foreman','Foreman'),
        ('worker','Worker')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='worker')

    def __str__(self):
        return self.username