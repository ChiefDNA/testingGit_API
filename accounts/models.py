from django.db import models
# from django.contrib.auth.models import AbstractUser

# Create your models here.
class Accounts(models.Model):
    username = models.CharField(unique=True,max_length=255)
    contact = models.CharField(unique=True,max_length=30)
    address = models.CharField(max_length=200)
    dateOfBirth = models.DateField(max_length=20)
    password = models.CharField(max_length=255)

    # USERNAME_FIELD ='username'
    # REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.name