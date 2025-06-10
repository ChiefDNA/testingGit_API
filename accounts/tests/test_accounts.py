from rest_framework import status
from django.contrib.auth.hashers import check_password
from accounts.models import Accounts
from .test_Data import SetUpTestData
from accounts.jwt_auth import decode_jwt, generate_jwt
import json

# Create your tests here.

class AccountsViewTests(SetUpTestData):

    def test_succesful_registration(self):
        
        response = self.client.post(self.registration_url,data=self.data_1_post, format='json')
        # checking response 201 create
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check if user is created
        self.assertEqual(Accounts.objects.count(), 1)
        user = Accounts.objects.get(username="newuser")
        # check if password is hasshed
        self.assertNotEqual(user.password, "StrongPass1!")
        self.assertTrue(check_password("StrongPass1!", user.password))
        self.assertEqual(response.data['message'],"Information placed succesfully")


    def test_registration_with_existing_contact(self):
        good_data =  self.data_1_post.copy()
        self.client.post(self.registration_url, good_data, format='json')
        response = self.client.post(self.registration_url, self.data_1_put, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'A user with this contact already exists.')

    
    def test_registrartion_with_existing_username(self):
        good_data =  self.data_1_post.copy()
        self.client.post(self.registration_url, good_data, format='json')
        good_data['contact'] = '072034058'
        response = self.client.post(self.registration_url, good_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'A user with this username already exists.')

    
    def test_registrartion_with_invalid_password(self):
        bad_data =  self.data_1_post.copy()
        bad_data['password'] = 'daniels'
        response = self.client.post(self.registration_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must include atleast, one uppercase, lowercase, number, and special chracters and atleast 8 characters long')


    def test_reistration_with_missing_fields(self):  
        response = self.client.post(self.registration_url, self.data_1_patch , format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_reistration_under_age(self):
        under_age = self.data_2_post.copy()
        under_age['dateOfBirth'] = '2020-10-20'  
        response = self.client.post(self.registration_url, under_age, format='json')
        self.assertEqual(response.data['error'], 'User must be at least 18 years old to register')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            

    def test_reistration_with_invalid_dateofbirth_format(self):
        under_age = self.data_2_post.copy()
        under_age['dateOfBirth'] = '10.2009.20'  
        response = self.client.post(self.registration_url, under_age, format='json')
        self.assertEqual(response.data['error'], 'Invalid date format. Use YYYY-MM-DD')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_data_retrieval(self):

        response = self.client.post(self.registration_url,data=self.data_1_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.registration_url,data=self.data_2_post, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check if users are created
        self.assertEqual(Accounts.objects.count(), 2)
        # testing the get 
        response = self.client.get(self.registration_url)
        users = response.data
        self.assertEqual(users[1]['username'], self.data_2_post['username'])
        self.assertTrue(len(users),2)


    def test_data_retrieval_with_id(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        self.client.post(self.registration_url, self.data_2_post, format='json')
        #get user infor by id
        response = self.client.get(self.registration_url+'2/')
        user = Accounts.objects.get(id=2) 
        self.assertTrue(len(response.data)==1)
        self.assertEqual(str(user), self.data_2_post['username'])


    def test_patching_succesful(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.patch(self.registration_url+'1/',self.data_1_patch, format='json' )#content_type='application/json'
        self.assertEqual(response.data['message'],'Information has been modified succesfully')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user = Accounts.objects.get(contact="newuser@example.com") #never changed
        self.assertNotEqual(self.data_1_post['username'],user.username)
        self.assertEqual(self.data_1_patch['username'], user.username)

    
    def test_patching_invalid_address(self):
        self.client.post(self.registration_url, self.data_1_post, format='json')
        bad_data = self.data_1_patch.copy()
        bad_data['address'] = 'at *dnaiels(3)'
        response = self.client.patch(self.registration_url+'1/', bad_data, format='json' )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = Accounts.objects.get(contact="newuser@example.com") #never changed
        self.assertEqual(self.data_1_post['username'],user.username)
        self.assertNotEqual(self.data_1_patch['username'], user.username)

    
    def test_patching_no_user(self):
        response = self.client.patch(self.registration_url+'1/',self.data_1_patch, format='json' )#content_type='application/json'
        self.assertEqual(response.data['error'],'Id not found')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_patching_with_unique_existing_fields(self):
        self.client.post(self.registration_url, self.data_1_post, format='json')
        self.client.post(self.registration_url, self.data_2_post, format='json')
        bad_data = self.data_1_patch.copy()
        bad_data['username'] = 'newuser2'
        response = self.client.patch(self.registration_url+'1/', bad_data, format='json' )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_delete_succesful(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.delete(self.registration_url+'1/', format='json' )#content_type='application/json'
        self.assertEqual(response.data['message'],'Account details deleted successfuly')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_delete_non_existing_user(self):
        response = self.client.delete(self.registration_url+'1/', format='json' )#content_type='application/json'
        self.assertEqual(response.data['error'],'Account does not exist')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_relacing_put_with_token(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.put(self.registration_url+'1/',self.data_1_put, format='json')#content_type='application/json'
        self.assertEqual(response.data['message'],'Information has been replaced successfully')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user = Accounts.objects.get(contact="newuser@example.com") #never changed
        self.assertNotEqual(self.data_1_post['username'],user.username)
        self.assertEqual(self.data_1_put['username'], user.username)
        
    
    def test_relacing_put_with_invalid_contact_type(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        bad_put_data = self.data_1_put.copy()
        bad_put_data['contact'] = 'danjon'
        response = self.client.put(self.registration_url+'1/', bad_put_data, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'Invalid contact format. Must be an email or phone number(7-15 characters)')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_relacing_put_with_invalid_username_type(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        bad_put_data = self.data_1_put.copy()
        bad_put_data['username'] = 'Typica@bad!!##name'
        response = self.client.put(self.registration_url+'1/', bad_put_data, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'Invalid username characters found')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_relacing_put_with_nonexisting_user(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.put(self.registration_url+'4/', self.data_1_put, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'Id not found')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    
    def test_relacing_put_with_partial_data(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
        response = self.client.put(self.registration_url+'1/', self.data_1_patch, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'please provide all Fields')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_relacing_put_with_wrong_authentication(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Danies '+token)
        response = self.client.put(self.registration_url+'1/',self.data_1_put, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'Authorization token missing')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_relacing_put_with_unathorized_user(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        wrong_user = Accounts.objects.create(
            username="unauthorized_user",
            contact="unauth@example.com",
            password="dummy",
            address="Unauthorized Zone",
            dateOfBirth="1995-01-01",
            role="worker"
        )
        token = generate_jwt(wrong_user)
        Accounts.objects.filter(username="unauthorized_user").delete()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.put(self.registration_url+'1/',self.data_1_put, format='json')#content_type='application/json'
        self.assertEqual(response.data['error'],'Invalid or expired token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class LoginTests(SetUpTestData):

    def test_login_with_username(self):

        self.client.post(self.registration_url, self.data_2_post, format='json')
        response = self.client.post(self.login_url, self.data_login_username, format='json')
        #check username and id returned
        self.assertEqual(response.data['username'],self.data_2_post['username'])
        #test jwt token
        token = decode_jwt(response.data['token'])
        self.assertTrue(token.username==self.data_login_username['username'])
        self.assertEqual(token.id, response.data['userId'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_with_contact(self):

        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.login_url, self.data_login_contact, format='json')
        #check username and returned
        self.assertEqual(response.data['username'],self.data_1_post['username'])
        #test jwt token
        token = decode_jwt(response.data['token'])
        self.assertEqual(token.id, response.data['userId'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_without_password(self):

        self.client.post(self.registration_url, self.data_1_post, format='json')
        single_data = {'contact':self.data_login_contact['contact']}
        response = self.client.post(self.login_url, single_data, format='json')
        self.assertEqual(response.data['error'], 'Password is required')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_login_with_wrong_credentials(self):

        self.client.post(self.registration_url, self.data_1_post, format='json')
        bad_credentials = self.data_login_contact.copy()
        bad_credentials['contact'] = 'daniels2'
        response = self.client.post(self.login_url, bad_credentials, format='json')
        self.assertEqual(response.data['error'], 'invalid contact or password')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
