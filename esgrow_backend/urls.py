from django.urls import path, include

from .views import LoginUserView, CreateUserView, EscrowTransactionsView, EscrowTransactionAddView, update_transaction, \
    search_users

urlpatterns = [
    path("v1/users/register", CreateUserView.as_view(), name="users"),
    path("v1/users/login", LoginUserView.as_view(), name="login"),
    path("v1/transactions/view", EscrowTransactionsView.as_view(), name="view_transactions"),
    path("v1/transactions/confirm/<uuid:transaction_id>", update_transaction, name=""),
    path("v1/transactions/create", EscrowTransactionAddView.as_view(), name="create_transactions"),
    path("v1/users/search", search_users, name="search_users")
]
