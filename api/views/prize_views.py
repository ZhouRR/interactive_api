from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from api.serializers import *

from api.utils import request_api


class PrizeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    primary_key = 'prize_id'
    model_class = Prize
    queryset = model_class.objects.all()
    serializer_class = PrizeSerializer
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
        if 'prize_file' in request.data:
            self.perform_destroy(self.get_queryset())
            prizes = handle_upload_file(request.FILES.get('prize_file', None))
            for prize in prizes:
                prize_detail = prize.split(',')
                data = {'prize_id': prize_detail[0], 'prize_name': prize_detail[1], 'prize_memo': prize_detail[2]}
                serializer = self.get_serializer(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                except ValidationError as exc:
                    request_api.log('ValidationError')
                    continue
            return Response({'prizes': prizes}, status=status.HTTP_200_OK)
        try:
            data = self.model_class.objects.get(prize_id=request.data[self.primary_key])
            # 删除奖品
            if request_api.is_delete(request.data, self.serializer_class, self.primary_key):
                self.perform_destroy(data)
                return Response({request.data[self.primary_key]}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(data)
        except self.model_class.DoesNotExist as e:
            request_api.log('data DoesNotExist')
        except self.model_class.MultipleObjectsReturned as e:
            request_api.log('data MultipleObjectsReturned')
        except MultiValueDictKeyError as e:
            request_api.log('data MultiValueDictKeyError')

        if serializer is None:
            # 添加奖品
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        else:
            # 更新奖品
            request_api.clone(data, request.data, self.serializer_class, self.primary_key)

            serializer = self.get_serializer(data, data=serializer.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


def handle_upload_file(uploaded_file):
    if "prize" not in uploaded_file.name:
        return None
    for chunk in uploaded_file.chunks():
        prize_str = chunk.decode("utf-8")
        return prize_str.split('\n')
