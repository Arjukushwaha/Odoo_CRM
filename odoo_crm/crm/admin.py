from django.contrib import admin
from .models import Lead, Customer
from django.urls import path
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        return HttpResponseRedirect('/dashboard/')

admin.site.register(Lead)
admin.site.register(Customer)

