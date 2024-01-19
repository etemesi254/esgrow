from django.contrib import admin

from esgrow_backend.models import EscrowTransactions, User

# Register your models here.
admin.site.register(EscrowTransactions)
admin.site.register(User)

