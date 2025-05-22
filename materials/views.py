from .serializers import MaterialSerializer, MaterialUsageSerializer, MaterialTypeSerializer, SupplierSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Material, MaterialUsage
from rest_framework.views import APIView
from accounts.jwt_auth import decode_jwt
from accounts.models import Accounts
from rest_framework import status
import re


Name_RegEx = re.compile(r"^[a-zA-Z0-9.', ]{2,}$")
Contact_RegEx = re.compile(r"^[a-zA-Z0-9,.\@+/ \-]+$")
NumberType_RegEx = re.compile(r"^[0-9]+(\.[0-9]+)?$")
number_fields = ['supplier', 'total_quantity', 'unit_cost', 'quantity_used', 'material', 'type', 'added_by']


def is_authorized(request):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return None
    
    user = decode_jwt(token.split(' ')[1])
    if user and user.role in ['admin', 'foreman']:
        return user
    
    return None


def validate_input(data):     



    # if 'material' in data and not Name_RegEx.fullmatch(data['material']):
    #     return False, {'error':'Expecting specific material name used without special characters'}

    if 'contact_info' in data and not Contact_RegEx.fullmatch(data['contact_info']):
        return False, {'error':'Expecting supplier address or contact or email'}
    

    for field in number_fields:
        if field in data and not NumberType_RegEx.fullmatch(str(data[field])):
            return False, {'error': f"Expecting numeric value for '{field}'"}

    
    if 'name' in data and not Name_RegEx.fullmatch(data['name']):
        return False, {'error':'Invalid characters found while expecting full-names'}

    return True, None



class MaterialView(APIView):


    def get(self, request):

        Materials = Material.objects.all()
        #cleaning response
        #for material in 

        serializer = MaterialSerializer(Materials,many=True)
        return Response(serializer.data)
    

    def post(self, request):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()

        serializer = MaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save(added_by=user)
            return Response({'message':'saved'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MaterialDetailView(APIView):


    def patch(self, request, id):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        try:
            material = Material.objects.get(id=id)
        except Material.DoesNotExist:
            return Response({'error':'Material not found'}, status.HTTP_404_NOT_FOUND)
        
        serializer =MaterialSerializer(material, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Changes saved'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request,id):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unaothorized access'},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            material = Material.objects.get(id=id)
            material.delete()
            return Response({'message':'Record deleted'},status=status.HTTP_204_NO_CONTENT)
        except Material.DoesNotExist:
            return Response({'error':'Material not found'}, status=status.HTTP_404_NOT_FOUND)
        


class MaterialUsageView(APIView):

    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MaterialUsageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Material log saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MaterialTypeView(APIView):

    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MaterialTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Material saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class SupplierView(APIView):

    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Supplier saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)