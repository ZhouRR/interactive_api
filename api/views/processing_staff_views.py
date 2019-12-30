from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

import random

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

        # 来自微信小程序之外
        if self.primary_key in request.data:
            try:
                data = self.model_class.objects.get(staff_id=request.data[self.primary_key])
                # 移出指定员工
                if request_api.is_delete(request.data, self.serializer_class, self.primary_key):
                    self.perform_destroy(data)
                    self.send_processing_message()
                    return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
                serializer = self.get_serializer(data)
            except self.model_class.DoesNotExist as e:
                request_api.log('data DoesNotExist')
                # 清空所有员工
                if 'staff_id' in request.data and request.data['staff_id'] == '-999999':
                    self.perform_destroy(self.get_queryset())
                    self.send_processing_message()
                    return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
                # 添加所有员工/未中奖员工
                if 'staff_id' in request.data and\
                        (request.data['staff_id'] == '999999' or request.data['staff_id'] == '999998'):
                    staffs = Staff.objects.filter(winning=False)
                    staffs_serializer = StaffSerializer(staffs, many=True)
                    serializer = self.get_serializer(self.model_class.objects.all(), data=staffs_serializer.data,
                                                     many=True)
                    try:
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)
                    except ValidationError as exc:
                        request_api.log(exc)
                    self.send_processing_message()
                    return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
                # 添加BSE
                elif 'staff_id' in request.data and\
                        (request.data['staff_id'] == '999997' or request.data['staff_id'] == '999996'):
                    staffs = Staff.objects.filter(is_bse=True, winning=False, times__gt=0)
                    if staffs.count() == 0:
                        return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
                    # 随机
                    if request.data['staff_id'] == '999996':
                        random_count = int(len(staffs)/14*3)
                        if random_count == 0:
                            random_count = 1
                        bse_data = random.sample(list(staffs), random_count)
                    else:
                        bse_data = staffs
                    staffs_serializer = StaffSerializer(bse_data, many=True)

                    # 添加BSE
                    staff_ids = [staff.staff_id for staff in bse_data]
                    processing_staffs = self.model_class.objects.filter(staff_id__in=staff_ids)
                    serializer = self.get_serializer(processing_staffs, data=staffs_serializer.data,
                                                     many=True)
                    try:
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)
                        # 减去剩余次数
                        for staff in bse_data:
                            staff.times -= 1
                        staffs_serializer = StaffSerializer(bse_data, many=True)
                        serializer = StaffSerializer(bse_data, data=staffs_serializer.data, many=True)
                        try:
                            serializer.is_valid(raise_exception=True)
                            self.perform_update(serializer)
                        except ValidationError as exc:
                            request_api.log(exc)
                    except ValidationError as exc:
                        request_api.log(exc)

                    self.send_processing_message()
                    return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
                # 添加参与过投票未中奖的员工
                elif 'staff_id' in request.data and request.data['staff_id'] == '999995':
                    staffs = Staff.objects.filter(is_bse=False, winning=False, times__lt=3)
                    staffs_serializer = StaffSerializer(staffs, many=True)
                    serializer = self.get_serializer(self.model_class.objects.all(), data=staffs_serializer.data,
                                                     many=True)
                    try:
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)
                    except ValidationError as exc:
                        request_api.log(exc)
                    self.send_processing_message()
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
                staff_data = Staff.objects.get(open_id=request.data['token'])
            except self.model_class.DoesNotExist as e:
                return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            except self.model_class.MultipleObjectsReturned as e:
                return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            except KeyError as e:
                return Response({'error': 'need token'}, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            data['staff_id'] = staff_data.staff_id
            data['avatar'] = staff_data.avatar
            data['is_bse'] = staff_data.is_bse
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
                self.send_processing_message()
            except Exception as e:
                data = self.model_class.objects.get(staff_id=staff_data.staff_id)
                self.perform_destroy(data)
                return Response({'error': 'update times exception'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 更新
            request_api.clone(data, request.data, self.serializer_class, self.primary_key)

            serializer = self.get_serializer(data, data=serializer.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def send_processing_message(self):
        # 统计参加活动的人数
        processing_staffs = self.model_class.objects.all()
        processing_count = processing_staffs.count()
        winning_rate = processing_count / Staff.objects.all().count() * 100
        request_api.send_long_message({'activity': '002',
                                       'processing_count': processing_count,
                                       'winning_rate': winning_rate})
