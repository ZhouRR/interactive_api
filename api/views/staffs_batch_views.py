from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api.serializers import *

from api.utils import request_api


class StaffBatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    primary_key = 'staff_id'
    queryset = Empty2.objects.all()
    model_class = Staff
    serializer_class = StaffSerializer
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
        queryset = self.model_class.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        data = None

        # 移出所有员工
        if 'staff_id' in request.data and request.data['staff_id'] == '-999999':
            self.perform_destroy(queryset)
            request_api.send_long_message({'activity': '001'})
            return Response(serializer.data, status=status.HTTP_200_OK)
        # 移出单个员工
        if 'staff_id' in request.data:
            data = self.model_class.objects.get(staff_id=request.data['staff_id'])
            self.perform_destroy(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # 批量添加员工
        if 'staff_file' in request.data:
            staffs = handle_upload_file(request.FILES.get('staff_file', None))

            for staff in staffs:
                staff_detail = staff.split(',')
                data = {'staff_id': staff_detail[0], 'name': staff_detail[1]}
                serializer = self.get_serializer(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                except ValidationError as exc:
                    request_api.log('ValidationError')
                    continue

        request_api.send_long_message({'activity': '001'})
        return Response(serializer.data, status=status.HTTP_200_OK)


def handle_upload_file(uploaded_file):
    if "staff" not in uploaded_file.name:
        return None
    for chunk in uploaded_file.chunks():
        staff_str = chunk.decode("utf-8")
        return staff_str.split('\n')