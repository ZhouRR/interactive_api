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
        if 'staffId' not in request.data:
            # 创建新员工
            if 'staff_id' in request.data and request.data['staff_id'] is not '':
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({'error': 'invalid parameter'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取openid
        openid = weixin_api.get_openid(request.data)
        if openid is None:
            return Response({'error': 'invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        staff_id = request.data['staffId']
        if staff_id is not '':
            # 未绑定openid,根据员工号取staff
            try:
                staff = Staff.objects.get(staff_id=staff_id)
            except Staff.DoesNotExist as e:
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
            except Staff.MultipleObjectsReturned as e:
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 绑定openid,根据员工号取staff
            try:
                staff = Staff.objects.get(open_id=openid)
            except Staff.DoesNotExist as e:
                return Response({'error': 'invalid openid'}, status=status.HTTP_400_BAD_REQUEST)
            except Staff.MultipleObjectsReturned as e:
                return Response({'error': 'invalid openid'}, status=status.HTTP_400_BAD_REQUEST)

        # 绑定openid
        staff_serializer = self.get_serializer(staff)
        if staff.open_id is '':
            staff.open_id = openid
            staff.nick_name = ''

            staff_serializer = self.get_serializer(staff, data=staff_serializer.data)
            try:
                staff_serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                request_api.log('ValidationError: ', e)
                return Response({'error': 'invalid staff'}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(staff_serializer)

        # 当前正在进行的活动
        activity_serializer = None
        try:
            activity = Activity.objects.get(processing=True)
            activity_serializer = ActivitySerializer(activity)
        except Activity.DoesNotExist as e:
            request_api.log('no processing activity')
        except Activity.MultipleObjectsReturned as e:
            request_api.log('more than 1 processing activity')

        resp = {'staff': staff_serializer.data}
        if activity_serializer is not None:
            resp = {'staff': staff_serializer.data, 'activity': activity_serializer.data}
            if activity_serializer.data['activity_id'] == '000' or activity_serializer.data['activity_id'] == '001':
                # 统计参加活动的人数
                processing_staffs = ProcessingStaff.objects.all()
                processing_count = processing_staffs.count()
                winning_rate = processing_count / self.get_queryset().count() * 100

                # 验证是否已经参加抽奖
                try:
                    processing_staff = ProcessingStaff.objects.get(staff_id=staff_serializer.data['staff_id'])
                    can_join = False
                except ProcessingStaff.DoesNotExist as e:
                    can_join = True
                except ProcessingStaff.MultipleObjectsReturned as e:
                    can_join = True

                # 验证剩余次数
                times = staff_serializer['times'].value
                if times <= 0:
                    can_join = False

                resp = {
                    'staff': staff_serializer.data,
                    'activity': activity_serializer.data,
                    'processing_count': processing_count,
                    'winning_rate': winning_rate,
                    'canJoin': can_join
                }
        return Response(resp, status=status.HTTP_200_OK)
