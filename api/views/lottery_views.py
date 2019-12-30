import json
import random

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api.serializers import *

from api.utils import request_api


class LotteryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    primary_key = 'staff_id'
    queryset = Empty1.objects.all()
    model_class = ProcessingStaff
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
        queryset = self.model_class.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        data = None

        # 添加投票次数
        if 'staff_id' in request.data and request.data['staff_id'] == '-999999':
            processing_queryset = ProcessingStaff.objects.all()
            processing_staff_mapping = \
                {processing_staff.staff_id: processing_staff for processing_staff in processing_queryset}
            staffs = Staff.objects.filter(is_bse=False, winning=False, times__lt=3,
                                          staff_id__in=processing_staff_mapping)
            # 加剩余次数
            for staff in staffs:
                staff.times += 1
            staffs_serializer = StaffSerializer(staffs, many=True)
            serializer = StaffSerializer(staffs, data=staffs_serializer.data, many=True)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except ValidationError as exc:
                request_api.log(exc)
            self.perform_destroy(processing_queryset)
            request_api.send_long_message({'activity': '001'})
            return Response(serializer.data, status=status.HTTP_200_OK)
        # 中奖员工
        elif 'staff_id' in request.data:
            # 将当前奖品移出奖池
            prize_serializer = None
            prize = None
            try:
                activity = Activity.objects.get(processing=True)
                prize = Prize.objects.get(prize_id=activity.prize)
                prize_serializer = PrizeSerializer(prize)
                prize.distribution = True
                prize_serializer = PrizeSerializer(prize, data=prize_serializer.data)
                prize_serializer.is_valid(raise_exception=True)
                self.perform_update(prize_serializer)
            except Activity.DoesNotExist as e:
                request_api.log('no processing activity')
            except Activity.MultipleObjectsReturned as e:
                request_api.log('more than 1 processing activity')
            except Prize.DoesNotExist as e:
                request_api.log('no processing prize')
            except Prize.MultipleObjectsReturned as e:
                request_api.log('more than 1 processing prize')
            except ValidationError as exc:
                request_api.log('prize update fail')

            # 更新获奖的员工信息
            staff_data = Staff.objects.get(staff_id=request.data['staff_id'])
            staff_serializer = StaffSerializer(staff_data)
            staff_data.winning = True
            staff_data.times = 0
            staff_data.prize = prize.prize_id
            staff_serializer = StaffSerializer(staff_data, data=staff_serializer.data)
            staff_serializer.is_valid(raise_exception=True)
            self.perform_update(staff_serializer)

            data = self.model_class.objects.get(staff_id=request.data['staff_id'])
            self.perform_destroy(data)

            return Response(staff_serializer.data, status=status.HTTP_200_OK)

        # 参加员工
        processing_staffs = []
        for staff in serializer.data:
            processing_staffs += [staff['staff_id'], ]
        # 获奖员工
        if 'lottery_staffs' in request.data:
            lottery_staffs = request.data['lottery_staffs']
        else:
            if 'lotteryCount' not in request.data:
                return Response({'error': 'invalid lotteryCount'}, status=status.HTTP_400_BAD_REQUEST)
            lottery_count = int(request.data['lotteryCount'])
            if lottery_count > queryset.count():
                return Response({'error': 'invalid lotteryCount'}, status=status.HTTP_400_BAD_REQUEST)
            lottery_staffs = random.sample(processing_staffs, lottery_count)
        # 移出未获奖员工
        for staff_id in processing_staffs:
            if staff_id not in lottery_staffs:
                data = self.model_class.objects.get(staff_id=staff_id)
                self.perform_destroy(data)
        update_serializer = ActivitySerializer(Activity.objects.all(), many=True)
        prize = '001'
        # 更新进行中的活动为小游戏
        for activity in update_serializer.data:
            update_from_data = Activity.objects.get(activity_id=activity['activity_id'])
            update_to_serializer = ActivitySerializer(update_from_data)
            if update_from_data.activity_id == '001':
                prize = update_from_data.prize
            if update_from_data.activity_id == '002':
                update_from_data.processing = True
                update_from_data.prize = prize
            else:
                update_from_data.processing = False
            update_to_serializer = ActivitySerializer(update_from_data, data=update_to_serializer.data)
            update_to_serializer.is_valid(raise_exception=True)
            self.perform_update(update_to_serializer)
            # 备份数据
            staff_serializer = StaffSerializer(Staff.objects.all(), many=True)
            processing_serializer = ProcessingStaffSerializer(ProcessingStaff.objects.all(), many=True)
            prize_serializer = PrizeSerializer(Prize.objects.all(), many=True)
            backup = {'staff': staff_serializer.data,
                      'processing': processing_serializer.data,
                      'prize': prize_serializer.data}
            request_api.save_backup(json.dumps(backup))
        request_api.send_long_message({'activity': '003',
                                       'lottery_staffs': lottery_staffs})
        return Response(lottery_staffs, status=status.HTTP_200_OK)
