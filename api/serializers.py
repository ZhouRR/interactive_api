from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import Staff
from api.models import ProcessingStaff
from api.models import Activity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('created', 'nick_name', 'name', 'open_id', 'staff_id', 'winning', 'times')


class ProcessingStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStaff
        fields = ('created', 'name', 'open_id', 'staff_id')


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('created', 'activity_id', 'activity_name', 'activity_memo', 'processing')
