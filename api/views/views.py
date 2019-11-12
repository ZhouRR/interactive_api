from rest_framework import viewsets

from api.serializers import *


from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})


def activity(request):
    return render(request, 'activity.html', {})


def prize(request):
    return render(request, 'prize.html', {})


def processing_staff(request):
    return render(request, 'processing_staff.html', {})


def staffs(request):
    return render(request, 'staffs.html', {})


class UserViewSet(viewsets.ModelViewSet):
    """ 45,34
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
