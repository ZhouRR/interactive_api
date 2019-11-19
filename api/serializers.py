from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import Staff
from api.models import ProcessingStaff
from api.models import Activity
from api.models import Prize
from api.models import Empty1
from api.models import Empty2


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
        fields = ('created', 'nick_name', 'avatar', 'name', 'open_id', 'staff_id', 'winning', 'is_bse', 'times', 'prize')


class ProcessingStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStaff
        fields = ('created', 'name', 'avatar', 'open_id', 'staff_id', 'is_bse')


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('created', 'activity_id', 'activity_name', 'activity_memo', 'processing', 'prize')


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ('created', 'prize_id', 'prize_name', 'prize_memo', 'distribution')


class LotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStaff
        fields = ('created', 'name', 'open_id', 'staff_id')
