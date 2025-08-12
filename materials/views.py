from .serializers import MaterialSerializer, MaterialUsageSerializer, MaterialTypeSerializer, SupplierSerializer
from .models import Material, MaterialUsage, MaterialType, Supplier
from rest_framework.permissions import IsAuthenticated
from accounts.validations import validate_input
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.jwt_auth import decode_jwt
from accounts.models import Accounts
from companies.models import Company
from rest_framework import status



def is_authorized(request):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return None
    
    user = decode_jwt(token.split(' ')[1])
    if user and user.role in ['superuser','admin','manager','supervisor','foreman','subcontractor']:
        return user
    
    return None


class MaterialView(APIView):


    def get(self, request):

        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
        print(user.company)     
        Materials = Material.objects.filter(company=user.company)
        #cleaning response
        serializer = MaterialSerializer(Materials,many=True)
        for material in serializer.data:
            material['type'] = MaterialType.objects.get(id=material['type']).name
            material['supplier'] = Supplier.objects.get(id=material['supplier']).name
            material['added_by'] = Accounts.objects.get(id=material['added_by']).username 
            material['company'] = Company.objects.get(id=material['company']).name

        return Response(serializer.data)
    

    def post(self, request):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        supplier = Supplier.objects.get(id=data['supplier'])
        type = MaterialType.objects.get(id=data['type'])
        if user.role == 'superuser':
            company = Company.objects.get(id=request.data["company"])
        else :
            company = Company.objects.get(id=user.company)
        serializer = MaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save(added_by=user,supplier=supplier,type=type,company=company)
            return Response({'message':'Saved'}, status=status.HTTP_201_CREATED)
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
            material = Material.objects.get(id=id, company=user.company)
        except Material.DoesNotExist:
            return Response({'error':'Material not found'}, status.HTTP_404_NOT_FOUND)
        
        company = Company.objects.get(id=user.company)
        serializer =MaterialSerializer(material, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response({'message':'Changes saved'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request,id):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            material = Material.objects.get(id=id,company=user.company)
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
        
        company = Company.objects.get(id=user.company)
        serializer = MaterialUsageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response({'message':'Material log saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
        usage = MaterialUsage.objects.filter(company=user.company)
        serializer = MaterialUsageSerializer(usage,many=True)
        return Response(serializer.data)
    


class MaterialTypeView(APIView):

    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        if user.role == 'superuser':
            company = Company.objects.get(id=request.data["company"])
        else :
            company = Company.objects.get(id=user.company)

        serializer = MaterialTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response({'message':'Material saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
        type = MaterialType.objects.filter(company=user.company)
        serializer = MaterialTypeSerializer(type, many=True)
        return Response(serializer.data)
     
    


class SupplierView(APIView):

    def post(self, request):
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
                
        valid, error = validate_input(request.data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        if user.role == 'superuser':
            company = Company.objects.get(id=request.data["company"])
        else :
            company = Company.objects.get(id=user.company)

        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response({'message':'Supplier saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
    def get(self, request):
        user = is_authorized(request)
        print(request.headers.get('Autorization'))
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

        supplier = Supplier.objects.filter(company=user.company)
        serializer = SupplierSerializer(supplier, many=True)
        return Response(serializer.data)