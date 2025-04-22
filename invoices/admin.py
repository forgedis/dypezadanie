from django.contrib import admin

from invoices.models import Invoice, Transaction


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['vs', 'issue_date', 'due_date', 'amount', 'note']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['vs', 'transaction_date', 'amount', 'note']
