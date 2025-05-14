from rest_framework import serializers
from .models import Lead, Customer

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Lead
        fields='__all__'
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields='__all__'
        