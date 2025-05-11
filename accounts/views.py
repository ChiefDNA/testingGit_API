from django.contrib.auth.hashers import check_password
from .serializers import  AccountsSerializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Accounts
import re

Email_RegEx = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
Phone_RegEx = re.compile(r"^[0-9]{7,15}$")
User_RegEx = re.compile(r"^[a-zA-Z0-9]{6,14}$")
Address_RegEx = re.compile(r"^[a-zA-Z0-9,.\-@+/ ]+$")
Password_RegEx = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[ @.!#$%&*])[a-zA-Z0-9 @.!#$%&*]{8,}$")


class AccountsView(APIView):
    def post(self, request):
        data = request.data
        valid, error = validate_input(data)

        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        serializers = AccountsSerializers(data=data)

        if serializers.is_valid():
            serializers.save()
            return Response({'message':'successful'},status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    

    def get(self, request, id=None):
        if id is None:
            users = Accounts.objects.values('id','username','contact','address','dateOfBirth','password')
            return Response(users)
        else:
            users = Accounts.objects.filter(id=id).values('id','username','address','contact','dateOfBirth','password')
            return Response(users)
        

    def put(self, request, id):
        data = request.data
        valid, error = validate_input(data)

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Accounts.objects.get(id=id)
        except Accounts.DoesNotExist:
            return Response({'message':'Id not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = AccountsSerializers(account, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message':"Information replaced successfully"},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'please provide all Fields'},status=status.HTTP_206_PARTIAL_CONTENT)
        

    def patch(self,request, id):
        data = request.data 
        valid, error = validate_input(data)

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Accounts.objects.get(id=id)
        except Accounts.DoesNotExist:
            return Response({'message':"Id not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializers = AccountsSerializers(account, data=data, partial=True)

        if serializers.is_valid():
            serializers.save()
            return Response({'message':'Information has been modified succesfully'},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':'Please provide atleast one Field to be modified'},status=status.HTTP_204_NO_CONTENT)
        

    def delete(self, request , id):
        accounts = Accounts.objects.filter(id=id)
        if accounts:
            accounts.delete()
            return Response({'message':'acount details deleted successfuly'},status=status.HTTP_410_GONE)
        return Response({'message':'Account does not exist'},status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request):
        data = request.data

        if 'password' in data:
            password = data['password']
        else:
            return Response({'error':"Password is required"},status=status.HTTP_401_UNAUTHORIZED)

        if 'username' in data :
            account = Accounts.objects.filter(username=data['username']).first()
            error = "invalid username or password"

        if 'contact' in data:
            account = Accounts.objects.filter(contact=data['contact']).first()
            error = "invalid contact or password"

        user = check_password(password, account.password)

        if user:
            return Response({'userId':account.id,'username':account.username}, status=status.HTTP_200_OK)
        else:
            return Response({'error':error},status=status.HTTP_401_UNAUTHORIZED)
        

def validate_input(data):     
    if 'password' in data and not Password_RegEx.match(data['password']):
        return False, {'error':'Password must include atleast, one uppercase, lowercase, number, and special chracters and atleast 8 characters long'}

    if 'contact' in data and not (Email_RegEx.match(data['contact']) or Phone_RegEx.match(data['contact'])):
        return False, {'error':'Invalid contact format. Must be an email or phone number(7-15 characters)'}
    
    if 'address' in data and not Address_RegEx.fullmatch(data['address']):
        return False, {'error':'Address field contains unKnown characters'}
    
    if 'username' in data and not User_RegEx.fullmatch(data['username']):
        return False, {'error':'Invalid username characters found'}

    return True, None