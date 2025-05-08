from rest_framework import viewsets, status
from .models import Accounts
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AccountsSerializers
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token


class AccountsView(APIView):
    def post(self, request):
        data = request.data
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


# class LoginViews(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         user = authenticate(username=username,password=password)

#         if user is not None:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({'token':token.key,
#                              'user_id':user.id,
#                              'username':user.username
#                              },
#                              status=status.HTTP_200_OK)
#         else: 
#             return Response({'error':'invalid username or password'},status= status.HTTP_401_UNAUTHORIZED)