from rest_framework.views import APIView
import hashlib
from rest_framework.response import Response
from rest_framework import status
from .models import get_data, get_data_by_id, create_data, update_data, delete_data


ALLOWED_FIELDS = {'username','contact','address','dateOfBirth','password'} 
REQUIRED_FIELDS = {'username','contact','address','dateOfBirth','password'}


class ObjectsView(APIView):
    def get(self, request, id=None):
        if id is None:
            data = get_data()
            sanitized = {k: sanitize_return(v) for k, v in data.items()}
            return Response(sanitized)
        else :
            data = get_data_by_id(id)
            if data :
                return Response(sanitize_return(data))
            return Response({"error": "Data not found"},status=status.HTTP_404_NOT_FOUND)
        

    def post(self, request):
        data = request.data
        data["password"] = hash_password(data["password"])
        valid, error = validate_input(data)

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        new_id = create_data(data)
        return Response({"id":new_id}, status=status.HTTP_201_CREATED)


    def put(self, request, id):
        data = request.data
        data["password"] = hash_password(data["password"])
        valid, error = validate_input(data)

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        if update_data(id, data):
            return Response({"message":"Data Updated successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def patch(self,request, id):
        data = request.data
        if "password" in data:
            data["password"] = hash_password(data["password"])
        valid, error = validate_input(data, partial=True)

        if not valid:
            return Response(error,  status=status.HTTP_400_BAD_REQUEST)
        
        if id in get_data():
            get_data()[id].update(data)
            return Response({"message": "Data patched successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def delete(self, request, id):
        if delete_data(id):
            return Response({"message": "Data deleted successfully"})
        return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)
    


def validate_input(data, partial=False):
    data_keys = set(data.keys())
    unkown_fields = data_keys - ALLOWED_FIELDS

    if unkown_fields:
        return False, {'error': f"Unkown field(s):{', '.join(unkown_fields)}"}

    if not partial:
        missing_fields = REQUIRED_FIELDS - data_keys
        if missing_fields:
            return False, {'error': f"Missing recquired field(s): {', '.join(missing_fields)}"}
        
    return True, None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def sanitize_return(data):
    return {key: value for key, value in data.items() if key !="password"}