from django.db import models
from django.conf import settings
from utils.models import UUIDModel
from apps.product.models import Product 
from utils.invoice import generate_invoice

class Member(UUIDModel):
    telephone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    point = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'tr_members'
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def __str__(self):
        return f"{self.name} ({self.telephone})"


class Transaction(UUIDModel):
    invoice = models.CharField(max_length=255, unique=True, blank=True, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='transactions'
    )
    
    is_member = models.BooleanField(default=False)
    member = models.ForeignKey(
        Member, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='transactions'
    )
    telephone = models.CharField(max_length=20, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)

    payment_amount = models.PositiveIntegerField(default=0)
    change_amount = models.PositiveIntegerField(default=0)
    subtotal = models.PositiveIntegerField(default=0)
    
    is_point = models.BooleanField(default=False)
    point = models.PositiveIntegerField(null=True, blank=True, default=0)
    total_quantity = models.IntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'tr_transactions'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return self.invoice

    def save(self, *args, **kwargs):
        if not self.invoice:
            self.invoice = generate_invoice(Transaction)
        super(Transaction, self).save(*args, **kwargs)


class TransactionDetail(UUIDModel):
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='details'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT, 
        related_name='transaction_details'
    )
    
    price = models.PositiveIntegerField() 
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    class Meta:
        db_table = 'tr_transaction_details'
        verbose_name = "Transaction Detail"
        verbose_name_plural = "Transaction Details"

    def __str__(self):
        return f"{self.transaction.invoice} - {self.product.name}"