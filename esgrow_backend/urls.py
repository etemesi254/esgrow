from django.urls import path, include
from rest_framework import serializers, routers, viewsets

from . import views
from .models import User, EscrowTransactions
from .views import LoginUserView, CreateUserView, EscrowTransactionsView


class SerializedTransaction(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EscrowTransactions
        fields = ["transaction_id", "from_user", "to_user", "amount", "stage", "created_date", "modified_date"]





urlpatterns = [
    path("v1/users/register", CreateUserView.as_view(), name="users"),
    path("v1/users/login", LoginUserView.as_view(), name="login"),
    path("v1/transactions/", EscrowTransactionsView.as_view(), name="transactions"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_auth'))
]
