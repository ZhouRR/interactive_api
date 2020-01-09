from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ValidationError

from api.serializers import *

from api.utils import weixin_api, request_api


class StaffViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        staffs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(staffs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        staffs_serializer = self.get_serializer(staffs, many=True)
        return Response(staffs_serializer.data, status=status.HTTP_200_OK)

    """
    Retrieve a model instance.
    """
    def create(self, request, *args, **kwargs):
        # 小程序以外,API ROOT
        if 'staffId' not in request.data:
            return self.create_staff(request)
        # 获取openid
        openid = weixin_api.get_openid(request.data)
        if openid is None:
            return Response({'error': 'invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        staff_id = request.data['staffId']
        # 根据staff_id或openid获取员工信息
        staff = self.get_staff(staff_id, openid)
        if isinstance(staff, Response):
            return staff

        if staff is not None:
            # 绑定过openid,根据openid取staff,去除openid
            staffs = Staff.objects.filter(open_id=openid)
            if staffs.count() > 0:
                staffs_serializer = self.get_serializer(staffs, many=True)
                for staff_bound_dict in staffs_serializer.data:
                    # 未绑定过openid,根据员工号取staff
                    try:
                        staff_bound = Staff.objects.get(staff_id=staff_bound_dict['staff_id'])
                        self.set_user_info(staff_bound, '', {})
                    except Staff.DoesNotExist as e:
                        continue
            # 解绑openid
            if 'logout' in request.data and request.data['logout'] == '1':
                return Response({'error': 'logout'}, status=status.HTTP_400_BAD_REQUEST)
            # 绑定openid
            self.set_user_info(staff, openid, request.data)

            # 已经中奖时,替换奖品id为奖品名称
            if staff.prize != '':
                staff = self.get_prize_name(staff)
            staff_serializer = self.get_serializer(staff)
            resp = {'staff': staff_serializer.data}
        else:
            resp = {}
            staff_serializer = None

        # 当前正在进行的活动
        activity_serializer = None
        processing_number = '1'
        prize_count = 1
        try:
            activity = Activity.objects.get(processing=True)
            processing_number = activity.prize
            prize = Prize.objects.get(prize_id=activity.prize)
            activity.prize = prize.prize_name
            activity_serializer = ActivitySerializer(activity)
            prize_count = Prize.objects.all().count()
        except Activity.DoesNotExist as e:
            request_api.log('no processing activity')
        except Activity.MultipleObjectsReturned as e:
            request_api.log('more than 1 processing activity')
        except Prize.DoesNotExist as e:
            request_api.log('no processing prize')
        except Prize.MultipleObjectsReturned as e:
            request_api.log('more than 1 processing prize')

        if activity_serializer is not None:
            resp['activity'] = activity_serializer.data
            resp['processing_number'] = processing_number[-2:]
            resp['prize_count'] = prize_count
            # 统计参加活动的人数
            processing_staffs = ProcessingStaff.objects.all()
            processing_count = processing_staffs.count()
            winning_rate = processing_count / self.get_queryset().count() * 100
            shooting = False

            # 验证是否已经参加抽奖
            if staff_serializer is None:
                shooting = False
                can_join = False
            else:
                try:
                    ProcessingStaff.objects.get(staff_id=staff_serializer.data['staff_id'])
                    shooting = True
                    can_join = False
                except ProcessingStaff.DoesNotExist as e:
                    can_join = activity_serializer.data['activity_id'] == '000'
                except ProcessingStaff.MultipleObjectsReturned as e:
                    can_join = False
                # 验证剩余次数
                times = staff_serializer['times'].value
                if times <= 0:
                    can_join = False

            resp['processing_count'] = processing_count
            resp['winning_rate'] = winning_rate
            resp['canJoin'] = can_join
            resp['shooting'] = shooting
        return Response(resp, status=status.HTTP_200_OK)

    def create_staff(self, request):
        # 创建新员工
        if 'staff_id' in request.data and request.data['staff_id'] is not '':
            staff_data = None
            try:
                staff_data = Staff.objects.get(staff_id=request.data['staff_id'])
            except Staff.DoesNotExist as e:
                # 创建新员工
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except Staff.MultipleObjectsReturned as e:
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
            if staff_data is not None:
                # 移出指定员工
                if request_api.is_delete(request.data, self.serializer_class, 'staff_id'):
                    self.perform_destroy(staff_data)
                    return Response({request.data['staff_id']}, status=status.HTTP_200_OK)
                # 更新员工
                request_api.clone(staff_data, request.data, self.serializer_class, 'staff_id', 'times')
                if 'times' in request.data and request.data['times'] != '':
                    staff_data.times = request.data['times']
                serializer = self.get_serializer(staff_data, data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'invalid parameter'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_staff(staff_id, open_id):
        if staff_id is not '':
            # 未绑定过openid,根据员工号取staff
            try:
                staff = Staff.objects.get(staff_id=staff_id)
            except Staff.DoesNotExist as e:
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
            except Staff.MultipleObjectsReturned as e:
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 绑定过openid,根据openid取staff
            try:
                staff = Staff.objects.get(open_id=open_id)
            except Staff.DoesNotExist as e:
                return Response({'error': 'invalid openid'}, status=status.HTTP_400_BAD_REQUEST)
            except Staff.MultipleObjectsReturned as e:
                return Response({'error': 'invalid openid'}, status=status.HTTP_400_BAD_REQUEST)
        return staff

    def get_prize_name(self, staff):
        try:
            prize_data = Prize.objects.get(prize_id=staff.prize)
            staff.prize = prize_data.prize_name
        except Prize.DoesNotExist as e:
            request_api.log('no prize')
        except Prize.MultipleObjectsReturned as e:
            request_api.log('more than 1 prize')
        return staff

    def set_user_info(self, staff, openid, request_data):
        staff_serializer = self.get_serializer(staff)
        staff.open_id = openid
        if 'nickName' in request_data:
            staff.nick_name = request_data['nickName']
        else:
            staff.nick_name = ''
        if 'avatarUrl' in request_data:
            staff.avatar = request_data['avatarUrl']
        else:
            staff.avatar = ''

        staff_serializer = self.get_serializer(staff, data=staff_serializer.data)
        try:
            staff_serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            request_api.log('ValidationError: ', e)
            return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(staff_serializer)
