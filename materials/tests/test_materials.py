from rest_framework import status
from accounts.models import Accounts
from rest_framework.test import APIClient
from accounts.models import Accounts
from django.test import TestCase
from accounts.jwt_auth import generate_jwt
from materials.models import Material, MaterialUsage, Supplier, MaterialType  # Replace 'materials' with your actual app name
from datetime import datetime


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
        self.worker = Accounts.objects.create(
            username="JohnTheBuider",
            contact="0778889999",
            address="Site 1",
            dateOfBirth="1998-03-12",
            password="VeryLegitpassword1",
            role="worker"
        )
        self.token = generate_jwt(self.admin_1)
        self.token2 = generate_jwt(self.worker)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
        self.headers_2 = {'HTTP_AUTHORIZATION': f'Bearer {self.token2}'}
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
        self.material_data_3 = lambda: {
            "name": "Cement 25kg",
            "supplier": self.supplier_data_2,
            "total_quantity": 100,
            "unit_cost": 12.5,
            "type": self.material_type_data_2,
            "added_by": self.admin_1  # Will be overridden
        }
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        


class MaterialTests(SetUpTestData1):


    def test_create_material_success(self):
        response = self.client.post('/materials/general/', self.material_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(response.data['message'], 'Saved')
        self.assertEqual(str(Material.objects.get(id=1)), f"{self.material_data['name']} - {self.material_data['total_quantity']}.0 units")


    def test_create_material_unauthorized(self):
        response = self.client.post('/materials/general/', self.material_data, format='json', **self.headers_2)  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Material.objects.count(), 0)

    def test_create_material_exists(self):
        self.client.post('/materials/general/', self.material_data, format='json', **self.headers) 
        response = self.client.post('/materials/general/', self.material_data, format='json', **self.headers)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Material.objects.count(), 1)


    def test_get_material_success(self):
        response = self.client.post('/materials/general/', self.material_data, format='json', **self.headers)
        get_response = self.client.get('/materials/general/', format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(get_response.data[0]['name'], self.material_data['name'])

    
    def test_get_material_unauthorized(self):
        self.client.post('/materials/general/', self.material_data, format='json', **self.headers)
        response = self.client.get('/materials/general/', format='json', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(response.data['error'], "Unauthorized access")


    def test_patch_material(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"total_quantity": 200}
        response = self.client.patch(f'/materials/general/{material.id}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertNotEqual(material.total_quantity, 200)

    
    def test_patch_material_wrong_field(self):
        Material.objects.create(**self.material_data_3())
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"name": "Cement 25kg"}
        response = self.client.patch(f'/materials/general/{material.id}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(material.total_quantity, 100)
    

    def test_patch_material_unauthorized(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"total_quantity": 200}
        response = self.client.patch(f'/materials/general/{material.id}/', patch_data, content_type='application/json', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    

    def test_patch_material_invalid_input(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"total_quantity": "20d"}
        response = self.client.patch(f'/materials/general/{material.id}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Expecting numeric value for 'total_quantity'")

    
    def test_patch_material_not_user_id(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"total_quantity": 200}
        response = self.client.patch(f'/materials/general/{material.id + 3}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Material not found")

    
    def test_invalid_patch_material(self):
        material = Material.objects.create(**self.material_data_2())
        patch_data = {"supplier": 30}
        response = self.client.patch(f'/materials/general/{material.id + 3}/', patch_data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_material(self):
        material = Material.objects.create(**self.material_data_2())
        response = self.client.delete(f'/materials/general/{material.id}/', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)
    

    def test_delete_material_unauthorized(self):
        material = Material.objects.create(**self.material_data_2())
        response = self.client.delete(f'/materials/general/{material.id}/', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Unauthorized access")
    

    def test_delete_no_material(self):
        material = Material.objects.create(**self.material_data_2())
        response = self.client.delete(f'/materials/general/{material.id + 3}/', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Material not found")


    def test_invalid_material_input(self):
        invalid_data = self.material_data.copy()
        invalid_data["name"] = "@@@bad!!!"  # fails regex
        response = self.client.post('/materials/general/', invalid_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_invalid_material_number_input_type(self):
        invalid_data = self.material_data.copy()
        invalid_data["total_quantity"] = "10c"  # fails regex
        response = self.client.post('/materials/general/', invalid_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Expecting numeric value for 'total_quantity'")



class MaterialUsageTests(SetUpTestData1):

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
        self.assertEqual(str(MaterialUsage.objects.get(id=1)), f"{self.material_data_2()['name']} used on {self.current_date}: {usage_data['quantity_used']}.0")


    def test_create_materialusage_unauthorized(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": 10,
            "date": "2025-05-19",
        }
        response = self.client.post('/materials/usage/', usage_data, format='json', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MaterialUsage.objects.count(), 0)


    def test_create_material_usage_invalid_type(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": "10f",
            "date": "2025-05-19",
        }
        response = self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MaterialUsage.objects.count(), 0)

    
    def test_create_material_usage_twice(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": 10,
            "date": "2025-05-19",
        }
        self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        response = self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MaterialUsage.objects.count(), 1)
    

    def test_get_material_usage_succesful(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": 10,
            "date": "2025-05-19",
        }
        self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        response = self.client.get('/materials/usage/', **self.headers)
        self.assertEqual(len(response.data), 1)

     
    def test_get_material_usage_unauthorized(self):
        material = Material.objects.create(**self.material_data_2())
        usage_data = {
            "material": material.id,
            "quantity_used": 10,
            "date": "2025-05-19",
        }
        self.client.post('/materials/usage/', usage_data, format='json', **self.headers)
        response = self.client.get('/materials/usage/', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Unauthorized access")
       


class MaterialTypeTests(SetUpTestData1):


    def test_create_material_type_success(self):
        response = self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Material saved')
        self.assertEqual(str(MaterialType.objects.get(id=2)), self.material_type_data['name'])


    def test_create_material_type_unauthorized(self):
        response = self.client.post('/materials/type/', self.material_type_data, format='json')  # no token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_material_type_invalid_name(self):
        bad_data = self.material_type_data.copy()
        bad_data['name'] = '@@@InvalidName!'
        response = self.client.post('/materials/type/', bad_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_create_material_type_twice(self):
        self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        response = self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_get_material_type_succesful(self):
        self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        response = self.client.get('/materials/type/', **self.headers)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['name'], self.material_type_data['name'])


    def test_get_material_type_unauthorized(self):
        self.client.post('/materials/type/', self.material_type_data, format='json', **self.headers)
        response = self.client.get('/materials/type/', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Unauthorized access")


class SupplierTests(SetUpTestData1):


    def test_create_supplier_success(self):
        response = self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Supplier saved')
        self.assertEqual(str(Supplier.objects.get(id=2)), self.supplier_data['name'])


    def test_create_supplier_unauthorized(self):
        response = self.client.post('/materials/supplier/', self.supplier_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_supplier_twice(self):
        self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        response = self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_invalid_contact(self):
        bad_data = self.supplier_data.copy()
        bad_data['contact_info'] = '### BAD!!'
        response = self.client.post('/materials/supplier/', bad_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_material_supplier_succesful(self):
        self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        response = self.client.get('/materials/supplier/', **self.headers)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['name'], self.supplier_data['name'])


    def test_get_material_supplier_unauthorized(self):
        self.client.post('/materials/supplier/', self.supplier_data, format='json', **self.headers)
        response = self.client.get('/materials/supplier/', **self.headers_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Unauthorized access")