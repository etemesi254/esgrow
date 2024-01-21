from django.contrib import admin

from esgrow_backend.models import EscrowTransactions, User, MonetaryTransactions, ComplianceDocuments

# Register your models here.
admin.site.register(EscrowTransactions)
admin.site.register(User)
admin.site.register(MonetaryTransactions)
admin.site.register(ComplianceDocuments)
