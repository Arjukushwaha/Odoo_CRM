from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
    LeadViewSet,
    CustomerViewSet,
    leads_and_customers,
    update_lead,
    delete_lead,
    update_customer,
    delete_customer,
    dashboard,
    
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'leads', LeadViewSet)
router.register(r'customers', CustomerViewSet)
#router.register(r'leads_and_customers', leads_and_customers)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('leads_and_customers/', leads_and_customers, name='leads_and_customers'),
    path('leads/<int:pk>/update/', update_lead, name='update_lead'),
    path('leads/<int:pk>/delete/', delete_lead, name='delete_lead'),
    path('customers/<int:pk>/update/', update_customer, name='update_customer'),
    path('customers/<int:pk>/delete/', delete_customer, name='delete_customer'),
    path('dashboard/', dashboard, name='dashboard'),
   
]