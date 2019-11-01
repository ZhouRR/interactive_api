from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from api.serializers import *

from api.utils import request_api


class ActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Activity.objects.all()
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
        activity_serializer = None
        try:
            activity = Activity.objects.get(activity_id=request.data['activity_id'])
            if request_api.is_delete(request.data, 'activity_name', 'activity_memo'):
                self.perform_destroy(activity)
                return Response({request.data['activity_id']}, status=status.HTTP_200_OK)
            activity_serializer = self.get_serializer(activity)
        except Activity.DoesNotExist as e:
            request_api.log('data DoesNotExist')
        except Activity.MultipleObjectsReturned as e:
            request_api.log('data MultipleObjectsReturned')

        if activity_serializer is None:
            activity_serializer = self.get_serializer(data=request.data)
            activity_serializer.is_valid(raise_exception=True)
            self.perform_create(activity_serializer)
        else:
            activity.activity_name = request.data['activity_name']
            activity.activity_memo = request.data['activity_memo']
            if 'processing' in request.data:
                activity.processing = request.data['processing']
            else:
                activity.processing = False

            activity_serializer = self.get_serializer(activity, data=activity_serializer.data)
            activity_serializer.is_valid(raise_exception=True)
            self.perform_update(activity_serializer)

        return Response(activity_serializer.data, status=status.HTTP_200_OK)
