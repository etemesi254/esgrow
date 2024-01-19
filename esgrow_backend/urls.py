from django.urls import path, include
from rest_framework import serializers, routers, viewsets

from . import views
from .api import CreateUserView
from .models import User, EscrowTransactions


class SerializedTransaction(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EscrowTransactions
        fields = ["transaction_id", "from_user", "to_user", "amount", "stage", "created_date", "modified_date"]


# ViewSets define the view behavior.
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SerializedTransaction


router = routers.DefaultRouter()
router.register(r"transactions", TransactionViewSet)
# router.register(r"users", CreateUserView, basename="CreateUser")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/users/register", CreateUserView.as_view(), name="users"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_auth'))

]
