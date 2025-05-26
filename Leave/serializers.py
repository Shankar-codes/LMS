# from rest_framework import serializers
# from .models import Leave,LeaveRequest
#
# class LeaveSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Leave
#         fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'is_approved']  # Include all necessary fields
#         read_only_fields = ['status', 'is_approved']  # Make these fields read-only if they're updated by admins only
#
#     def create(self, validated_data):
#         # Ensure the request context is available
#         request = self.context.get('request')
#         if request and hasattr(request, 'user'):
#             validated_data['user'] = request.user
#         else:
#             raise serializers.ValidationError("User information is missing in the request context.")
#         return super().create(validated_data)
#
#
# class LeaveRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveRequest
#         fields = '__all__'

from rest_framework import serializers
from .models import Leave, LeaveRequest

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            'id', 'user', 'startdate', 'enddate', 'leavetype', 'leave_category',
            'start_time', 'end_time', 'reason', 'status', 'is_approved',
            'defaultdays', 'updated', 'created', 'half_day'
        ]
        read_only_fields = ['user', 'status', 'is_approved', 'updated', 'created']

    def create(self, validated_data):
        # Assign the logged-in user to the leave request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'user', 'start_date', 'end_date', 'reason', 'status'
        ]
        read_only_fields = ['user', 'status']

    def create(self, validated_data):
        # Assign the logged-in user to the leave request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)