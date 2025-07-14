from .serializers import CompanySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Company


class CompanyView(APIView):
    def post(self, request):
        data = request.data

        serializer = CompanySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Company created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        data = request.data 
        
        try:
            company = Company.objects.get(id=id)
        except Company.DoesNotExist:
            return Response({'error':"Id not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializers = CompanySerializer(company, data=data, partial=True)

        if serializers.is_valid():
            serializers.save()
            return Response({'message':'Information has been modified succesfully'},status=status.HTTP_202_ACCEPTED)
        else:
            return Response( serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        
