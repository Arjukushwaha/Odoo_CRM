from django.shortcuts import render,redirect,get_object_or_404
from rest_framework import viewsets, status
from .models import Lead, Customer
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import LeadSerializer, CustomerSerializer
from rest_framework.permissions import IsAuthenticated
from .odoo_client import OdooClient
import logging
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils.timezone import now, timedelta

odoo_client = OdooClient()

def leads_and_customers(request):
   
    leads = Lead.objects.all()
    customers = Customer.objects.all()
    return render(request, 'leads_and_customers.html', {'leads': leads, 'customers': customers})

def update_lead(request, pk):
    
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.name = request.POST.get('name')
        lead.email = request.POST.get('email')
        lead.save()
        if lead.odoo_id:
            odoo_client.update_lead(lead.odoo_id, lead.name, lead.email)
        return redirect('leads_and_customers')
    
def delete_lead(request, pk):
   
    lead = get_object_or_404(Lead, pk=pk)
    if lead.odoo_id:
        odoo_client.delete_lead(lead.odoo_id)
    lead.delete()
    return redirect('leads_and_customers')

def update_customer(request, pk):
    
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.save()
        if customer.odoo_id:
            odoo_client.update_customer(customer.odoo_id, customer.name, customer.email, customer.phone)
        return redirect('leads_and_customers')
    
def delete_customer(request, pk):
    
    customer = get_object_or_404(Customer, pk=pk)
    if customer.odoo_id:
        odoo_client.delete_customer(customer.odoo_id)
    customer.delete()
    return redirect('leads_and_customers')

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    filter_backends=[SearchFilter,OrderingFilter,DjangoFilterBackend]
    search_fields=['name','email']
    filterset_fields=['status']
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        lead = serializer.save()
        odoo_id=odoo_client.create_lead(lead.name, lead.email)
        if odoo_id:
            lead.odoo_id = odoo_id
            lead.save()

    def destroy(self, request, *args, **kwargs):
        lead = self.get_object()
        if lead.odoo_id:
            odoo_client.delete_lead(lead.odoo_id)  
        lead.delete()
        return Response({'status': 'Lead deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        lead = self.get_object()
        serializer = self.get_serializer(lead, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_lead = serializer.save()
        if update_lead.odoo_id:
            odoo_client.update_lead(updated_lead.odoo_id, updated_lead.name, updated_lead.email)
        return Response(serializer.data)
    @action(detail=True, methods=['post'])
    def convert_to_opportunity(self, request,pk=None):
        lead= self.get_object()
        lead.status = 'Qualified'
        lead.save()
        if lead.odoo_id:
            odoo_client.update_lead(lead.odoo_id, lead.name, lead.email)
        return Response({'status': 'Lead converted to opportunity'}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'])
    def stats(self,request):
        stats={
            'total_leads': Lead.objects.count(),
            'new_leads': Lead.objects.filter(status='New').count(),
            'contacted_leads': Lead.objects.filter(status='Contacted').count(),
            'qualified_leads': Lead.objects.filter(status='Qualified').count(),
            'lost_leads': Lead.objects.filter(status='Lost').count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends=[SearchFilter,OrderingFilter]
    search_fields=['name','email','phone']
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        customer = serializer.save()
        odoo_id=odoo_client.create_customer(customer.name, customer.email, customer.phone)
        if odoo_id:
            customer.odoo_id = odoo_id
            customer.save()
            
    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        
        if customer.odoo_id:
            odoo_client.delete_customer(customer.odoo_id)
        customer.delete()
        return Response({'status': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        customer = self.get_object()
        serializer = self.get_serializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_customer = serializer.save()
        if updated_customer.odoo_id:
            odoo_client.update_customer(updated_customer.odoo_id, updated_customer.name, updated_customer.email, updated_customer.phone)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def stats(self,request):
        stats={
            'total_customers': Customer.objects.count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
    
def dashboard(request):
    last_week = now() - timedelta(days=7)
    analytics = {
        'total_leads': Lead.objects.count(),
        'leads_by_status': Lead.objects.values('status').annotate(count=Count('status')),
        'total_customers': Customer.objects.count(),
        'new_customers_last_week': Customer.objects.filter(created_at__gte=last_week).count(),
    }
    return render(request, 'dashboard.html', {'analytics': analytics})

