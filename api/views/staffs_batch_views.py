import json
import os

from django.conf import settings

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
        queryset = self.filter_queryset(self.model_class.objects.all())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        processing_serializer = ProcessingStaffSerializer(ProcessingStaff.objects.all(), many=True)
        prize_serializer = PrizeSerializer(Prize.objects.all(), many=True)
        backup = {'staff': serializer.data,
                  'processing': processing_serializer.data,
                  'prize': prize_serializer.data}
        request_api.save_backup(json.dumps(backup))

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
            return Response(serializer.data, status=status.HTTP_200_OK)
        # 移出单个员工
        if 'staff_id' in request.data:
            data = self.model_class.objects.get(staff_id=request.data['staff_id'])
            self.perform_destroy(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # 批量添加员工
        if 'staff_file' in request.data:
            staffs = handle_upload_file(request.FILES.get('staff_file', None))
            staffs_data = []
            for staff in staffs:
                staff_detail = staff.split(',')
                is_bse = len(staff_detail) == 3
                data = {'staff_id': staff_detail[0], 'name': staff_detail[1],
                        'is_bse': is_bse}
                staffs_data += [data, ]
            if staffs_data is None:
                return Response({'error': 'batch file not found'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(self.model_class.objects.all(), data=staffs_data, many=True)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except ValidationError as exc:
                request_api.log(exc)

        # 恢复备份
        if 'backup_file' in request.data:
            backup_dict = get_backup(request.data['backup_file'])
            if backup_dict is None:
                return Response({'error': 'backup file not found'}, status=status.HTTP_400_BAD_REQUEST)
            # 恢复员工
            serializer = self.get_serializer(self.model_class.objects.all(), data=backup_dict['staff'], many=True)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except ValidationError as exc:
                request_api.log(exc)
            # 恢复参与员工
            serializer = ProcessingStaffSerializer(ProcessingStaff.objects.all(), data=backup_dict['processing'],
                                                   many=True)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except ValidationError as exc:
                request_api.log(exc)
            # 恢复奖品
            serializer = PrizeSerializer(Prize.objects.all(), data=backup_dict['prize'], many=True)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except ValidationError as exc:
                request_api.log(exc)
        return Response(serializer.data, status=status.HTTP_200_OK)


def handle_upload_file(uploaded_file):
    if "staff" not in uploaded_file.name:
        return None
    for chunk in uploaded_file.chunks():
        staff_str = chunk.decode("utf-8")
        return staff_str.split('\n')


def get_backup(backup_file_type):
    backup_path = os.path.join(settings.BASE_DIR, 'cache/backup/')

    try:
        # 读取文件
        file_paths = request_api.list_dirs(backup_path)
        file_paths.sort()
        if backup_file_type == 'earliest':
            backup_path = file_paths[0]
        elif backup_file_type == 'earlier' and len(file_paths) > 2:
            backup_path = file_paths[1]
        elif backup_file_type == 'recent':
            backup_path = file_paths[-1]
        with open(backup_path, 'r', encoding='utf-8', errors='ignore') as fp:
            backup_str = fp.read()
    except FileNotFoundError as e:
        request_api.log(e)
        return None
    except IsADirectoryError as e:
        request_api.log(e)
        return None
    return json.loads(backup_str)
