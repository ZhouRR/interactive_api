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


class StaffListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        staff_mapping = {staff.staff_id: staff for staff in instance}
        data_mapping = {item['staff_id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for staff_id, data in data_mapping.items():
            staff = staff_mapping.get(staff_id, None)
            if staff is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(staff, data))

        # Perform deletions.
        for staff_id, staff in staff_mapping.items():
            if staff_id not in data_mapping:
                staff.delete()

        return ret


class StaffSerializer(serializers.ModelSerializer):
    staff_id = serializers.CharField()

    ...
    staff_id = serializers.CharField(required=False)

    class Meta:
        model = Staff
        fields = ('created', 'nick_name', 'avatar', 'name', 'open_id', 'staff_id', 'winning', 'is_bse', 'times', 'prize')
        list_serializer_class = StaffListSerializer


class ProcessingStaffSerializer(serializers.ModelSerializer):
    staff_id = serializers.CharField()

    ...
    staff_id = serializers.CharField(required=False)

    class Meta:
        model = ProcessingStaff
        fields = ('created', 'name', 'avatar', 'open_id', 'staff_id', 'is_bse')
        list_serializer_class = StaffListSerializer


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('created', 'activity_id', 'activity_name', 'activity_memo', 'processing', 'prize')


class PrizeListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        prize_mapping = {prize.prize_id: prize for prize in instance}
        data_mapping = {item['prize_id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for prize_id, data in data_mapping.items():
            prize = prize_mapping.get(prize_id, None)
            if prize is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(prize, data))

        # Perform deletions.
        for prize_id, prize in prize_mapping.items():
            if prize_id not in data_mapping:
                prize.delete()

        return ret


class PrizeSerializer(serializers.ModelSerializer):
    prize_id = serializers.CharField()

    ...
    prize_id = serializers.CharField(required=False)

    class Meta:
        model = Prize
        fields = ('created', 'prize_id', 'prize_name', 'prize_memo', 'distribution')
        list_serializer_class = PrizeListSerializer


class LotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStaff
        fields = ('created', 'name', 'open_id', 'staff_id')
