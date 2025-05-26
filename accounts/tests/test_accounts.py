from rest_framework import status
from django.contrib.auth.hashers import check_password
from accounts.models import Accounts
from .test_Data import SetUpTestData
from accounts.jwt_auth import decode_jwt
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


    def test_registrartion_with_existing_contact(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.post(self.registration_url, self.data_1_put, format='json')
        #should return 400 bad request for duplicate
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_reistration_with_missing_fields(self):
        
        response = self.client.post(self.registration_url, self.data_1_patch , format='json')
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
        user = response.data 
        self.assertTrue(len(user)==1)
        self.assertEqual(user[0]['username'], self.data_2_post['username'])


    def test_patching(self):
        
        self.client.post(self.registration_url, self.data_1_post, format='json')
        response = self.client.patch(self.registration_url+'1/',self.data_1_patch, format='json' )#content_type='application/json'
        self.assertEqual(response.data['message'],'Information has been modified succesfully')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user = Accounts.objects.get(contact="newuser@example.com") #never changed
        self.assertNotEqual(self.data_1_post['username'],user.username)
        self.assertEqual(self.data_1_patch['username'], user.username)
        

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

