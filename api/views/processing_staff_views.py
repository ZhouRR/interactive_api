from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from api.serializers import *

from api.utils import request_api


class ProcessingStaffViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = ProcessingStaff.objects.all()
    serializer_class = ProcessingStaffSerializer
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = None
        try:
            data = ProcessingStaff.objects.get(staff_id=request.data['staff_id'])
            if request_api.is_delete(request.data, 'name', 'open_id'):
                self.perform_destroy(data)
                return Response({request.data['staff_id']}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data)
        except ProcessingStaff.DoesNotExist as e:
            request_api.log('data DoesNotExist')
        except ProcessingStaff.MultipleObjectsReturned as e:
            request_api.log('data MultipleObjectsReturned')

        if serializer is None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        else:
            if 'name' in request.data:
                data.name = request.data['name']
            if 'open_id' in request.data:
                data.open_id = request.data['open_id']

            serializer = self.get_serializer(data, data=serializer.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
