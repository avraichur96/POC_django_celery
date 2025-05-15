from rest_framework import serializers

from .models import *


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Write only for password ensures we do not serialize this fields in listing by mistake if we use the same serializer.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'password', 'phone_number')

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            phone_number=validated_data.get('phone_number', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscribeRequestSerializer(serializers.Serializer):
    """
    Handles both subscribe/ unsubscribe request.
    """
    username = serializers.CharField(required=True)
    is_subscribe = serializers.BooleanField(required=False, default=True)
    plan_id = serializers.IntegerField(required=True)


class ListInvoicesRequestSerializer(serializers.Serializer):
    """
    Handles invoices listing filter inputs.
    """

    username = serializers.CharField(required=False)
    plan_id = serializers.IntegerField(required=False)
    status = serializers.IntegerField(required=False)


class ListInvoicesOutputSerializer(serializers.ModelSerializer):
    """
    Handles output data format from the listing invoices view.
    """
    username = serializers.CharField(source="user.username")
    plan_name = serializers.CharField(source="plan.name")
    plan_description = serializers.CharField(source="plan.description")

    class Meta:
        model = Invoice
        include = ["username", "plan_name", "plan_description", "issue_date", "due_date", "status"]
