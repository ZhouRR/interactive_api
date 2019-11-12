from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

import random

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

        # 中奖员工
        if 'staff_id' in request.data:
            staff_data = Staff.objects.get(staff_id=request.data['staff_id'])
            staff_serializer = StaffSerializer(staff_data)
            staff_data.winning = True
            staff_data.times = 0
            staff_serializer = StaffSerializer(staff_data, data=staff_serializer.data)
            staff_serializer.is_valid(raise_exception=True)
            self.perform_update(staff_serializer)

            data = self.model_class.objects.get(staff_id=request.data['staff_id'])
            self.perform_destroy(data)

            # 当前正在进行的活动
            prize_serializer = None
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

            request_api.send_long_message({'activity': '001'})
            return Response(staff_serializer.data, status=status.HTTP_200_OK)

        if 'lotteryCount' not in request.data:
            return Response({'error': 'invalid lotteryCount'}, status=status.HTTP_400_BAD_REQUEST)
        lottery_count = int(request.data['lotteryCount'])
        if lottery_count > queryset.count():
            return Response({'error': 'invalid lotteryCount'}, status=status.HTTP_400_BAD_REQUEST)

        # 参加员工
        processing_staffs = []
        for staff in serializer.data:
            processing_staffs += [staff['staff_id'], ]
        # 获奖员工
        lottery_staffs = random.sample(processing_staffs, lottery_count)
        # 移出未获奖员工
        for staff_id in processing_staffs:
            if staff_id not in lottery_staffs:
                data = self.model_class.objects.get(staff_id=staff_id)
                self.perform_destroy(data)
        request_api.send_long_message({'activity': '001'})
        return Response(lottery_staffs, status=status.HTTP_200_OK)
