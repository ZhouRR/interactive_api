from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from api.serializers import *

from api.utils import request_api


class ActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    primary_key = 'activity_id'
    model_class = Activity
    queryset = model_class.objects.all()
    serializer_class = ActivitySerializer
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
            data = self.model_class.objects.get(activity_id=request.data[self.primary_key])
            # 删除活动
            if request_api.is_delete(request.data, self.serializer_class, self.primary_key):
                self.perform_destroy(data)
                return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data)
        except self.model_class.DoesNotExist as e:
            request_api.log('data DoesNotExist')
        except self.model_class.MultipleObjectsReturned as e:
            request_api.log('data MultipleObjectsReturned')

        # 其他活动去除'正在进行'
        if 'processing' in request.data and (request.data['processing'] == 'true' or request.data['processing'] is True):
            update_serializer = self.get_serializer(self.get_queryset(), many=True)
            for activity in update_serializer.data:
                update_from_data = self.model_class.objects.get(activity_id=activity[self.primary_key])
                update_to_serializer = self.get_serializer(update_from_data)
                update_from_data.processing = False
                update_to_serializer = self.get_serializer(update_from_data, data=update_to_serializer.data)
                update_to_serializer.is_valid(raise_exception=True)
                self.perform_update(update_to_serializer)

        if serializer is None:
            # 添加活动
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        else:
            # 更新活动
            request_api.clone(data, request.data, self.serializer_class, self.primary_key, 'processing')
            if 'processing' in request.data:
                data.processing = request.data['processing']
            else:
                data.processing = False

            serializer = self.get_serializer(data, data=serializer.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
