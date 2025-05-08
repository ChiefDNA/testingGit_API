from rest_framework.views import APIView
import hashlib, re
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from .models import get_data, get_data_by_id, create_data, update_data, delete_data


ALLOWED_FIELDS = {'username','contact','address','dateOfBirth','password'} 
REQUIRED_FIELDS = {'username','contact','address','dateOfBirth','password'}
Email_RegEx = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
Phone_RegEx = re.compile(r"^[0-9]{7,15}$")
User_RegEx = re.compile(r"^[a-zA-Z0-9]{6,14}$")
Address_RegEx = re.compile(r"^[a-zA-Z0-9,.\-@+/ ]+$")
Password_RegEx = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@.!#$%&*])[a-zA-Z0-9@.!#$%&*]{8,}$")
def date_check(string):
    try:
        datetime.strptime(string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


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
        valid, error = validate_input(data)
        
        if "password" in data:
            data["password"] = hash_password(data["password"])

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        new_id = create_data(data)
        return Response({"id":new_id}, status=status.HTTP_201_CREATED)


    def put(self, request, id):
        data = request.data
        valid, error = validate_input(data)

        if "password" in data:
            data["password"] = hash_password(data["password"])

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        if update_data(id, data):
            return Response({"message":"Data Updated successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def patch(self,request, id):
        data = request.data
        valid, error = validate_input(data, partial=True)

        if "password" in data:
            data["password"] = hash_password(data["password"])

        if not valid:
            return Response(error,  status=status.HTTP_400_BAD_REQUEST)
        
        if id in get_data():
            get_data()[id].update(data)
            return Response({"message": "Data patched successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def delete(self, request, id):
        if delete_data(id):
            return Response({"message": "Data deleted successfully"}, status=status.HTTP_204_NO_CONTENT )
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
        
    if 'password' in data and not Password_RegEx.match(data['password']):
        return False, {'error':'Password must include atleast, one uppercase, lowercase, number, and special chracters and atleast 8 characters long'}

    if 'contact' in data and not (Email_RegEx.match(data['contact']) or Phone_RegEx.match(data['contact'])):
        return False, {'error':'Invalid contact format. Must be an email or phone number(7-15 characters)'}
    
    if 'address' in data and not Address_RegEx.fullmatch(data['address']):
        return False, {'error':'Address field contains unKnown characters'}
    
    if 'username' in data and not User_RegEx.fullmatch(data['username']):
        return False, {'error':'Invalid username characters found'}
    
    if 'dateOfBirth' in data and not date_check(data['dateOfBirth']):
        return False, {'error':'Invalid date format'}

    return True, None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def sanitize_return(data):
    return {key: value for key, value in data.items() if key !="password"}