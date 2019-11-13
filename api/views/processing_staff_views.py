from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api.serializers import *

from api.utils import request_api


class ProcessingStaffViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    primary_key = 'staff_id'
    model_class = ProcessingStaff
    queryset = model_class.objects.all()
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
        data = None

        try:
            data = self.model_class.objects.get(staff_id=request.data[self.primary_key])
            # 移出指定员工
            if request_api.is_delete(request.data, self.serializer_class, self.primary_key):
                self.perform_destroy(data)
                request_api.send_long_message({'activity': '001'})
                return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data)
        except self.model_class.DoesNotExist as e:
            request_api.log('data DoesNotExist')
            # 清空所有员工
            if 'staff_id' in request.data and request.data['staff_id'] == '-999999':
                self.perform_destroy(self.get_queryset())
                request_api.send_long_message({'activity': '001'})
                return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
            # 添加所有员工
            if 'staff_id' in request.data and\
                    (request.data['staff_id'] == '999999' or request.data['staff_id'] == '999998'):
                staffs = Staff.objects.all()
                staffs_serializer = StaffSerializer(staffs, many=True)
                for staff in staffs_serializer.data:
                    # 已经中奖的员工排除
                    if staff['winning'] is True and request.data['staff_id'] == '999998':
                        continue
                    serializer = self.get_serializer(data=staff)
                    try:
                        serializer.is_valid(raise_exception=True)
                        self.perform_create(serializer)
                    except ValidationError as exc:
                        request_api.log('ValidationError')
                        continue
                request_api.send_long_message({'activity': '001'})
                return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
        except self.model_class.MultipleObjectsReturned as e:
            request_api.log('data MultipleObjectsReturned')

        if serializer is None:
            # 验证当前活动是否可以参加
            try:
                activity = Activity.objects.get(processing=True)
                if activity.activity_id != '000':
                    return Response({'error': 'invalid activity'}, status=status.HTTP_400_BAD_REQUEST)
            except Activity.DoesNotExist as e:
                request_api.log('no processing activity')
            except Activity.MultipleObjectsReturned as e:
                request_api.log('more than 1 processing activity')

            # 参加活动
            staff_data = None
            try:
                staff_data = Staff.objects.get(staff_id=request.data['staff_id'])
            except self.model_class.DoesNotExist as e:
                return Response({'error': 'invalid staff_id'}, status=status.HTTP_400_BAD_REQUEST)
            except self.model_class.MultipleObjectsReturned as e:
                return Response({'error': 'invalid staff_id'}, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            data['open_id'] = staff_data.open_id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # 更新员工剩余参加次数
            try:
                staff_serializer = StaffSerializer(staff_data)
                staff_data.times = staff_data.times - 1
                staff_serializer = StaffSerializer(staff_data, data=staff_serializer.data)
                staff_serializer.is_valid(raise_exception=True)
                self.perform_update(staff_serializer)
            except Exception as e:
                data = self.model_class.objects.get(staff_id=staff_data.staff_id)
                self.perform_destroy(data)
        else:
            # 更新
            request_api.clone(data, request.data, self.serializer_class, self.primary_key)

            serializer = self.get_serializer(data, data=serializer.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        request_api.send_long_message({'activity': '001'})
        return Response(serializer.data, status=status.HTTP_200_OK)
