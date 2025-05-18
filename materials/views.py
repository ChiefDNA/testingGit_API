from .serializers import MaterialSerializer, MaterialUsageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Material, MaterialUsage
from rest_framework.views import APIView
from accounts.jwt_auth import decode_jwt
from accounts.models import Accounts
from rest_framework import status


def is_authorized(request):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return None
    
    user = decode_jwt(token.split(' ')[1])
    if user and user.role in ['admin', 'foreman']:
        return user
    
    return None



class MaterialView(APIView):


    def get(self, request):

        Materials = Material.objects.all()
        serializer = MaterialSerializer(Materials,many=True)
        return Response(serializer.data)
    

    def post(self, request):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['added_by'] = user.id

        serializer = MaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'saved'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MaterialDetailView(APIView):


    def patch(self, request, id):
        
        user = is_authorized(request)
        if not user:
            return Response({'error':'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({'error':'Unaothorized access'},status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({'error':'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MaterialUsageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Material log saved'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)