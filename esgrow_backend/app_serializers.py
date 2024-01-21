import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from esgrow_backend.models import User, EscrowTransactions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")
        write_only_fields = ("password",)
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("password", None)
        return response


class EscrowTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscrowTransactions
        fields = ("transaction_id", "stage", "amount", "from_user", "to_user", "created_date", "modified_date")
        read_only_fields = ("transaction_id", "stage", "created_date", "modified_date")

    def create(self, validated_data):
        transaction = EscrowTransactions.objects.create(
            amount=validated_data["amount"],
            stage="Initiated",
            from_user=validated_data["from_user"],
            to_user=validated_data["to_user"]
        )
        transaction.save()
        return transaction

    def to_representation(self, instance):
        response = super().to_representation(instance)

        return response


class EscrowViewTransactionSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(many=False, read_only=True)
    to_user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = EscrowTransactions
        fields = ("transaction_id", "stage", "amount", "from_user", "to_user", "created_date", "modified_date",
                  "from_user_confirmed", "from_user_confirmed_date", "to_user_confirmed", "to_user_confirmed_date")
        read_only_fields = ("transaction_id", "stage", "created_date", "modified_date")
