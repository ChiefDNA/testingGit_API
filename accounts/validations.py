from datetime import date
import re


Name_RegEx = re.compile(r"^[a-zA-Z0-9.', ]{2,}$")
Contact_RegEx = re.compile(r"^[a-zA-Z0-9,.\@+/ \-]+$")
NumberType_RegEx = re.compile(r"^[0-9-]+(\.[0-9]+)?$")
number_fields = ['supplier', 'total_quantity', 'unit_cost', 'quantity_used', 'material', 'type', 'added_by']
Email_RegEx = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
Phone_RegEx = re.compile(r"^[0-9]{7,15}$")
User_RegEx = re.compile(r"^[a-zA-Z0-9]{6,14}$")
Address_RegEx = re.compile(r"^[a-zA-Z0-9,.\-@+/ ]+$")
Password_RegEx = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[ @.!#$%&*])[a-zA-Z0-9 @.!#$%&*]{8,}$")

def validate_input(data):     
    
    if 'password' in data and not Password_RegEx.match(data['password']):
        return False, {'error':'Password must include atleast, one uppercase, lowercase, number, and special chracters and atleast 8 characters long'}

    if 'contact' in data and not (Email_RegEx.match(data['contact']) or Phone_RegEx.match(data['contact'])):
        return False, {'error':'Invalid contact format. Must be an email or phone number(7-15 characters)'}
    
    if 'address' in data and not Address_RegEx.fullmatch(data['address']):
        return False, {'error':'Address field contains unKnown characters'}
    
    if 'username' in data and not User_RegEx.fullmatch(data['username']):
        return False, {'error':'Invalid username characters found'}
    
    if 'dateOfBirth' in data:
        dob = data['dateOfBirth']
        try:
            birth_date = date.fromisoformat(dob)
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                return False, {'error': 'User must be at least 18 years old to register'}
        except ValueError:
            return False, {'error': 'Invalid date format. Use YYYY-MM-DD'}

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
