from django.db import models


class Invoice(models.Model):
    vs = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(null=True)
    due_date = models.DateField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Faktura {self.vs}: {self.amount} Kč"


class Transaction(models.Model):
    vs = models.CharField(max_length=50, blank=True, default="")
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)
    matched_invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )

    def __str__(self):
        return f"Transakce {self.vs}: {self.amount} Kč ({self.transaction_date})"