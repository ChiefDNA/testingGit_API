from django.contrib.auth.hashers import check_password
from .jwt_auth import generate_jwt, decode_jwt
from django.shortcuts import render, redirect
from rest_framework.response import Response
from .serializers import AccountsSerializer
from rest_framework.views import APIView
from .validations import validate_input
from companies.models import Company
from rest_framework import status
from django.views import View
from .models import Accounts
from django.apps import apps
import importlib



class AccountsView(APIView):
    def post(self, request):
        data = request.data

        if Accounts.objects.filter(contact=data['contact']).exists():
            return Response({"error":"A user with this contact already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Accounts.objects.filter(username=data['username']).exists():
            return Response({"error":"A user with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        valid, error = validate_input(data)
        if not valid :
            return Response(error,status=status.HTTP_400_BAD_REQUEST)
        
        company = Company.objects.get(id=data['company'])
        serializers = AccountsSerializer(data=data)


        if serializers.is_valid():
            serializers.save(company=company)
            return Response({'message':'Information placed succesfully'},status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, id=None):
        if id is None:
            users = Accounts.objects.values('id','username','contact','address','dateOfBirth', 'company','role')
            return Response(users)
        else:
            users = Accounts.objects.filter(id=id).values('id','username','address','contact', 'company', 'role','dateOfBirth')
            return Response(users)
        

    def put(self, request, id):
        # adding token authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error' : 'Authorization token missing'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        user = decode_jwt(token)
        if not user:
            return Response({'error' : 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        valid, error = validate_input(data)

        if not valid:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Accounts.objects.get(id=id)
        except Accounts.DoesNotExist:
            return Response({'error':'Id not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = AccountsSerializer(account, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message':"Information has been replaced successfully"},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error':'please provide all Fields'},status=status.HTTP_400_BAD_REQUEST)
        

    def patch(self,request, id):
        data = request.data 
        valid, error = validate_input(data)

        if not valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Accounts.objects.get(id=id)
        except Accounts.DoesNotExist:
            return Response({'error':"Id not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializers = AccountsSerializer(account, data=data, partial=True)

        if serializers.is_valid():
            serializers.save()
            return Response({'message':'Information has been modified succesfully'},status=status.HTTP_202_ACCEPTED)
        else:
            return Response( serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request , id):
        accounts = Accounts.objects.filter(id=id)
        if accounts:
            accounts.delete()
            return Response({'message':'Account details deleted successfuly'},status=status.HTTP_204_NO_CONTENT)
        return Response({'error':'Account does not exist'},status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request):
        data = request.data
        
        if 'password' in data:
            password = data['password']
        else:
            return Response({'error':"Password is required"},status=status.HTTP_400_BAD_REQUEST)

        if 'username' in data :
            account = Accounts.objects.filter(username=data['username']).first()
            error = "invalid username or password"

        if 'contact' in data:
            account = Accounts.objects.filter(contact=data['contact']).first()
            error = "invalid contact or password"

        try:
            user = check_password(password, account.password)
        except:
            user = None

        if user:
            token = generate_jwt(account)
            return Response({'token' : token,
                             'userId' : account.id,
                             'role' : account.role,
                             'username' : account.username,
                             'company' : account.company.id
                             }, status=status.HTTP_200_OK)
        else:
            return Response({'error':error},status=status.HTTP_401_UNAUTHORIZED)
        

class CrudDashBoardView(APIView):
    def get(self, request, path=None):
        user = hass_access(request)
        if not user:
            return Response({'error':'You are not authorized to access this site'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = path.strip('/').split('/') if path else []

        if len(parts) == 2:
            # List all records
            activeModel, activeSerializer = get_model(parts)
            records = activeModel.objects.filter(**access_levels(parts, user))

            serializer = activeSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif len(parts) == 3:
            # Single record
            activeModel, activeSerializer = get_model(parts)
            try:
                record = activeModel.objects.get(pk=parts[2], **access_levels(parts, user))
            except activeModel.DoesNotExist:
                return Response({'error': 'Record does not exist'}, status=status.HTTP_404_NOT_FOUND)

            serializer = activeSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, path=None):
        # update
        user = hass_access(request)
        if not user:
            return Response({'error':'Your Are not authorized to acesse this site'},status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data 
        valid, error = validate_input(data)

        if not valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        parts = path.strip('/').split('/') if path else []

        if len(parts) == 3:
            activeModel, activeSerializer = get_model(parts)
            records = activeModel.objects.filter(**access_levels(parts, user))
            
            if records:
                serializer = activeSerializer(records, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message':'Information has been modified succesfully'},status=status.HTTP_202_ACCEPTED)
                else:
                    return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'error':'Recoerd does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error':'Bad request'},status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, path=None):
        # create
        user = hass_access(request)
        if not user:
            return Response({'error':'Your Are not authorized to acesse this site'},status=status.HTTP_401_UNAUTHORIZED)
        
        data = request.data 
        valid, error = validate_input(data)

        if not valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        parts = path.strip('/').split('/') if path else []

        if len(parts) == 2:
            activeModel, activeSerializer = get_model(parts)

            serializer = activeSerializer(data=data)
            company_id = user.company
            if user.role in ['superuser','manager']:
                company_id= data.company
                if serializer.is_valid() and parts[1]=='Company':
                    serializer.save()
                    return Response({'message':'Information placed succesfully'},status=status.HTTP_201_CREATED)
                elif parts[1]=='Company':
                    return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            company = Company.objects.get(id=company_id)
            if serializer.is_valid():
                serializer.save(company=company)
                return Response({'message':'Information placed succesfully'},status=status.HTTP_201_CREATED)
            else:
                return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
            
        return Response({'error':'Bad request'},status=status.HTTP_400_BAD_REQUEST)

        
    def delete(self, request, path=None):
        # delete
        user = hass_access(request)
        if not user:
            return Response({'error':'Your Are not authorized to acesse this site'},status=status.HTTP_401_UNAUTHORIZED)
        
        parts = path.strip('/').split('/') if path else []

        if len(parts) == 3:
            activeModel, activeSerializer = get_model(parts)
            records = activeModel.objects.filter(**access_levels(parts, user))
            
            if records:
                records.delete()
                return Response({'message':'Record deleted successfuly'},status=status.HTTP_204_NO_CONTENT)
            
            return Response({'error':'Recoerd does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error':'Bad request'},status=status.HTTP_400_BAD_REQUEST)
        


def hass_access(request):
    authorization = request.headers.get('Authorization')
    print("stage 0 complete")
    if not authorization or not authorization.startswith('Bearer '):
        return None
    
    print("stage 1 complete role")
    token = authorization.split(' ')[1]
    user = decode_jwt(token)
    print(token)
    if user:
        print("User role:", user.role)

    if user and user.role in ['admin', 'foreman', 'manager', 'supervisor', 'subcontractor', 'superuser']:
        print("stage 2 complete")
        return user
    
    return None

def access_levels(parts, user):
    tableString = parts[1]
    levels = {
        'superuser':     ['superuser','admin','manager','supervisor','foreman','subcontractor','worker','client','guest'],
        'admin':         ['admin','manager','supervisor','foreman','subcontractor','worker','client','guest'],
        'manager':       ['manager','supervisor','foreman','subcontractor','worker','client','guest'],
        'supervisor':    ['supervisor','foreman','subcontractor','worker','client','guest'],
        'foreman':       ['foreman','subcontractor','worker','client','guest'],
        'subcontractor': ['subcontractor','worker','client','guest']
    }
    companies = {
        'superuser':     None,
        'admin':         None,
        'manager':       user.company,
        'supervisor':    user.company,
        'foreman':       user.company,
        'subcontractor': user.company
    }

    # Helper to decide if role has unlimited access
    def has_unlimited_access(role):
        return role in ['superuser', 'admin']

    if len(parts) == 3:
        id = parts[2]
        if has_unlimited_access(user.role):
            # Superuser/Admin: no company filtering
            if tableString == 'Accounts':
                return {
                    'id': id,
                    'role__in': levels.get(user.role, [])
                }
            elif tableString == 'Company':
                return {'id': id}
            else:
                return {'id': id}
        else:
            # Limited access roles
            match tableString:
                case 'Accounts':
                    return {
                        'company': companies.get(user.role),
                        'id': id,
                        'role__in': levels.get(user.role, [])
                    }
                case 'Company':
                    return {
                        'id': user.company
                    }
                case _:
                    return {
                        'company': user.company
                    }

    elif len(parts) == 2:
        if has_unlimited_access(user.role):
            # No company filtering for superuser/admin on list views
            if tableString == 'Accounts':
                return {
                    'role__in': levels.get(user.role, [])
                }
            elif tableString == 'Company':
                return {}
            else:
                return {}
        else:
            # Limited access
            match tableString:
                case 'Accounts':
                    return {
                        'company': companies.get(user.role),
                        'role__in': levels.get(user.role, [])
                    }
                case 'Company':
                    return {
                        'id': companies.get(user.role)
                    }
                case _:
                    return {
                        'company': companies.get(user.role)
                    }

            
def get_model(parts):
    app_Label, model_Name = parts[0], parts[1]
    # import serializer module
    serializer_module = importlib.import_module(f"{parts[0]}.serializers")
    # Build serializer clss name
    serializer_class = getattr(serializer_module, f"{parts[1]}Serializer")

    return apps.get_model(app_Label, model_Name), serializer_class

class DashboardView(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/?next=/dashboard/')  # Force login

        user = Accounts.objects.get(id=user_id)
        if user.role not in ['admin', 'superuser']:
            return render(request, 'login.html', {'error': 'Unauthorized access'})

        token = generate_jwt(user)
        tables_by_app = {}
        for model in apps.get_models():
            app_label = model._meta.app_label
            if app_label in ['accounts', 'materials', 'companies']:
                if app_label not in tables_by_app:
                    tables_by_app[app_label] = []
                tables_by_app[app_label].append({
                    'model_name': model.__name__ ,   # model.meta.model_name 
                    'verbose_name': model._meta.verbose_name.title()
                })

        return render(request, 'dashboard.html', {
            'tables': tables_by_app,
            'user': user,
            'token': token
        })


def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            request.session['user_id'] = user.id
            # Respect the ?next= param, or fallback to /dashboard/
            next_url = request.GET.get('next') or '/dashboard/'
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def authenticate(username, password):
    account = Accounts.objects.filter(username=username).first()

    if account and check_password(password, account.password):
        if account.role in ['admin', 'superuser']:
            # Tell Django which backend is being used
            account.backend = 'django.contrib.auth.backends.ModelBackend'
            return account
    
    return None
