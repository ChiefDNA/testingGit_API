from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

class SetUpTestData(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/accounts/user/'
        self.login_url = '/accounts/login/'
        self.data_1_post = {
            "username": "newuser",
            "contact": "newuser@example.com",
            "password": "StrongPass1!",
            "address": "456 Test Ave",
            "dateOfBirth": "1990-01-01"
        }
        self.data_1_put = {
            "username": "Replacer",
            "contact": "newuser@example.com", #same contact
            "password": "StrongPass12!",
            "address": "456 Tests Avenue",
            "dateOfBirth": "1990-01-02"
        }
        self.data_1_patch = {
            "username": "JohnDeo",
            "contact": "newuser@example.com", #same contact
            "address": "456 Tests Avenue"
        }
        self.data_1_empty = {
            "username": "",
            "contact": "",
            "password": "",
            "address": "",
            "dateOfBirth": ""
        }
        self.data_2_post = {
            "username": "newuser2",
            "contact": "newuser2@example.com",
            "password": "StrongPass2!",
            "address": "465 Test Market",
            "dateOfBirth": "1990-03-20"
            }
        self.data_2_put = {
            "username": "DeoJohn",
            "contact": "newuser2@example.com", # same contact 2
            "password": "StrongPass21!",
            "address": "465 Test Market St",
            "dateOfBirth": "1990-03-22"
            }
        self.data_2_patch = {
            "username": "DeoJohn",
            "contact": "newuser2@example.com", # same contact 2
            "address": "465 Test Market St"
            }
        self.data_login_contact = {
            "contact": "newuser@example.com",
            "password": "StrongPass1!"
        }
        self.data_login_username = {
            "username": "newuser2",
            "password": "StrongPass2!"  
        }