from django.urls import path, include

from .views import LoginUserView, CreateUserView, EscrowTransactionsView, EscrowTransactionAddView

urlpatterns = [
    path("v1/users/register", CreateUserView.as_view(), name="users"),
    path("v1/users/login", LoginUserView.as_view(), name="login"),
    path("v1/transactions/view", EscrowTransactionsView.as_view(), name="view_transactions"),
    path("v1/transactions/create", EscrowTransactionAddView.as_view(), name="create_transactions"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework_auth'))
]
