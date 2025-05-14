from django.db import models
from django.core.exceptions import ValidationError

class Lead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    odoo_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('New', 'New'),
            ('Contacted', 'Contacted'),
            ('Qualified', 'Qualified'),
            ('Lost', 'Lost'),
        ],
        default='New'
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='leads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def clean(self):
        if not self.email:
            raise ValidationError('Email is required.')

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    odoo_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.name} ({self.email})"