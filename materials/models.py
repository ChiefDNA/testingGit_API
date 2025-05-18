from django.db import models
from accounts.models import Accounts

# Create your models here.


class MaterialType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class Material(models.Model):
    name  = models.CharField(max_length=255)
    type = models.ForeignKey(MaterialType, on_delete=models.SET_NULL, null=True, blank=True)
    Supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_quatity = models.FloatField()
    date_added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(Accounts, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.total_quatity} units"
    

class MaterialUsage(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='usage_logs')
    date =models.DateField()
    quantity_used = models.FloatField()

    class Meta:
        unique_toether = ['material', 'date'] #to avoid duplicte logs on same day

    def __str__(self):
        return f"{self.material.name} used on {self.date}: {self.quantity_used}"