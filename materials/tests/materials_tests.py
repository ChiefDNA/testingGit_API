from rest_framework import status
from accounts.models import Accounts
from rest_framework.test import APIClient
from accounts.models import Accounts
from django.test import TestCase
from accounts.jwt_auth import generate_jwt
from materials.models import Material, MaterialUsage, Supplier, MaterialType  # Replace 'materials' with your actual app name
from accounts.tests.test_Data import SetUpTestData


class SetUpTestData1(TestCase):
    def setUp(self):
        #self.client = APIClient
        self.admin_1 = Accounts.objects.create(
            username="adminuser",
            contact="admin@example.com",
            address="123 Admin St",
            dateOfBirth="1990-01-01",
            password="Strong.password2",
            role="admin"
        )
        self.admin = Accounts.objects.create(
            username="foremanjoe",
            contact="foreman@example.com",
            address="Site 1",
            dateOfBirth="1988-03-12",
            password="Some_hashed_password1",
            role="admin"
        )
        self.token = generate_jwt(self.admin_1)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        self.material_type_data = {
            "name": "Concrete",
        }
        self.material_type_data_2 = MaterialType.objects.create(
            name= "Stones"
        )
        self.supplier_data = {
            "name": "Best Supplies Ltd",
            "contact_info": "123 Supply Lane, City"
        }
        self.supplier_data_2 = Supplier.objects.create(
            name= "Joshua and Sons"
        )
        self.material_data = {
            "name": "Cement 50kg",
            "supplier": 1,
            "total_quantity": 100,
            "unit_cost": 12.5,
            "type": 1,
            "added_by": self.admin_1.id  # Will be overridden
        }
        self.material_data_2 = lambda: {
            "name": "Cement 50kg",
            "supplier": self.supplier_data_2,
            "total_quantity": 100,
            "unit_cost": 12.5,
            "type": self.material_type_data_2,
            "added_by": self.admin_1  # Will be overridden
        }
        


class MaterialTests(SetUpTestData1):


    def test_create_material_success(self):
        response = self.client.post('/materials/general/', self.material_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(response.data['message'], 'saved')


    def test_create_material_unauthorized(self):
        response = self.client.post('/materials/general/', self.material_data, format='json')  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Material.objects.count(), 0)


    def test_patch_material(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"total_quantity": 200}
        response = self.client.patch(f'/materials/general/{material.id}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertNotEqual(material.total_quantity, 200)


    def test_delete_material(self):
        material = Material.objects.create(**self.material_data_2())
        response = self.client.delete(f'/materials/general/{material.id}/', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)


    def test_invalid_material_input(self):
        invalid_data = self.material_data.copy()
        invalid_data["name"] = "@@@bad!!!"  # fails regex
        response = self.client.post('/materials/general/', invalid_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_material_usage(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": 10,
            "date": "2025-05-19",
        }
        response = self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaterialUsage.objects.count(), 1)



class MaterialTypeTests(SetUpTestData1):


    def test_create_material_type_success(self):
        response = self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Material saved')


    def test_create_material_type_unauthorized(self):
        response = self.client.post('/materials/type/', self.material_type_data, format='json')  # no token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_material_type_invalid_name(self):
        bad_data = self.material_type_data.copy()
        bad_data['name'] = '@@@InvalidName!'
        response = self.client.post('/materials/type/', bad_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class SupplierTests(SetUpTestData1):


    def test_create_supplier_success(self):
        response = self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Supplier saved')


    def test_create_supplier_unauthorized(self):
        response = self.client.post('/materials/supplier/', self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_supplier_invalid_contact(self):
        bad_data = self.supplier_data.copy()
        bad_data['contact_info'] = '### BAD!!'
        response = self.client.post('/materials/supplier/', bad_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
