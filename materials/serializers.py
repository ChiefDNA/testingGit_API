from rest_framework import serializers
from .models import MaterialType, Material, MaterialUsage, Supplier


class MaterialTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MaterialType
        fields = ['id', 'name', 'company']
        read_only_fields = ['company']


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_info', 'company']
        read_only_fields = ['company']


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ['id', 'type', 'name', 'supplier', 'unit_cost', 'total_quantity', 'added_by', 'date_added']
        read_only_fields = ['added_by', 'date_added', 'company']


class MaterialUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaterialUsage
        fields = ['id', 'material', 'date', 'quantity_used', 'company']
        read_only_fields = ['company']