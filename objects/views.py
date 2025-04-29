from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import get_data, get_data_by_id, create_data, update_data, delete_data


class ObjectsView(APIView):
    def get(self, request, id=None):
        if id is None:
            data = get_data()
            return Response(data)
        else :
            data = get_data_by_id(id)
            if data :
                return Response(data)
            return Response({"error": "Data not found"},status=status.HTTP_404_NOT_FOUND)
        

    def post(self, request):
        data = request.data
        new_id = create_data(data)
        return Response({"id":new_id}, status=status.HTTP_201_CREATED)


    def put(self, request, id):
        data = request.data
        if update_data(id, data):
            return Response({"message":"Data Updated successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def patch(self,request, id):
        data = request.data
        if id in get_data():
            get_data()[id].update(data)
            return Response({"message": "Data patched successfully"})
        return Response({"error": "Data not Found"},status=status.HTTP_404_NOT_FOUND)
    

    def delete(self, request, id):
        if delete_data(id):
            return Response({"message": "Data deleted successfully"})
        return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)